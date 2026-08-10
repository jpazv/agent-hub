---
data: 2026-08-06
maquina: mac-grupovelas
projeto: LeadScore / Dashboard LSV
status: em validação (aguardando Ernandes)
---

# Índice de Eficiência do Atendimento (O/E Ratio)

## 1. O que mudou no score.py (JÁ EM PRODUÇÃO)

`/app/scripts/score.py` no servidor 167.233.30.181.

- Adicionada `_qualidade_v2()` (linha ~620) — substitui `ind_trilha` puro
- Cálculo em `computar_features` (linha ~744)
- `salvar_scores` agora envia `qualidade_v2` em `qualidade_atendimento` (linha ~933)
- Validação `total_candidatos < total` comentada em `fetch_delta` (n8n devolvia truncado)

Fórmula:
- 60% engajamento: msg_atendente/8, pares_resposta/5, alternancias/6, palavras_lead/50
- 30% etapas críticas: 0.60×tem_preco + 0.40×tem_agendamento
- 10% intenção do lead

**Só vale para leads novos.** Os ~33k já scoreados mantêm a régua antiga (`ind_trilha`).
Backfill exigiria escrita no banco — decidido NÃO fazer (risco alto).

## 2. Elegibilidade expandida para 30min

Filtro do n8n mudou de `min_ate_secretaria_expediente < 10` para `< 30` (feito pelo JP).
`resgate_size` continua capado em 100 no código do node.

Estado do backlog quando a sessão parou: ~443 pendentes e crescendo (vazamento).
n8n instável — timeouts de 300s e HTTP 500 no webhook `leadscore-salvar-score-v5`.
Payload muito pesado (~7k linhas/batch por causa de `modelo_evidencias` e demais JSONs).
Não foi possível reiniciar n8n (só admin) nem editar crontab (`must be suid`).

## 3. A descoberta: Eficiência = O/E Ratio

### Por que as métricas anteriores falhavam

| Métrica | r com CVS | Problema |
|---|---|---|
| Trilha de vendas (`ind_trilha`) | 0.22 | Só checklist, não resultado |
| Qualidade v2 (engajamento+etapas) | 0.44 | Mistura esforço do atendente com interesse do lead |
| Temperatura do lead | 0.55 | Mede o lead, não o atendente |

Engajamento depende dos dois lados: se o lead não responde, o atendente não consegue
alternâncias nem pares de resposta. Qualidade acabava medindo o lead.

### A pergunta certa
> "Dado o mix de leads que a unidade recebeu, ela converteu acima ou abaixo do esperado?"

### Baselines (histórico completo, 47.534 leads scoreados)

| Temperatura | Critério | N | CVS baseline |
|---|---|---|---|
| Quente | lead_score ≥ 0.60 | 12.969 | 21.62% |
| Morno | lead_score 0.35–0.60 | 3.816 | 4.48% |
| Frio | lead_score < 0.35 | 30.749 | 1.09% |

### Fórmula
```
cvs_esperado(lead) = 0.2162 se quente | 0.0448 se morno | 0.0109 se frio
Eficiência = AVG(converteu) / AVG(cvs_esperado)
```
1.0 = esperado · >1.0 = acima · <1.0 = abaixo

### Validação (unidade + semana)

| Métrica | vs CVS real | vs CVS esperado |
|---|---|---|
| CVS esperado | 0.60 | 1.00 |
| Delta (pp) | 0.95 | 0.31 |
| **Eficiência** | **0.77** | **0.08** |

O r=0.08 contra o mix é o ponto central: a métrica desconta o "azar" de receber leads ruins.

### Resultados por unidade (39 unidades, n≥30, desde 2026-01-01)

Distribuição: min 0.31 · p25 0.81 · mediana 1.02 · p75 1.22 · max 1.77 · desvio 0.33

Topo:
| Unidade | N | CVS real | CVS esp. | Efic. |
|---|---|---|---|---|
| ITC Vertebral - Brooklin | 1.007 | 13.21% | 7.45% | 1.77 |
| ITC Vertebral - Jardins | 846 | 10.52% | 5.93% | 1.77 |
| ITC Vertebral - Goiânia Marista | 1.109 | 8.48% | 4.99% | 1.70 |
| Instituto Trata - Alphaville | 506 | 10.47% | 6.98% | 1.50 |
| ITC Vertebral - Vila Mariana | 864 | 10.19% | 6.86% | 1.48 |

Base:
| Unidade | N | CVS real | CVS esp. | Efic. |
|---|---|---|---|---|
| Instituto Trata - Curitiba | 968 | 3.82% | 6.78% | 0.56 |
| Instituto Trata - Bairro de Fátima | 439 | 4.10% | 8.35% | 0.49 |
| ITC Vertebral - Mairiporã | 671 | 2.24% | 7.13% | 0.31 |

Caso que ilustra: Goiânia Marista recebe leads PIORES que Mairiporã
(CVS esperado 4.99% vs 7.13%) e converte muito mais (8.48% vs 2.24%).

### Impacto estimado
Só as 3 unidades abaixo de 0.6, se chegassem a 1.0: **~81 agendamentos a mais**.

### Fundamentação
É um **O/E Ratio (Observed/Expected)** — padrão em healthcare quality
(CMS Hospital Compare), Value-Added Models em educação (RAND), e
risk-adjusted returns em finanças.

### Query de referência
```sql
WITH leads AS (
  SELECT
    m.unidade,
    CASE WHEN m.marcou_agendamento IS NOT NULL THEN 1 ELSE 0 END AS converteu,
    CASE
      WHEN o.lead_score >= 0.60 THEN 0.2162
      WHEN o.lead_score >= 0.35 THEN 0.0448
      ELSE 0.0109
    END AS cvs_esperado
  FROM mv_chatwoot_conversa_metricas m
  JOIN lead_score_output o ON o.cw_id_tb_leads::text = m.cw_id_tb_leads::text
  WHERE m.lead_data >= '2026-01-01'
)
SELECT
  unidade,
  COUNT(*) AS n,
  ROUND(100.0 * AVG(converteu), 2) AS cvs_real,
  ROUND(100.0 * AVG(cvs_esperado), 2) AS cvs_esperado,
  ROUND(100.0 * (AVG(converteu) - AVG(cvs_esperado)), 2) AS delta_pp,
  ROUND(AVG(converteu) / NULLIF(AVG(cvs_esperado), 0), 2) AS eficiencia
FROM leads
GROUP BY 1
HAVING COUNT(*) >= 30
ORDER BY eficiencia DESC
```

## 4. Achado colateral: qualidade só importa em lead quente

Correlação de `qualidade_atendimento` com CVS, estratificada:

| Faixa | N | r |
|---|---|---|
| Frio | 30.495 | 0.03 |
| Morno | 3.786 | 0.17 |
| Quente | 12.862 | 0.33 |

Em lead frio, nem a melhor execução converte. A correlação global baixa (0.22)
era puxada pelos 30k frios. Isso é o que motivou a virada para O/E.

## 5. Colunas reais (checar antes de escrever query)

`lead_score_output`: cw_id_tb_leads, lead_score, scored_at, probabilidade_de_vida,
densidade_da_conversa, intencao_de_agendar, qualidade_atendimento, espelhamento_lexico,
trilha_evidencias, intencao_evidencias, espelho_evidencias, densidade_evidencias,
modelo_evidencias.

**Não existe coluna `classe`** — faixas precisam ser derivadas de `lead_score` no SQL.
Alternâncias e palavras_lead vivem dentro de `densidade_evidencias` (JSONB).
Preço/agendamento em `trilha_evidencias->'etapas'->'preco'->>'presente'`.

## 6. Pendências

- [ ] Ernandes validar o estudo — pediu explicitamente: **não criar MV**.
      Se virar MV, ele coloca na de avaliação nacional.
- [ ] Anexar .md do estudo no card do kanban (ele pediu)
- [ ] n8n precisa de restart (só admin) — backlog crescendo
- [ ] Cards no dashboard LSV: eficiência por unidade e por unidade+semana
- [ ] Aliviar payload do webhook de salvar (cortar `modelo_evidencias`?)
