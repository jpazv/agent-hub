"""Fase de scoring: le o cache local e calcula a qualidade de atendimento.

Nao toca o banco. Roda em segundos — e o loop de iteracao da formula.

Estrato: apenas leads respondidos em ate 30 min de expediente. Como a
velocidade da primeira resposta vira constante dentro do estrato, a dimensao
de responsividade foi redefinida para medir o RITMO ao longo da conversa
(min_resposta_media_humana), que continua variando muito (p10 1,4 min,
p90 456 min).
"""
from __future__ import annotations

import json
import pathlib
import re
import unicodedata

import numpy as np
import pandas as pd

BASE = pathlib.Path(__file__).parent
CACHE = BASE / "cache"

# ---------------------------------------------------------------- parametros

# Corte do estrato, em minutos de expediente.
CORTE_RESPOSTA_MIN = 30

# Pesos da composicao. Ajustar AQUI e so aqui.
#
# Responsividade foi REMOVIDA da composicao (peso 0) apos o diagnostico por
# decil: ela se comporta invertida (Spearman -0.14 contra conversao; decil 1
# converte 18,6% e decil 10 converte 5,3%).
#
# O motivo e que min_resposta_media_humana e o intervalo medio entre respostas:
# conversa longa e engajada se estende por horas com pausas naturais do lead,
# entao a media sobe. Troca curta que morre rapido tem media baixa. "Ritmo
# rapido" marca conversa morta, nao bom atendimento. A velocidade que importa
# — a da primeira resposta — ja e o filtro do estrato.
#
# A dimensao continua sendo calculada e exportada como diagnostico.
PESOS = {
    "cobertura": 0.30,
    "profundidade": 0.35,
    "responsividade": 0.00,
    "conducao": 0.35,
}

# Ordem canonica, inferida do proprio historico (ordem_detectada em
# lead_score_output): abordagem -> sondagem -> captura/apresentacao ->
# preco/agendamento. Preco e agendamento se alternam, entao a checagem de
# ordem tolera a troca entre os dois.
ORDEM_CANONICA = ["abordagem", "sondagem", "captura", "apresentacao", "preco", "agendamento"]
PARES_TOLERADOS = {("preco", "agendamento"), ("agendamento", "preco")}

# Peso por etapa na cobertura: etapa final vale mais que saudacao.
PESO_ETAPA = {
    "abordagem": 0.5,
    "sondagem": 1.5,
    "captura": 1.0,
    "apresentacao": 1.5,
    "preco": 1.2,
    "agendamento": 2.0,
}

# Saturacao da profundidade: a partir de quantas ocorrencias / termos
# distintos a etapa e considerada "bem executada".
SAT_OCORRENCIAS = 3
SAT_TERMOS = 3

# Responsividade: teto do ritmo em minutos (acima disso, nota 0).
TETO_RITMO_MIN = 480.0

# Conducao
SAT_PERGUNTAS = 4      # perguntas do atendente para nota cheia
SAT_ALTERNANCIA = 6    # trocas de turno para nota cheia

# Gate: conversa abandonada pelo atendente (lead falou por ultimo e ninguem
# respondeu) tem a nota multiplicada por isto.
PENALIDADE_ABANDONO = 0.55

# Mensagens de midia (audio/imagem/video) chegam com content nulo: o fornecedor
# de dados nao entrega transcricao. Isso e dado FALTANTE, nao atendimento ruim.
#
# A decisao e NAO imputar. Creditar etapas nao observadas trocaria falso
# negativo por falso positivo, e num experimento que testa justamente se
# qualidade preve conversao o falso positivo contamina o achado: se midia for
# mais comum nas conversas engajadas (que ja convertem), a imputacao inflaria o
# score onde a conversao ja e alta e a correlacao subiria por construcao.
#
# Em vez disso mede-se a cegueira (visibilidade_textual) e estratifica-se.
CORTE_VISIBILIDADE = 0.70


# ---------------------------------------------------------------- utilitarios

def normalizar(s: pd.Series) -> pd.Series:
    """minusculas + sem acento, para casar 'avaliacao' com 'avaliação'."""
    out = s.fillna("").astype(str).str.lower()
    out = out.map(
        lambda t: unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    )
    return out.str.replace(r"\s+", " ", regex=True)


def carregar_vocab() -> dict[str, list[str]]:
    vocab = json.loads((BASE / "vocab_atual.json").read_text(encoding="utf-8"))
    # Normaliza e remove duplicatas que colapsam ao tirar acento
    # ("avaliação"/"avaliacao" viram o mesmo termo).
    limpo = {}
    for etapa, termos in vocab.items():
        vistos, saida = set(), []
        for t in termos:
            n = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode("ascii")
            n = re.sub(r"\s+", " ", n).strip()
            if n and n not in vistos:
                vistos.add(n)
                saida.append(n)
        limpo[etapa] = saida
    return limpo


def _saturar(x, teto: float):
    return np.clip(np.asarray(x, dtype=float) / teto, 0, 1)


# ---------------------------------------------------------------- carga

def carregar():
    leads = pd.read_parquet(CACHE / "leads.parquet")
    msgs = pd.read_parquet(CACHE / "messages.parquet")
    baseline = pd.read_parquet(CACHE / "baseline.parquet")

    for c in ["primeira_msg_lead_em", "primeiro_humano_em", "ultima_msg_lead_em",
              "ultima_msg_humana_em", "marcou_agendamento", "realizou_av",
              "converteu_tto", "cancelou"]:
        leads[c] = pd.to_datetime(leads[c], errors="coerce")
    for c in ["min_ate_secretaria", "min_ate_secretaria_expediente",
              "min_resposta_media_humana", "pares_resposta_humana",
              "msg_total", "msg_inbound", "msg_humano", "msg_bot"]:
        leads[c] = pd.to_numeric(leads[c], errors="coerce")
    msgs["created_at"] = pd.to_datetime(msgs["created_at"], errors="coerce")
    return leads, msgs, baseline


def aplicar_estrato(leads: pd.DataFrame) -> pd.DataFrame:
    m = leads["min_ate_secretaria_expediente"] <= CORTE_RESPOSTA_MIN
    return leads[m].copy()


# ---------------------------------------------------------------- dimensoes

def preparar_mensagens(msgs: pd.DataFrame, leads: pd.DataFrame, vocab) -> pd.DataFrame:
    m = msgs[msgs["cw_id_tb_leads"].isin(leads["cw_id_tb_leads"])].copy()
    m = m.merge(leads[["cw_id_tb_leads", "primeiro_humano_em"]], on="cw_id_tb_leads", how="left")

    # Papel: sender_id nao serve (99,7% das saidas vem da conta de integracao
    # "WhatsApp"). O corte por primeiro_humano_em reproduz msg_humano exato em
    # 78% dos leads e com erro <=1 em 88% — ver README.
    saida = m["message_type"] == 1
    m["papel"] = np.where(
        ~saida, "lead",
        np.where(m["created_at"] >= m["primeiro_humano_em"], "atendente", "bot"),
    )

    m = m.sort_values(["cw_id_tb_leads", "created_at", "message_id"])
    m["seq"] = m.groupby("cw_id_tb_leads").cumcount()
    m["norm"] = normalizar(m["content"])
    m["pergunta"] = m["norm"].str.contains(r"\?", regex=True)

    for etapa, termos in vocab.items():
        pat = "|".join(re.escape(t) for t in termos)
        m[f"et_{etapa}"] = m["norm"].str.contains(pat, regex=True, na=False)
        m[f"nt_{etapa}"] = sum(
            m["norm"].str.contains(re.escape(t), regex=True, na=False).astype("int8")
            for t in termos
        )
    return m


def dimensoes(m: pd.DataFrame, leads: pd.DataFrame, vocab) -> pd.DataFrame:
    at = m[m["papel"] == "atendente"]
    etapas = list(vocab.keys())

    # --- presenca, ocorrencias, termos distintos e primeira posicao por etapa
    ag = {}
    for e in etapas:
        g = at.groupby("cw_id_tb_leads")
        ag[f"pres_{e}"] = g[f"et_{e}"].max()
        ag[f"occ_{e}"] = g[f"et_{e}"].sum()
        ag[f"trm_{e}"] = g.apply(lambda d, e=e: d.loc[d[f"et_{e}"], f"nt_{e}"].max(), include_groups=False)
        ag[f"pos_{e}"] = g.apply(lambda d, e=e: d.loc[d[f"et_{e}"], "seq"].min(), include_groups=False)
    df = pd.DataFrame(ag)
    df.index.name = "cw_id_tb_leads"
    df = df.reindex(leads["cw_id_tb_leads"]).fillna(0)

    pres = df[[f"pres_{e}" for e in etapas]].astype(bool)
    pres.columns = etapas

    # --- COBERTURA CONDICIONAL -------------------------------------------
    # Denominador nao e o total de etapas: e a etapa mais avancada alcancada.
    # Conversa que morreu cedo por culpa do lead nao e punida pelo que veio
    # depois. Este e o conserto central sobre a metrica atual.
    idx = {e: i for i, e in enumerate(ORDEM_CANONICA)}
    ordem_pres = pres[ORDEM_CANONICA].values
    alcance = np.where(ordem_pres.any(axis=1), ordem_pres.argmax(axis=1) * 0, 0)
    # indice da etapa mais avancada presente
    ult = np.full(len(pres), -1)
    for i, e in enumerate(ORDEM_CANONICA):
        ult = np.where(ordem_pres[:, i], i, ult)

    pesos_ord = np.array([PESO_ETAPA[e] for e in ORDEM_CANONICA])
    obtido = (ordem_pres * pesos_ord).sum(axis=1)
    mascara_ate = (np.arange(len(ORDEM_CANONICA))[None, :] <= ult[:, None])
    possivel = (mascara_ate * pesos_ord).sum(axis=1)
    cobertura = np.divide(obtido, possivel, out=np.zeros(len(pres)), where=possivel > 0)

    # bonus por ordem correta
    posicoes = df[[f"pos_{e}" for e in ORDEM_CANONICA]].values.astype(float)
    posicoes[~ordem_pres] = np.nan
    ordem_ok = np.ones(len(pres), dtype=bool)
    for i in range(len(ORDEM_CANONICA) - 1):
        for j in range(i + 1, len(ORDEM_CANONICA)):
            if (ORDEM_CANONICA[i], ORDEM_CANONICA[j]) in PARES_TOLERADOS:
                continue
            viola = posicoes[:, i] > posicoes[:, j]
            ordem_ok &= ~np.nan_to_num(viola, nan=False).astype(bool)
    cobertura = np.clip(cobertura * np.where(ordem_ok, 1.05, 0.95), 0, 1)

    # --- PROFUNDIDADE ------------------------------------------------------
    # Deixa de ser binaria: quantas vezes a etapa foi trabalhada e com quantos
    # termos distintos, com saturacao para nao premiar repeticao.
    prof_partes = []
    for e in ORDEM_CANONICA:
        occ = _saturar(df[f"occ_{e}"], SAT_OCORRENCIAS)
        trm = _saturar(df[f"trm_{e}"], SAT_TERMOS)
        prof_partes.append(np.where(pres[e], 0.5 * occ + 0.5 * trm, np.nan))
    prof_arr = np.vstack(prof_partes).T
    with np.errstate(invalid="ignore"):
        profundidade = np.nan_to_num(np.nanmean(prof_arr, axis=1), nan=0.0)

    # --- RESPONSIVIDADE (ritmo) -------------------------------------------
    ritmo = leads["min_resposta_media_humana"].values.astype(float)
    resp = 1.0 - np.log1p(np.clip(ritmo, 0, TETO_RITMO_MIN)) / np.log1p(TETO_RITMO_MIN)
    resp = np.where(np.isnan(ritmo), np.nan, np.clip(resp, 0, 1))
    # quem nao tem par de resposta medido fica na mediana, para nao virar zero
    resp = np.where(np.isnan(resp), np.nanmedian(resp), resp)

    # --- CONDUCAO ----------------------------------------------------------
    g_at = at.groupby("cw_id_tb_leads")
    perguntas = g_at["pergunta"].sum().reindex(leads["cw_id_tb_leads"]).fillna(0).values
    msgs_at = g_at.size().reindex(leads["cw_id_tb_leads"]).fillna(0).values

    troca = m.assign(prev=m.groupby("cw_id_tb_leads")["papel"].shift())
    troca = troca[(troca["papel"] != troca["prev"]) & troca["prev"].notna()]
    alternancias = troca.groupby("cw_id_tb_leads").size().reindex(leads["cw_id_tb_leads"]).fillna(0).values

    cta = at[at[f"et_agendamento"] & at["pergunta"]].groupby("cw_id_tb_leads").size()
    cta = (cta.reindex(leads["cw_id_tb_leads"]).fillna(0) > 0).values.astype(float)

    conducao = (
        0.40 * _saturar(perguntas, SAT_PERGUNTAS)
        + 0.35 * _saturar(alternancias, SAT_ALTERNANCIA)
        + 0.25 * cta
    )

    # --- VISIBILIDADE TEXTUAL ---------------------------------------------
    # Quanto das mensagens do atendente da para LER. normalizar() ja devolve ""
    # para content nulo, entao a midia cai aqui naturalmente.
    tem_texto = at["norm"].str.strip().ne("")
    vis = at.assign(_t=tem_texto).groupby("cw_id_tb_leads")["_t"].mean()
    visibilidade = vis.reindex(leads["cw_id_tb_leads"]).fillna(0.0).values
    midias_at = at.assign(_m=~tem_texto).groupby("cw_id_tb_leads")["_m"].sum()
    midias_at = midias_at.reindex(leads["cw_id_tb_leads"]).fillna(0).values

    # --- GATE: abandono ----------------------------------------------------
    ultimo = m.sort_values(["cw_id_tb_leads", "created_at", "message_id"]).groupby("cw_id_tb_leads")["papel"].last()
    ultimo = ultimo.reindex(leads["cw_id_tb_leads"])
    abandonou = (ultimo == "lead").fillna(True).values
    gate = np.where(abandonou, PENALIDADE_ABANDONO, 1.0)

    out = pd.DataFrame({
        "cw_id_tb_leads": leads["cw_id_tb_leads"].values,
        "cobertura": cobertura,
        "profundidade": profundidade,
        "responsividade": resp,
        "conducao": conducao,
        "abandonou": abandonou,
        "etapas_presentes": pres.sum(axis=1).values,
        "etapa_alcancada": [ORDEM_CANONICA[i] if i >= 0 else None for i in ult],
        "ordem_ok": ordem_ok,
        "msgs_atendente": msgs_at,
        "perguntas_atendente": perguntas,
        "alternancias": alternancias,
        "visibilidade_textual": visibilidade,
        "midias_atendente": midias_at,
    })
    bruto = sum(PESOS[k] * out[k].values for k in PESOS)
    out["qualidade"] = np.clip(bruto * gate, 0, 1)
    return out


def rodar(estratificar: bool = True) -> pd.DataFrame:
    """estratificar=False scoreia a base inteira.

    Necessario para a regressao multipla: dentro do estrato <=30min o tempo de
    resposta e quase constante, entao o R² incremental dele sairia perto de
    zero por falta de variancia, nao por falta de efeito.
    """
    leads, msgs, baseline = carregar()
    vocab = carregar_vocab()
    estrato = aplicar_estrato(leads) if estratificar else leads.copy()
    m = preparar_mensagens(msgs, estrato, vocab)
    dims = dimensoes(m, estrato, vocab)

    res = estrato.merge(dims, on="cw_id_tb_leads", how="left")
    res = res.merge(
        baseline[["cw_id_tb_leads", "lead_score", "qualidade_atendimento"]]
        .rename(columns={"lead_score": "temperatura", "qualidade_atendimento": "qualidade_antiga"}),
        on="cw_id_tb_leads", how="left",
    )
    res["converteu"] = res["marcou_agendamento"].notna()

    # Volume de conversa sozinho preve conversao de forma brutal (1 msg do
    # atendente = 0,47%; 11+ = 31,0%) e parte disso e o lead engajado puxando
    # papo, nao o atendente entregando. `qualidade_residual` e o que sobra do
    # score depois de descontar o tamanho da conversa — se ISSO ainda prever
    # conversao, e sinal de atendimento de verdade.
    x = np.log1p(res["msgs_atendente"].fillna(0).values)
    y = res["qualidade"].fillna(0).values
    beta = np.polyfit(x, y, 1)
    res["qualidade_residual"] = y - np.polyval(beta, x)
    return res


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    r = rodar()
    print(f"leads no estrato: {len(r):,}")
    print(f"conversao: {100*r['converteu'].mean():.2f}%\n")
    print(r[["cobertura", "profundidade", "responsividade", "conducao", "qualidade",
             "qualidade_antiga"]].describe().round(3).to_string())
    print(f"\nabandono: {100*r['abandonou'].mean():.1f}%")
    print(f"zeros na qualidade nova: {100*(r['qualidade']==0).mean():.1f}%  "
          f"| na antiga: {100*(r['qualidade_antiga']==0).mean():.1f}%")
