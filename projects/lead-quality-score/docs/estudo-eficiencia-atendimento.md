# Estudo: Índice de Eficiência do Atendimento

**Autor:** João Paulo Azevedo
**Data:** 06/08/2026
**Status:** Validado estatisticamente
**Issue:** #240 · `Grupo-Velas/produtividade-bi-dev`

> Esta versão substitui os números publicados anteriormente. A base foi
> reprocessada sobre a matriz completa unidade × semana (414 células, 39
> unidades, 12 semanas: 18/05 a 03/08/2026) e foram acrescentados os testes de
> confiabilidade, que antes não existiam.

---

## Fundamentação metodológica

A métrica segue o framework de **Observed/Expected Ratio (O/E)**, usado em
healthcare quality measurement (CMS) e em Value-Added Models na educação (RAND).

Princípio: ajustar a performance observada pela dificuldade inerente do caso
recebido, permitindo comparação justa entre unidades que operam em contextos
diferentes.

**Referências**
- CMS Hospital Compare Methodology (cms.gov)
- RAND Corporation, *Value-Added Models* (2014)
- Iezzoni, L. *Risk Adjustment for Measuring Healthcare Outcomes*, 4ª ed.

---

## 1. O problema

Medir a qualidade do atendimento de forma justa, sem penalizar unidades que
recebem leads menos qualificados.

Métricas tradicionais falham porque misturam dois fatores: o **esforço do
atendente** (que ele controla) e o **interesse do lead** (que ele não controla).

### Abordagens anteriores testadas

| Métrica | Correlação com CVS | Problema |
|---|---|---|
| Trilha de vendas (`ind_trilha`) | 0,22 | Mede checklist, não resultado |
| Qualidade v2 (engajamento + etapas) | 0,44 | Mistura esforço do atendente com interesse do lead |
| Temperatura do lead | 0,55 | Mede o lead, não o atendente |

### A pergunta certa

> Dado o mix de leads que a unidade recebeu, ela converteu acima ou abaixo do esperado?

---

## 2. Metodologia

### 2.1 Baseline por temperatura

Agregando todo o histórico scoreado (**47.703 leads**):

| Temperatura | Critério | N | CVS baseline |
|---|---|---|---|
| Quente | `score >= 0.60` | 13.030 | **21,61%** |
| Morno | `0.35 <= score < 0.60` | 3.830 | **4,46%** |
| Frio | `score < 0.35` | 30.843 | **1,11%** |

As constantes em produção seguem `0.2162 / 0.0448 / 0.0109`. A diferença na
segunda casa vem do crescimento da base desde o cálculo original e é
irrelevante para o índice.

### 2.2 CVS esperado

```
cvs_esperado_lead = 0.2162  se score >= 0.60
                    0.0448  se score >= 0.35
                    0.0109  caso contrário

CVS_esperado_unidade = média(cvs_esperado) de todos os leads recebidos
```

### 2.3 Eficiência

```
Eficiência = CVS_real / CVS_esperado
```

| Valor | Significado |
|---|---|
| 1,0 | Converteu exatamente o esperado |
| 1,5 | Converteu 50% acima do esperado |
| 0,7 | Converteu 30% abaixo do esperado |

---

## 3. Validação estatística

A métrica foi submetida a três testes independentes, cada um respondendo a uma
objeção diferente.

### 3.1 Validade — a métrica acompanha o resultado?

| Par | Nível | n | Pearson |
|---|---|---|---|
| Eficiência × CVS real | unidade | 39 | **+0,881** |
| Eficiência × CVS real | unidade + semana | 414 | **+0,805** |

**Ressalva honesta:** `CVS_real` é o numerador da eficiência, então parte dessa
correlação é aritmética, não empírica. Ela confirma que a conta está correta —
não é, sozinha, evidência de que a métrica capture algo real. Por isso os dois
testes seguintes.

### 3.2 Confiabilidade — a métrica se reproduz?

Teste split-half: calcula-se a eficiência de cada unidade usando **apenas as
semanas ímpares**, depois **apenas as pares**, e correlacionam-se os dois
conjuntos. São amostras independentes — o resultado não pode vir de tautologia.

| Teste | Valor |
|---|---|
| Split-half bruto (37 unidades com 6+ semanas) | **+0,796** |
| Corrigido por Spearman-Brown | **+0,887** |
| Persistência semana → semana seguinte (368 pares) | +0,438 |
| ICC — fração da variância entre unidades | 0,359 |

**A eficiência da unidade é um atributo estável, não acaso da amostra.** Este é
o resultado que sustenta a métrica.

### 3.3 Independência do mix — a métrica desconta o azar?

É a promessa central do índice.

| Par | Nível | Pearson | p |
|---|---|---|---|
| Eficiência × CVS esperado | unidade | −0,184 | 0,26 |
| Eficiência × % de leads quentes | unidade | −0,174 | 0,29 |
| Eficiência × CVS esperado | unidade + semana | −0,094 | 0,06 |

Todos estatisticamente indistinguíveis de zero. **A métrica de fato desconta o
mix de leads recebidos.**

### 3.4 Um achado que reforça a tese

| Par | Nível | Pearson | p |
|---|---|---|---|
| CVS esperado × CVS real | unidade | +0,280 | 0,085 |

O mix de leads que a unidade recebe **quase não explica o resultado dela** — nem
atinge significância estatística. O que explica é o que ela faz com os leads.

---

## 4. Resultados por unidade

### 4.1 Distribuição (39 unidades, 12 semanas)

| Estatística | Valor |
|---|---|
| Mínimo | 0,297 |
| 25º percentil | 0,802 |
| **Mediana** | **1,013** |
| 75º percentil | 1,204 |
| Máximo | 1,787 |
| Desvio padrão | 0,336 |
| Unidades acima de 1,0 | 20 de 39 |

### 4.2 Topo

| # | Unidade | N | CVS real | CVS esperado | Δ pp | Eficiência |
|---|---|---|---|---|---|---|
| 1 | ITC Vertebral — Jardins | 847 | 10,63% | 5,95% | +4,68 | **1,787** |
| 2 | ITC Vertebral — Brooklin | 1.008 | 13,19% | 7,44% | +5,75 | **1,774** |
| 3 | ITC Vertebral — Goiânia Setor Marista | 1.017 | 6,49% | 4,02% | +2,47 | **1,615** |
| 4 | ITC Vertebral — Vila Mariana | 870 | 10,11% | 6,87% | +3,24 | 1,473 |
| 5 | Instituto Trata — Alphaville | 493 | 10,14% | 6,93% | +3,21 | 1,463 |

### 4.3 Base

| # | Unidade | N | CVS real | CVS esperado | Δ pp | Eficiência |
|---|---|---|---|---|---|---|
| 37 | Instituto Trata — Curitiba | 970 | 3,81% | 6,77% | −2,96 | 0,563 |
| 38 | Instituto Trata — Bairro de Fátima | 309 | 2,91% | 8,37% | −5,46 | 0,348 |
| 39 | ITC Vertebral — Mairiporã | 642 | 2,18% | 7,33% | −5,15 | **0,297** |

**Goiânia Setor Marista recebe os piores leads da rede** (CVS esperado 4,02%) e
mesmo assim entrega 1,62. **Mairiporã recebe leads bons** (7,33%) e entrega
0,30. O atendimento faz diferença.

---

## 5. Impacto estimado

Se as 10 unidades abaixo de 0,8 chegassem apenas à média (1,0), no período de 12
semanas analisado:

| Unidade | Leads | CVS real | CVS esperado | Eficiência | Conversões perdidas |
|---|---|---|---|---|---|
| ITC Vertebral — Curitiba | 3.037 | 4,84% | 6,31% | 0,77 | 45 |
| ITC Vertebral — Recife | 2.082 | 5,48% | 7,23% | 0,76 | 36 |
| ITC Vertebral — Mairiporã | 642 | 2,18% | 7,33% | 0,30 | 33 |
| ITC Vertebral — Campinas Cambuí | 1.596 | 6,39% | 8,27% | 0,77 | 30 |
| Instituto Trata — Curitiba | 970 | 3,81% | 6,77% | 0,56 | 29 |
| ITC Vertebral — Ipanema | 1.895 | 5,28% | 6,72% | 0,78 | 27 |
| ITC Vertebral — São José dos Campos | 918 | 5,77% | 8,01% | 0,72 | 21 |
| Instituto Trata — Savassi | 1.310 | 4,20% | 5,63% | 0,75 | 19 |
| Instituto Trata — Bairro de Fátima | 309 | 2,91% | 8,37% | 0,35 | 17 |
| Instituto Trata — Ribeirão Preto | 953 | 5,35% | 6,70% | 0,80 | 13 |
| **Total** | **13.712** | | | | **~270** |

**~270 agendamentos em 12 semanas** — cerca de 22 por semana — só recuperando o
que já era esperado dos leads que essas unidades já receberam.

---

## 6. Recomendação de implementação

### O card por unidade está sólido

Confiabilidade de 0,89 sustenta ranking, meta e acompanhamento.

### O card por unidade + semana precisa de tratamento

O ICC de 0,359 significa que **64% da variância semanal está dentro da própria
unidade** — é ruído de amostragem, não atendimento oscilando.

O efeito é visível: Goiânia Marista tem eficiência 1,62 com desvio semanal de
**1,73**, oscilando de 0,84 a 5,11. ITC Alphaville tem eficiência parecida
(1,39) com desvio de apenas 0,28. Sem tratamento, o card vai mostrar unidade
saltando de 0,8 para 2,8 sem nada ter acontecido, e gestor vai reagir a ruído.

Três medidas, em ordem de prioridade:

1. **Média móvel de 4 semanas** em vez do valor semanal cru
2. **Banda de confiança na célula** — com 40 leads e ~7% de conversão, o
   intervalo de 95% contém 1,0 quase sempre
3. **Piso de leads por célula maior que 30** — a 100 leads o ruído cai pela
   metade

Nota técnica: a eficiência correlaciona **−0,115 (p=0,019)** com o número de
leads da célula. Célula pequena infla o índice, o que reforça a medida 3.

---

## 7. Limitações

- **Baseline é média geral** — não considera sazonalidade nem variação por marca
- **Não mede atendente individual**, só unidade (limitação da fonte)
- **Depende da acurácia da temperatura** — se o `lead_score` errar, a eficiência
  erra junto
- **Janela de 12 semanas** (18/05 a 03/08/2026), limitada pelo início da
  cobertura do `lead_score_output`
- **Parte da correlação com CVS é aritmética** (§3.1). A sustentação da métrica
  vem da confiabilidade e da independência do mix, não dessa correlação

---

## 8. Query de referência

```sql
WITH base AS (
  SELECT
    m.unidade,
    m.marca,
    DATE_TRUNC('week', m.lead_data)::date AS semana,
    CASE WHEN m.marcou_agendamento IS NOT NULL THEN 1 ELSE 0 END AS converteu,
    CASE
      WHEN o.lead_score >= 0.60 THEN 'quente'
      WHEN o.lead_score >= 0.35 THEN 'morno'
      ELSE 'frio'
    END AS faixa,
    CASE
      WHEN o.lead_score >= 0.60 THEN 0.2162
      WHEN o.lead_score >= 0.35 THEN 0.0448
      ELSE 0.0109
    END AS cvs_esperado
  FROM mv_chatwoot_conversa_metricas m
  JOIN lead_score_output o
    ON o.cw_id_tb_leads::text = m.cw_id_tb_leads::text
  WHERE m.lead_data IS NOT NULL
    [[AND {{lead_data}}]]
    [[AND {{unidade}}]]
    [[AND {{marca}}]]
)
SELECT
  unidade,
  semana,
  COUNT(*)                                                        AS n_leads,
  COUNT(*) FILTER (WHERE faixa = 'quente')                        AS n_quente,
  COUNT(*) FILTER (WHERE faixa = 'morno')                         AS n_morno,
  COUNT(*) FILTER (WHERE faixa = 'frio')                          AS n_frio,
  ROUND(100.0 * COUNT(*) FILTER (WHERE faixa = 'quente') / COUNT(*), 2) AS pct_quente,
  SUM(converteu)                                                  AS agend_real,
  ROUND(SUM(cvs_esperado)::numeric, 2)                            AS agend_esperado,
  ROUND(100.0 * AVG(converteu), 2)                                AS cvs_real,
  ROUND(100.0 * AVG(cvs_esperado)::numeric, 2)                    AS cvs_esperado,
  ROUND(100.0 * (AVG(converteu) - AVG(cvs_esperado))::numeric, 2) AS delta_pp,
  ROUND((AVG(converteu) / NULLIF(AVG(cvs_esperado), 0))::numeric, 3) AS eficiencia
FROM base
GROUP BY 1, 2
HAVING COUNT(*) >= 30
ORDER BY unidade, semana
```

Para o ranking por unidade, remover `semana` do `SELECT` e do `GROUP BY` e
elevar o `HAVING` para `>= 100`.

---

## 9. Anexo

`matriz_eficiencia.xlsx` — 7 abas:

| Aba | Conteúdo |
|---|---|
| `matriz_eficiencia` | unidade × semana, valor da eficiência |
| `matriz_n_leads` | unidade × semana, N de cada célula (ler junto com a anterior) |
| `ranking_unidade` | ranking com desvio semanal, mínimo e máximo |
| `celulas` | base completa, 414 linhas |
| `validacao` | correlações com as ressalvas de construção |
| `confiabilidade` | split-half, Spearman-Brown, persistência, ICC |
| `pares_semana_seguinte` | pares consecutivos usados no teste de persistência |

---

## 10. Próximos passos

- [ ] Validação com @ernandes-lima
- [ ] Card de eficiência por unidade no dashboard LSV
- [ ] Card por unidade + semana **com média móvel de 4 semanas**
- [ ] Filtros de data / marca / unidade
- [ ] Adicionar à MV de avaliação nacional
- [ ] Documentar fórmula no README do projeto
- [ ] Acompanhamento semanal da evolução
