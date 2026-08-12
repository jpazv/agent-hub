---
data: 2026-08-10
maquina: mac-grupovelas
projeto: Metabase / Dashboard 316 (Trafego Pago) / auditoria de KPI
status: card 13399 entregue e conferido; %CVS corrigido pelo JP; 4 achados abertos no dash 316
---

# Auditoria do Trafego Pago e as fontes oficiais em "Dados Gerais"

Complementa `2026-08-10-regua-expectativa-e-fontes-oficiais.md` e
`2026-08-06-mapa-dados-mkt-trafego-pago.md`.

## 0. REGRA DE OURO (decisao do JP, 10/08/2026)

> "Sempre que fizermos um dashboard que tenham kpi genericas, teste no performance,
> usando todo tipo de filtro, entao pedirei a mesma coisa."

Toda vez que um card novo calcular KPI generica (leads, agendamentos, avaliacoes,
faturamento, investimento, CVS, projecoes, metas):

1. **Ancorar no dashboard 10** (Performance Geral). Ele e a verdade. Rodar o mesmo
   periodo nos dois e comparar numero a numero.
2. **Exercitar TODOS os filtros**, um a um e combinados. Filtro nao mapeado nao da
   erro — ele silenciosamente mostra o universo inteiro. Foi assim que a aba
   Criativos passou meses ignorando Unidade e Socio.
3. **Testar em mes fechado E em mes corrente parcial.** Vario bug so aparece quando
   o periodo selecionado difere do periodo de comparacao (ver secao 3).
4. **Conferir contra as fontes oficiais da colecao "Dados Gerais"** antes de escrever
   SQL novo — a definicao ja existe lá como metric.

## 1. Onde vivem os numeros oficiais e as regras de negocio

Colecao **"Dados Gerais" = id 13** (`/api/collection/13/items`). 27 subpastas.
Cada subpasta tem 1 `dataset` (o modelo, a fonte) e N `metric` (as definicoes
oficiais de cada KPI). **A metric e a regra de negocio versionada** — se a sua conta
divergir dela, a sua conta esta errada, nao a dela.

| id  | pasta                | conteudo |
|-----|----------------------|----------|
| 608 | **Trafego Pago**     | 2 modelos + 22 metrics — a pasta desta auditoria |
| 168 | Agendamentos         | modelo 2141 + `% D2`, `Qtd. D2`, `Projecao Agendamentos` |
| 165 | Avaliacao            | 5 metrics |
| 181 | Leads Z-Api          | modelo 2228 + `Qtd. Leads (PS)`, `Projecao Leads (PS)`, `Leads Medio (dia)` |
| 179 | Leads Scal           | 10 metrics |
| 183 | Metas                | modelo 2131 "Modelo de Metas - Proprias" + 10 metrics de distribuicao |
| 164 | Vendas               | 27 metrics |
| 189 | Hibrido Unidade      | 57 metrics — a MV `mv_hibrida_unidade_propria` |
| 184 | Hibrido Fisio        | 36 metrics |
| 169 | Atendimentos         | 7 metrics |
| 194 | Segmentacao          | modelo de segmentacao (socio/marca/regiao) |
| 585 | LSV                  | 21 metrics |
| 167 | Fechamento           | 5 modelos + 6 cards + 4 metrics |
| 553 | DRE - Helder         | 5 subpastas de metricas de DRE |
| 456 | Balanco / 182 Estoque / 166 NPS / 195 Evolucao de Clinicas / 599 Pendencias | demais |

Franquias tem colecao propria: **"Dados Franquias" = id 64**, com 14 subpastas
espelhadas (Agendamento, Atendimento, Avaliacao, Leads, Metas, Vendas,
Hibridas Unidades, Historico, Segmentacao...).

### 1.1 Dados Gerais > Trafego Pago (608) — a pasta que importa aqui

Dois modelos, e a diferenca entre eles e **regra de negocio de atribuicao**:

- `dataset 11229` — **Trafego pago - Ancoragem no Lead**
- `dataset 11234` — **Trafego pago - Ancoragem no Momento**

Os cards 11265 ("Leads e Investimento") e 11343 ("Comparativo de dia") do dash 316
sao GUI questions sobre `card__11234`, ou seja **Ancoragem no Momento**. Os cards
nativos (11336, 13399, os scalars) vao direto na matview
`public.mv_mkt_outcomes_diario`. Confirmar qual ancoragem se quer antes de comparar.

Metrics oficiais na 608 (todas sufixadas "- Ancoragem no momento"):

| metric | nome |
|--------|------|
| 11237 | Leads |
| 11238 | **Investimento (Com Franquias)** |
| 11239 | **Investimento (Sem Franquias)** |
| 11240 | Agendamentos |
| 11241 | Avaliacoes Realizadas |
| 11245 | Avaliacoes Canceladas |
| 11246 | Avaliacoes Agendadas |
| 11242 | Tratamentos |
| 11243 | Renovacoes |
| 11244 | Faturamento |
| 11261 | %CVS |
| 11257 | % Meta Leads |
| 11263 | %Meta Faturamento |
| 11247..11252 | Metas Leads / Agendamento / Avaliacoes / Faturamentos / Investimentos / CPL |
| 11253..11255 | Proj. Faturamento / Proj. Investimento / Proj. Leads |

**Atencao ao par com/sem franquias:** na matview as colunas sao
`invest_total_com` e `invest_total_sem`. Os cards de tabela do dash 316 usam
`invest_total_sem` (sem franquias). Em julho/2026: sem = R$475.232,53,
com = R$487.232,22 (delta R$12.000). Nao misturar.

## 2. Ancoras conferidas — dashboard 10 x dashboard 316 (julho/2026)

Numeros identicos nas duas pontas, ate a casa decimal:

| KPI | valor |
|-----|-------|
| Leads | 20.271 |
| Agendamentos | 2.283 |
| Faturamento | R$ 5.969.550,02 |
| %CVS | 11,2624% (= 2283/20271) |
| Projecao Leads | 25.161,67 (mes corrente) |
| Projecao Agend. | 2.503,2 (mes corrente) |
| Projecao Faturamento | R$ 5.848.625,83 (mes corrente) |

Cards ancora no dash 10 (aba RPD): `125` Leads, `217` Agendamentos, `218`
Faturamento, `11425` Proj.Leads, `11428` Proj.Agend., `11424` Proj.Faturamento,
`11427`/`1822` %CVS, `11441` Meta Leads, `11443` Meta Agendamentos,
`11439` Meta Faturamento. Param de data do dash 10 = `ff97c004`.
Param de data do dash 316 = `99fbb78f`.

**%CVS = agendamentos / leads**, nas duas pontas. No card "Consolidado Unidade"
(13359, dash 10 aba Consolidado) o mesmo numero se chama **%SEC**
(`round(agend::numeric / nullif(leads,0), 4)`).

## 3. Achados da auditoria do dash 316

### 3.1 %CVS do card 11279 estava errado — CORRIGIDO PELO JP em 10/08

Sintoma: filtrando Trata Alphaville no mes corrente, mostrava **51,28%**.
Na visao geral mostrava 37,62% onde a verdade era 8,56%.

Causa: `FILTER` colado no agregado errado.

```sql
sum(agendamentos)/sum(leads) FILTER (WHERE {{data}}) AS CVS
...
WHERE ({{data}} OR {{data_comparacao}})
```

Em SQL o `FILTER` liga **apenas no ultimo agregado** — so no `sum(leads)`. O
`sum(agendamentos)` fica sem filtro de data, e o `WHERE` admite os dois periodos.
Resultado: numerador soma mes atual + mes de comparacao, denominador so o atual.
Prova: Trata Alphaville tinha 33 agend em julho e 7 em agosto, 78 leads em agosto
-> (33+7)/78 = 51,28%.

**Por que ficou escondido:** o default do filtro "Data comparacao" e `past1months`.
Em 10/08 isso aponta para julho, entao quem seleciona julho cai em
`WHERE (julho OR julho)` e o card acerta por coincidencia. Erra so na visao padrao.

Forma correta:
```sql
sum(agendamentos) FILTER (WHERE {{data}})
  / NULLIF(sum(leads) FILTER (WHERE {{data}}), 0) AS CVS
```

Varri todos os cards nativos do 316: **so o 11279 tinha esse padrao**. Os cards
11280 e 11344 usam `(data OR data_comparacao)` legitimamente (calculam os dois
periodos, com FILTER em cada agregado).

### 3.2 ABERTO — card 11343 "Comparativo de dia" nao esta ligado ao filtro Data

Mapeado so em "Data comparacao". Testado com julho e com mes corrente: devolve as
mesmas 71 linhas (01/06 a 10/08) nos dois casos. O grafico ignora o periodo.

### 3.3 ABERTO — aba Criativos ignora Unidade, Socio e Boutique

Cards `13294` (Ranking de Metricas) e `13352` (Tabelao) nao tem
`parameter_mappings` para `unidades`, `socio` nem `boutique`. Provado: 486 linhas e
R$330.307,72 identicos com e sem filtro de unidade e de socio. Marca funciona.
**Consequencia: socio que filtra a unidade dele ve os criativos da empresa toda.**

### 3.4 ABERTO — dois widgets "Campanha" que nao conversam

| param id | nome | valores de | afeta |
|----------|------|-----------|-------|
| `11ce07e1` | `Campanha ` (com espaco no fim) | card 13352 | so a aba Criativos |
| `c9b3e83c` | `Campanha` | card 11234 | Trafego + Financeiro + o resto |

As listas de valores sao realmente diferentes porque a taxonomia difere: a MV de
criativos colapsa `[MSG] [PDR]` + `[MSG] [AUT]` num unico `[MSG]`.

### 3.5 ABERTO — a aba Criativos so cobre Meta Ads

`mv_mkt_criativos_ad_dia` **nao tem linha nenhuma de Google Ads**. Julho/2026:

| tipo_campanha | outcomes | criativos |
|---------------|----------|-----------|
| `[Search]` | R$133.965 | 0 |
| `[Search] [BR]` | R$10.954 | 0 |
| `[Video] [YT]` | R$6.673 | 0 |
| `[Pmax] [Brand]` | R$2.273 | 0 |
| `[Pmax]` | R$924 | 0 |

Total ausente: **R$154.790 (32,6% do mes)**. E onde ha dado (Meta), o criativos usa
investimento **com** franquias enquanto as tabelas usam **sem** — dai `[ENG] [BR]`
aparecer 36.957 lá e 32.957 aqui.

Leads tambem nao sao a mesma coisa: 25.437 no criativos contra 20.271 no resto —
lá e conversao reportada pela plataforma, aqui e lead no CRM.

### 3.6 Tres definicoes de investimento no mesmo dashboard (julho/2026)

| aba | cards | valor | coluna |
|-----|-------|-------|--------|
| Trafego | 11336, 13399 | R$475.232,53 | `invest_total_sem` |
| Criativos | 13352 | R$330.307,72 | equivale a `invest_total_com`, so Meta |
| Financeiro | 11354, 13216 | R$475.231 / R$475.228 | `invest_real` / `gasto_distribuido` |

O card **11422 "Projecao Investimento" fica na aba Trafego mas le
`mv_mkt_financeiro`** — unico card da aba que nao le a mesma tabela do resto. Em
agosto o financeiro tem R$175.119 de realizado contra R$186.099,76 do outcomes
(R$10.980 de atraso). Diferenca nas projecoes: R$0,57 a R$2,07.

### 3.7 PARADO POR DECISAO — Guararapes com meta zerada

Os cards `11341` (% Leads), `11342` (% Agend.) e `11339` (% Meta x Fat.) divergem
do dash 10 (124,78% vs 118,07%; 106,93% vs 101,84%; 91,82% vs 88,35%).

Causa unica: **Guararapes tem meta oficial e meta ZERO na MV de marketing.**
Agosto: `mb_metas_proprias` (Ativa/Propria/nao-Matriz) soma 21.311 leads de meta;
`mv_mkt_outcomes_diario` soma 20.164. Diferenca 1.147 = ITC Guararapes 632 +
Trata Guararapes 512 + 3 de arredondamento do rateio diario. Guararapes tem 155
linhas na MV, com investimento (R$2.420 + R$2.459) e agendamentos (4 + 12), mas
`meta_leads`, `meta_agendamentos` e `meta_faturamento` todos zero.

Os cards do dash 10 usam `mb_metas_proprias.leads_secretaria` com
`log_unidades.status='Ativa' AND tipo='Propria' AND canal<>'Matriz'`.
Os do 316 usam `SUM(meta_leads)` da propria MV de marketing.

### 3.8 ABERTO — unidades fantasma na MV

`Instituto Trata - Guararapes - 2` e `Instituto Trata - Santos - 2`: 62 linhas cada
em jul-ago, zero leads, zero agendamentos, zero investimento. A de Santos tem
**R$26.040,66 de faturamento pendurado**. Ocupam 2 das 44 linhas de qualquer tabela
por unidade.

## 4. Card 13399 "Performance de Trafego Pago por Unidade" — spec final

Criado em 10/08, colecao 12, creator 179 (JP). Vive no **dash 316, aba Trafego**
(dashcard 18904). Derivado do card 11336, trocando `GROUP BY tipo_campanha` por
`GROUP BY unidade`.

**16 colunas, na ordem:** Unidade | SOS | Investimento | Leads | CPL | CVS (%) |
Agendamentos | CPAg | Avaliacoes | CPAv | Tratamentos | CPTto | Faturamento | ROI |
Projecao de Investimento | Projecao de Faturamento.
`ORDER BY "% do Investimento" DESC`.

### 4.1 SOS = Share of Spend

E a coluna `% do Investimento` renomeada (o card 11336 faz igual, via
`column_settings.column_title`). Regra do denominador, decidida em 10/08:

```sql
total_geral AS (
    SELECT COALESCE(SUM(invest_total_sem), 0) AS invest_total_geral
    FROM public.mv_mkt_outcomes_diario
    WHERE {{data}} AND {{marca}} AND {{campanha}}
)
```

**O denominador acompanha Data, Marca e Campanha** (filtros que definem o universo
de gasto) **e ignora Unidade, Socio e Boutique** (filtros que so escolhem quais
linhas aparecer). Antes era `SUM(b.invest) OVER()`, o que fazia filtrar uma unidade
mostrar 100% — errado.

Comportamento verificado (julho/2026, Trata Alphaville R$1.216,68):

| filtro | SOS da unidade | soma da coluna |
|--------|----------------|----------------|
| nenhum | 0,26% | 100,0000% |
| Unidade=Trata Alphaville | 0,26% | 0,26% (1 linha) |
| Campanha=`[ENG] [BR]` | — | 100,0000% |
| Campanha + Unidade | 1,51% | 1,51% |

Sem `ROUND` na expressao — com `ROUND(...,6)` a soma dava 100,0002%.

### 4.2 Mes-tocado nas duas projecoes

Mesma regra do Consolidado: **um dia dentro do mes traz o mes inteiro**, e se o
periodo toca dois meses, soma os dois meses cheios.

```sql
tocados AS (SELECT DISTINCT date_trunc('month', dia)::date AS mes
            FROM public.mv_mkt_outcomes_diario WHERE {{data}}),
proj_mes AS (... WHERE date_trunc('month', dia)::date IN (SELECT mes FROM tocados)
             GROUP BY unidade, date_trunc('month', dia)::date),
proj_metrics AS (SELECT unidade, SUM(projecao_fat), SUM(projecao_invest)
                 FROM proj_mes GROUP BY unidade)
```

Formulas (inalteradas):
- `projecao_fat` = (faturamento ate ontem / dias uteis ate hoje) * dias uteis do mes
- `projecao_invest` = investimento ate ontem + `budget_sem` de ontem * dias restantes

Verificado:

| filtro de data | realizado | proj. investimento | proj. faturamento |
|----------------|-----------|--------------------|-------------------|
| 15/07 (um dia) | R$14.178,82 | R$475.233 | R$5.969.550,02 |
| julho inteiro | R$475.232,53 | R$475.233 | R$5.969.550,02 |
| 15/06 a 15/07 | R$500.498,23 | R$928.501 | R$11.155.410,12 |

Verdade do banco: junho cheio R$453.263,06 / R$5.185.860,10; julho cheio
R$475.232,53 / R$5.969.550,02; jun+jul R$928.495,59 / R$11.155.410,12. O delta de
R$5,41 no investimento e o `ROUND(projecao_invest, 0)` linha a linha (44 linhas).

### 4.3 Formatacao condicional

Das 9 colunas com regra no Consolidado Unidade (13359), **nenhuma coincide pelo
nome** com a tabela de trafego. A unica que coincide na conta e `%SEC`, que e a
mesma formula de `CVS (%)`. As 6 regras foram copiadas:

| faixa | cor |
|-------|-----|
| < 10% | `#EF8C8C` |
| < 12% | `#F7C4C4` |
| < 12,5% | `#FBE499` |
| < 15% | `#F9D45C` |
| < 20% | `#A7D07C` |
| >= 20% | `#88BF4D` |

As outras 8 (`% Proj Fat`, `% Proj Leads`, `% Proj Agendamentos`,
`% Proj Avaliacoes`, `% Meta Fat/Av`, `% Meta Ticket Medio`, `%no-show`,
`% Estorno/Venda`) nao tem equivalente — o Consolidado e meta x projecao x
realizado, a tabela de trafego e investimento x custo por etapa. Cor em CPL/CPAg/
CPAv/CPTto/ROI exige escala nova, a definir com o JP.

### 4.4 Conferencia contra a aba Trafego — 7 cenarios, tudo batido

Investimento, Leads, Agendamentos, Avaliacoes, Faturamento e %CVS identicos ao
centavo contra o card 11336 e o combo 11265, em: mes corrente sem filtro;
+ Marca=ITC; + Marca=Trata; julho fechado; julho + Socio=Monica; julho +
Campanha=`[ENG] [BR]`; junho + Boutique=Ipanema. Projecao de Faturamento tambem
(1 centavo de arredondamento no mes corrente).

**A tabela nao tem projecao de leads nem de agendamentos** — a aba Trafego tem
(25.162 e 2.503). Se pedirem, usar a mesma formula do faturamento.

### 4.5 ABERTO — filtro de Marca do 13399 devolvendo 0 linhas

Em 10/08, apos as edicoes, `unidades`, `data`, `socio`, `boutique` e `campanha`
respondem normal, mas `marca` voltou 0 linhas. O field 8385 tem exatamente
`Instituto Trata` e `ITC Vertebral`. A tag `marca` esta com
`widget-type: string/contains` e `options: {case-sensitive: false}` — esse `options`
foi adicionado por mim para copiar o card 11336; e o primeiro lugar para olhar.
**JP disse que ajusta na mao.**

## 5. Metodo e ferramentas

- Token de sessao do Metabase: **nao versionar** (ver ressalva em
  `2026-08-05-metabase-api-filters.md`). Usar via env var.
- `scratchpad/q.sh 'SELECT ...'` — runner read-only, bloqueia o que nao comeca com
  SELECT/WITH.
- Testar card dentro do dashboard (com os filtros de verdade), nao isolado:
  `POST /api/dashboard/{dash}/dashcard/{dc}/card/{card}/query` com o array
  `parameters`.
- **O `type` de cada parametro tem que casar com o do dashboard.** Os do dash 316
  sao `string/=`; mandar `string/contains` devolve
  `invalid-parameter / template-tag-type / allowed-types`.
- `PUT /api/dashboard/{id}` **exige o array `tabs` junto de `dashcards`**, senao da
  violacao de FK em `dashboard_tab_id` e o Postgres faz rollback da transacao toda.
- Matview nao aparece em `information_schema.columns`. Usar `pg_class` +
  `pg_namespace` (`relkind='m'`). `public.mv_mkt_*` sao as matviews reais;
  `analytics.*` e `marketing.*` sao views por cima. Todos os cards usam `public`.
- Nunca colar SQL no Metabase pelo terminal (corrompe). `pbcopy < arquivo.sql`, ou
  gravar direto pela API.
