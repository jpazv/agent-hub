# Handoff — NPS IA: voltar pro hub e tratamento de boutique com duas unidades

**Data:** 2026-08-26
**Sessão:** global, máquina do JP
**Issue:** [Grupo-Velas/produtividade-bi-dev#270](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/270)
**Relacionado:** `2026-08-20-nps-ia-tabela-separada-e-periodo.md`, `2026-08-19-nps-relatorio-html-e-dashboard-387.md`

---

## Contexto

Duas demandas do JP sobre o fluxo de relatório NPS por unidade, já em produção
no dashboard 59 (abas `Relatório` e `🚨 Alertas & Risco`):

1. O botão Voltar do front não levava a lugar nenhum útil.
2. O dashboard filtra por **boutique**, mas o relatório é por **unidade** — e
   uma boutique é um endereço com duas unidades distintas (ITC + Trata). O
   comportamento nunca tinha sido verificado.

## Diagnóstico

### Voltar

`Render Front NPS` → `detailPage()` usava
`<a class="back" href="javascript:history.back()">`. Vindo do clique no
Metabase (aba nova, ou `window.top` forçado pelo script `BREAKOUT`) o histórico
está vazio ou aponta pro Metabase — botão morto ou volta pro lugar errado.
Pior: a **página do relatório gerado** (`Render Relatorio HTML`) não tinha
botão Voltar nenhum. Beco sem saída.

### Boutique ≠ unidade

`dim_unidades` tem coluna `boutique`; **42 boutiques têm ≥2 unidades**, cada uma
com seu `id_interno`. Entre as 25 elegíveis (≥40 comentários):

- **6 endereços com as duas pontas elegíveis**: Barra da Tijuca, Brooklin,
  Curitiba, Ipanema, Ribeirão Preto, Vila Mariana.
- Casos em que só um lado é elegível e o outro sumia em silêncio:
  Bairro de Fátima (ITC 52 ✔ / Trata 27 ✘), Meireles (ITC 46 ✔ / Trata 31 ✘),
  Niterói (Trata 59 ✔ / ITC 33 ✘).
- **`boutique` não está normalizado**: o mesmo endereço aparece como
  `Boutique - Ipanema` mas também como `Instituto Trata - Brooklin` /
  `ITC Vertebral - Brooklin`, e Savassi está partida em `Boutique - Savassi` e
  `Boutique - BH - Savassi`.
- O card 13645 (`Unidades elegíveis`) tinha `parameter_mappings: []` — filtrar
  Boutique no dashboard **não filtrava** a tabela.

## O que foi feito

### 1. Workflow n8n — `NPS - Relatório por Unidade`

Arquivo gerado: `~/Downloads/NPS - Relatório por Unidade-4 (voltar-hub + boutique).json`
(base: `NPS - Relatório por Unidade-3.json`, export de 26/08).

| Node | Mudança |
|---|---|
| `Buscar Unidades Elegiveis` | SQL reescrito: CTE `grp` + `alvo`, devolve a unidade pedida **+ as irmãs da mesma boutique física**. Colunas novas `is_alvo` e `boutique` |
| `Render Front NPS` | `VC_HUB` const; `detailPage(u, irmas)`; bloco `.irmas`; Voltar → hub em detalhe, lista e "não encontrada"; dispatch por `id_interno` da URL |
| `Render Relatorio HTML` | Link `← Connect Hub` na topbar (dentro de `.topbar-btns`, que o CSS já esconde na captura do PDF) |

**Chave de pareamento da boutique** (a decisão central):

```
lower(sem_acento(cidade)) | lower(uf) | lower(sem_acento(boutique sem prefixo de marca))
```

- Tirar o prefixo (`Boutique -` / `ITC Vertebral -` / `Instituto Trata -`) é o
  que faz Brooklin e Vila Mariana parearem — **2 dos 6** endereços com as duas
  pontas elegíveis.
- `cidade + uf` na chave é obrigatório: sem isso, `Santo André` casava a unidade
  cadastrada em **Fortaleza/CE** (id 46) com a de Santo André/SP (id 592).
- Irmã só entra com **≥1 comentário** (`HAVING`), o que derruba cadastro
  duplicado e encerrado (Curitiba tem 4 registros, Tatuapé 3 — só um de cada
  tem dado).

Resultado: **16 das 25 elegíveis têm exatamente uma irmã**, sem ruído.

**Dispatch:** o `Render Front NPS` escolhia detalhe vs lista por
`unidades.length === 1`. Com irmãs na query isso quebraria — passou a ler o
`id_interno` de `$('NPS Relatorio - Interno')`, com fallback pro comportamento
antigo se o `$()` falhar.

**Voltar:** link fixo pro `velas-hub`. Só volta um passo (`history.back()`)
quando o `referrer` é a própria lista interna do fluxo — aí o rótulo vira
"Voltar à lista".

### 2. Metabase — dashboard 59

| Objeto | Mudança | Status |
|---|---|---|
| Card **13645** `Unidades elegíveis` | coluna `Boutique` no SELECT e visível; `{{unidade}}` (morto — o filtro não existe mais no dash) → `{{boutique}}`, field 2298 | ✅ |
| Dashcard **20232** | `parameter_mappings` `[]` → `Data` (857d5cf4), `Marca` (d15dc75f), `Boutique` (5c3fc048) | ✅ |
| Card **13700** `Boutiques por sensibilidade` | `[[AND {{boutique}}]]` na CTE `neg` + tag `boutique` | ✅ |
| Dashcard **20309** | mapeado em `5c3fc048` — a tabela passa a filtrar a si mesma no clique | ✅ |

O card 13700 **já tinha** o `click_behavior` crossfilter na coluna Boutique — o
clique alimentava o resto da aba mas a própria tabela continuava inteira, então
não ficava claro que havia filtro ativo. Faltava só a tag + o mapeamento.

## Verificação

**SQL do workflow** (rodado no banco, db 2): id 137 → alvo + irmã;
id 67 (Brooklin, só pega via normalização) → alvo + irmã; id 174 → só o alvo;
id 0 → as 25 da lista, intacta.

**JS** executado no Node nos 5 caminhos de render (detalhe com irmã, sem irmã,
irmã abaixo do mínimo, lista, não encontrada) e conferido visualmente nos temas
dark e light.

**Dashboard 59** — diff estrutural contra snapshot a cada gravação: 49 → 49
dashcards, nenhum sumiu/novo, e **cada PUT alterou exatamente um campo de um
dashcard** (`parameter_mappings` do 20232, depois do 20309). Demais 48 com
`card_id`/`row`/`col`/`size`/`tab`/`visualization_settings` idênticos em cada
passo, inclusive o `click_behavior` do link do relatório; 6 abas na ordem;
10 filtros idênticos.

**Atenção ao ler o diff ponta a ponta:** entre as duas gravações o JP mexeu no
layout da aba Alertas pela UI (11 dashcards com `row`/`size_y`/`viz_settings`
alterados — 20247, 20253, 20254, 20300, 20301, 20306..20311). Não é efeito dos
PUTs; o payload da segunda gravação foi montado a partir de um `GET` posterior
e preservou tudo. Diff encadeado (before → after_put1 → base2 → final) confirma
a autoria de cada mudança.

**Filtro funcional** pelo endpoint do dashcard. Card 13645: sem filtro 25
linhas; `Boutique - Ipanema` → 2 (Trata 70 + ITC 55); `Boutique - Barra da
Tijuca` → 2 (ITC 82 + Trata 44); `Marca = Instituto Trata` → 12. Card 13700:
sem filtro 24 linhas, `Boutique - Ipanema` → 1 — e como as 24 linhas têm
boutique distinta e o filtro é igualdade sobre a chave do `GROUP BY`, qualquer
linha clicada colapsa a tabela em exatamente uma.

## Pendências

- [ ] **JP**: importar `NPS - Relatório por Unidade-4 (voltar-hub + boutique).json` no n8n
- [ ] **Normalização de `dim_unidades.boutique`** (Ernandes): Brooklin, Vila Mariana,
      `Boutique - Savassi` vs `Boutique - BH - Savassi`, e a unidade de Fortaleza
      cadastrada com boutique `Santo André`. Enquanto não normalizar, nesses
      endereços o aviso aparece na página do relatório mas **não** no filtro do
      dashboard, que compara a string crua
- [ ] `DROP public.nps.ia_analise` — destravado desde 21/08 (herdado)
- [ ] Agrupar as 13 áreas em 4-5 macro-temas para material executivo (herdado)
- [ ] Replicar a tabela de sensibilidade dentro do relatório HTML (herdado)

## Decisões tomadas

1. **Relatório continua por unidade, não por boutique.** Juntar as duas marcas
   num relatório só misturaria operações distintas. A boutique vira **aviso +
   atalho** para o relatório da irmã.
2. **Pareamento por cidade+UF+boutique normalizada**, não por string crua — sem
   isso Brooklin e Vila Mariana ficam de fora. E não por boutique normalizada
   sozinha — sem cidade+UF, Fortaleza casa com Santo André.
3. **Irmã só com ≥1 comentário** em vez de filtrar por `situacao`, que está
   nulo na maioria dos registros.
4. **Voltar vai pro hub por padrão**, não pro Metabase: o relatório costuma
   abrir em aba nova, onde `history.back()` não tem para onde ir.
5. **Não normalizar `boutique` via SQL no Metabase** — o filtro do dashboard
   compara string crua; corrigir ali seria maquiar dado de cadastro.

## Arquivos tocados

- `~/Downloads/NPS - Relatório por Unidade-4 (voltar-hub + boutique).json` (novo)
- Metabase: cards 13645 e 13700, dashcards 20232 e 20309
- Issue #270: comentário de fechamento postado (`issuecomment-5426387293`)
