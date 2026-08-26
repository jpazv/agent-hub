# Handoff — Agendamentos Share / issue #326: validação, correção do fechamento mensal e aba de análise

Data: 2026-08-26
Máquina: mac-grupovelas
Hub: `/Users/grupovelas/dev/agent-hub`
Modo: global.
Dashboard: https://metabase.grupovelas.com.br/dashboard/389 — `[TESTE] Agendamentos Share`, collection 569
Issue: https://github.com/Grupo-Velas/produtividade-bi-dev/issues/326

## O que esta sessão fez

Validou a implementação contra a issue e contra a proposta técnica já publicada no
comentário da #326, encontrou um defeito que invalidava a meta ponderada, corrigiu,
e reconstruiu os 8 cards do dashboard sobre uma única base.

## Achado principal (F1) — a meta ponderada não fechava o mês

A versão anterior (card 13792) calculava:

```text
meta_semanal = meta_mensal * 5 / dias_uteis_do_mes      -- constante para toda semana
meta_dia     = meta_semanal * peso_dow_renormalizado_na_semana
```

Como `meta_semanal` era a mesma para qualquer semana, uma semana com feriado recebia
a meta inteira de 5 dias distribuída em 4 dias. Consequência medida:

| mês | meta mensal | dias úteis | Σ meta ponderada | erro |
|---|---|---|---|---|
| 2026-01 | 1842 | 21 | 2192,86 | +19,0% |
| 2026-02 | 2126 | 18 | 2362,22 | +11,1% |
| 2026-03 | 2141 | 22 | 2432,95 | +13,6% |
| 2026-04 | 2141 | 20 | 2676,25 | +25,0% |
| 2026-05 | 2176 | 20 | 2176,00 | 0,0% |
| 2026-06 | 2138 | 21 | 2545,24 | +19,0% |
| 2026-07 | 2324 | 23 | 2526,09 | +8,7% |
| 2026-08 | 2415 | 21 | 2875,00 | +19,0% |

Fechava só quando `dias_uteis = 5 × nº de semanas` (maio/2026). Isso contrariava dois
pontos escritos na própria issue: preservar a soma mensal e "semana com feriado recebe
meta menor".

### Correção aplicada

Normalização passou para o **mês**:

```text
meta_dia = meta_mensal * peso_dow / Σ(pesos dos dias elegíveis do mês)
```

Validado nos 8 meses de 2026: **erro 0,00 em todos**. E a semana com feriado passou a
receber menos: abril 424,20 (semana de 4 dias) contra 535,66 (semana cheia); junho
408,81 contra 495,62.

## Achado F3 — semanas encurtadas contaminavam o share

`hist` incluía semanas com feriado no cálculo do share, inflando o peso dos dias
sobreviventes. Corrigido com a CTE `sem_completas` (só semanas com os 5 dias úteis,
sem feriado). Impacto medido: até 0,49 p.p. (sexta). A baseline caiu de 52 para
**44 semanas completas** (janela 2025-08-25 a 2026-08-17), com soma dos pesos 100%.

Pesos vigentes: Segunda 28,09% · Terça 20,81% · Quarta 18,29% · Quinta 17,52% · Sexta 15,30%.

## Achado F2 — perfil de peso: comparação que a proposta pedia (item 8/9)

| dia | simples | mediana | aparada 10% | recência (13 sem.) | aparada+recência | desvio |
|---|---|---|---|---|---|---|
| Segunda | 28,09% | 28,17% | 28,03% | 27,62% | 27,94% | 3,16 p.p. |
| Terça | 20,81% | 20,59% | 20,76% | 21,21% | 20,98% | 2,76 p.p. |
| Quarta | 18,29% | 18,35% | 18,30% | 18,14% | 18,11% | 2,14 p.p. |
| Quinta | 17,52% | 17,58% | 17,53% | 17,55% | 17,51% | 1,84 p.p. |
| Sexta | 15,30% | 15,30% | 15,37% | 15,47% | 15,46% | 2,08 p.p. |

Spread máximo entre os cinco métodos: **0,55 p.p.** A média aparada ponderada por
recência com meia-vida de 13 semanas, que a proposta recomendava, não traz ganho.
**Decisão: média simples fica como regra oficial**, documentada com esses números.

## Achado F4 — fonte do realizado: RESOLVIDO, a proposta é que estava errada

A proposta publicada dizia usar `mv_agendamento_propria`; a implementação usa
`mv_hibrida_unidade_propria.agend`. Reconciliação executada:

```text
mv_hibrida.agend  ==  COUNT(*) de mv_agendamento_propria com status IS NOT NULL
```

243 dias comparados (jan–ago/2026), **0 divergências**, total idêntico: 14.511.
Junho/julho/agosto por mês: 1673/1673, 2212/2212, 1801/1801.
Duplicidade por `id`: **zero** — `COUNT(*) = COUNT(DISTINCT id)` em todos os status.

Conclusão: as duas fontes são o mesmo universo. `mv_hibrida` continua como fonte
(já agregada). **O texto da proposta na issue precisa ser corrigido**, não o SQL.

## Achado F5 — NÃO corrigido (decisão pendente)

Semana que atravessa a virada do mês continua usando uma única competência
(`ref.mes` = mês do `MAX(data)` do filtro). No default de hoje (`thismonth`), a janela
de 4 semanas começa em 27/07 e essa semana é medida contra a meta de agosto.
A proposta previa dividir a meta entre as duas competências. Fica como próximo passo.

## Achado F7 — NÃO entregue

O escopo "definir a estratégia de geração automática (MV/view/ETL)" segue aberto.
O cálculo vive no SQL dos cards. Isso ainda bloqueia o fechamento da issue.

## Estado final do dashboard 389

Três abas. **Todos os 8 cards saem da mesma base** (`base_v2`), com as 11 template-tags
e os 11 parameter_mappings idênticos — conferido card por card.

### Aba 958 — Visão executiva
- dc20415 — texto `Como ler esta aba` (reescrito com a regra nova)
- dc20424 → card **13796** `Realizado vs metas — semanas completas por dia` (combo diário)
- dc20425 → card **13797** `Acompanhamento semanal — meta ponderada e gap` (tabela)
- dc20426 → card **13798** `Share histórico por dia da semana` (barra)

### Aba 960 — Análise entre semanas (criada nesta sessão)
- dc20432 — texto `Análise entre semanas`
- dc20427 → card **13799** `Evolução semanal — realizado versus meta ponderada` (combo)
- dc20428 → card **13800** `Gap por dia da semana — % versus meta ponderada` (barra, linha de meta em 0%)
- dc20429 → card **13801** `Matriz de gap — semana versus dia da semana` (pivot)

### Aba 959 — Validação e auditoria
- dc20430 → card **13802** `Controle da baseline — 52 semanas` (tabela, 1 linha)
- dc20431 → card **13803** `Auditoria diária — elegibilidade e cálculo` (tabela)

10 dashcards, nenhum id duplicado, 6 parâmetros preservados
(`p-data`, `p-marca`, `p-unidade`, `p-boutique`, `p-socio`, `p-semanas`).

### Cards arquivados
13792, 13787, 13779, 13789, 13794, 13795, 13780, 13782 (13790 já estava arquivado).

Os 8 cards novos foram criados com `dashboard_id: 389` e `collection_id: 569`
(a API exige que a collection case com a do dashboard, senão devolve 400
`Incompatibilidade detectada entre collection_id`). Por serem dashboard questions,
**não aparecem na listagem da collection 569** — zero poluição confirmada.

## Bateria de validação executada

| teste | resultado |
|---|---|
| `numero_semanas` = 4 / 2 / 1 | 20 / 10 / 5 linhas no diário; 4 / 2 / 1 no semanal |
| soma cruzada entre as 4 visões | Σ realizado 2085, Σ meta 2256,56, Σ gap −171,56 em todas |
| filtro marca ITC | 1490 realizado / 1510,12 meta |
| filtro marca Trata | 595 / 746,96 — soma dos realizados = 2085 = total |
| semana corrente ausente | janela termina 21/08 com hoje = 26/08 |
| matriz sem erro de coluna | 20 linhas, ordenação por ano-semana ISO |
| auditoria diária | 28 linhas (20 elegíveis + 8 de fim de semana marcados como excluídos) |
| fechamento mensal | erro 0,00 nos 8 meses de 2026 |

## Pegadinhas técnicas encontradas

1. **`round(double precision, integer)` não existe** no Postgres — `power()`,
   `stddev_samp()` e divisões devolvem double. Precisa `ROUND((expr)::numeric, 2)`.
2. **ORDER BY prefere o alias de saída.** `SELECT to_char(...) semana ... ORDER BY semana`
   ordena o texto (27/07 cai no fim). Solução: subquery + `ORDER BY x.semana` qualificado.
3. **Pivot reordena as linhas** pelo valor do rótulo. Rótulo de semana precisa ser
   ordenável — usei `to_char(semana,'IYYY-IW')||' · '||to_char(semana,'DD/MM')`.
4. **POST /api/card com `dashboard_id` auto-anexa um dashcard** na primeira aba.
   O PUT completo seguinte reaproveita esses dashcards e descarta os antigos.
5. **A API do Metabase bloqueia urllib do Python** (WAF, HTTP 403 `error code: 1010`).
   Usar `curl`.

## Próximos passos

1. Corrigir o comentário da proposta na issue #326: fonte do realizado
   (`mv_hibrida` = `mv_agendamento_propria` com status), perfil de peso (média simples,
   com a tabela de comparação) e a fórmula de normalização mensal.
2. Decidir o F5 (semana que atravessa a virada do mês).
3. Definir o F7 (MV/view/ETL) — é o que falta para fechar a issue.
4. Conferir visualmente as três abas no navegador; os pivots e combos foram validados
   por query, não por render.

## Arquivos desta sessão

Scratchpad (temporário):
`/private/tmp/claude-501/-Users-grupovelas/b15470fa-b8e0-418c-a33c-afbdc2471a03/scratchpad/share/`
- `base_v2.sql` — base corrigida com as 11 tags
- `sql_v2.json` — os 8 SELECTs finais
- `v2_*.json` — payloads dos 8 POSTs
- `put389.json` — payload do PUT do dashboard
- `t_fechamento.sql`, `t_v2_fechamento.sql`, `t_perfis.sql`, `t_semanas_curtas.sql`,
  `q4.sql`, `q5.sql` — queries de validação (somente leitura)

## Regras operacionais

- Somente SELECT no banco.
- Para card existente, não usar PUT de query: recriar via POST e trocar no dashboard.
- PUT de dashboard exige `tabs` + `dashcards` no mesmo payload.
- Não expor nem commitar tokens.
