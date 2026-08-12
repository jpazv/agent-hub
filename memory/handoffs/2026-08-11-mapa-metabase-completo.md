---
data: 2026-08-11
maquina: mac-grupovelas
projeto: Metabase — Grupo Velas
status: mapeamento completo
---

# Mapa Completo do Metabase — Grupo Velas

257 dashboards · 22 tabelas reais · 689 cards com SQL nativo

---

## Tabelas e Materialized Views

### MVs de Performance (core)

| Tabela | Dashboards | Descrição |
|---|---|---|
| `mv_hibrida_unidade_propria` | 42 | Híbrida principal — vendas, avaliações, agendamentos, faturamento por unidade/dia |
| `mv_agendamento_propria` | 23 | Agendamentos de unidades próprias |
| `mv_leads_ps_propria` | 23 | Leads pós-scoring de próprias |
| `mv_avaliacoes_propria` | 1 | Avaliações de próprias |
| `mv_venda_propria` | 1 | Vendas de próprias |
| `mv_data_geral` | 1 | Dados gerais consolidados |

### MVs de Marketing

| Tabela | Dashboards | Descrição |
|---|---|---|
| `mv_mkt_outcomes_diario` | 2 | Outcomes — leads, invest, agend, aval, fat, scores por unidade/dia |
| `mv_mkt_criativos_ad_dia` | 1 | Criativos por anúncio/dia — impressões, cliques, CTR, CPC, CPL |
| `mv_mkt_financeiro` | 1 | Financeiro de marketing |

### MVs de Lead Score / Chatwoot

| Tabela | Dashboards | Descrição |
|---|---|---|
| `mv_chatwoot_conversa_metricas` | 3 | Métricas por conversa — scores, qualidade, vitalidade, funil |
| `lead_score_output` | 3 | Output do modelo de lead scoring |

### MVs de Franquias / Serviços

| Tabela | Dashboards | Descrição |
|---|---|---|
| `mv_avaliacoes_franquia` | 1 | Avaliações de franquias |
| `mv_servicos` | 1 | Serviços |

### MVs Financeiro

| Tabela | Dashboards | Descrição |
|---|---|---|
| `mv_dre_gerencial_ebitda_detalhe` | 1 | DRE gerencial com EBITDA detalhado |

### Tabelas Base

| Tabela | Dashboards | Descrição |
|---|---|---|
| `tb_leads_z_api` | 23 | Leads Z-API — base do tempo de resposta |
| `tb_faturamento_franquias` | 1 | Faturamento de franquias |

### Dimensões / Fatos / Logs

| Tabela | Dashboards | Descrição |
|---|---|---|
| `dim_unidades` | 3 | Dimensão de unidades — região, UF, cidade, sócio |
| `mb_metas_proprias` | 1 | Metas por unidade |
| `fat_extrato_lancamentos_itau` | 1 | Extratos bancários Itaú |
| `fat_3_meses` | 1 | Faturamento últimos 3 meses (franquias) |
| `log_unidades` | 1 | Log de alterações de unidades |
| `pipeline_bastion_log` | 1 | Log de execuções do pipeline ETL |

---

## Dashboards por Grupo

### Performance Geral (1 dashboard, 91 cards)

| ID | Nome | Abas | Tabelas |
|---|---|---|---|
| 10 | Relatório de Performance | RPD · Acelerômetros · Consolidado · Vendas Detalhado · Evolução de Clínicas · Histórico · Distribuição | mv_hibrida_unidade_propria, mv_agendamento_propria, mv_avaliacoes_propria, mv_data_geral, mv_leads_ps_propria, mv_venda_propria, dim_unidades, mb_metas_proprias, log_unidades |

### Performance Sócios (19 dashboards, ~84 cards cada)

Todos usam `mv_hibrida_unidade_propria`. Abas padrão: RPD · Acelerômetros · Consolidado · Vendas Detalhado · Distribuição · Evolução.

| ID | Sócio |
|---|---|
| 343 | Alessandra |
| 341 | Alexandre Almeida |
| 103 | Carolina Carvalho |
| 351 | Cleyton França |
| 344 | Daniel Luis |
| 271 | Fernando/Tariane |
| 348 | Híkaro Costa |
| 273 | Jhonatha Oliveira |
| 345 | Juliana Ramiro |
| 352 | Luciano Nóbrega |
| 347 | Maria Ferreira |
| 274 | Mariana Martins |
| 346 | Márcio Pimentel |
| 353 | Mário Andrade |
| 84 | Mônica Peixoto |
| 277 | Pedro Aquino |
| 279 | Pedro Jettar |
| 349 | Pietro Daniel |
| 350 | Vanderson Duarte |

### Tráfego Pago (1 dashboard, 28 cards)

| ID | Nome | Abas | Tabelas |
|---|---|---|---|
| 316 | Tráfego Pago | Tráfego · Financeiro · Criativos · Alertas | mv_mkt_outcomes_diario, mv_mkt_criativos_ad_dia, mv_mkt_financeiro |

### Lead Score (5 dashboards)

| ID | Nome | Tabelas |
|---|---|---|
| 369 | Lead Score Velas | mv_chatwoot_conversa_metricas, lead_score_output |
| 380 | [Novo MV] Lead Score Velas | mv_mkt_outcomes_diario, mv_chatwoot_conversa_metricas, lead_score_output |
| 381 | [RASCUNHO] Storytelling LSV | mv_chatwoot_conversa_metricas, lead_score_output |
| 317 | Lead Score (antigo) | — |
| 323 | Lead Score Velas (antigo) | — |

### Tempo de Resposta (23 dashboards)

Todos usam: `tb_leads_z_api`, `mv_agendamento_propria`, `mv_hibrida_unidade_propria`, `mv_leads_ps_propria`.

| ID | Nome |
|---|---|
| 305 | Tempo de Resposta (geral) |
| 354 | Alessandra Saraiva |
| 365 | Alexandre |
| 334 | Carolina Carvalho |
| 362 | Cleyton França |
| 355 | Daniel Luis |
| 329 | Fernando/Tariane |
| 359 | Híkaro Costa |
| 373 | ITC Vertebral - Brooklin |
| 377 | ITC Vertebral - Tatuapé |
| 333 | Jhonatha Oliveira |
| 356 | Juliana Ramiro |
| 363 | Luciano Nóbrega |
| 358 | Maria Ferreira |
| 331 | Mariana Martins |
| 357 | Márcio Pimentel |
| 364 | Mário Andrade |
| 328 | Mônica Peixoto |
| 335 | Pedro Aquino |
| 332 | Pedro Jettar |
| 360 | Pietro Daniel |
| 372 | Savassi |
| 361 | Vanderson Duarte |

### Financeiro / DRE (3 dashboards)

| ID | Nome | Tabelas |
|---|---|---|
| 293 | DRE - Grupo Velas | mv_dre_gerencial_ebitda_detalhe |
| 301 | Visão de Caixa Diário | fat_extrato_lancamentos_itau, dim_unidades |
| 319 | DRE Gerencial - FZA | (structured query) |

### Franquias (5 dashboards)

| ID | Nome | Tabelas |
|---|---|---|
| 374 | Ranking - Franquias | mv_avaliacoes_franquia, mv_servicos, tb_faturamento_franquias, fat_3_meses, dim_unidades |
| 302 | Gestão de Franquias 3.0 | (structured query) |
| 304 | Dash IA - Franquias | (structured query) |
| 309 | Controle - Franquias | (structured query) |
| 70 | Teste - Franquias | (structured query) |

### Unidades — Farol (81 dashboards, 12 cards cada)

Dashboards individuais por unidade. Structured queries (não SQL nativo).

### Unidades — Relatório de Performance (102 dashboards, 61 cards cada)

Dashboards individuais por unidade/multifranqueado. Abas: RPD · Consolidado · Metas. Structured queries.

### Operacional (2 dashboards)

| ID | Nome | Tabelas |
|---|---|---|
| 324 | Acompanhamento de Atualizações | pipeline_bastion_log |
| 314 | MKT1 (teste) | — |

### Outros (12 dashboards)

| ID | Nome |
|---|---|
| 28 | B2B |
| 59 | NPS |
| 68 | Teste de Performance |
| 72 | Teste - CD |
| 73 | RPD - Multifranqueados |
| 285 | ITC Vertebral |
| 286 | Análise Trimestral |
| 299 | NPS - Gestão |
| 311 | LSV |
| 318 | Pendências C.A.R. (Desativado) |
| 320 | Pendências C.A.R. |
| 321 | Posição de caixa - FZA |

---

## Dependência Tabela → Dashboard (índice reverso)

| Tabela | Qtd | Onde é usada |
|---|---|---|
| `mv_hibrida_unidade_propria` | 42 | Dash 10, 19 sócios, Tempo de Resposta (23) |
| `mv_agendamento_propria` | 23 | Dash 10, Tempo de Resposta (23) |
| `mv_leads_ps_propria` | 23 | Dash 10, Tempo de Resposta (23) |
| `tb_leads_z_api` | 23 | Tempo de Resposta (23) |
| `mv_chatwoot_conversa_metricas` | 3 | Lead Score (369, 380, 381) |
| `lead_score_output` | 3 | Lead Score (369, 380, 381) |
| `dim_unidades` | 3 | Dash 10, Caixa (301), Ranking Franquias (374) |
| `mv_mkt_outcomes_diario` | 2 | Tráfego (316), Lead Score (380) |
| `mv_mkt_criativos_ad_dia` | 1 | Tráfego (316) |
| `mv_mkt_financeiro` | 1 | Tráfego (316) |
| `mv_avaliacoes_propria` | 1 | Dash 10 |
| `mv_avaliacoes_franquia` | 1 | Ranking Franquias (374) |
| `mv_data_geral` | 1 | Dash 10 |
| `mv_venda_propria` | 1 | Dash 10 |
| `mv_servicos` | 1 | Ranking Franquias (374) |
| `mv_dre_gerencial_ebitda_detalhe` | 1 | DRE (293) |
| `fat_extrato_lancamentos_itau` | 1 | Caixa (301) |
| `fat_3_meses` | 1 | Ranking Franquias (374) |
| `tb_faturamento_franquias` | 1 | Ranking Franquias (374) |
| `mb_metas_proprias` | 1 | Dash 10 |
| `log_unidades` | 1 | Dash 10 |
| `pipeline_bastion_log` | 1 | Acompanhamento (324) |

---

## Notas

- Dashboards de Farol (81) e Relatório de Unidade (102) usam structured queries — as tabelas não aparecem no SQL nativo mas consomem `mv_hibrida_unidade_propria` via modelo Metabase.
- CTEs internas (ex: `mes_cheio`, `projecao`, `real`, `base_agg`) não são tabelas reais — são aliases dentro dos SQLs.
- Ao criar uma nova MV, adicionar neste mapa e atualizar o índice reverso.
