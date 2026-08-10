---
data: 2026-08-10
maquina: mac-grupovelas
projeto: Metabase / Dashboards de unidade / LSV
status: dashboards entregues; spec da MV enviada ao chefe; grafico do LSV parado aguardando MV
---

# Metabase: correcao do dash Chapeco, novo dash Tatuape, e spec da MV do LSV

Complementa `2026-08-10-regua-expectativa-e-fontes-oficiais.md` (mesmo dia).
Aquele traz a regua; este traz o que foi feito no Metabase e o que falta.

## 1. Dash 270 (Chapeco) — filtro de socio errado, corrigido

**Sintoma:** o Relatorio de Performance de Chapeco mostrava dados do Tatuape.

**Causa:** o dashboard foi clonado do dashboard do Alexandre Almeida (Tatuape) e o
filtro `socio contains 'Alexandre'` ficou embutido **dentro de 66 saved questions**,
nao no dashboard. O parametro "Unidade" do dash apontava Chapeco e nao adiantava nada.

Comprovado por query: `socio contains Alexandre` devolve ITC Vertebral - Tatuape (366
linhas); `unidade contains ITC Vertebral - Chapeco` devolve Chapeco (242).

**Feito:** troca de `socio contains 'Alexandre'` por
`unidade contains 'ITC Vertebral - Chapeco'` em **64 dos 66 cards** (79 dashcards,
5 abas). Clause era uniforme, sempre em `query.filter` (solto ou dentro de um `and`).

**Nao corrigidos — 2 cards:** `8740` (Distribuicao de agendamentos x Hora) e `8763`
(Agendamentos por), aba Distribuicao. Usam o **modelo 1815**, que devolve
`403 Voce nao tem permissao` para a conta do JP. **Nao e regressao** — o card ja dava
403 antes da edicao. Precisa de alguem com permissao no 1815.

**Verificacao util:** `dashboard_count` do card conta **dashcards, nao dashboards
distintos**. Os 14 cards que pareciam compartilhados eram duplicatas dentro do proprio
dash 270. Sempre conferir contando dashcards no payload antes de concluir que um card
e usado em outro dashboard.

## 2. Dash 377 (Tempo de Resposta - Tatuape) — criado

Pedido: replicar na collection 132 o que a collection 100 tem para o Brooklin.

**Feito:** `POST /api/dashboard/373/copy` com `is_deep_copy: true` para a collection
132. Isso duplica dashboard **e** cards — muito mais confiavel que remontar 13
dashcards na mao. Depois troquei o SQL dos 11 cards novos (13283-13293).

Troca: `unidade IN ('ITC Vertebral - Brooklin')` para `'ITC Vertebral - Tatuape'`,
**43 ocorrencias** nos 11 SQLs (o "Comparativo periodo" tem 17 e o "Histograma" 16,
por causa dos `FILTER (WHERE)`). Os cards do Brooklin nao foram tocados.

Validado: card 13284 devolve `ITC Vertebral - Tatuape / 2.277`; o 13046 do Brooklin
segue em `ITC Vertebral - Brooklin / 1.065`.

## 3. Grafico novo do LSV — PARADO, aguardando MV do chefe

Pedido: agendamentos por faixa de temperatura versus os esperados daquela faixa.

### O que travou

O agendamento real tem que vir da `mv_hibrida_unidade_propria` (fonte oficial), mas
ela **nao tem identificador de lead**. Chaves testadas:

| Chave | Resultado |
|---|---|
| `mv_agendamento_propria.lead_id` | **16,2%** preenchido (era 21% no handoff anterior — piorou). Estavel 14-21% mes a mes, sem tendencia |
| `log_id` (existe nas duas pontas, 100% preenchido) | **e id de UNIDADE** — 229 valores distintos para 240.080 leads. Joinar por ele multiplica tudo |
| `client_id` / `people_id` / `patient_name` | 56,9% / 73,6% / 54,1% |

**O join de 100% por faixa nao existe, e nao e problema de chave:** 72% dos
agendamentos oficiais nao tem lead de origem (retorno, walk-in, ligacao) e portanto
nao tem temperatura para serem classificados. E definicional.

Numeros 2026: `mv_hibrida` = **13.280** agendamentos; grao do lead = **3.673** (28%).

### Desenho aprovado pelo JP

4 faixas com real vs esperado + uma 5a barra "Sem lead atribuivel" com o resto ate o
total oficial. Mantem o eixo de temperatura E reconcilia com os 13.280.

Query pronta e nao testada em `scratchpad/lsv_regua.sql` (a sessao acabou antes).
Usa a regua **por marca** do handoff da regua, CTE `oficial` limitada por
`unidade IN (SELECT DISTINCT unidade FROM mvf)` e o range de `lead_data` — jeito de
fazer o total oficial respeitar os filtros do dashboard sem acesso ao valor dos
field filters. `tipo_campanha` **nao existe** na `mv_hibrida`; esse filtro nao se
aplica ao lado oficial.

### Confirmacao boa

A regua congelada em 07/08 bate com o dado corrente:

| Faixa | Regua congelada | Observado 2026 |
|---|---|---|
| Quente > 0,719 | 25,55% | 25,28% |
| Pre-quente 0,60-0,719 | 13,63% | 13,53% |
| Morno 0,35-0,60 | 4,41% | 4,28% |
| Frio < 0,35 | 1,11% | 1,07% |

## 4. Spec da MV — enviada ao chefe

O dash LSV (369, 22 cards) le **duas tabelas fisicas**; todo o resto e CTE.

**`mv_chatwoot_conversa_metricas`** — cw_id_tb_leads, lead_data, unidade, marca,
tipo_campanha, marcou_agendamento, contact_nome, contact_telefone
(os 4 filtros do dash sao os fields 6531 / 6252 / 6279 / 6268)

**`lead_score_output`** — cw_id_tb_leads, lead_score, scored_at,
qualidade_atendimento, intencao_de_agendar, espelhamento_lexico,
densidade_da_conversa, probabilidade_de_vida, trilha_evidencias

**Deixar de fora:** `intencao_evidencias`, `espelho_evidencias`,
`densidade_evidencias`, `modelo_evidencias` — nenhum card usa, e sao os jsonb que
deixaram o payload do n8n em ~7k linhas por batch.

**`mv_hibrida_unidade_propria`** (separada) — data, unidade, marca, agend, leads_sec

### Tres regras passadas junto

1. **Nao pode ser MV unica** — grao incompativel (lead vs unidade x dia). Recomendado:
   MV no grao do lead + hibrida separada, join por `unidade + data`. Pre-agregar por
   unidade x semana quebraria os cards que precisam de linha por lead (lista de
   retorno, ranking, histograma)
2. **Guardar `lead_score` cru, nunca a faixa nem o `cvs_esperado`** — a regua ja mudou
   duas vezes; faixa materializada vira rebuild a cada mudanca
3. **Nomear os numeradores** `agend_oficial` vs `agend_atribuivel_a_lead` — sem rotulo,
   quem misturar infla a eficiencia ~3,6x

## 5. Documentos desatualizados (confirmado nesta sessao)

O estudo "Indice de Eficiencia do Atendimento" (06/08, JP) e a planilha
`~/Downloads/eficiencia_matriz.xlsx` (414 linhas, unidade x semana, 13 colunas) usam a
regua **antiga**: 3 faixas, corte 0,60, constantes 0.2162 / 0.0448 / 0.0109.
Supersedidos pela regua de 4 faixas por marca.

## 6. Pendencias

- [ ] Testar e criar o card do grafico de faixas no LSV (query em `lsv_regua.sql`)
- [ ] Modelo **1815** sem permissao — trava 2 cards do dash 270 e ja era pendencia do
      handoff da regua (junto com o `card__67`)
- [ ] Varrer os outros 18 dashboards de socios: se algum foi clonado do dashboard
      errado, tem o mesmo sintoma do 270 (filtro de socio divergente do nome do dash)
- [ ] Atualizar o estudo de eficiencia e a planilha para a regua de 4 faixas por marca

## 7. Token

A sessao `a8fc6a42-fa5f-4107-946f-b62ccff2dbf0` (do handoff de 05/08) **continua
valida** em 10/08.
