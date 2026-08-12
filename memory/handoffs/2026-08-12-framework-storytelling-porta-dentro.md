# Handoff: Framework Storytelling — Porta Pra Dentro

**Data:** 2026-08-12
**Autor:** JP + Claude
**Projeto:** lead-quality-score
**Status:** plano aprovado, pendente execução

---

## Contexto

Sessão de brainstorming (~1h) para definir o framework estratégico de como apresentar os dados de conversa do LeadScore aos gestores de unidade. O problema não é falta de dado — é que o gestor (1) não acredita nos dados, (2) não sabe o que fazer com eles, (3) não sente urgência.

O framework será um documento interno do BI em `projects/lead-quality-score/docs/framework-storytelling-porta-dentro.md`.

---

## Decisões tomadas

### Modelo mental: Porta Pra Fora × Porta Pra Dentro

- **Porta pra fora** (marketing): campanha → criativo → clique → lead chega. Já coberto no dashboard Tráfego Pago.
- **Porta pra dentro** (atendimento): lead chega → conversa → agendamento. Dados existem, falta storytelling.
- **Divisor**: primeira mensagem do lead. A partir dali, responsabilidade da unidade.

### Audiência e resistências

- **Público**: gestor de cada uma das 38 unidades
- **Resistências**: não acreditam nos dados, não sabem agir, falta urgência
- **Argumento central**: "dinheiro na mesa" — leads quentes que chegaram e não foram convertidos
- **Ticket médio**: parametrizável (cada unidade inputa o seu)

### 4 faixas de temperatura (NÃO 3)

O dashboard LSV usa 4 faixas. O estudo de eficiência original (`docs/estudo-eficiencia-atendimento.md`) usou 3 (thresholds 0.35/0.60). O framework adota as 4:

| Faixa | Temperatura | Score | Volume (90d) | CVS |
|---|---|---|---|---|
| Muito Quente | 73° – 100° | ≥0.73 | 9.536 | 26,0% |
| Quente | 51° – 72° | 0.51–0.72 | 8.194 | 11,4% |
| Morno | 26° – 50° | 0.26–0.50 | 6.781 | 2,9% |
| Frio | 0° – 25° | <0.26 | 31.004 | 0,9% |

**Implicação**: os baselines do estudo de eficiência precisam ser recalculados com 4 faixas.

### PILAR CENTRAL — Arco da Conversa

**Gap identificado**: hoje o score mede lead e secretária separadamente (monólogos paralelos). Não mede o DIÁLOGO — como o interesse do lead evoluiu ao longo da conversa e o que a secretária fez em cada momento.

**Conceito**: dividir conversa em 3 terços (início, meio, fim). Para cada terço:
- Temperatura do lead (aplicar `_intencao_agendar()` só nas msgs do lead daquele terço)
- Ação da secretária (aplicar `_detect_trilha()` só nas msgs da secretária daquele terço)

**6 arcos** (compara faixa do 1º terço vs último):

| Arco | Direção | Exemplo | Implicação |
|---|---|---|---|
| Conquista | Subiu ≥2 faixas | Frio→Quente | Atendimento excelente — estudar |
| Aquecimento | Subiu 1 faixa | Quente→Muito Quente | Bom sinal |
| Manutenção | Manteve | Quente→Quente | Padrão esperado |
| Esfriamento | Caiu 1 faixa | Muito Quente→Quente | Atenção |
| Perda | Caiu ≥2 faixas | Quente→Frio | **Maior oportunidade** |
| Indiferença | Frio→Frio | Nunca engajou | Problema porta pra fora |

**100% determinístico** — mesmas funções do score.py aplicadas por janela, sem LLM, sem treinar modelo.

### Framework de convencimento: 3 camadas

1. **"O número que não dá pra ignorar"** — leads_quentes_perdidos × ticket_médio = R$ na mesa
2. **"O benchmark justo"** — índice de eficiência (já validado, confiabilidade 0,89)
3. **"O que fazer"** — decomposição em SLA, trilha, densidade, espelho + arco da conversa

### Trilha da secretária: 3 níveis de evolução

A trilha tem 6 etapas (abordagem → sondagem → captura → apresentação → agendamento → preço), definidas por marca (ITC vs Trata) em `score.py` nas dicts `TRILHA_ITC` e `TRILHA_TRATA`.

- **Nível 1 (atual)**: keyword presente sim/não
- **Nível 2**: ordem correta, profundidade (tokens por etapa), reação do lead pós-etapa, ratio sondagem/preço
- **Nível 3**: pares pergunta-resposta, objeção→contorno, ritmo temporal

### Impacto na arquitetura

**score.py** — nova função `_arco_conversa(transcript)`, aditiva:
- Chamada dentro de `computar_features()`
- Não altera os 4 indicadores existentes nem a fórmula de temperatura
- Retorna: arco (string) + temperatura_tercos (dict)

**n8n (LeadScore - V5-3.json)** — novos campos no payload do webhook "Salvar Score":
- `arco_conversa`: VARCHAR(20)
- `temperatura_tercos`: JSONB

**lead_score_output** — ALTER TABLE com 2 colunas novas (nullable, zero risco)

---

## Dados levantados nesta sessão (Metabase, 90 dias)

- CPL médio: R$ 16,46 | Investimento total: R$ 942k | 57k leads
- ~14.000 leads Quentes+Muito Quentes não agendaram → ~R$ 230k em custo de aquisição
- Spread entre unidades (leads muito quentes): Jardins 40,8% vs Mairiporã 6,5%
- SLA de resposta: 0-15 min ~23,7% CVS → 4+ hrs 19,2% (efeito moderado, ~4pp)
- Eficiência: Goiânia Marista recebe piores leads (CVS esperado 4,02%), entrega 1,62. Mairiporã recebe bons leads (7,33%), entrega 0,30.

---

## Pendências da sessão (além do framework)

### Dashboard 316 — Tráfego Pago

**Aba Alertas (929)** — 5 cards criados:
- Card 13518: Alerta CPL — Criativos (CPL com delta 7d/30d, tipo_campanha)
- Card 13519: Alerta Leads — Criativos sem Leads (3 dias, tipo_campanha)
- Card 13520: Alerta CPL — Unidades (CPL com delta 7d/30d)
- Card 13526: CPL acima de R$25 — Criativos (30d, filtro invest_min R$100)
- Card 13528: Alerta CPV — Engajamento (ENG, filtro invest_min R$10)
- Text card explicativo com legenda de cores

**Aba Criativos (915)** — 1 card criado:
- Card 13532: Visão por Tipo de Campanha — Criativos (pivot com total investido no header)
  - Mesma lógica do card 13294 (Ranking de Métricas), com total investido dos criativos rankeados no header
  - Filtros conectados: Métrica, Top N, Investimento mínimo, Data, Marca
  - Texto da aba atualizado com nota sobre a segunda tabela

### Outros pendentes
- Atualizar issue 249 no kanban (Grupo-Velas/produtividade-bi-dev)
- Cleanup dashboard 382 (criado por engano)
- Texto explicativo da aba Alertas já inclui os novos cards

---

## Próximo passo

Executar o plano em `~/.claude/plans/functional-giggling-beaver.md`:
1. Escrever o documento framework em `projects/lead-quality-score/docs/framework-storytelling-porta-dentro.md`
2. Recalcular baselines de eficiência com 4 faixas
3. Prototipar `_arco_conversa()` e validar sobre amostra de conversas reais
