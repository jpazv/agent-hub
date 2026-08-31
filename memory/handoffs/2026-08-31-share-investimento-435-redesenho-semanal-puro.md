# Handoff — Share de Investimento (435) redesenhado para share semanal puro

**Data:** 2026-08-31
**Máquina:** `mac-grupovelas`
**Sessão:** global / Metabase
**Responsável:** JP
**Status:** entregue e **aprovado pelo usuário**

Fecha o passo 5 do handoff `2026-08-31-share-dashboard10-e-leads-tatuape-investigacao.md`.
Substitui o entregável de `2026-08-28-share-investimento-dashboard-435.md`.

---

## 1. Escopo executado

O dashboard `435` foi reconstruído do zero como **estudo puro de share de investimento**,
conforme a redefinição de escopo registrada no handoff de investigação:

1. somente share de investimento;
2. granularidade semanal;
3. leitura histórica de **quais posições da semana/mês recebem mais investimento**;
4. validação entre semanas e entre unidades;
5. **nenhuma** comparação com Leads, Agendamentos ou Faturamento.

- URL: `https://metabase.grupovelas.com.br/dashboard/435`
- Collection: `677 — Estudos`
- Fonte exclusiva: `public.mv_mkt_outcomes_diario` (database `2`)
- Metabase `v0.55.3`

### Decisões tomadas pelo usuário nesta sessão

| Decisão | Escolha |
|---|---|
| Coluna de investimento | **As duas**, alternáveis por filtro (`invest_total_com` / `invest_total_sem`) |
| Recorte de sazonalidade | **Todos os três**: dia da semana, semana do mês, dia do mês |
| Forma de aplicar | **Reconstruir no 435**, arquivando os 9 cards antigos |

Justificativa do usuário para os três recortes: *"por se tratar de um estudo, preciso ver qual
granularidade eh mais interessante para observar"*.

---

## 2. Definição canônica

```text
share da unidade na semana
= investimento da unidade na semana
÷ investimento total do escopo na mesma semana
```

- Semana operacional: **domingo → sábado**, via
  `(date_trunc('week', dia + interval '1 day') - interval '1 day')::date`
- Somente **semanas fechadas**: `semana + 6 < CURRENT_DATE`
- Somente semanas com investimento real: `HAVING SUM(investimento) > 0`
- Janela histórica: **13 semanas** a partir da última semana fechada
- Sazonalidade diária: `dia < CURRENT_DATE` e `dia >= MIN(dia com investimento > 0)`

### Regra crítica do denominador (preservada)

**Marca, Boutique e Sócio definem o denominador do share. O filtro de Unidade apenas escolhe
quem aparece; ele não recalcula a unidade filtrada para 100%.**

Implementação: os filtros de escopo entram no CTE `diario` (antes de `totais`), enquanto
`unidades_filtradas` é aplicado só depois de `shares`, via `JOIN` em `visivel`.

---

## 3. Estrutura da base (CTE comum a todos os 13 cards)

Todo card = `base.sql` + cauda própria. Cadeia:

```
diario            -- dia, semana, unit_id, dimensoes, investimento (coluna escolhida pelo filtro)
                  -- filtros de escopo aqui: [[AND {{marca}}]] [[AND {{boutique}}]] [[AND {{socio}}]]
unidades_filtradas-- SELECT DISTINCT unit_id ... [[AND {{unidade}}]]   (NAO afeta denominador)
semanal           -- agregado semana x unit_id
semanas_validas   -- semanas fechadas COM investimento > 0
referencia        -- MAX(semana) das validas = ultima semana fechada
historico         -- 13 semanas ate referencia
totais            -- SUM(investimento) por semana = DENOMINADOR do escopo
shares            -- share = investimento / investimento_escopo
visivel           -- shares JOIN unidades_filtradas          (13 semanas)
janela             -- visivel limitado por {{numero_semanas}} (N semanas)
estatistica       -- por unidade nas 13 semanas: media, stddev, min, max, soma
dia_base          -- diario JOIN unidades_filtradas, dia < CURRENT_DATE, era de investimento
dia_semana        -- dia_base restrito as 13 semanas fechadas
```

Cards que leem `visivel`/`estatistica` mostram sempre **13 semanas** e ignoram
`{{numero_semanas}}` de propósito (concentração e estabilidade perderiam sentido numa
janela curta). Cards que leem `janela` respeitam o filtro.

CTEs não referenciados não são executados no Postgres — o custo é o do card, não o da base inteira.

---

## 4. Filtros do dashboard

| ID | Nome | Slug | Tipo | Default | Template tag |
|---|---|---|---|---|---|
| `si-marca` | Marca | `marca` | string/= | — | dimension, field `8385` |
| `si-unidade` | Unidade | `unidade` | string/= | — | dimension, field `8397` |
| `si-boutique` | Boutique | `boutique` | string/= | — | dimension, field `8396` |
| `si-socio` | Sócio | `socio` | string/= | — | dimension, field `8391` |
| `si-base` | Base de investimento | `base_investimento` | string/= | `Sem nacional` | text, required |
| `si-semanas` | Semanas completas exibidas | `numero_semanas` | number/= | `8` | number, required |

`si-base` usa `values_source_type: static-list` com `[["Com nacional","Com nacional"],
["Sem nacional","Sem nacional"]]` e alterna a coluna dentro do CTE `diario`:

```sql
CASE WHEN {{base_investimento}} = 'Com nacional'
     THEN invest_total_com ELSE invest_total_sem END
```

**Removidos:** `si-resultado` (Resultado comparado) e `si-leitura` (Leitura) — pertenciam à
fase de comparação com resultados, fora do escopo atual.

Todos os 13 cards recebem os **6 mappings** (4 `dimension` + 2 `variable`), porque a base
referencia todas as 6 tags.

---

## 5. Cards e layout

3 abas (IDs reaproveitados), 13 questions, 16 textos, **29 dashcards**.

| Card | Nome | Display | Dashcard | Row | Tamanho |
|---:|---|---|---:|---:|---|
| **Aba 1226 — Share semanal** | | | | | |
| 15303 | Resumo da última semana fechada | table | 22684 | 5 | 16x9 |
| 15304 | Ranking de share na última semana fechada | row | 22686 | 14 | 16x7 |
| 15305 | Evolução semanal do share — 8 maiores e demais unidades | line | 22688 | 21 | 16x8 |
| 15309 | Concentração do investimento por semana | line | 22690 | 29 | 16x7 |
| 15307 | Quem ganhou ou perdeu share contra a média de 13 semanas | bar | 22692 | 36 | 16x8 |
| 15316 | Matriz unidade × semana — share do investimento | table (pivot) | 22694 | 44 | 16x8 |
| 15308 | Estabilidade do share em 13 semanas | table | 22696 | 52 | 16x8 |
| **Aba 1227 — Sazonalidade do investimento** | | | | | |
| 15310 | Participação de cada dia da semana no investimento | bar | 22699 | 6 | 16x8 |
| 15311 | Posição da semana no mês — índice de investimento | bar | 22701 | 14 | 16x8 |
| 15312 | Posição do dia no mês — índice de investimento | bar | 22703 | 22 | 16x8 |
| 15317 | Matriz dia da semana × semana — estabilidade do padrão | table (pivot) | 22705 | 30 | 16x10 |
| **Aba 1228 — Validação e auditoria** | | | | | |
| 15314 | Controle da base — share semanal de investimento | table | 22708 | 3 | 16x7 |
| 15315 | Auditoria semanal por unidade | table | 22710 | 10 | 16x12 |

Padrão de leitura mantido do desenho anterior: **question em 16 colunas + explicação lateral
em 8 colunas**, cada texto com *o que estou vendo / como decidir / qual cuidado tomar*.
Zero sobreposições de layout verificadas por varredura de células em todas as abas.

### Cards arquivados

- Fase anterior (comparação com resultados): `15269`, `15270`, `15271`, `15272`, `15273`,
  `15274`, `15275`, `15277`, `15278`
- Descartados nesta sessão por bug de render: `15306`, `15313`

---

## 6. Bug encontrado e corrigido — `display: "pivot"` não funciona em SQL nativo

**Sintoma:** os dois cards de matriz renderizavam
`"Tabelas dinâmicas só podem ser usadas em perguntas agregadas"`.
A API não revelava nada: `POST /api/dashboard/435/dashcard/{dc}/card/{card}/query` retornava
`202` com 352 e 91 linhas normalmente.

**Causa:** no Metabase `v0.55.3` o display `pivot` (`pivot_table.column_split`) exige pergunta
**agregada em MBQL**. Query nativa não é aceita. Foi por isso que o card antigo `15274` usava
`display: "table"` — o `pivot_table.column_split` que ele carregava era inerte.

**Correção:** `display: "table"` + **pivot simples de tabela**, que aceita nativo e gera as
colunas dinamicamente a partir de um resultado de exatamente 3 colunas:

```json
{
  "table.pivot": true,
  "table.pivot_column": "semana",
  "table.cell_column": "share_pct",
  "table.column_formatting": [{
    "columns": ["share_pct"], "type": "range",
    "min_type": "custom", "min_value": 0,
    "max_type": "custom", "max_value": 6,
    "colors": ["#FFFFFF", "#227FD2"]
  }]
}
```

- `15316` (unidade × semana): `pivot_column = semana`
- `15317` (dia da semana × semana): `pivot_column = dia_da_semana`, escala de cor 10–20

**Requisito:** a query tem de devolver exatamente 3 colunas — (dimensão, dimensão, métrica).

### Armadilha secundária: dashcard duplicado

Criar card com `dashboard_id: 435` faz o Metabase **auto-inserir um dashcard** no fim da
primeira aba. No `PUT` seguinte eu reenviei o array vindo do `GET`, que já continha esses
auto-inseridos — resultado: `31` dashcards, `15316` e `15317` duplicados, as cópias em
`row 63`, `12x9`, com `0` mappings.

Corrigido removendo os dashcards `22712` e `22713` do array e reenviando o `PUT`.

**Regra para a próxima sessão:** depois de criar cards com `dashboard_id`, sempre reconciliar
a lista de dashcards antes do `PUT` — ou montar o array desejado do zero, como no deploy
inicial, onde o problema não apareceu.

---

## 7. Auditoria final

Estrutura:

- `29` dashcards = `13` questions + `16` textos
- nenhum `card_id` duplicado
- todos os cards com **6** `parameter_mappings`
- todos em `collection 677` e com `dashboard_id 435`
- nenhum card arquivado referenciado pelo dashboard
- `0` sobreposições de layout nas 3 abas

Execução dentro do dashboard (`POST /api/dashboard/435/dashcard/{dc}/card/{card}/query`),
todos `202`:

| Card | Linhas |
|---|---:|
| Resumo | 1 |
| Ranking | 20 |
| Evolução | 72 |
| Concentração | 13 |
| Ganho/perda | 12 |
| Matriz unidade × semana | 352 |
| Estabilidade | 44 |
| Dia da semana | 7 |
| Semana do mês | 5 |
| Dia do mês | 31 |
| Matriz dia × semana | 91 |
| Controle | 1 |
| Auditoria | 352 |

Filtro `numero_semanas` na matriz: `6 → 264` linhas, `8 → 352`, `13 → 560`.
`44 × 8 = 352` exato; em 13 semanas faltam 12 linhas de `44 × 13 = 572`, coerente com
unidades que entraram depois (`semanas_com_dados < 13` no card de estabilidade).

Controle da base nos 4 cenários — `soma_share_do_escopo_pct = 100,00` em todos:

| Cenário | unid. escopo | unid. exibidas | investimento 13s |
|---|---:|---:|---:|
| sem filtro | 44 | 44 | 1.475.003,92 |
| Base = Com nacional | 44 | 44 | 1.511.914,92 |
| Unidade = ITC Vertebral - Alphaville | 44 | **1** | **1.475.003,92** |
| Marca = ITC Vertebral | 26 | 26 | 916.363,91 |

A terceira linha é a prova da regra do denominador: filtrar Unidade reduz o que aparece
(`44 → 1`) e **não** move o denominador. A quarta mostra Marca recalculando o escopo.

---

## 8. Diagnóstico da base (condiciona a leitura)

| Fato | Valor |
|---|---|
| Primeira linha da MV | `2026-05-11` |
| Primeiro dia com investimento | `2026-05-17` |
| Última semana fechada | `2026-08-23` (→ 29/08) |
| Último dia completo | `2026-08-30` |
| Semanas fechadas disponíveis | `15` |
| Janela histórica usada | `13` (31/05 → 23/08) |
| Unidades | `44` |
| Marcas | `2` |
| Meses na sazonalidade | `4` (mai parcial, jun, jul, ago) |

Dois pontos que forçaram desenho específico:

1. **`31/08` é dia parcial** — R$ 9.614 contra ~R$ 18.000/dia normal. Excluído por
   `dia < CURRENT_DATE`. A partir de `01/09` a MV só tem linhas futuras com investimento zero
   (até `2026-10-01`), também descartadas.
2. **Histórico mensal curto.** Meses calendário completos e integralmente dentro da era de
   investimento seriam apenas junho e julho (`n = 2`). Para não perder a leitura, os cards de
   posição no mês usam **índice diário normalizado pelo mês**, permitindo que meses parciais
   contribuam com seus dias válidos:

   ```text
   indice = (investimento medio por dia da posicao)
          ÷ (investimento medio por dia do mes)
   ```

   Cada card devolve `meses_observados` por posição, para que o `n` fique visível na tela.

---

## 9. Resultados do estudo

### Dia da semana — n = 13, base sólida

| Dia | Share médio | Desvio | Investimento médio |
|---|---:|---:|---:|
| Domingo | 15,12% | 1,63 | 17.167,41 |
| Segunda | **15,77%** | 1,51 | 17.900,40 |
| Terça | 14,80% | **0,53** | 16.796,75 |
| Quarta | 13,79% | 0,70 | 15.604,62 |
| Quinta | 13,67% | 0,61 | 15.534,60 |
| Sexta | **13,34%** | 1,31 | 15.125,83 |
| Sábado | 13,50% | 1,67 | 15.332,22 |

Referência de uniformidade: `100 ÷ 7 = 14,29%`. Amplitude de **2,43 p.p.** entre segunda e sexta.
Terça é o dia mais previsível (desvio 0,53); sábado e domingo os mais erráticos (~1,65).

### Posição da semana no mês — o achado mais forte

| Posição | Meses | Índice | Desvio | Investimento/dia |
|---|---:|---:|---:|---:|
| Semana 1 | 3 | 0,956 | −4,4% | 15.641,42 |
| Semana 2 | 3 | 0,947 | −5,3% | 15.479,88 |
| Semana 3 | 4 | **0,909** | −9,1% | 14.259,95 |
| Semana 4 | 4 | 1,064 | +6,4% | 16.460,59 |
| Semana 5 | 4 | **1,172** | **+17,2%** | 18.020,77 |

Aceleração clara de gasto no fechamento do mês: vale na semana 3, pico na semana 5.
Padrão compatível com queima de budget. A semana 5 tem só 1–3 dias — o índice é normalizado
por dia justamente para isso, mas o `n` continua pequeno.

### Concentração do investimento

| Semana | Top 5 | Top 10 |
|---|---:|---:|
| 2026-05-31 | 22,22% | 38,35% |
| 2026-06-21 | **25,52%** | **43,26%** |
| 2026-08-16 | **18,47%** | **34,37%** |
| 2026-08-23 | 21,71% | 38,38% |

Última semana fechada: escopo de R$ 121.101,75, líder **Instituto Trata - Brooklin** com
`5,79%`, `HHI = 285` contra `227` de uniformidade perfeita entre 44 unidades — verba bem
distribuída.

### Diferença entre as bases de investimento

`Com nacional` = `invest_direto + invest_locais + invest_nacional_com`. O nacional adiciona
~R$ 12.000/mês, deslocando shares em fração de p.p. — ex.: ITC Vertebral - Alphaville na
última semana fechada vai de `2,0175%` (sem) para `2,0015%` (com).

---

## 10. Ressalvas a manter explícitas

1. **13 semanas descrevem comportamento recente, não sazonalidade anual.**
2. **A leitura de posição no mês tem `n` entre 3 e 4.** É indício, não padrão estabelecido.
   O card `15312` (dia do mês) é o mais frágil do estudo e o texto lateral diz isso.
   Sazonalidade mensal confiável exige mais histórico.
3. Semana corrente e dia corrente nunca aparecem — por construção.
4. O ranking mostra 20 de 44 unidades; as barras não somam 100%.
5. `investimento_do_escopo` na auditoria repete por unidade dentro da semana — é o
   denominador comum. **Não somar essa coluna.**

---

## 11. Arquivos locais

Em `/private/tmp/claude-501/-Users-grupovelas/1a3e784e-955f-4a29-b8a4-558a77b56501/scratchpad/`:

| Arquivo | Conteúdo |
|---|---|
| `base.sql` | CTE comum aos 13 cards |
| `cards.py` | as 13 questions: nome, display, cauda SQL, visualization_settings |
| `deploy.py` | criação dos cards, `PUT` do dashboard, arquivamento dos antigos |
| `fix_pivot.py` | troca dos 2 cards de matriz para `table.pivot` |
| `mb.py` | cliente da API + resolvedor local de template tags para teste |
| `audit.py` | auditoria de estrutura, execução no dashboard e teste dos filtros |
| `d435-backup.json` | estado do dashboard **antes** da reconstrução |
| `novos-cards.json` | mapa key → card_id |

`mb.py` precisou de `User-Agent: curl/8.7.1` — a API devolve `403` para requests do
`urllib` com UA default.

---

## 12. Pendências / próximo passo

1. **Aprovado pelo usuário em 31/08.** Prints serão anexados por ele.
2. Decidir se a aba experimental `Share — 13 semanas` sai do dashboard `434 — Pulso`,
   agora que o 435 é o estudo canônico de share de investimento.
3. Só depois desta aprovação, iniciar a **fase 2**: comparação do share de investimento com
   resultados. Correlações já calculadas em sessão anterior, nas 13 semanas — investimento ×
   Leads `0,738`; × Agendamentos `0,563`; × Faturamento `0,414`; × Faturamento da semana
   seguinte `0,403`. Os cards da fase 1 anterior estão arquivados, não deletados, e servem
   de ponto de partida.
4. Reavaliar a aba de sazonalidade quando houver **6+ meses completos**, para promover a
   leitura de posição no mês de indício a padrão.
5. Pendências herdadas e **ainda abertas** do handoff de investigação, sem relação com o 435:
   - dashboard `10`: `columnValuesMapping` do dashcard `22656` aponta para o card antigo
     `15259` em vez de `15279` — card mostra "Sem resultado" no dashboard;
   - issue `#358`: leads de Tatuapé (unidade 224) parados desde `25/08`, causa a montante
     das MVs não identificada.
