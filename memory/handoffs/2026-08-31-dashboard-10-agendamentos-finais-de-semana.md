# Handoff — Dashboard 10: agendamentos com finais de semana

**Data:** 2026-08-31  
**Máquina:** `mac-grupovelas`  
**Sessão:** global / Metabase  
**Responsável:** JP (`jpazv`)

## Demanda

Auditar o tratamento de sábado e domingo nos gráficos de Investimento, Leads e Agendamentos do dashboard `10 — Performance` e corrigir Agendamentos para também considerar o fim de semana.

## Auditoria anterior à mudança

- `15251 — Investimento x Período`: já incluía sábado e domingo. O SQL não possuía filtro de dia útil. A barra rotulada como semana de 27/07 continha somente 01/08 (sábado, R$ 18.841,72) e 02/08 (domingo, R$ 20.819,94), totalizando exatamente R$ 39.661,66.
- `124 — Leads x Dia`: já incluía sábado e domingo. Na semana 02–08/08, 4.445 leads vieram de segunda a sexta e 1.601 do fim de semana, totalizando 6.046.
- `15259 — Realizado, Cancelamentos e Metas — Semanas Completas por Período`: excluía finais de semana e feriados do realizado por `dia_util = 1`; a grade de saída também era formada apenas por segunda a sexta.

Os rótulos semanais eram diferentes:

- Investimento usava `date_trunc('week', dia)` e rotulava pela segunda-feira.
- Leads usava o agrupamento nativo do Metabase e rotulava pelo domingo.
- Agendamentos já usava a semana operacional domingo–sábado, mas não mostrava os dados do fim de semana.

## Alteração aplicada

O card de Agendamentos foi recriado do zero, conforme a regra de segurança para dashboard questions.

- Dashboard: `10`
- Card novo: `15279`
- Dashcard novo: `22656`
- Card substituído e arquivado: `15259`
- Collection: `12`
- Aba: `5`
- Layout preservado: linha `55`, coluna `0`, tamanho `24 × 8`
- Mappings preservados: `9`
- Nome preservado: `Realizado, Cancelamentos e Metas — Semanas Completas por Período`

Mudanças na query:

1. Realizado e cancelamentos não filtram mais `dia_util = 1`.
2. Realizado não é mais descartado quando a data é feriado.
3. A grade diária agora parte do calendário completo, incluindo sábado e domingo.
4. Os rótulos diários passaram a reconhecer `Sábado` e `Domingo`.
5. Semana continua definida como domingo a sábado.
6. Metas flat e ponderada continuam com a metodologia aprovada de dias úteis; sábado, domingo e feriado recebem meta zero, sem redistribuição automática da meta mensal.

## Validação

No período retornado pelo card em 31/08/2026:

- 23 pontos diários;
- 7 datas de fim de semana;
- 43 agendamentos no fim de semana;
- 22 cancelamentos no fim de semana.

Datas verificadas:

- 09/08 · Domingo: 3 realizados, 0 cancelamentos
- 15/08 · Sábado: 11 realizados, 10 cancelamentos
- 16/08 · Domingo: 5 realizados, 0 cancelamentos
- 22/08 · Sábado: 4 realizados, 3 cancelamentos
- 23/08 · Domingo: 4 realizados, 0 cancelamentos
- 29/08 · Sábado: 8 realizados, 9 cancelamentos
- 30/08 · Domingo: 8 realizados, 0 cancelamentos

Totais reconciliados nas três granularidades:

| Agrupamento | Pontos | Realizado | Cancelamentos |
|---|---:|---:|---:|
| Dia | 23 | 1.477 | 415 |
| Semana | 4 | 1.477 | 415 |
| Mês | 1 | 1.477 | 415 |

Auditoria estrutural:

- dashboard permaneceu com `116` dashcards;
- todos os cards diferentes do substituído permaneceram idênticos;
- novo card ativo, vinculado ao dashboard `10` e à collection `12`;
- novo card aparece exatamente uma vez;
- card antigo `15259` retorna `404` após o arquivamento.

## Backups e temporários

- `/private/tmp/dashboard-10-before-agendamentos-weekends-2026-08-31.json`
- `/private/tmp/dashboard-10-after-agendamentos-weekends-2026-08-31.json`
- `/private/tmp/include_weekends_agendamentos_dashboard10.py`
- `/private/tmp/audit_weekends_dashboard10.py`

## Ponto que ainda exige decisão

A demanda atendida foi incluir sábado e domingo no realizado e nos cancelamentos. A meta e o share continuam calculados apenas sobre dias úteis. Incluir sábado e domingo também na distribuição da meta exigirá recalcular a baseline para sete dias e deve ser aprovado como uma mudança metodológica separada.
