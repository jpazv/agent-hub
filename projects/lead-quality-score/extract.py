"""Fase de extracao: puxa o bruto do Metabase e grava em cache Parquet local.

Roda uma vez (lento). Depois disso todo o scoring itera em cima do cache, sem
tocar o banco. Somente SELECT — ver o guarda em mb._assert_readonly.

Janela: 6 semanas COMPLETAS. A semana em curso e descartada de proposito — uma
semana parcial entra na matriz unidade x semana com denominador menor e
distorce a correlacao.
"""
from __future__ import annotations

import pathlib
import sys
import warnings

import pandas as pd

import mb

warnings.filterwarnings("ignore")

CACHE = pathlib.Path(__file__).parent / "cache"
CACHE.mkdir(exist_ok=True)

WEEKS = 6
# Segunda-feira da semana corrente: limite superior EXCLUSIVO.
END = "date_trunc('week', current_date)"
START = f"({END} - interval '{WEEKS} weeks')"


SQL_LEADS = f"""
select
    cw_id_tb_leads,
    contact_id,
    unidade,
    marca,
    socio,
    regiao,
    uf,
    lead_data,
    date_trunc('week', lead_data)::date          as semana,
    qtd_conversas,
    primeira_msg_lead_em,
    primeiro_humano_em,
    ultima_msg_lead_em,
    ultima_msg_humana_em,
    min_ate_secretaria,
    min_ate_secretaria_expediente,
    min_resposta_media_humana,
    pares_resposta_humana,
    msg_total,
    msg_inbound,
    msg_humano,
    msg_bot,
    nos_assumimos,
    faixa_tempo_expediente,
    faixa_tempo_geral,
    estagio_funil,
    scal_status,
    marcou_agendamento,
    realizou_av,
    converteu_tto,
    cancelou
from analytics.mv_chatwoot_conversa_metricas
where lead_data >= {START} and lead_data < {END}
"""


SQL_MESSAGES = """
select
    b.cw_id_tb_leads,
    m.id                as message_id,
    m.conversation_id,
    m.created_at,
    m.message_type,
    m.content
from analytics.mv_chatwoot_conversa_metricas b
join conversations c on c.contact_id = b.contact_id
join messages      m on m.conversation_id = c.id
where b.lead_data >= '{wstart}' and b.lead_data < '{wend}'
  and m.private = false
  and m.message_type in (0, 1)
  and m.created_at >= coalesce(b.primeira_msg_lead_em, b.lead_data::timestamp) - interval '1 day'
  and m.created_at <= coalesce(b.primeira_msg_lead_em, b.lead_data::timestamp) + interval '30 days'
"""


SQL_BASELINE = f"""
select
    o.cw_id_tb_leads,
    o.lead_score,
    o.probabilidade_de_vida,
    o.densidade_da_conversa,
    o.intencao_de_agendar,
    o.qualidade_atendimento,
    o.espelhamento_lexico,
    o.scored_at
from lead_score_output o
where o.cw_id_tb_leads in (
    select cw_id_tb_leads
    from analytics.mv_chatwoot_conversa_metricas
    where lead_data >= {START} and lead_data < {END}
)
"""


# Matriz B: o %CVS oficial (metric 2589 = sum(agend)/sum(leads_sec)).
SQL_CVS = f"""
select
    unidade,
    date_trunc('week', data)::date as semana,
    sum(agend)      as agend,
    sum(leads_sec)  as leads_sec
from mv_hibrida_unidade_propria
where data >= {START} and data < {END}
group by 1, 2
"""

# Mesmo numero sem quebra, para bater contra a metric 2589 no Metabase.
SQL_CVS_TOTAL = f"""
select sum(agend) as agend, sum(leads_sec) as leads_sec
from mv_hibrida_unidade_propria
where data >= {START} and data < {END}
"""


def _save(df: pd.DataFrame, name: str) -> None:
    path = CACHE / f"{name}.parquet"
    df.to_parquet(path, index=False)
    print(f"  -> {name}.parquet  {len(df):,} linhas  {path.stat().st_size/1e6:.1f} MB")


def main() -> int:
    if not mb.check_session():
        print("ERRO: sessao do Metabase invalida ou expirada.", file=sys.stderr)
        print("Renove em /api/session e regrave em .metabase_session", file=sys.stderr)
        return 1

    bounds = mb.query_df(f"select {START}::date as inicio, ({END} - interval '1 day')::date as fim")
    inicio, fim = bounds.iloc[0]["inicio"], bounds.iloc[0]["fim"]
    print(f"Janela: {inicio} a {fim} ({WEEKS} semanas completas)\n")

    print("[1/4] leads (espinha lead-level)")
    leads = mb.query_df(SQL_LEADS)
    _save(leads, "leads")

    print("[2/4] cvs (matriz B) + total de conferencia")
    _save(mb.query_df(SQL_CVS), "cvs")
    total = mb.query_df(SQL_CVS_TOTAL)
    print(f"     conferencia metric 2589: agend={int(total.iloc[0]['agend']):,} "
          f"leads_sec={int(total.iloc[0]['leads_sec']):,} "
          f"%CVS={100*total.iloc[0]['agend']/total.iloc[0]['leads_sec']:.2f}%")

    print("[3/4] baseline (lead_score_output)")
    _save(mb.query_df(SQL_BASELINE), "baseline")

    print("[4/4] messages (em blocos semanais)")
    semanas = sorted(leads["semana"].unique())
    partes = []
    for i, w in enumerate(semanas, 1):
        wstart = pd.Timestamp(w).date()
        wend = (pd.Timestamp(w) + pd.Timedelta(days=7)).date()
        print(f"  semana {i}/{len(semanas)} {wstart} ...", end=" ", flush=True)
        part = mb.query_df(SQL_MESSAGES.format(wstart=wstart, wend=wend))
        print(f"{len(part):,} msgs")
        partes.append(part)
    msgs = pd.concat(partes, ignore_index=True)
    msgs = msgs.drop_duplicates(subset=["cw_id_tb_leads", "message_id"])
    _save(msgs, "messages")

    print("\nCache pronto em ./cache")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
