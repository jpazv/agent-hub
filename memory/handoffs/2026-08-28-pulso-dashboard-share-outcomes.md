# Handoff — Dashboard Pulso e share semanal na MKT Outcomes

**Data:** 2026-08-28  
**Máquina:** `mac-grupovelas`  
**Sessão:** global / Metabase  
**Responsável:** JP (`jpazv`)

## Resultado executivo

- O gráfico de agendamentos no dashboard 10 foi recriado corretamente com Realizado, Cancelamentos, Meta Flat e Meta Ponderada.
- O gráfico responde a Dia, Semana e Mês; a Meta Ponderada pelo share aparece somente em Dia, que é o padrão.
- Foi criado o dashboard **434 — Pulso** na collection **Estudos (677)**.
- O Pulso usa exclusivamente `public.mv_mkt_outcomes_diario` e trabalha com as 13 semanas completas disponíveis.
- Foram criadas 3 abas, 9 questions reais e 12 cards de texto explicativo.

## Dashboard 10 — card definitivo

- Dashboard: `10`
- Card: `15259`
- Dashcard: `22611`
- Collection do card: `12` — a mesma do dashboard; não depende de Estudos.
- Nome: `Realizado, Cancelamentos e Metas — Semanas Completas por Período`
- Posição: aba `5`, linha `63`, largura `24`, altura `8`.
- Mappings: Data, Marca, Unidade e Sócio duplicados entre realizado/meta oficial, mais Agrupamento de tempo; total `9`.
- Semana operacional: domingo a sábado.

Validação:

| Agrupamento | Pontos | Cancelamentos | Meta ponderada/share |
|---|---:|---:|---:|
| Dia | 20 | 549 | 20 valores |
| Semana | 4 | 549 | 0 valores |
| Mês | 1 | 549 | 0 valores |

O dashboard 10 permaneceu com `117` dashcards. Nenhuma série preexistente foi perdida. O card intermediário `15256` foi removido após a substituição.

## Dashboard 434 — Pulso

- URL: `https://metabase.grupovelas.com.br/dashboard/434`
- Collection: `677` — Estudos.
- Filtros: Marca, Unidade, Sócio, Boutique e Tipo de campanha.
- Todos os cards foram criados já com `dashboard_id=434` e `collection_id=677`.
- Auditoria final: 3 abas, 21 dashcards, 5 filtros; cada question aparece uma vez e possui 5 mappings.

### Abas

1. `Pulso semanal` (`tab_id=1223`)
2. `Causa do desvio` (`tab_id=1224`)
3. `Share — 13 semanas` (`tab_id=1225`)

### Questions

| Card | Nome |
|---:|---|
| 15260 | Pulso — Unidades por estado |
| 15261 | Pulso — Mapa semanal das unidades |
| 15262 | Pulso — Ritmo semanal da rede |
| 15263 | Pulso — Causa dominante do gap |
| 15264 | Pulso — Quadrante investimento x agendamentos |
| 15265 | Pulso — Decomposição do gap por unidade |
| 15266 | Pulso — Gap de share da última semana |
| 15267 | Pulso — Share da última semana |
| 15268 | Pulso — Estabilidade do share em 13 semanas |

Teste de filtro: card `15261` com Marca `ITC Vertebral` completou e retornou 25 unidades; sem filtro retornava 41.

## Metodologia do Pulso

### Estados

- Saudável e sustentada: semana fechada e projeção atual >= 100% da meta.
- Boa, mas desacelerando: fechou >= 100%, projeção atual < 100%.
- Recuperando: fechou < 100%, projeção atual >= 100%.
- Abaixo persistente: fechou e projeta abaixo, com pelo menos 2 das últimas 3 semanas abaixo.
- Abaixo/volátil: demais casos abaixo sem persistência suficiente.

### Projeção da semana atual

`projeção = realizado até D-1 / share histórico dos dias transcorridos`

Os shares de investimento, leads e agendamentos são calculados separadamente sobre as 13 semanas completas.

### Decomposição do gap

Referência: oito semanas anteriores à última semana fechada.

1. efeito investimento;
2. efeito geração de leads por real;
3. efeito da relação agendamentos/leads.

A soma reconcilia a diferença entre agendamentos observados e a referência. É diagnóstico descritivo, não inferência causal.

### Share

- `share_investimento = investimento da unidade / investimento da rede na semana`
- `share_leads = leads da unidade / leads da rede na semana`
- `share_agendamentos = agendamentos da unidade / agendamentos da rede na semana`
- `gap_share = share_agendamentos - share_investimento`

## Achados iniciais do share — 13 semanas

- 13 semanas e 44 unidades no grid da outcomes.
- Correlação share investimento × share leads: `0,738`.
- Correlação share investimento × share agendamentos: `0,563`.
- Na última semana fechada: 20 unidades com gap positivo e 21 com gap negativo; as demais ficaram neutras/sem volume comparável.
- Top 5 unidades: 18,5% do share de investimento e 20,5% do share de agendamentos.
- Mediana da volatilidade semanal do share de investimento: `0,49 p.p.`.
- 17 unidades tiveram gap médio positivo ao longo das 13 semanas.

Interpretação: investimento explica melhor a distribuição de leads do que a distribuição de agendamentos. O gap de share ajuda a encontrar eficiência relativa, mas não deve ser usado isoladamente para cortar ou aumentar verba.

## Limitações

- A outcomes começa operacionalmente em 20/05/2026; há apenas 13 semanas completas.
- `agendamentos` e `leads` estão agregados por data, unidade e campanha, sem vínculo de coorte entre o lead e o agendamento.
- `agendamentos / leads` é uma relação operacional do período, não uma taxa de conversão causal de coorte.
- A projeção da semana atual é uma projeção de ritmo e deve ser recalculada a cada atualização da MV.

## Temporários da sessão

- `/private/tmp/add_cancellations_share_period_dashboard10.py`
- `/private/tmp/create_pulso_dashboard.py`
- backups do dashboard 10 em `/private/tmp/dashboard-10-before-*`

## Próximos passos sugeridos

1. Validar visualmente o Pulso com o usuário e ajustar densidade/ordenação das tabelas.
2. Revisar thresholds dos estados após uso operacional.
3. Testar fallback de projeção por marca/unidade quando houver mais semanas.
4. Se aprovado, documentar o estudo na issue #353.
