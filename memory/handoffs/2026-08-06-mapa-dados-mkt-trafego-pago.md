---
data: 2026-08-06
maquina: mac-grupovelas
projeto: LeadScore / Marketing / Tráfego Pago
status: análise concluída
escopo: SOMENTE unidades próprias (39 unidades) — franquias fora
janela: 2026-05-20 a 2026-08-06 (79 dias)
---

# Mapa de dados de Marketing + Tráfego Pago

Companheiro de `2026-08-06-estudo-oe-tres-eixos.md`. Aquele documento trata de
eficiência de atendimento. Este trata de **origem e custo do lead**: de onde ele vem,
que temperatura tem, e quanto custa.

## 1. Onde estão as coisas

**Metabase:** `https://metabase.grupovelas.com.br` · Database **id 2** ("Grupo Velas")
· Dashboard de tráfego pago: **id 316** (abas "Tráfego" e "Financeiro")
· Dashboard de performance: **id 10** (7 abas)

| Camada | Tabela | Papel |
|---|---|---|
| Mídia paga (fato) | `bcpc.fat_media_windsor` | 1 linha por dia×campanha×conjunto×anúncio. `spend`, `impressions`, `clicks`, `ctr`, `cpc`, métricas de vídeo/engajamento. Vem do Windsor.ai |
| Mídia paga (dim) | `bcpc.dim_campanhas` | Taxonomia **decodificada**: `tipo`, `escopo`, `objetivo`, `nivel`, `uf`, `marca`, `plataforma` |
| | `bcpc.dim_conjunto` / `dim_anuncio` | Conjunto (adset) e anúncio |
| Baldes prontos | `bcpc.vw_campanha_balde` | Já entrega `cpl_real`, `cpa_avaliacao`, `cpa_conversao`, `taxa_*` por tipo_campanha×marca×período |
| Denominadores | `bcpc.leads_denominadores` | leads_gerados/cadastrados/agendados/avaliados/convertidos por tipo_campanha |
| Engajamento | `bcpc.vw_engajamento_eng` | Métricas de vídeo/perfil para campanhas [ENG] |
| Lead + funil | `public.mv_chatwoot_conversa_metricas` | 54 colunas. Origem, funil, tempos de resposta |
| Score do lead | `public.lead_score_output` | `lead_score` e subscores |
| **Decodificador** | `public.dim_campanhas_chatwoot` | **A pedra de roseta** — ver seção 3 |
| Receita | `analytics.mv_venda_propria` | `total_value`, `tipo_campanha`, `lead_id` |

**Chaves de ligação:**
- Lead ↔ score: `cw_id_tb_leads` (text nos dois, sem cast)
- Lead ↔ investimento: `mv_chatwoot_conversa_metricas.id_interno` = `fat_media_windsor.id_interno_hint` (casa 39/39)
- **Não** use `unidade_hint` (78 valores sujos vs 41 no `id_interno_hint`)

## 2. Dicionário da taxonomia de campanha

Nome de campanha segue: `[TIPO] <escopo|cidade> - <segmento> [LP-xx] [UF] <flags>`

Exemplo real: `[MR] BR - UPs [LP-c07] eBook "De volta ao Movimento" [GO]`

### Os tipos (o "balde")

| Sigla | Significado | Objetivo na API | Papel no funil |
|---|---|---|---|
| `[Redirect]` | Manda para landing page / WhatsApp | OUTCOME_LEADS | Aquisição, maior volume de campanhas (1.886) |
| `[MSG]` | Click-to-WhatsApp, conversa direta | OUTCOME_SALES | Aquisição, maior investimento |
| `[QUIZ]` | Quiz / formulário de qualificação | OUTCOME_LEADS | Aquisição qualificada |
| `[Search]` | Google Search (intenção ativa) | SEARCH | Fundo de funil |
| `[ENG]` | Engajamento (curtida, vídeo, visita ao perfil) | OUTCOME_ENGAGEMENT | Topo de funil |
| `[MR]` | **Material Rico** — eBook, Webinar, Checklist | OUTCOME_LEADS | Isca de conteúdo |
| `[BRAND]` | Marca | OUTCOME_LEADS | Institucional |
| `[PMax]` | Performance Max (Google) | PERFORMANCE_MAX | Automação Google |
| `[RMKT]` | Remarketing | OUTCOME_ENGAGEMENT | Reimpacto |
| `[YT]` | YouTube | VIDEO | Vídeo |
| `[REFORÇO]` | Reforço de verba em unidade | — | Tático |
| `[GMN]` | Google Meu Negócio | — | Orgânico local |

### Os modificadores

| Token | Significado | Como confirmar |
|---|---|---|
| `[BR]` / `-BR` | **Brasil = campanha nacional.** `escopo='BR'` ⟺ `nivel='NAC'` (552 de 600) | vs. `nivel='IND'` = unidade individual (3.734) |
| `UPs` | **Unidades Próprias.** 646 campanhas, 551 nacionais | 98% do investimento nacional tem "UPs" no nome |
| `[LP-xx]` / `[LP-cxx]` | Variante de landing page | `dim_campanhas_chatwoot.landing_page` |
| `[GO]`, `[SP]`... | UF | coluna `uf` |
| `[01]`...`[84]` | **Etiqueta** — código dentro da 1ª mensagem | ver seção 3 |
| `*RUSH`, `*Somente CEPs` | Flags livres do gestor | texto livre |
| `[3º/4º Quartil]` | Segmentação de público por quartil | texto livre |

### Os tipos que só existem no lado do lead

| Sigla | O que é | Mensagem-gatilho |
|---|---|---|
| `[MSG] [PDR]` | **PaDRão do Meta** — texto genérico que o Meta preenche sozinho | *"Olá! Posso saber mais informações sobre isto?"* |
| `[MSG] [AUT]` | **Customizada** — o gestor escreveu as opções | *"Sinto dor na Coluna e preciso de ajuda!"*, *"Já tentei outros tratamentos e não resolveu"* |
| `[Site]` | Site institucional | *"...entrando em contato através do site do ITC VERTEBRAL"* |
| `[Monitora]` | Fonte externa "Monitora" | *"Olá!! Gostaria de mais informações."* |
| `[Inbound]` | **Paciente antigo remarcando** — não é lead novo | *"Olá, gostaria de remarcar minha avaliação!"* |
| `[Indicacao]` | Indicação | — |
| `[Organico]` | Orgânico | — |

## 3. A pedra de roseta: como a origem do lead é descoberta

**A origem é identificada pelo TEXTO da primeira mensagem do WhatsApp.**

Cada landing page/campanha gera um texto de abertura com um código `[NN]` (a `etiqueta`).
O pipeline normaliza a mensagem recebida (`exemplo_msg_norm`) e casa com
`public.dim_campanhas_chatwoot`, que devolve `tipo_campanha`, `landing_page`, `nome` e
`campanha`.

```
Lead clica no anúncio → WhatsApp abre com texto pré-preenchido
  "[08] Olá! Estou entrando em contato através da página de Hérnia e Dor Ciática..."
       ↓ normaliza
  dim_campanhas_chatwoot.exemplo_msg_norm  → codigo ITC008
       ↓
  tipo_campanha = [Search] - [BR] · landing_page = lp-hernia-de-disco... · nome = "Hérnia e Dor Ciática"
```

**Consequência:** se o lead apagar o texto, editar, ou a campanha usar um texto não
cadastrado, cai em **"Não identificado"** — 5.485 leads (11,5%) e, do lado da receita,
**58%**. Ver seção 6.

## 4. Situação atual — temperatura por origem

39 unidades próprias, 47.641 leads scoreados. Baselines de conversão por temperatura:
quente (score ≥0,60) 21,6% · morno (0,35–0,60) 4,5% · frio (<0,35) 1,1%.

| Origem | Leads | % quente | CVS | % tratamento |
|---|---|---|---|---|
| `[ENG]` (unidade) | 700 | **42,3%** | **14,57%** | 4,29% |
| `[Search] - [BR]` | 210 | 41,9% | 13,81% | 4,76% |
| `[Site]` | 1.549 | 40,7% | 12,72% | 5,62% |
| Não identificado | 5.479 | 36,8% | 12,34% | 3,83% |
| `[Redirect] - [BR]` | 3.410 | 33,8% | 9,97% | 3,11% |
| `[Search]` | 3.668 | 33,4% | 9,92% | 2,92% |
| `[ENG] [BR]` | 4.259 | 30,5% | 7,56% | 2,00% |
| `[Redirect]` | 3.377 | 26,4% | 5,89% | 1,54% |
| `[MSG] [AUT]` | 4.425 | 23,7% | 4,66% | 1,31% |
| `[MSG] [PDR]` | **10.855** | 19,6% | 3,66% | 0,88% |
| `[Monitora]` | 2.097 | **11,0%** | 2,34% | 0,62% |

Spread de **4x em temperatura** e **6x em CVS** entre a melhor e a pior origem.
O maior volume da rede (`[MSG] [PDR]`, 23% dos leads) está entre os piores.

## 5. Situação atual — investimento e retorno

Investimento na janela: **R$ 1.234.627**. Relevante para próprias: **R$ 1.212.930 (98,2%)**
— R$ 853,8k atribuído a unidade + R$ 359,1k nacional "UPs". Descartado: R$ 21,7k.

| Canal | Investido | CPL | % quente | Custo/tratamento | ROAS |
|---|---|---|---|---|---|
| PMax Brand | R$ 5.543 | R$ 19 | 27,3% | **R$ 504** | **16,50** |
| ENG-BR | R$ 71.674 | **R$ 17** | 30,6% | **R$ 843** | **9,93** |
| Redirect-BR | R$ 223.251 | R$ 24 | 28,7% | R$ 1.540 | 6,25 |
| Search-BR | R$ 22.925 | R$ 50 | 35,6% | R$ 1.763 | 5,73 |
| ENG (unidade) | R$ 48.136 | R$ 69 | **42,3%** | R$ 1.605 | 4,47 |
| **MSG** | **R$ 336.669** | R$ 22 | 20,8% | R$ 2.200 | **3,79** |
| **Search** | **R$ 319.483** | R$ 87 | 33,4% | R$ 2.986 | **2,85** |
| Redirect | R$ 160.800 | R$ 48 | 26,4% | R$ 3.092 | 2,55 |
| Redirect-Locais | R$ 26.412 | R$ 33 | 25,2% | R$ 3.301 | 2,51 |

### O achado central

**r(investimento, ROAS) = −0,453.** Quanto mais verba um canal recebe, pior o retorno.
A alocação está invertida.

- **69,4% do orçamento (R$ 843k) está em canais com ROAS < 4**
- 24,7% (R$ 300k) em canais com ROAS ≥ 6
- ROAS médio ponderado: 4,29

**O CPL engana.** MSG tem o 2º melhor CPL da rede (R$ 22) e o 3º pior custo por
tratamento (R$ 2.200) — porque compra lead frio (20,8% quente). ENG-BR tem CPL
parecido (R$ 17) e custo por tratamento **2,6x menor** (R$ 843).
**Não existe lead barato; existe lead que converte.**

### A oportunidade grátis: trocar o texto da mensagem

| | Leads | % quente | CVS | Tratamentos |
|---|---|---|---|---|
| `[MSG] [AUT]` (customizada) | 4.429 | 23,7% | 4,65% | 58 |
| `[MSG] [PDR]` (padrão Meta) | 10.858 | 19,7% | 3,66% | 95 |
| **PDR se performasse como AUT** | | | | **142** |

**+47 tratamentos em 79 dias** = 217/ano × R$ 3.641 = **~R$ 790 mil/ano**, sem gastar
um real a mais de mídia. Só reescrevendo o texto de abertura das campanhas
click-to-WhatsApp para nomear a dor do lead.

## 6. Problemas de dados encontrados (corrigir antes de decidir)

1. **Grafias divergentes entre as bases.** Investimento usa `[ENG] - [BR]`; leads e
   receita usam `[ENG] [BR]`. A grafia com espaço existe no investimento só em
   2026-06-20 (R$ 704 vs R$ 70.970 da grafia com hífen) — carga furada. **Sem
   normalizar (`regexp_replace(upper(x),'[^A-Z0-9]','','g')`), todo CPL por tipo sai errado.**
2. **58% da receita é "Não identificado"** (R$ 7,4 mi de ~R$ 13,8 mi). O ROAS por canal
   só cobre 42% da receita — o ranking vale, os valores absolutos subestimam.
3. **`[Inbound]` não é lead novo** — é paciente remarcando avaliação. Contamina CVS.
4. **`min_ate_secretaria_expediente` está quebrada** — zera o contador de quem chega
   fora do expediente (ver estudo de O/E, seção 5).
5. **A MV de leads só guarda de 2026-05-20** em diante.
6. **`[Video]` e `[Vídeo]`** são o mesmo balde duplicado (R$ 4.905 + R$ 4.420).

## 7. Recomendações

| # | Ação | Ganho estimado | Custo |
|---|---|---|---|
| 1 | Reescrever texto das campanhas `[MSG]` (PDR → AUT) | **~R$ 790k/ano** | zero |
| 2 | Realocar verba de MSG/Search/Redirect para ENG-BR e Redirect-BR | alto | zero |
| 3 | Corrigir atribuição de receita (58% cega) | destrava decisão | baixo |
| 4 | Normalizar taxonomia entre as 3 bases | destrava CPL | baixo |
| 5 | Escalar PMax Brand (ROAS 16,5 com só R$ 5,5k) com teste controlado | médio | baixo |
| 6 | Auditar `[Monitora]` — 11% quente, pior fonte da rede | corta desperdício | zero |
| 7 | Separar `[Inbound]` do cálculo de CVS | corrige métrica | baixo |

**Ressalva sobre a #2 e #5:** ROAS alto em canal pequeno não escala linearmente.
PMax Brand com R$ 5,5k a 16,5x não vira R$ 300k a 16,5x. Escalar em degraus e medir.
ENG-BR é o candidato mais seguro (já roda R$ 72k a 9,93x).

## 8. Ponte com o estudo de O/E

Os dois estudos se encontram aqui: **tráfego pago compra temperatura, atendimento
converte temperatura.** Um lead quente entregue a uma unidade com O/E de agendamento
0,56 (Trata Curitiba) rende metade do que renderia em uma de 1,79 (ITC Jardins).

Consequência prática: **a decisão de alocação de verba deveria considerar o O/E da
unidade de destino**, não só o CPL da campanha. Verba em unidade ineficiente é verba
com desconto embutido. Isso ainda não está medido — é o próximo estudo.

## 9. SQL de referência — ROAS por canal normalizado

```sql
WITH
kn AS (SELECT CASE WHEN regexp_replace(upper(coalesce(tipo_campanha,'')),'[^A-Z0-9]','','g') LIKE 'MSG%'
                   THEN 'MSG'
                   ELSE regexp_replace(upper(coalesce(tipo_campanha,'')),'[^A-Z0-9]','','g') END AS k,
              spend
       FROM bcpc.fat_media_windsor
       WHERE data_ref BETWEEN '2026-05-20' AND '2026-08-06'),
sp AS (SELECT k, sum(spend) AS spend FROM kn GROUP BY 1),
ld AS (SELECT CASE WHEN regexp_replace(upper(coalesce(m.tipo_campanha,'')),'[^A-Z0-9]','','g') LIKE 'MSG%'
                   THEN 'MSG'
                   ELSE regexp_replace(upper(coalesce(m.tipo_campanha,'')),'[^A-Z0-9]','','g') END AS k,
              count(*) AS leads,
              count(*) FILTER (WHERE o.lead_score >= 0.60) AS quentes,
              sum((m.converteu_tto IS NOT NULL)::int) AS tto
       FROM mv_chatwoot_conversa_metricas m
       JOIN lead_score_output o ON o.cw_id_tb_leads = m.cw_id_tb_leads
       GROUP BY 1),
rv AS (SELECT CASE WHEN regexp_replace(upper(coalesce(tipo_campanha,'')),'[^A-Z0-9]','','g') LIKE 'MSG%'
                   THEN 'MSG'
                   ELSE regexp_replace(upper(coalesce(tipo_campanha,'')),'[^A-Z0-9]','','g') END AS k,
              sum(total_value) AS receita
       FROM analytics.mv_venda_propria
       WHERE data BETWEEN '2026-05-20' AND '2026-08-06'
         AND converteu_tto IS NOT NULL AND total_value > 0
       GROUP BY 1)
SELECT coalesce(sp.k, ld.k)                                  AS canal,
       round(sp.spend)                                       AS investido,
       ld.leads,
       round(100.0 * ld.quentes / nullif(ld.leads,0), 1)      AS pct_quente,
       round(sp.spend / nullif(ld.leads,0))                   AS cpl,
       round(sp.spend / nullif(ld.quentes,0))                 AS cpl_quente,
       ld.tto,
       round(sp.spend / nullif(ld.tto,0))                     AS custo_por_tratamento,
       round(rv.receita)                                      AS receita,
       round((rv.receita / nullif(sp.spend,0))::numeric, 2)   AS roas
FROM sp
FULL JOIN ld ON ld.k = sp.k
LEFT JOIN rv ON rv.k = coalesce(sp.k, ld.k)
WHERE coalesce(sp.spend,0) >= 3000
ORDER BY roas DESC NULLS LAST;
```

## 10. Nota sobre RH / remuneração (busca lateral desta sessão)

Não existe folha de pagamento neste banco. O que existe:

- `fechamento.remuneracao` / `vw_remuneracao_mensal` — **piloto de 2021**, 25 pessoas,
  1 unidade. `salario_base` + bônus. Não é folha corrente.
- `public.tb_colab_fech` — **remuneração variável corrente**: jun–jul/2026, 215 pessoas,
  30 unidades. `premiacao_total` + modelo (`paf`, `pas`, `colegiado`, `rateio`).
- `fechamento.unidade.gasto_folha` — custo de folha **agregado** por unidade (DRE).

Cargos existentes: Fisioterapeuta (161), Líder (38), Consultora (21), Secretária (19),
Sócio (12). **Não há cargo de tecnologia/administrativo** — time da matriz não está
neste banco.

**Ideia derivada:** `tb_colab_fech` tem `premiacao_total` e `avs`/`ttos`/`faturamento`
por pessoa. Cruzar com o O/E de três eixos permitiria checar se a premiação vai para
quem tem eficiência ajustada por mix ou para quem recebeu carteira quente — dado que o
CVS bruto tem r=0,40 com o mix, o risco de premiar sorte é real.

## 11. Segurança

O token de sessão do Metabase está em **texto puro** em
`memory/handoffs/2026-08-05-metabase-api-filters.md`, versionado no git. Ele carrega as
permissões completas do usuário `jp@grupovelas.com.br`. Recomendação: variável de
ambiente + conta de serviço separada (só `public` e `analytics`) para trabalho analítico.
