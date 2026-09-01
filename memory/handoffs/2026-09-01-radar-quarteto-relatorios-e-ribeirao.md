# Handoff — RADAR (quarteto, foto, evolução), correção do dash 10 e separação de Ribeirão

**Data:** 2026-09-01
**Máquina:** `mac-grupovelas`
**Sessão:** global / Metabase
**Responsável:** JP

Sessão longa. Cinco frentes independentes, todas com artefato entregue e card no GitHub.
Continua o trabalho de `2026-08-31-share-investimento-435-redesenho-semanal-puro.md` e
`2026-08-31-share-faturamento-dashboard-436.md`.

---

## 0. Índice do que foi feito

| Frente | Artefato | Card |
|---|---|---|
| Auxiliares do ritmo de agendamento | dashboard `437` aba 1 | #366 |
| Proposta do quarteto (Ritmo 5d na contagem) | dashboard `437` aba 2 | #366 |
| Foto do fechamento do mês | dashboard `438` | #370 |
| Evolução do RADAR dentro do mês | dashboard `439` | #371 |
| Bug do 1º dia útil do mês | — (só diagnosticado) | #372 |
| Meta não seguia filtros no dash 10 | card `15299` corrigido | #357 |
| Relacionar os estudos de share | — (só planejado) | #368 |
| Separar Ribeirão em ITC e Trata | colls `681`/`684`, dashs `442`–`447`, grupos `136`/`137` | #373 |

**Dashboards criados:** `437 Estudo Radar`, `438 Relatório Foto`, `439 Evolução Radar` — todos em
`677 — Estudos`.

---

## 1. Auxiliares do ritmo de agendamento — dashboard 437, aba "Ritmo de agendamento"

Nasceram na aba `🧪 Laboratório` do dashboard `316`, ancorados no card `15250`
*"Ritmo de Agendamento — 5 últimos dias úteis x média do mês (rascunho)"*, **que permanece lá**.

Seis cards: `15341` ritmo vs meta/dia útil · `15342` variação ordenada · `15343` quadrante tamanho ×
variação · `15344` painel auditável · `15345` ritmo diário com MM5 · `15346` perfil por dia da semana.

### Crítica ao card de origem, que motivou os auxiliares

1. É um `line` sobre categoria com `ORDER BY delta` — as duas linhas são **obrigadas** a se cruzar
   uma vez. O X que aparece é artefato da ordenação, não achado.
2. `graph.x_axis.labels_enabled: false` e `y_axis.labels_enabled: false` — não se lê unidade nem valor.
3. **Não tem template tag**: ignora os 14 filtros do dashboard 316.
4. Confunde nível com variação: −0,8 sobre base 4,8 é queda de 17%; sobre base 1,0 é colapso de 80%.
5. `d5` é subconjunto da média do mês (5 de 20 dias úteis, 25% de sobreposição), então **subestima**
   a desaceleração.

### 🔴 Correção de fonte — o erro que cometi e corrigi

A primeira versão dos auxiliares usava `mv_mkt_outcomes_diario`. **O RADAR usa
`mv_hibrida_unidade_propria`.** As duas divergem em **uma** unidade:

| Unidade | outcomes | híbrida |
|---|---:|---:|
| ITC Vertebral - BH - Savassi | 0,2 / 0,1 | **2,2 / 2,6** |

43 das 44 unidades batem. Com a fonte errada eu afirmei que o RADAR tinha um ponto cego em
BH-Savassi — **o RADAR estava certo**: com 2,6 contra meta de 2,81 ela fica corretamente fora.
Reescrevi os seis sobre a híbrida, com o mesmo roster do `13576`
(`meta_fat > 0 AND meta_lead > 0 AND meta_agd > 0`, 41 unidades). O ritmo passou a ser **idêntico
ao do RADAR nas 24 unidades** que ele lista, com valores não arredondados.

⚠️ **O card `15250` ainda lê a fonte antiga.** Pendência.

### Achado que serve a tudo o mais

Perfil por dia da semana, 9 semanas: **segunda 131,2 (índice 135) → sexta 79,2 (índice 82)**.
Segunda vale **1,66×** a sexta; sábado/domingo índice 8.

Cinco dias úteis consecutivos contêm um de cada dia da semana e se autobalanceiam — **mas feriado
quebra isso**. A base marca feriado com `dia_util = 0` (ex.: `04/06`, 14 agendamentos contra ~75 de
uma quinta normal). Se a segunda cai em feriado, a janela pega duas sextas e o ritmo despenca sem
nada ter acontecido.

---

## 2. Proposta do quarteto — dashboard 437, aba "Proposta do quarteto"

Cards `15347` (tabela-verdade das 16 combinações) e `15348` (RADAR com quarteto, 41 unidades com
colunas `L A F R`).

**Decisão estrutural:** os dois **reaproveitam o SQL de produção até o CTE `flag`** e trocam só a
lógica de nível e diagnóstico dali para baixo. Correção na base do `13576` se propaga sozinha.

### O que muda

Hoje `ritmo_caiu` (queda ≤ −30% **e** base ≥ 2 agend/dia útil) é **modificador de ±1** e
**nunca faz entrar** quem não falhou lead nem agendamento. Na proposta o ritmo entra na contagem;
16 combinações com nível e diagnóstico próprios, `CASE` explícito, sem score.

Escala **aditiva**: `P0 · Crítico` no topo, `P5 · Ritmo caindo` no piso, **P1–P4 preservam o
significado atual**.

### Seis decisões documentadas

1. Mapa explícito das 16 combinações, não score ponderado — preserva a explicabilidade declarada.
2. `ritmo_caiu` deixa de ser modificador (senão conta duas vezes).
3. **`fat_batido` não rebaixa o P5** — as 4 unidades do P5 têm todas a meta de faturamento batida;
   sem essa exceção elas cairiam do radar e a mudança não serviria para nada.
4. Ritmo pesa como agendamento, não como lead — é derivada dele.
5. `FAT` sozinho continua FORA; o que muda é `· · X X`.
6. Escala aditiva, não renumerada.

### Efeito, medido em 31/08

| Nível | Hoje | Proposto |
|---|---:|---:|
| P0 | — | 1 |
| P1 | 5 | 4 |
| P2 | 9 | 9 |
| P3 | 7 | 8 |
| P4 | 3 | 3 |
| P5 | — | 4 |
| **No radar** | **24** | **29** |

**Só 4 das 16 células mudam, e duas estão vazias.** O modificador de ±1 já aproxima bem o quarteto
nas células ocupadas. **O ganho está inteiro nas duas células que hoje são FORA:**

- `· · · X` (4 unidades) — Curitiba (−81%), Porto Alegre (−54%), Campinas (−41%), Barra da Tijuca
  (−35%). **Batendo as três metas** e invisíveis.
- `· · X X` (1) — Goiânia: fat projetado em 44% da meta e ritmo −59%, fora pela regra "fat sozinho
  é operação".

Conclusão registrada no #366: **renumerar P1–P5 teria custo alto e benefício quase nulo** — mexeria
no significado de quatro níveis para reorganizar células que já estão no lugar certo.

### Argumentos CONTRA registrados no #366

Dois são fortes o bastante para derrubar a proposta:

1. **Ritmo é derivada de Agend**, não eixo independente — contar os dois faz o agendamento pesar
   duas vezes (2 falhas do mesmo fenômeno contra 1 de lead e 1 de fat).
2. **O radar deixaria de ser triagem**: 29 de 41 = **71% da rede**.

Mais: o ganho prático são 5 unidades contra reestruturar escala/filtro/documentação; fragilidade da
métrica em três frentes; foi preciso abrir exceção (`fat_batido` no P5); e P5 fala do mês seguinte
enquanto P1–P4 falam do corrente.

**Três alternativas mais baratas** ficaram no card: deixar o ritmo como modificador mas permitindo
entrar num nível-piso; lista separada fora da escala P; ou corrigir a sobreposição de janelas antes
de recalibrar qualquer corte.

---

## 3. Foto do fechamento — dashboard 438 "Relatório Foto"

Pedido da diretoria (#370). Card `15350`, filtro **Mês de referência** (`date/single`, default
`2026-08-01`), página única.

### Três diferenças em relação ao RADAR

1. **Realizado, não projetado.** `du_h` sai, `du_t` entra; `%Lead/%Agend/%FAT` = realizado ÷ meta
   cheia. Efeito colateral: `fat_batido` deixa de ser independente de `f_fat` — com o mês fechado os
   dois olham o mesmo número e ele só distingue algo na faixa 90–100%.
2. **Nível pelo quarteto**, com a coluna `Nível (trinca)` ao lado — foi a saída registrada no #370
   para o risco de publicar lógica não aprovada.
3. **Imune ao bug do dia 1** (§5): não usa `dia_util_ate_hoje` nem `current_date` nas métricas.

`Ritmo 5d` aqui = 5 últimos dias úteis **do mês escolhido** contra a média dos dias úteis do mês.

### Validado em três meses

| Nível | Junho | Julho | Agosto |
|---|---:|---:|---:|
| P0 | — | — | 1 |
| P1 | 13 | 8 | 6 |
| P2 | 7 | 7 | 6 |
| P3 | 3 | 2 | 5 |
| P4 | 5 | 6 | 7 |
| P5 | 2 | 3 | 5 |
| FORA | 8 | 15 | 11 |
| Roster | 38 | 41 | 41 |
| Dias úteis | 21 | **23** | 21 |

Julho com 23 dias úteis e junho com 38 unidades cobrem o critério de validar fora do caso base.
**A rede melhorou:** P1 de 13 para 6.

**Achado colateral:** comparando a trinca no fechamento com a projetada em 31/08, o total no radar
é o mesmo (24) mas **P1 vai de 5 para 7** — a projeção era otimista. Vale card próprio se repetir.

---

## 4. Evolução do RADAR no mês — dashboard 439 "Evolução Radar"

Card #371. Cards `15354` (evolução por unidade, com **diagnóstico em texto**), `15355` (composição
da rede por dia útil), `15356` (direção por marca). Filtro de mês compartilhado.

### Método

Para cada dia útil `D`, recalcula o nível com o acumulado até `D` projetado ao mês, como produção:
`%Agend`/`%FAT` por dias úteis, `%Lead` por dias corridos, `Ritmo 5d` com janela alcançando o mês
anterior. 41 unidades × 21 dias úteis = **861 pontos** em agosto.

A coluna `Evolução` comprime por blocos: `P2×3 → P1×8 → FORA×4`.

### 🔴 Dois achados sobre o próprio RADAR

**Os 4 primeiros dias úteis não servem de referência.** No 1º dia útil a rede aparece com **30 das
41 unidades no radar**, contra 11 no fechamento — projetar um dia para 21 é ruído. Estabiliza no
**5º dia útil**, e é por isso que a coluna de início usa o 5º. Distinto do bug do dia 1: lá
`du_h = 0`; aqui há dado, mas a projeção sobre poucos dias é instável **por natureza do método**.

**O nível é volátil:** média de **4,5 trocas** por unidade em 21 dias úteis; Instituto Trata -
Ribeirão Preto trocou **11 vezes**. Ler o nível de um único dia é instantâneo frágil.

### Achado do mês — padrão de marca

**11 melhoraram · 15 pioraram · 15 estáveis.**

| Marca | Unidades | Melhoraram | Estáveis | Pioraram | % melhorou | Em P5 |
|---|---:|---:|---:|---:|---:|---:|
| Instituto Trata | 16 | **9** | 5 | 2 | **56%** | 0 |
| ITC Vertebral | 25 | 2 | 10 | **13** | **8%** | **5** |

56% contra 8%, e as **5 unidades que fecharam em P5 são todas ITC Vertebral**, todas vindas de FORA.
Se setembro confirmar, é conversa de diretoria.

- **Instituto Trata - Santos** — `P3×1 → P2×4 → FORA×2 → P2×3 → FORA×11`, recuperação sustentada.
- **ITC Vertebral - Chapecó** — P2 → **P0**, única com os quatro eixos falhando.
- **ITC Vertebral - Goiânia** — `FORA×9 → P3×12`, virou no meio do mês e não voltou.

A coluna de diagnóstico distingue casos que `Direção` junta: Goiânia virou no meio e ficou 12 dias;
Niterói-RJ caiu só no último dia depois de 12 dias fora. As duas são "piorou".

---

## 5. 🔴 BUG ATIVO — 1º dia útil do mês zera a trinca (#372)

**Verificado ao vivo em 2026-09-01 no card `13576`: 17 de 17 unidades em `P1 · Trinca ruim`, com
`%Lead = %Agend = %FAT = 0,0000`.**

`dia_util_ate_hoje` só vira `1` **depois** que o dia fecha:

| Dia | `dia_util` | `dia_util_ate_hoje` |
|---|---:|---:|
| 2026-08-31 | 1 | 1 |
| 2026-09-01 | 1 | **0** |

Com `du_h = 0` e `dc_h = 0`, as três projeções caem no `ELSE 0`, os três percentuais viram zero,
`n_falhas = 3` → **P1 para todas**. O `ELSE 0` trata "sem base para projetar" como "realizou zero".

Frequência: **~12 dias por ano**, um por mês. Volta no 2º dia útil.

**Correção proposta, não aplicada:** devolver `NULL` em vez de `0`, para a unidade sair do radar por
falta de base. Duas perguntas em aberto: sair silenciosamente ou expor estado `base insuficiente`; e
se o guard cobre só o dia 1 ou os 4 primeiros dias úteis (§4).

Observação: o roster caiu de 41 para 17 em 01/09 porque **as metas de setembro só estão carregadas
para 17 unidades** — ingestão de meta, não este bug, mas mascara o problema.

Esta classe de bug **já estava documentada** no texto do Laboratório do 316: *"Toda janela relativa
a `current_date` precisa ser testada num dia em que 'ontem' cai fora do balde atual — segunda-feira
para semana, dia 1 para mês."* A regra existia; este caso não foi coberto.

---

## 6. Correção em produção — meta não seguia os filtros (dash 10, card 15299) — #357

O gráfico ` Agendamentos x Período ` da aba RPD comparava **realizado filtrado contra meta da rede
inteira**.

Causa: `meta_por_mes` filtrava por `{{meta_unidade}}`, `{{meta_marca}}`, `{{meta_socio}}`,
`{{meta_boutique}}`, `{{meta_data}}` — **cinco tags nunca mapeadas a parâmetro nenhum** do dashboard
10 (que tem 10 parâmetros e nenhum `meta_*`). Bloco `[[ ]]` sem valor é descartado.

| Filtro | realizado | meta antes | meta depois |
|---|---:|---:|---:|
| sem filtro | 2.188 | 2.415,0 | 2.415,0 |
| unidade Alphaville | 81 | 2.415,0 | **63,0** |
| marca Instituto Trata | 636 | 2.415,0 | **797,0** |
| marca ITC Vertebral | 1.552 | 2.415,0 | **1.618,0** |
| sócio Alexandre | 77 | 2.415,0 | **94,1** |

**Correção:** `meta_por_mes` passou a derivar o escopo de `dim_selecionada`, CTE que já existia no
card e resolve `id_interno` a partir de `{{marca}}`/`{{unidade}}`/`{{boutique}}`/`{{socio}}`. Saíram
`escopo_meta_ids`, o join com `dim_unidades` e as 5 tags `meta_*`. Restaram 6 tags.

**Três validações:** `797 + 1.618 = 2.415` exatos; Alphaville dá `81/63 = 1,286`, idêntico ao
`%Agend` de 1,286 da foto de agosto por outro caminho; e unidade sem meta (`Guararapes - 2`) deixou
de herdar a meta da rede.

**Aplicado com `PUT` no mesmo card `15299`**, seguindo a convenção do Laboratório do 316
(*"substituir SQL/visualização no mesmo id, não trocar o card do dashcard"*). O card não tem
`columnValuesMapping` e as 14 colunas de saída são idênticas. Auditoria: dash 10 com os mesmos
**116 dashcards**, dashcard `22669` com os **5 mappings intactos**.

Backups em `c15299-backup.json` e `d10-backup.json`.

---

## 7. Separação de Ribeirão Preto (#373)

Decisão executiva: separar a praça em ITC e Trata. **A pasta `55 — Boutique Ribeirão Preto` foi
mantida** como visão consolidada; as novas são **irmãs** dela em Sócios, não filhas.

```
Sócios (180)
├── Boutique Ribeirão Preto (55)     ← intacta: Dados (56) · Dashboards (57)
├── ITC Ribeirão Preto (681)         ← grupo 136
│   ├── Dados (682)      → modelo 15411
│   └── Dashboards (683) → 442 NPS · 443 Performance · 444 Tempo de Resposta
└── Trata Ribeirão Preto (684)       ← grupo 137
    ├── Dados (685)      → modelo 15412
    └── Dashboards (686) → 445 NPS · 446 Performance · 447 Tempo de Resposta
```

Os modelos delimitam por `unidade` e preservam `status = 'Ativa' AND tipo = 'Própria' AND
socio <> 'Matriz'` — o que exclui os registros encerrados de nome parecido. Cada um retorna 1 linha.

**240 cards novos** (120 por marca: 32 NPS + 77 Performance + 11 Tempo). Deep copy, que é a
convenção — os cards de dashboard de sócio são dashboard questions próprias, não compartilhadas
(`dashboard_count` 1 ou 2, e o 2 é o mesmo card em duas abas).

### 🔴 Correções ao entendimento inicial

**Os dashboards não usam o modelo `7782` nas queries.** Usam os modelos compartilhados da rede
(`2457`, `51`, `2098`, `2141`, `1816`, `2228`, `2131`, `2158`, `2231`, `2091` — os mesmos do dash
10). **O recorte vem dos filtros**; o modelo de segmentação alimenta a *lista de opções* do filtro
de Unidade.

**A convenção de filtro difere por dashboard**, conferida contra o ITC Brooklin antes de aplicar:

| Dashboard | Filtro Unidade | Default original |
|---|---|---|
| NPS | `static-list` com a unidade | sim |
| Performance | `values_source` = modelo da pasta | **não tinha** |
| Tempo de Resposta | `values_source` = modelo da pasta | **não tinha** |

### Ajustes de filtro

**`Marca` removido dos dois NPS** (12 mapeamentos cada). Tinha `default: null` — nunca filtrou nada.
Conferido que os dados não mudaram.

**`Unidade` travado, não removido.** Os 32 cards do NPS e 77 do Performance **estão todos mapeados
nele** — é o mecanismo de recorte. Remover faria mostrar a rede inteira. Em vez disso, `values_source`
repontado para o modelo da pasta e **default adicionado** em `443`, `444`, `446`, `447`.

Validação com o card `15562` do `446`: sem filtro devolve `P0 - Márcio Pimentel · ITC Vertebral`;
com o default, `P0 - Maria Ferreira · Instituto Trata`.

Tirar o widget da tela exigiria fixar a unidade em **218 cards** (9 em SQL nativo). Registrado como
possibilidade, não executado.

### Grupos e permissões

`136 ITC Ribeirão Preto` e `137 Trata Ribeirão Preto`, nomes idênticos às coleções (convenção das
próprias). `read` na pasta e nas duas subpastas, espelhando o `ITC Brooklin`. Grafo `242 → 243`.

⚠️ **O grupo `Boutique Ribeirão Preto` (13) tem `read` nas seis coleções novas.** Elas nasceram
dentro da `55` e **herdaram a permissão do pai**; a herança ficou depois de eu movê-las. Hoje o
grupo tem 0 membros, então não há exposição — mas se voltar a ter gente, ela verá as duas marcas.
Decisão pendente: é o desejado (grupo da praça vê tudo) ou é vazamento?

---

## 8. Lições de operação desta sessão

**🔴 O Metabase aplicou escritas retornando erro, três vezes.** Um `connection reset`, um
`IncompleteRead` e um `HTTP 400` (*"Este painel tem uma guia, o que garante que cada cartão tenha
uma guia"*). Nos três casos a mudança **tinha sido aplicada**. Regra: diante de erro do Metabase,
**conferir o estado** antes de repetir a operação.

**Dashboard não pode ficar sem abas** se tem cards. Para voltar a página única, é preciso manter uma
aba, não `tabs: []`.

**Criar card com `dashboard_id` auto-insere dashcard órfão na primeira aba** — já documentado no
Laboratório do 316, e aconteceu em todos os deploys. Montar o array de dashcards do zero evita;
reenviar o array vindo do `GET` duplica.

**`display: "pivot"` não funciona com SQL nativo** (v0.55.3) — usar `display: "table"` com
`table.pivot: true` + `table.pivot_column` + `table.cell_column`, e query de exatamente 3 colunas.
Já registrado na sessão anterior, reaplicado aqui desde o início.

**Backticks em heredoc de bash são interpretados pelo shell** — escrever patches de texto em arquivo
Python, não inline.

**Scripts de deploy não são idempotentes na criação de cards.** O de Ribeirão gravou progresso em
`ribeirao-dashboards.json` e pode ser re-rodado; os outros não. Se um deploy falhar no meio, conferir
o que já foi criado antes de re-executar.

---

## 9. Pendências

### Alta

1. **#372 — bug do 1º dia útil.** Produção está errada um dia por mês. Decidir `NULL` vs estado
   explícito, e se o guard cobre o dia 1 ou os 4 primeiros dias úteis.
2. **Permissão herdada do grupo 13** nas coleções `681`–`686` (§7).
3. **Card `15250` ainda lê `mv_mkt_outcomes_diario`** — diverge do RADAR em BH-Savassi.

### Média

4. **#366 — decidir o quarteto:** promover, ajustar ou descartar. Cinco decisões abertas: célula
   `X · X X`, corte de −30%, `fat_batido` no P5, guarda de volume, e atualização do filtro `Nível` e
   do texto "Como ler esta aba" ao promover.
5. **#370 — publicar a foto com quarteto ou trinca?** Hoje tem as duas colunas.
6. **#371 — replay ou snapshot?** Hoje recalcula do zero e acompanha correções na lógica; snapshot
   diário seria mais barato mas congelaria a lógica.
7. **#368 — cruzar os estudos de share** (435 × 436). Grade idêntica, mesma última semana fechada
   `23/08`. Correlações já medidas: investimento × Faturamento `0,414`, × semana seguinte `0,403`.
   Contrastes: fim de semana **28,78% da verba × 1,28% da receita**; vale mensal na Semana 3 do
   investimento e Semana 1 do faturamento.
8. **#373 — estender a separação** às outras 6 praças com pasta própria e duas marcas: Alphaville,
   Bairro de Fátima, Curitiba, Guararapes, Meireles, Savassi. Barra da Tijuca, Ipanema e Niterói
   também misturam marcas mas não têm pasta própria.
9. **Performance da praça (`253`) e a família de sócios abrem sem default de unidade** — mostram a
   rede inteira. Vale rever no conjunto.
10. **Aba experimental `Share — 13 semanas` no dashboard `434 — Pulso`** — decidir se sai, agora que
    435 e 436 são canônicos.

### Herdadas, ainda abertas

11. **Issue #358** — leads de Tatuapé (unidade 224) parados desde `25/08`, causa a montante das MVs.
12. **Handoff de 28/08 do 435 segue untracked** no hub, junto de 21 outros arquivos (caches, mapas
    gerados, plugins). Nada disso foi commitado.

---

## 10. Arquivos locais

Em `/private/tmp/claude-501/-Users-grupovelas/1a3e784e-955f-4a29-b8a4-558a77b56501/scratchpad/`:

| Arquivo | Conteúdo |
|---|---|
| `mb.py` | cliente da API (User-Agent `curl`, senão dá 403) |
| `cards_ritmo.py` / `cards_ritmo2.py` | auxiliares v1 (outcomes) e v2 (híbrida) |
| `radar_quarteto.py` | mapa das 16 combinações sobre o SQL de produção |
| `foto_card.py` | card da foto do fechamento |
| `replay.sql` / `cards_trajetoria.py` / `diag_evolucao.py` | replay diário e diagnóstico da evolução |
| `fix_meta.py` | correção do card 15299 |
| `criar_ribeirao.py` / `copiar_dashboards_ribeirao.py` | estrutura e dashboards de Ribeirão |
| `collection-graph-backup.json` | grafo de permissões antes da mudança |
| `c15299-backup.json` / `d10-backup.json` / `d316-backup*.json` / `d437-backup*.json` | backups |
| `ribeirao-dashboards.json` | progresso do deploy de Ribeirão (re-executável) |
