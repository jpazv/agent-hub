# Handoff — Share de Faturamento (dashboard 436)

**Data:** 2026-08-31
**Máquina:** `mac-grupovelas`
**Sessão:** global / Metabase
**Responsável:** JP
**Status:** entregue e **aprovado pelo usuário**

Segundo estudo da série de share. Irmão do `2026-08-31-share-investimento-435-redesenho-semanal-puro.md`.
Card de acompanhamento: issue `#365`.

---

## 1. Escopo executado

Dashboard novo, criado do zero:

- URL: `https://metabase.grupovelas.com.br/dashboard/436`
- Nome: **Share de Faturamento**
- Collection: `677 — Estudos` (confirmado: `location: "/"`, única coleção com esse nome)
- Fonte: `public.mv_mkt_outcomes_diario` (database `2`), alimentada por `tb_faturamento_proprias`
- Estrutura: 3 abas, **15 questions**, 18 textos, **33 dashcards**

Fase 1: **apenas faturamento**. Nenhuma comparação com investimento — fase posterior.

### Decisões tomadas pelo usuário

| Decisão | Escolha |
|---|---|
| Semana operacional | **Domingo → sábado**, igual ao 435, para a fase 2 casar sem reconciliar grades |
| Semanas-unidade negativas | **Mostrar o valor real e sinalizar**, com card dedicado na aba de validação |
| Base de faturamento | Líquido / Bruto, alternável por filtro (espelha a decisão do 435) |

---

## 2. Achado de fonte — semântica do estorno (resolvida na definição da MV)

`pg_get_viewdef` sobre `mv_mkt_outcomes_diario` (14.886 chars, salvo em `mvdef.sql`):

```sql
sum(mb.service_value - mb.discount)                                    AS faturamento,
sum(mb.service_value - mb.discount) FILTER (WHERE i.service_type ~~ '%TTO%') AS faturamento_tratamento,
sum(mb.service_value - mb.discount) FILTER (WHERE i.service_type ~~ '%REN%') AS faturamento_renovacao,
sum(mb.service_value - mb.discount) FILTER (WHERE COALESCE(mb.status,'') = 'refund') AS estorno
FROM tb_faturamento_proprias mb
```

**Conclusão: `faturamento` já é líquido.** `estorno` é um `FILTER` sobre o mesmo somatório — um
**subconjunto** de `faturamento`, não uma dedução paralela. Portanto:

| Leitura | Expressão |
|---|---|
| **Líquido** (default) | `faturamento` |
| **Bruto (sem estorno)** | `faturamento - estorno` |

`estorno` é sempre `<= 0`, então subtrair devolve as reversões.

**Registre o erro evitado:** `faturamento + estorno` subtrairia o estorno duas vezes. Era a
suposição inicial e estava errada.

Provas na amostra:

| Dia | Unidade | faturamento | trat | renov | estorno | bruto |
|---|---|---:|---:|---:|---:|---:|
| 21/08 | Instituto Trata - Brooklin | −41.350,00 | −20.700 | −20.650 | −41.350,00 | 0,00 |
| 10/08 | ITC Vertebral - Vila Maria | 33.400,00 | 0 | 33.400 | −22.000,00 | 55.400,00 |

Confirmação estatística: `faturamento < 0 AND estorno = 0` ocorre **0 vezes** em 30 semanas —
faturamento só fica negativo quando há estorno. E na base **Bruto** o número de semanas-unidade
negativas cai de `7` para `0`.

### Outros fatos da fonte

- `faturamento <> faturamento_tratamento + faturamento_renovacao`: resíduo de **R$ 2.179.936,04**
  em 4.123 de 68.857 linhas (~11%). Existe uma terceira categoria de serviço além de TTO e REN.
  Por isso a composição é apresentada como três fatias, sendo `outros_servicos` um **resíduo**, não
  uma categoria nomeada na fonte.
- `competencia` é **sempre** o mês de `dia` (`COUNT(DISTINCT date_trunc('month', dia)) = 1` por
  competência). Não há lançamento retroativo cruzando mês, então a regra de semana fechada do 435
  se transporta. **Mas** o estorno lança na data da reversão e reverte receita de semana anterior:
  é retroatividade de efeito, e é a origem dos negativos.
- Fonte cobre **apenas unidades próprias**. Das 44 unidades do escopo, **2 nunca faturam**.

---

## 3. Base da query

Estrutura idêntica à do 435 (`base_fat.sql`), com `receita` no lugar de `investimento`:

```
diario            -- dia, semana, unit_id, dimensoes, receita (Liquido|Bruto), estorno,
                  -- fat_tratamento, fat_renovacao, fat_liquido
                  -- filtros de escopo aqui: [[marca]] [[boutique]] [[socio]]
unidades_filtradas-- DISTINCT unit_id ... [[unidade]]     (NAO afeta denominador)
semanal / semanas_validas / referencia / historico
totais            -- SUM(receita) por semana = DENOMINADOR
shares / visivel / janela
estatistica       -- + semanas_com_receita, semanas_negativas, estorno_13s
dia_base          -- dia < CURRENT_DATE, era de receita (dia >= MIN(dia) WHERE receita <> 0)
dia_semana        -- dia_base restrito as 13 semanas fechadas
```

`fat_liquido` é carregado até `visivel` de propósito: o card de composição usa **sempre** o líquido,
porque `faturamento_tratamento` e `faturamento_renovacao` só existem na versão líquida. Se usasse
`receita` no denominador da composição, o resíduo absorveria o estorno quando o filtro estivesse em
Bruto.

### Regra do denominador (idêntica ao 435)

**Marca, Boutique e Sócio definem o denominador. Unidade apenas escolhe quem aparece.**

---

## 4. Filtros

| ID | Nome | Slug | Tipo | Default |
|---|---|---|---|---|
| `sf-marca` | Marca | `marca` | string/= | — |
| `sf-unidade` | Unidade | `unidade` | string/= | — |
| `sf-boutique` | Boutique | `boutique` | string/= | — |
| `sf-socio` | Sócio | `socio` | string/= | — |
| `sf-base` | Base de faturamento | `base_faturamento` | string/= | `Líquido` |
| `sf-semanas` | Semanas completas exibidas | `numero_semanas` | number/= | `8` |

Template tags reusam os mesmos field IDs do 435: marca `8385`, unidade `8397`, boutique `8396`,
socio `8391`. `sf-base` é `static-list` com `[["Líquido","Líquido"],["Bruto (sem estorno)","Bruto (sem estorno)"]]`.

Todos os 15 cards recebem os **6 mappings** (4 dimension + 2 variable).

---

## 5. Cards e layout

| Card | Nome | Display | Dashcard | Row | Tamanho |
|---:|---|---|---:|---:|---|
| **Aba 1229 — Share semanal** | | | | | |
| 15318 | Resumo da última semana fechada | table | 22730 | 7 | 16x9 |
| 15319 | Ranking de share na última semana fechada | row | 22732 | 16 | 16x10 |
| 15320 | Evolução semanal do share — 8 maiores e demais unidades | line | 22734 | 26 | 16x8 |
| 15321 | Concentração do faturamento por semana | line | 22736 | 34 | 16x7 |
| 15322 | Quem ganhou ou perdeu share contra a média de 13 semanas | bar | 22738 | 41 | 16x8 |
| 15323 | Matriz unidade × semana — share do faturamento | table (pivot) | 22740 | 49 | 16x10 |
| 15324 | Estabilidade do share em 13 semanas | table | 22742 | 59 | 16x10 |
| 15325 | Composição do faturamento — tratamento, renovação e outros | bar (stacked) | 22744 | 69 | 16x8 |
| **Aba 1230 — Sazonalidade do faturamento** | | | | | |
| 15326 | Participação de cada dia da semana no faturamento | bar | 22747 | 8 | 16x8 |
| 15327 | Posição da semana no mês — índice de faturamento | bar | 22749 | 16 | 16x8 |
| 15328 | Posição do dia no mês — índice de faturamento | bar | 22751 | 24 | 16x8 |
| 15329 | Matriz dia da semana × semana — estabilidade do padrão | table (pivot) | 22753 | 32 | 16x10 |
| **Aba 1231 — Validação e auditoria** | | | | | |
| 15330 | Controle da base — share semanal de faturamento | table | 22756 | 4 | 16x8 |
| 15331 | Semanas com faturamento líquido negativo | table | 22758 | 12 | 16x8 |
| 15332 | Auditoria semanal por unidade | table | 22760 | 20 | 16x12 |

Padrão mantido: question em 16 colunas + explicação lateral em 8, cada texto com
*o que estou vendo / como decidir / qual cuidado tomar*.

**Dois cards que o 435 não tem:**

- `15325 Composição` — de que serviço vem a receita. Adjacente ao share, mas necessário para não
  ler volume como mix.
- `15331 Semanas negativas` — exigido pela decisão de mostrar negativos. Usa `visivel`, então
  ignora o filtro de semanas e cobre sempre as 13.

Aplicado desde o início o aprendizado do 435: **`display: "table"` + `table.pivot`**, nunca
`display: "pivot"` (inválido em SQL nativo no v0.55.3).

---

## 6. Auditoria

- `33` dashcards = `15` questions + `18` textos
- nenhum `card_id` duplicado · todos com `6` mappings · todos em collection `677` com
  `dashboard_id 436` · nenhum arquivado referenciado · `0` sobreposições nas 3 abas
- 15/15 executando via `POST /api/dashboard/436/dashcard/{dc}/card/{card}/query`, todos `202`
- Filtro de semanas na matriz: `6 → 264`, `8 → 352`, `13 → 560`
- Cards testados também **standalone** (`POST /api/card/{id}/query`) e com os defaults em três
  formatos (ausente, lista `['Líquido']`, escalar `'Líquido'`) — resultado idêntico

Controle nos 4 cenários — `soma_share_do_escopo_pct = 100,00` em todos:

| Cenário | Unid. escopo | Exibidas | Receita 13s | Sem. negativas |
|---|---:|---:|---:|---:|
| sem filtro | 44 | 44 | 17.283.508,51 | 7 |
| Base Bruto | 44 | 44 | 18.846.118,22 | **0** |
| Unidade = ITC Vertebral - Alphaville | 44 | **1** | **17.283.508,51** | 1 |
| Marca = Instituto Trata | 18 | 18 | 6.194.446,68 | 2 |

Estorno acumulado em 13 semanas: **R$ −1.562.609,71**. Unidades sem faturamento: `2`.

---

## 7. Diagnóstico da base

| Fato | Valor |
|---|---|
| Primeiro dia com faturamento | `2026-05-20` |
| Primeira semana cheia | `2026-05-24` |
| Última semana fechada | `2026-08-23` — **mesma do 435**, a fase 2 casa |
| Último dia completo | `2026-08-30` |
| Semanas fechadas disponíveis | `15` |
| Janela histórica | `13` (31/05 → 23/08) |
| Unidades no escopo / que faturam | `44` / `42` |
| Meses na sazonalidade | `4` |

`31/08` é dia parcial (R$ 150.698 com 35 unidades, contra R$ 396.719 na sexta anterior) e é
excluído por `dia < CURRENT_DATE`. De `01/09` a `01/10` a MV tem linhas futuras zeradas.

---

## 8. Resultados do estudo

### Dia da semana — o achado estrutural

n = 13. A coluna renormalizada exclui sábado e domingo; nela a uniformidade é 20%.

| Dia | Share nos 7 dias | Entre dias úteis | Desvio | Receita média |
|---|---:|---:|---:|---:|
| Domingo | **0,15%** | — | 0,45 | 1.645,32 |
| Segunda | 20,71% | 20,99% | 4,97 | 275.292,63 |
| Terça | **22,13%** | **22,45%** | 6,19 | 290.001,10 |
| Quarta | 20,10% | 20,35% | 2,72 | 265.908,26 |
| Quinta | **16,15%** | **16,32%** | 5,46 | 222.444,51 |
| Sexta | 19,63% | 19,89% | 4,74 | 260.277,14 |
| Sábado | **1,13%** | — | 0,90 | 13.931,69 |

Duas leituras:

1. **Fim de semana é estrutural.** Sábado e domingo somam `1,28%` da receita. As clínicas não
   operam. Comparação direta com o 435: investimento coloca **28,78%** da verba em sábado+domingo.
   Esse contraste é o gancho mais forte da fase 2, mas **não é conclusão** — investimento em mídia
   no fim de semana pode gerar lead que converte na segunda.
2. **Terça é pico, quinta é vale** — 6,1 p.p. de diferença entre dias úteis.

**Volatilidade muito maior que a do investimento:** desvios de 2,72 a 6,19 p.p. contra 0,53 a 1,67
no 435. Receita depende de fechamento de contrato; verba é programada.

### Posição da semana no mês

| Posição | Meses | Índice | Desvio | Receita/dia |
|---|---:|---:|---:|---:|
| Semana 1 | 3 | **0,857** | −14,3% | 164.403,74 |
| Semana 2 | 3 | 0,988 | −1,2% | 187.678,43 |
| Semana 3 | 4 | 0,985 | −1,5% | 180.330,04 |
| Semana 4 | 4 | 1,073 | +7,3% | 196.329,27 |
| Semana 5 | 4 | **1,128** | +12,8% | 200.606,22 |

Mês começa devagar e acelera no fechamento. **Mesmo formato do investimento** (0,956 → 1,172),
com vale em posição diferente: no faturamento o vale é a Semana 1; no investimento é a Semana 3.

### Concentração

| Semana | Top 5 | Top 10 |
|---|---:|---:|
| 2026-05-31 | **32,64%** | **54,45%** |
| 2026-06-21 | 22,68% | 41,75% |
| 2026-06-28 | 31,15% | 51,98% |
| 2026-08-16 | 23,23% | 41,62% |
| 2026-08-23 | 28,48% | 48,96% |

Receita é **mais concentrada que verba**: top5 entre 22,7% e 32,6%, contra 18,5% a 25,5% no
investimento. Top10 chega a 54,5%.

### Composição

Tratamento sustenta de **69,6% a 82,4%** da receita; renovação de **7,9% a 18,8%**;
outros serviços de **8,5% a 14,0%**.

### Semanas com líquido negativo — todos os 7 casos

| Semana | Unidade | Líquido | Estorno | Bruto | Share |
|---|---|---:|---:|---:|---:|
| 16/08 | Instituto Trata - Brooklin | −18.320,00 | −41.350,00 | 23.030,00 | −1,192% |
| 26/07 | ITC Vertebral - Alphaville | −16.808,35 | −16.808,35 | 0,00 | −1,157% |
| 26/07 | ITC Vertebral - BH - Savassi | −9.542,38 | −24.562,38 | 15.020,00 | −0,657% |
| 31/05 | ITC Vertebral - Mairiporã | −4.884,80 | −6.596,80 | 1.712,00 | −0,613% |
| 07/06 | ITC Vertebral - Niterói | −3.694,21 | −7.354,21 | 3.660,00 | −0,297% |
| 31/05 | ITC Vertebral - Niterói | −1.772,00 | −2.720,00 | 948,00 | −0,223% |
| 09/08 | Instituto Trata - Santos | −283,50 | −283,50 | 0,00 | −0,018% |

Padrão: onde `bruto = 0` a semana foi só de reversão; onde a bruta é saudável e a líquida negativa
houve reversão de contrato anterior. Brooklin em 16/08 é o caso mais relevante.

---

## 9. Falso positivo investigado — "todos sem Nenhum resultado"

O usuário reportou o dashboard inteiro vazio. **Não era bug.** Os filtros estavam em
`Marca = Instituto Trata` **e** `Unidade = ITC Vertebral - ...` — interseção vazia.

Reproduzido com esses dois parâmetros: **13 dos 15 cards retornam 0 linhas**. Só `Resumo` e
`Controle` devolvem 1 linha, porque são construídos apenas com subqueries escalares.

O `Controle` já denuncia o caso:

```
unidades_no_escopo        18
unidades_exibidas          0     <-- interseccao vazia
soma_share_do_escopo_pct 100.0
```

Antes de concluir isso, foi verificado e descartado: cards standalone (retornam linhas), execução
via endpoint do dashcard (retorna linhas), defaults em três formatos (idênticos), estrutura do
dashcard campo a campo contra o 435 que funciona (só diferem id/row/tab/timestamp), parâmetros e
mappings salvos, `result_metadata` presente. Nada disso apontava problema — porque não havia.

### Lacuna de desenho, decisão pendente

O modo de falha é silencioso e vale para o **435 também**: a regra do denominador é a parte sutil
do desenho, e o efeito colateral dela é um dashboard vazio sem explicação na primeira tela — o
diagnóstico está na terceira aba, o último lugar onde se olha.

Proposta apresentada e **não aplicada** (aguarda decisão): card de aviso no topo de cada aba, que
só exibe conteúdo quando `unidades_exibidas = 0`, dizendo que o cruzamento é vazio e qual filtro
afrouxar. Custo: 3 cards por dashboard, aplicados nos dois para ficarem consistentes.

---

## 10. Arquivos locais

Em `/private/tmp/claude-501/-Users-grupovelas/1a3e784e-955f-4a29-b8a4-558a77b56501/scratchpad/`:

| Arquivo | Conteúdo |
|---|---|
| `base_fat.sql` | CTE comum aos 15 cards |
| `cards_fat.py` | as 15 questions + textos laterais + intros das abas |
| `deploy_fat.py` | cria o dashboard, os cards e faz o `PUT` do layout |
| `mbf.py` | resolvedor local de template tags do estudo de faturamento |
| `explore_fat.py` / `explore_fat2.py` | exploração da base que sustentou as decisões |
| `mvdef.sql` | definição completa de `mv_mkt_outcomes_diario` (14.886 chars) |
| `audit_fat.py` | auditoria de estrutura e execução |
| `fat-cards.json` | mapa key → card_id |

O padrão de criar tabs novas no mesmo `PUT` com **IDs negativos** (`-1`, `-2`, `-3`) e montar o
array de dashcards do zero funcionou — Metabase remapeou para `1229/1230/1231` e **não** deixou
dashcards auto-inseridos órfãos, ao contrário do que aconteceu no 435 quando reenviei o array do
`GET`.

---

## 11. Pendências / próximo passo

1. **Aprovado pelo usuário em 31/08.** Prints serão anexados por ele na issue `#365`.
2. **Decidir o card de aviso de interseção vazia** (seção 9). Aplicar nos dois dashboards ou
   apenas documentar no texto de introdução.
3. Issue `#365` está com Status `Em andamento` e Tipo `Demanda`; a irmã `#353` está em
   `Em validação` / `Relatório`. Alinhar se for o caso.
4. **Fase 2 — comparação investimento × faturamento.** Já se sabe:
   - correlação share de investimento × Faturamento `0,414`; × Faturamento da semana seguinte `0,403`;
   - as duas séries têm a **mesma última semana fechada** (`23/08`) e a mesma grade domingo→sábado,
     então o join é direto;
   - o contraste de fim de semana (28,78% da verba × 1,28% da receita) e a diferença de posição do
     vale mensal (Semana 3 no investimento, Semana 1 no faturamento) são as duas primeiras
     hipóteses a testar.
5. Reavaliar a aba de sazonalidade quando houver **6+ meses completos**.
6. Pendências herdadas, **ainda abertas**, sem relação com este estudo:
   - dashboard `10`: `columnValuesMapping` do dashcard `22656` aponta para o card antigo `15259`;
   - issue `#358`: leads de Tatuapé (unidade 224) parados desde `25/08`.
