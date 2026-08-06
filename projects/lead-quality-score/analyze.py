"""Curva de decis, matrizes unidade x semana, correlacoes e Excel.

Le o cache, chama o score, nao toca o banco.
"""
from __future__ import annotations

import pathlib
import warnings

import numpy as np
import pandas as pd
from scipy import stats

import score

warnings.filterwarnings("ignore")

BASE = pathlib.Path(__file__).parent
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

MIN_LEADS_CELULA = 20  # celula mais magra que isto vira ruido


# ------------------------------------------------------------- curva de decis

def curva_decis(r: pd.DataFrame, col: str = "qualidade") -> pd.DataFrame:
    d = r[[col, "converteu"]].dropna().copy()
    d["decil"] = pd.qcut(d[col].rank(method="first"), 10, labels=range(1, 11))
    g = d.groupby("decil", observed=True).agg(
        leads=(col, "size"),
        score_min=(col, "min"),
        score_max=(col, "max"),
        score_medio=(col, "mean"),
        conversao=("converteu", "mean"),
    ).reset_index()
    g["conversao_pct"] = (100 * g["conversao"]).round(2)
    base = d["converteu"].mean()
    g["lift"] = (g["conversao"] / base).round(2)
    return g.drop(columns=["conversao"])


def escolher_corte(dec: pd.DataFrame) -> tuple[float, str]:
    """Acha o cotovelo: o decil onde o salto de conversao e maior.

    Se o maior salto for muito maior que os demais, a relacao e de degrau e o
    corte do '% bom' sai dali. Se os saltos forem parecidos, a relacao e
    linear e a media e a metrica melhor.
    """
    saltos = dec["conversao_pct"].diff().fillna(0)
    i = int(saltos.idxmax())
    maior = saltos.iloc[i]
    demais = saltos.drop(index=i)
    razao = maior / max(demais.abs().mean(), 1e-9)
    forma = "degrau" if razao >= 2.0 else "linear"
    corte = float(dec.loc[i, "score_min"])
    return corte, f"{forma} (maior salto {maior:.2f}pp no decil {dec.loc[i,'decil']}, {razao:.1f}x a media dos demais)"


# ------------------------------------------------------------------- matrizes

def matriz_score(r: pd.DataFrame, corte: float) -> pd.DataFrame:
    g = r.groupby(["unidade", "semana"]).agg(
        leads=("cw_id_tb_leads", "size"),
        score_medio=("qualidade", "mean"),
        pct_bom=("qualidade", lambda s: (s >= corte).mean()),
        score_residual=("qualidade_residual", "mean"),
        score_antigo=("qualidade_antiga", "mean"),
        temperatura=("temperatura", "mean"),
        msgs_atendente=("msgs_atendente", "mean"),
        visib_media=("visibilidade_textual", "mean"),
        conversao_lead=("converteu", "mean"),
    ).reset_index()
    # semana vem do parquet como texto; alinhar com a matriz B senao o merge
    # devolve zero celulas.
    g["semana"] = pd.to_datetime(g["semana"]).dt.normalize()
    return g


def matriz_cvs() -> pd.DataFrame:
    c = pd.read_parquet(BASE / "cache" / "cvs.parquet")
    c["semana"] = pd.to_datetime(c["semana"]).dt.normalize()
    c["cvs"] = c["agend"] / c["leads_sec"].replace(0, np.nan)
    return c


# --------------------------------------------------------------- correlacoes

def _corr(x, y, w=None):
    m = np.isfinite(x) & np.isfinite(y)
    x, y = np.asarray(x)[m], np.asarray(y)[m]
    if len(x) < 4:
        return dict(n=len(x), pearson=np.nan, p_pearson=np.nan, spearman=np.nan, p_spearman=np.nan)
    pr, pp = stats.pearsonr(x, y)
    sr, sp = stats.spearmanr(x, y)
    return dict(n=len(x), pearson=round(pr, 4), p_pearson=round(pp, 5),
                spearman=round(sr, 4), p_spearman=round(sp, 5))


def correlacoes(painel: pd.DataFrame, metricas: list[str], alvo: str = "cvs") -> pd.DataFrame:
    linhas = []
    for met in metricas:
        d = painel[[met, alvo, "unidade", "leads"]].dropna()
        # pooled: mistura variacao entre unidades e dentro delas
        linhas.append({"metrica": met, "leitura": "pooled", **_corr(d[met], d[alvo])})
        # within: cada unidade centralizada na propria media (efeito fixo)
        dw = d.copy()
        dw[met] = dw[met] - dw.groupby("unidade")[met].transform("mean")
        dw[alvo] = dw[alvo] - dw.groupby("unidade")[alvo].transform("mean")
        linhas.append({"metrica": met, "leitura": "within-unidade", **_corr(dw[met], dw[alvo])})
    return pd.DataFrame(linhas)


# ------------------------------------------------------------------ relatorio

def main() -> int:
    print("Rodando score...")
    r = score.rodar()
    print(f"  {len(r):,} leads no estrato (<= {score.CORTE_RESPOSTA_MIN} min expediente)\n")

    # --- curva de decis e escolha da metrica agregada
    dec = curva_decis(r)
    corte, diagnostico = escolher_corte(dec)
    print("Curva de decis (qualidade nova):")
    print(dec.to_string(index=False))
    print(f"\n  forma: {diagnostico}")
    print(f"  corte para '% bom': {corte:.3f}\n")

    dec_antiga = curva_decis(r, "qualidade_antiga")

    # --- confundimento: quanto do score e so tamanho de conversa
    conf = pd.DataFrame([
        {"par": "qualidade x msgs_atendente", **_corr(r["qualidade"], r["msgs_atendente"])},
        {"par": "qualidade x msg_inbound (lead falou)", **_corr(r["qualidade"], r["msg_inbound"])},
        {"par": "qualidade_antiga x msgs_atendente", **_corr(r["qualidade_antiga"], r["msgs_atendente"])},
        {"par": "msgs_atendente x converteu", **_corr(r["msgs_atendente"], r["converteu"].astype(float))},
        {"par": "qualidade x converteu", **_corr(r["qualidade"], r["converteu"].astype(float))},
    ])
    print("Confundimento com tamanho de conversa:")
    print(conf.to_string(index=False))
    print()

    # --- matrizes
    A = matriz_score(r, corte)
    B = matriz_cvs()
    painel = A.merge(B[["unidade", "semana", "agend", "leads_sec", "cvs"]],
                     on=["unidade", "semana"], how="inner")
    painel_f = painel[painel["leads"] >= MIN_LEADS_CELULA].copy()
    print(f"Painel: {len(painel)} celulas | {len(painel_f)} com >= {MIN_LEADS_CELULA} leads")
    print(f"  unidades {painel_f['unidade'].nunique()} | semanas {painel_f['semana'].nunique()}\n")

    metricas = ["score_medio", "pct_bom", "score_residual", "score_antigo",
                "temperatura", "msgs_atendente"]

    # Dois alvos, porque eles NAO sao a mesma coisa: o %CVS oficial conta
    # agendamentos que nao vieram destes leads (ver aba alvos).
    corr_cvs = correlacoes(painel_f, metricas, "cvs").assign(alvo="%CVS oficial")
    corr_lead = correlacoes(painel_f, metricas, "conversao_lead").assign(alvo="conversao lead-level")
    corr = pd.concat([corr_cvs, corr_lead], ignore_index=True)
    corr = corr[["alvo", "metrica", "leitura", "n", "pearson", "p_pearson", "spearman", "p_spearman"]]
    print("Correlacoes contra %CVS oficial:")
    print(corr_cvs.drop(columns="alvo").to_string(index=False))
    print("\nCorrelacoes contra conversao lead-level (mesma celula):")
    print(corr_lead.drop(columns="alvo").to_string(index=False))

    concordancia = correlacoes(painel_f, ["conversao_lead"], "cvs")
    agend_biz = int(painel_f["agend"].sum())
    agend_cw = int((painel_f["conversao_lead"] * painel_f["leads"]).sum())
    alvos = pd.DataFrame([
        {"item": "agendamentos no %CVS (negocio)", "valor": agend_biz},
        {"item": "agendamentos rastreaveis aos leads (chatwoot)", "valor": agend_cw},
        {"item": "excedente nao rastreavel", "valor": agend_biz - agend_cw},
        {"item": "excedente %", "valor": round(100 * (agend_biz - agend_cw) / max(agend_cw, 1), 1)},
        {"item": "correlacao entre os dois alvos (pooled r)", "valor": concordancia.iloc[0]["pearson"]},
        {"item": "correlacao entre os dois alvos (within r)", "valor": concordancia.iloc[1]["pearson"]},
    ])
    print("\nOs dois alvos nao medem a mesma coisa:")
    print(alvos.to_string(index=False))

    # --- visibilidade textual: medir a cegueira, nao imputar
    vis = visibilidade(r)
    print("\nVisibilidade textual (midia chega sem transcricao — nada foi imputado):")
    print(vis.to_string(index=False))

    metricas_vis = ["score_medio", "pct_bom", "msgs_atendente", "temperatura"]
    corr_vis = correlacoes_estratificadas(painel_f, metricas_vis, "conversao_lead")
    print("\nCorrelacao estratificada por visibilidade (alvo: conversao lead-level):")
    print(corr_vis.to_string(index=False))

    # --- Excel
    xlsx = OUT / "qualidade_atendimento.xlsx"
    cols_lead = ["cw_id_tb_leads", "unidade", "marca", "socio", "semana", "lead_data",
                 "min_ate_secretaria_expediente", "min_resposta_media_humana",
                 "msgs_atendente", "perguntas_atendente", "alternancias",
                 "etapas_presentes", "etapa_alcancada", "ordem_ok", "abandonou",
                 "visibilidade_textual", "midias_atendente",
                 "cobertura", "profundidade", "responsividade", "conducao",
                 "qualidade", "qualidade_antiga", "temperatura",
                 "marcou_agendamento", "realizou_av", "converteu_tto", "converteu"]
    with pd.ExcelWriter(xlsx, engine="xlsxwriter") as xw:
        r[cols_lead].to_excel(xw, sheet_name="scores_lead", index=False)
        painel.to_excel(xw, sheet_name="matriz_score_semana", index=False)
        B.to_excel(xw, sheet_name="matriz_cvs_semana", index=False)
        corr.to_excel(xw, sheet_name="correlacoes", index=False)
        alvos.to_excel(xw, sheet_name="alvos", index=False)
        vis.to_excel(xw, sheet_name="visibilidade", index=False)
        corr_vis.to_excel(xw, sheet_name="corr_por_visibilidade", index=False)
        dec.to_excel(xw, sheet_name="curva_decis", index=False)
        dec_antiga.to_excel(xw, sheet_name="curva_decis_antiga", index=False)
        _decis_dimensoes(r).to_excel(xw, sheet_name="decis_por_dimensao", index=False)
        conf.to_excel(xw, sheet_name="confundimento", index=False)
        _dicionario(corte, diagnostico).to_excel(xw, sheet_name="dicionario", index=False)

    print(f"\nExcel: {xlsx}")
    return 0


def visibilidade(r: pd.DataFrame) -> pd.DataFrame:
    """Quanto do atendimento e ilegivel, e o que isso faz com o score.

    Midia (audio/imagem) chega sem transcricao. Nada e imputado — so medido.
    """
    v = r["visibilidade_textual"]
    faixas = pd.cut(v, [-0.01, 0.25, 0.5, 0.7, 0.9, 1.0],
                    labels=["0-25%", "25-50%", "50-70%", "70-90%", "90-100%"])
    g = r.assign(faixa=faixas).groupby("faixa", observed=True).agg(
        leads=("cw_id_tb_leads", "size"),
        visib_media=("visibilidade_textual", "mean"),
        midias_media=("midias_atendente", "mean"),
        msgs_atendente=("msgs_atendente", "mean"),
        qualidade=("qualidade", "mean"),
        cobertura=("cobertura", "mean"),
        conducao=("conducao", "mean"),
        conversao=("converteu", "mean"),
    ).reset_index()
    g["conversao"] = (100 * g["conversao"]).round(2)
    return g.round(3)


def correlacoes_estratificadas(painel: pd.DataFrame, metricas: list[str],
                               alvo: str) -> pd.DataFrame:
    """Mesma correlacao em alta e baixa visibilidade textual.

    Se o score funciona onde da para ler e falha onde nao da, a conclusao e
    'o dado e cego', nao 'o score nao presta'. E o teste que separa os dois.
    """
    saida = []
    for nome, sub in [
        (f"alta (>= {score.CORTE_VISIBILIDADE:.0%})", painel[painel["visib_media"] >= score.CORTE_VISIBILIDADE]),
        (f"baixa (< {score.CORTE_VISIBILIDADE:.0%})", painel[painel["visib_media"] < score.CORTE_VISIBILIDADE]),
    ]:
        if len(sub) < 10:
            saida.append(pd.DataFrame([{"estrato": nome, "metrica": "-", "leitura": "-",
                                        "n": len(sub), "pearson": np.nan, "p_pearson": np.nan,
                                        "spearman": np.nan, "p_spearman": np.nan}]))
            continue
        c = correlacoes(sub, metricas, alvo).assign(estrato=nome)
        saida.append(c)
    out = pd.concat(saida, ignore_index=True)
    return out[["estrato", "metrica", "leitura", "n", "pearson", "p_pearson", "spearman", "p_spearman"]]


def _decis_dimensoes(r: pd.DataFrame) -> pd.DataFrame:
    """Conversao por decil de CADA dimensao — mostra qual delas se comporta."""
    linhas = []
    for col in ["cobertura", "profundidade", "responsividade", "conducao",
                "qualidade", "qualidade_antiga", "msgs_atendente"]:
        d = r[[col, "converteu"]].dropna()
        if d.empty:
            continue
        d = d.assign(q=pd.qcut(d[col].rank(method="first"), 10, labels=range(1, 11)))
        g = d.groupby("q", observed=True)["converteu"].mean().mul(100).round(2)
        linhas.append({"dimensao": col, **{f"d{i}": g.get(i, np.nan) for i in range(1, 11)}})
    return pd.DataFrame(linhas)


def _dicionario(corte: float, diagnostico: str) -> pd.DataFrame:
    linhas = [
        ("estrato", f"apenas leads com min_ate_secretaria_expediente <= {score.CORTE_RESPOSTA_MIN}"),
        ("janela", "6 semanas completas; a semana em curso e descartada"),
        ("cobertura", "etapas da trilha presentes / etapas possiveis ATE a etapa mais avancada alcancada, ponderadas; +-5% por ordem"),
        ("profundidade", f"por etapa presente: 0.5*sat(ocorrencias/{score.SAT_OCORRENCIAS}) + 0.5*sat(termos distintos/{score.SAT_TERMOS})"),
        ("responsividade", f"ritmo ao longo da conversa (min_resposta_media_humana), log-decay ate {score.TETO_RITMO_MIN:.0f} min. NAO e a primeira resposta — essa virou o filtro do estrato"),
        ("conducao", f"0.40*sat(perguntas/{score.SAT_PERGUNTAS}) + 0.35*sat(alternancias/{score.SAT_ALTERNANCIA}) + 0.25*CTA de agendamento"),
        ("gate abandono", f"lead falou por ultimo e ninguem respondeu -> nota x {score.PENALIDADE_ABANDONO}"),
        ("pesos", str(score.PESOS)),
        ("papel da mensagem", "sender_id nao serve (99,7% das saidas vem da conta de integracao WhatsApp); usa-se o corte primeiro_humano_em, que reproduz msg_humano exato em 78% dos leads e com erro <=1 em 88%"),
        ("qualidade_antiga", "lead_score_output.qualidade_atendimento — baseline de comparacao"),
        ("%CVS", "metric 2589 = sum(agend)/sum(leads_sec) sobre mv_hibrida_unidade_propria"),
        ("corte % bom", f"{corte:.3f} — derivado do cotovelo da curva de decis, forma {diagnostico}"),
        ("celulas", f"unidade x semana com pelo menos {MIN_LEADS_CELULA} leads entram nas correlacoes"),
        ("ALERTA confundimento", "volume de conversa preve conversao de forma brutal (1 msg do atendente = 0,47%; 11+ = 31,0%). Parte disso e o lead engajado puxando conversa, nao o atendente. Ver aba confundimento"),
        ("ALERTA alvo", "o %CVS oficial conta ~65% mais agendamentos do que os rastreaveis a estes leads: inclui conversao que nao passou pela secretaria. Contra ele o score nao correlaciona; contra a conversao lead-level da mesma celula, correlaciona. Ver aba alvos"),
        ("responsividade", "peso ZERO na composicao — comportamento invertido (ver aba decis_por_dimensao). Mantida so como diagnostico"),
        ("qualidade_residual", "score menos o efeito de log(msgs_atendente): a parte que NAO e tamanho de conversa"),
    ]
    return pd.DataFrame(linhas, columns=["campo", "definicao"])


if __name__ == "__main__":
    raise SystemExit(main())
