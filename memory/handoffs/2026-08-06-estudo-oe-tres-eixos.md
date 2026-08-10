---
data: 2026-08-06
maquina: mac-grupovelas
projeto: LeadScore / Dashboard LSV
status: estudo concluído — pronto para validação
base: Metabase DB 2 (Grupo Velas), schema public
janela: 2026-05-20 a 2026-08-06 (47.641 leads com score, 52.650 na MV)
---

# Estudo — O/E de Três Eixos e a peneira out-of-sample

Continuação de `2026-08-06-eficiencia-atendimento-oe-ratio.md`. Aquele estudo achou o
O/E de agendamento. Este responde três perguntas novas: (1) o O/E se aplica ao resto do
funil? (2) é habilidade ou sorte? (3) qual comportamento controlável move o índice?

## 0. Onde estão os dados (Metabase)

| O que | Onde |
|---|---|
| Base URL | `https://metabase.grupovelas.com.br` |
| Database | id **2** = "Grupo Velas" (postgres). id 4 = "Base LSV" (não tem o score) |
| Score | `public.lead_score_output` (table 422) |
| Funil + conversa | `public.mv_chatwoot_conversa_metricas` (table 383) — 54 colunas |
| Faixas de resposta | `public.mv_chatwoot_faixa_resposta` (table 462) |
| Mensagens | `public.mv_chatwoot_mensagens` (472) + `public.messages` (sender_id) |
| Receita | `analytics.mv_venda_propria` / `mv_venda_franquia` (`total_value`) |
| Dashboard 10 | 7 abas (RPD, Acelerômetros, Consolidado, Vendas Detalhado, Evolução, Histórico, Distribuição). Cards nativos + modelos card__2457/51/2141/1816/2228 |

Join: `lead_score_output.cw_id_tb_leads = mv_chatwoot_conversa_metricas.cw_id_tb_leads`
(ambos text — o cast `::text` do estudo anterior é desnecessário nesta base).

**Atenção:** a MV só guarda de 2026-05-20 em diante. O `WHERE lead_data >= '2026-01-01'`
do estudo anterior não filtra nada hoje.

## 1. Confirmação do O/E de agendamento (mais forte que antes)

Nível unidade+semana, 414 células com n≥30:

| Correlação | r | Leitura |
|---|---|---|
| Eficiência × CVS real | **0,806** | mede resultado |
| Eficiência × mix (CVS esperado) | **−0,092** | imune à sorte |
| CVS bruto × mix | 0,402 | 16% da variação do CVS bruto é sorte no mix |

## 2. Achado principal: são TRÊS eixos ortogonais, não um

O funil tem três transições e cada uma tem seu próprio baseline por temperatura:

| Etapa | Quente | Morno | Frio |
|---|---|---|---|
| **Agendar** (lead → agend.) | 21,62% | 4,48% | 1,09% |
| **Comparecer** (agend. → AV) | 73,77% | 54,39% | 49,11% |
| **Fechar** (AV → tratamento) | 42,02% | 32,26% | 17,47% |

Comparecimento e fechamento **também** dependem fortemente do mix — por isso precisam
de O/E próprio, e por isso hoje parecem ruído.

Matriz entre os três O/E por unidade (37 unidades):

| | ag × comp | ag × fech | comp × fech |
|---|---|---|---|
| r | −0,09 | +0,10 | −0,16 |

**Ortogonais.** Quem agenda bem não faz comparecer nem fecha melhor. Um índice único
esconde três problemas distintos. Exemplos:

| Unidade | O/E agendar | O/E comparecer | O/E fechar | Diagnóstico |
|---|---|---|---|---|
| Goiânia Marista | **1,72** | 0,94 | **0,49** | agenda muito, perde na avaliação |
| ITC Curitiba | **0,77** | **1,26** | 0,75 | agenda pouco, mas quem agenda vem |
| Trata Brooklin | 1,25 | **0,70** | **1,57** | no-show alto, fechamento excelente |
| ITC Jardins | 1,79 | 1,03 | 1,34 | forte nos três |

## 3. Teste de habilidade: split-half por unidade

Semanas pares vs ímpares, mesma unidade. Se é habilidade, persiste.

| Índice | Estabilidade |
|---|---|
| O/E agendar | **0,70** |
| O/E comparecer | 0,57 |
| O/E fechar | 0,47 |
| CVS bruto | 0,68 (mas contaminado — o mix também é persistente por unidade) |

O/E agendar é habilidade real e reprodutível.

## 4. A peneira que matou os candidatos: driver na metade A → O/E na metade B

Correlação cross-half. Só passa quem prevê o **futuro**, não o próprio período.

| Driver | Prevê O/E futuro |
|---|---|
| **O/E (baseline)** | **0,742** |
| msg_bot | 0,186 |
| cadência resposta p50 | 0,150 |
| % SLA > 30min | 0,058 |
| msg_humano | 0,055 |
| reciprocidade | −0,096 |
| **qualidade_v2 (em produção)** | **−0,168** |
| carga leads/dia | −0,187 |
| **densidade_da_conversa** | **−0,281** |
| **espelhamento_lexico** | **−0,295** |

**Nenhum comportamento de conversa prevê eficiência.** E três subscores em produção são
negativamente preditivos.

### O caso da reciprocidade (armadilha instrutiva)

`pares_resposta_humana / msg_inbound` = fração das falas do lead que foram respondidas.
A nível de lead pareceu espetacular:

| Reciprocidade | n | CVS | CVS esp. | O/E |
|---|---|---|---|---|
| <20% | 313 | 4,79% | **11,69%** | **0,41** |
| 20–40% | 1.693 | 3,31% | 7,22% | 0,46 |
| 40–60% | 2.021 | 6,58% | 9,14% | 0,72 |
| 60–80% | 8.280 | 4,84% | 7,92% | 0,61 |
| 80%+ | 16.109 | 15,79% | 12,14% | **1,30** |

Estabilidade split-half de **0,95** — a métrica mais estável que medimos. E prevê O/E
futuro a **−0,10**. É causalidade reversa: lead interessado continua falando e é
respondido; lead que esfria é abandonado no meio do fio. Reciprocidade é *consequência*
do interesse, não causa da conversão.

Lição: correlação alta + estabilidade alta não bastam. **Só o teste cross-half separa
métrica de espelho.**

## 5. Duas hipóteses operacionais derrubadas

### SLA instantâneo não compra conversão

`min_ate_secretaria_expediente` está **contaminada**: zera o contador de quem chega fora
do expediente. No bucket "<1min", o SLA *geral* mediano é 39,4 min (pior que os 32,8 min
do resto) e 54% dos leads chegaram fora do horário. A métrica que a operação persegue
mede a hora de chegada do lead, não a velocidade do time.

Refazendo com `min_ate_secretaria` e só leads dentro do expediente (8h–18h, seg–sex):

| SLA | n | O/E |
|---|---|---|
| <1min | 6.730 | 1,06 |
| 1–5min | 5.792 | 1,14 |
| 5–15min | 2.637 | 1,16 |
| 15–30min | 1.238 | **1,20** |
| 30–60min | 508 | 0,85 |
| >3h | 542 | 1,00 |

**Plano de 0 a 30 min, degrau depois.** Não há gradiente — perseguir <2min não tem
retorno medido; garantir <30min tem.

### Sobrecarga diária não derruba eficiência

Entre unidades, carga × O/E dá r=−0,36 — parece saturação. Within-unit (mesma unidade,
dia de pico vs dia normal) o O/E é plano:

| Carga do dia | n | O/E | SLA p90 |
|---|---|---|---|
| baixa | 7.638 | 1,001 | 32,6 min |
| normal | 29.334 | 1,004 | 28,4 min |
| alta | 8.274 | 0,980 | 49,2 min |
| pico | 2.395 | 1,022 | 58,6 min |

O SLA p90 dobra no pico e a conversão não cai. O r=−0,36 era confounding: unidades
grandes têm eficiência menor por razões estruturais, não por saturação.

## 6. Bloqueio de infraestrutura: não há como medir atendente

Passo natural após O/E por unidade seria O/E por atendente. Hoje é impossível:

| Remetente | Mensagens | % |
|---|---|---|
| conta de integração (`sender_id` 181 "WhatsApp" + 1 "Não direcionar") | 487.461 | **98,42%** |
| atendentes nomeados (83 usuários) | 7.811 | 1,58% |

Só **4,83%** dos leads têm atendente identificável. `conversations.assignee_id` está
preenchido em 2% (o time não usa atribuição).

**Recomendação:** um usuário Chatwoot por atendente na integração WhatsApp. Sem isso,
nenhuma métrica individual é possível — e é aí que mora o maior ganho de gestão.

## 7. Tamanho da oportunidade

Gap das unidades abaixo de 1,0 na janela de 2,5 meses (37 unidades, n≥200 e AV≥15):

| Eixo | Realizado | Gap | Unidades abaixo |
|---|---|---|---|
| Agendar | 3.319 | **+357** | 18 / 39 |
| Comparecer | 2.332 | **+111** | 20 / 39 |
| Fechar | 930 | **+90** | 19 / 39 |

Simulação em cascata (os três eixos a 1,0): 925 → 1.008 tratamentos = **+83 (+8,9%)**.
Os gaps não se somam justamente porque os eixos são ortogonais — quem está mal em
agendar geralmente está bem em fechar.

Ticket médio R$ 3.641 (mediana R$ 2.850, 3.925 vendas na janela):
**+83 tratamentos em 79 dias ≈ 383/ano ≈ R$ 1,1–1,4 mi/ano.**

## 8. Recomendações

1. **Dashboard LSV: três cards de O/E**, não um. Agendar / Comparecer / Fechar por
   unidade. O diagnóstico está no *perfil* dos três, não na média.
2. **Tirar `espelhamento_lexico` e `densidade_da_conversa` do composto de qualidade** —
   são negativamente preditivos (−0,30 e −0,28). A `qualidade_v2` inteira precisa de
   revisão (−0,17).
3. **Trocar a meta de SLA**: de "responder em <2min" para "nenhum lead acima de 30min
   no expediente". E **corrigir `min_ate_secretaria_expediente`**, que hoje mede a hora
   de chegada do lead.
4. **Um usuário Chatwoot por atendente** — desbloqueia O/E individual.
5. **Adotar o teste cross-half como critério** de aceite de qualquer métrica nova de
   qualidade. Foi o que separou o O/E dos espelhos.
6. Investigar o que sobra: os três O/E são estáveis e nada da conversa os explica. A
   causa está fora do chat — agenda/capacidade, equipe clínica, tratamento de preço,
   follow-up fora do Chatwoot.

## 9. SQL de referência — O/E dos três eixos

```sql
WITH b AS (
  SELECT m.unidade,
    (m.marcou_agendamento IS NOT NULL)::int AS agend,
    (m.realizou_av        IS NOT NULL)::int AS av,
    (m.converteu_tto      IS NOT NULL)::int AS tto,
    CASE WHEN o.lead_score >= 0.60 THEN 0.2162
         WHEN o.lead_score >= 0.35 THEN 0.0448 ELSE 0.0109 END AS e_agend,
    CASE WHEN o.lead_score >= 0.60 THEN 0.7377
         WHEN o.lead_score >= 0.35 THEN 0.5439 ELSE 0.4911 END AS e_compar,
    CASE WHEN o.lead_score >= 0.60 THEN 0.4202
         WHEN o.lead_score >= 0.35 THEN 0.3226 ELSE 0.1747 END AS e_fech
  FROM mv_chatwoot_conversa_metricas m
  JOIN lead_score_output o ON o.cw_id_tb_leads = m.cw_id_tb_leads
)
SELECT unidade,
  count(*) AS n,
  round(100.0 * avg(agend), 2)                                   AS cvs,
  round(100.0 * avg(e_agend), 2)                                 AS cvs_esperado,
  round((avg(agend) / nullif(avg(e_agend), 0))::numeric, 2)       AS oe_agendar,
  round((sum(av)::numeric  / nullif(sum(e_compar * agend), 0)), 2) AS oe_comparecer,
  round((sum(tto)::numeric / nullif(sum(e_fech   * av),    0)), 2) AS oe_fechar
FROM b
GROUP BY 1
HAVING count(*) >= 200 AND sum(av) >= 15
ORDER BY oe_agendar DESC;
```

Baselines de comparecer/fechar recalculados nesta janela — **recalcular junto com os de
agendar** se a régua for revisada.

## 10. Pendências herdadas (do handoff anterior)

- [ ] Ernandes validar — pediu **não criar MV**
- [ ] Anexar .md do estudo no card do kanban (este arquivo serve)
- [ ] n8n precisa de restart (só admin) — backlog crescendo
- [ ] Aliviar payload do webhook de salvar (cortar `modelo_evidencias`?)
