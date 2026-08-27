# Handoff — NPS distribuído por sócio e unidade + escopo Própria/Ativa no 59

**Data:** 2026-08-27
**Sessão:** global, máquina do JP (Claude Opus 5)
**Issue:** [Grupo-Velas/produtividade-bi-dev#270](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/270)
**Comentários postados:** [5442379582](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/270#issuecomment-5442379582) (distribuição) e [5442667064](https://github.com/Grupo-Velas/produtividade-bi-dev/issues/270#issuecomment-5442667064) (escopo Própria/Ativa)
**Relacionado:** `2026-08-26-nps-ia-voltar-hub-e-boutique.md`, `2026-08-27-issue-334-lead-dia-tatuape.md`

---

## O que foi feito

Duas demandas encadeadas. **42 dashboards de NPS novos** (390–432), mais alterações no 59 de produção.

### 1. Tabela solta → dashboard de performance (18 cards)

`Consolidado Unidade - mes tocado (SQL)` estava solto na collection de cada sócio. O card **já estava** na aba Consolidado do `🚀 Relatório de Performance`; o que estava errado era onde ele morava. A Alessandra era a única no padrão certo (card interno do dashboard, `dashboard_id` preenchido).

`PUT /api/card/<id> {"dashboard_id": <dash>}` nos outros 18 → o Metabase move o card para a subcollection `Dashboards` sozinho. Mônica era caso à parte: o dela estava solto dentro de `/Dashboards`, não na raiz.

| Sócio | card → dash | Sócio | card → dash |
|---|---|---|---|
| Alexandre | 13362 → 341 | Cleyton | 13372 → 351 |
| Daniel Luis | 13363 → 344 | Luciano | 13373 → 352 |
| Juliana | 13364 → 345 | Mário Andrade | 13374 → 353 |
| Márcio | 13365 → 346 | Mônica | 13360 → 84 |
| Maria Ferreira | 13366 → 347 | Carolina | 13375 → 103 |
| Fernando/Tariane | 13367 → 271 | Jhonatha | 13376 → 273 |
| Híkaro | 13368 → 348 | Pedro Aquino | 13377 → 277 |
| Mariana | 13369 → 274 | Pedro Jettar | 13378 → 279 |
| Pietro | 13370 → 349 | Vanderson | 13371 → 350 |

### 2. NPS replicado — 19 sócios (390–408) e 23 unidades (409–432)

`POST /api/dashboard/59/copy {is_deep_copy: true}` para a subcollection `Dashboards` de cada pasta em `Próprias / Sócios` (collection 180). O deep copy duplica os 33 cards como **internos do novo dashboard**, o que é exatamente o que se quer.

**Sócios** — filtro `contains(socio, "<nome completo>")` no MBQL e `AND dim_unidades.socio ILIKE '%<nome>%'` no nativo. Nome completo por causa dos dois Pedros. **Jettar ficou em `%Jettar%`** a pedido do JP: existe `P2 - Jettar` (Instituto Trata - Pinheiros, própria encerrada) com 8 respostas que o nome completo deixava fora.

**Unidades** — escopo por `unidade`, nunca por `boutique`. As 23 pastas: 7 Boutique, 13 ITC, 3 Trata.

O escopo de cada pasta veio do **Modelo de Segmentação que já existia nela**, não do nome da pasta. Isso pegou:
- `ITC Campinas` = `ITC Vertebral - Campinas Cambuí`
- `ITC Goiânia` = `ITC Vertebral - Goiânia - Setor Marista`
- `Boutique Savassi` usa `unidade like '%Savassi'` porque o cadastro parte o endereço em `Boutique - Savassi` (Trata) e `Boutique - BH - Savassi` (ITC)

### 3. Segmentação de marca no layout

O 59 é 12+12 — ITC à esquerda, Trata à direita. **28 dos 42 têm uma marca só.** Nesses, 14 dashcards da marca ausente (10 cards + 4 títulos, em 4 abas) removidos e os 14 sobreviventes esticados para `col 0` / `size_x 24`.

Marca lida **pela query**, nunca pelo nome do card — os nomes mentem: `Estrutura Trata`, `ITC Técnicas tratamento`, `Negativos — Instituto Trata`, e um `NPS Tratamento Trata` que fica na aba Avaliação. Detecção: `["=",["field","marca"],...]` no MBQL, `dim_unidades.marca = '...'` no nativo. Checagem de colisão (aba+linha) antes de cada PUT; nenhuma ocorreu.

### 4. Filtros — dois novos, quatro removidos

**Área** (`string/contains`, 13 valores) e **Intuito** (`string/=`, 6 valores), sobre `nps_ia.analise`, em **dois cards por caminhos diferentes**:
- `Comentários Tratamentos` (MBQL sobre `card__13673`) → dimensão nos campos `areas` / `intuito`
- `Alertas — lista para ação` (nativo) → variável de template com `EXISTS (... jsonb_array_elements_text(analise->'areas') a WHERE a ILIKE '%'||{{area}}||'%')`

**Removidos** `Recepção`, `Anamnese`, `Técnicas`, `Estrutura` (decisão do chefe do JP), com os 8 mapeamentos e os `click_behavior` de crossfilter das pizzas da aba Pesquisa de satisfação.

### 5. Relatório fora dos filhos

Aba `Relatório` removida, card `Unidades elegíveis` arquivado, `click_behavior` de link da coluna `Relatório` da tabela de alertas removido **e a coluna `'Abrir relatório 📄'` tirada do SELECT**. Nenhum caminho para `connect.grupovelas.com.br/webhook/nps-relatorio-unidade` sobrou. O fluxo do n8n segue exclusivo do 59.

### 6. Dashboard 59 — escopo Própria + Ativa

Filtro Boutique listava inativa e franqueada, e elas entravam nos totais. Critério aplicado: `dim_unidades` com `tipo='Própria' AND status='Ativa'`, marca ITC/Trata → **45 unidades / 36 valores de boutique**.

- Lista estática do filtro: **48 → 36**
- Os **33 cards** ganharam `boutique IN (<36>)` — 23 MBQL, 10 nativos

**Saíram 14 unidades / 124 respostas**: 2 franqueadas ativas (São Luis 37, Araçatuba 7), 10 próprias encerradas (55), 2 **Matriz** (`ITC Vertebral - Matriz` 21 + `Instituto Trata - Matriz` 2) e 2 órfãs sem match em `dim_unidades`.

`NPS por Unidade` foi de 54 un / 2.118 resp para **40 un / 2.021**. Fechamento pela base: 3.803 − 124 = **3.679** = total de Própria+Ativa contado direto no `dim_unidades`.

## Decisões tomadas

1. **Escopo por `unidade`, não por `boutique`** nos dashboards de unidade. `Boutique - Ribeirão Preto` cobre a ITC do Márcio e a Trata da Maria — por boutique, sócio nenhum teria recorte limpo.
2. **Modelo de Segmentação como fonte de verdade** do escopo de cada pasta, não o nome da pasta.
3. **Marca do dashcard lida da query**, não do nome do card.
4. **Filtros de IA na aba Tratamento**, não na de Alertas — decisão do JP: a lista de alertas é fila de ação (só Alta/Crítica), a de Tratamento tem a base analisada completa e "os comentários já bem bonitinhos". Depois Área e Intuito foram ligados **nos dois**.
5. **Sentimento e Temperatura descartados como filtro.** Dentro dos alertas, sentimento é 100% Negativo em 107 de 107 — botão morto. Temperatura duplicaria o Urgência.
6. **Nenhum card novo de comentários.** Proposto e recusado: "eu quero ver so os alertas mesmo, entao pode ser profissional e aparecer somente 2, esse é o intuito".
7. **`ITC Vertebral - Rateio` mantido** nos 36 (Própria/Ativa) apesar de `socio = 'Matriz'` e 0 respostas. Não altera número.
8. **`Instituto Trata - Pinheiros` mantido** no dashboard do Jettar mesmo sendo própria encerrada — base histórica dele.
9. **Card de menções não aberto** — o JP dispensou.

## Armadilhas encontradas (registrar, custaram tempo)

- **Teto de 2000 linhas.** O card de comentários da mãe devolve 2000 cravado — limite de exibição do Metabase. Fatiar esse resultado por unidade compara recorte truncado e acusa divergência falsa em quase todos. A mãe precisa ser **filtrada antes** de comparar.
- **`string/contains` em variável nativa não funciona sem `parameter_mapping` no dashcard.** A API aceita a chamada e ignora o filtro em silêncio, sem erro. Com o mapping, funciona.
- **Coluna `Comentário` vinha `enabled: false`** no `table.columns` da tabela de alertas, herdado do 59. Era o motivo real de o texto do cliente não aparecer — não era espaço.
- **`urllib` leva 403 sem `User-Agent`** no Metabase (curl passa). Módulo `mb.py` manda `User-Agent: curl/8.7.1`.
- **Unidades `marca = 'Matriz'`** não aparecem em recorte por ITC/Trata mas entram nos cards, porque `card__2098` usa LEFT JOIN com `dim_unidades`. Só apareceram quando a conta não fechou.
- **Parâmetro duplicado** ao copiar o 59 depois de já ter Área/Intuito nele — o script somava de novo. Dedup por id, e mapeamento por `parameter_id`.
- **`is_deep_copy` mantém o card interno do dashboard novo** (`dashboard_id` do filho), o que é o comportamento desejado.

## Verificação

Cada um dos 42 conferido contra o 59:
- `NPS por Unidade` **linha a linha** nas abas Tratamento e Avaliação (NPS, Respostas, Promotor, Detrator, Comentários)
- contagens de Comentários Tratamento, Comentários Avaliação e Alertas, com a mãe filtrada para escapar do teto
- todas as queries com `status: completed`
- filtros: mesmo conjunto de ids da mãe, sem duplicata, sem mapeamento órfão
- layout: nenhum card da marca ausente, sobreviventes em largura cheia, zero colisão

**42/42 sem divergência.** Sócios: 19/19 ✓. Unidades: 23/23 ✓. pass5 (remoção dos 4 filtros): 20/20 ✓.

Um incidente: **ITC Jardins** caiu no meio por conexão derrubada e deixou o dashboard 420 pela metade (cópia crua). Arquivado e refeito como **432**.

## Arquivos tocados

Nada no repositório. Tudo via API do Metabase:
- **Cards**: 18 realocados (13360, 13362–13378); ~1.400 cards editados nos 42 dashboards; 33 cards do 59
- **Dashboards criados**: 390–419, 421–432 (420 arquivado)
- **Dashboard 59**: parâmetros (48→36 no Boutique, +Área +Intuito, −4 de pesquisa), 33 queries, mapeamentos e click behaviors
- **GitHub**: 2 comentários na issue 270

Scripts e backups no scratchpad da sessão (**efêmero**): `mb.py`, `build_unidade.py`, `marca_unica.py`, `aba1.py`, `segmentos.py`, `swap_unidade.py`, `nps_socio.py`, e os backups `backup_59_queries.json`, `backup_59_params_v2.json`, `backup_layout.json`.

## Pendências

- [ ] **Backups do 59 só existem no scratchpad efêmero.** Para reverter o escopo Própria/Ativa: tirar `boutique IN (...)` dos 33 cards. Para reverter o filtro: lista antiga de 48 valores. Se for para preservar, copiar para o hub antes de a sessão morrer.
- [ ] **Normalização de `dim_unidades.boutique`** (Ernandes, herdado): Savassi/BH-Savassi, Brooklin, Vila Mariana, e a unidade de Fortaleza cadastrada com boutique `Santo André`.
- [ ] **Crossfilter das pizzas da Pesquisa de satisfação morreu** em todos os 43 dashboards — era alimentado pelos 4 filtros removidos. As pizzas seguem corretas, o clique não filtra mais. Reativar = recriar os parâmetros.
- [ ] **Nome do profissional citado** não existe em campo nenhum, só no texto do comentário. Caminho seria a IA devolver `mencoes` no fluxo do n8n. JP dispensou card por ora.
- [ ] **NPS geral do 59 mudou de valor** com a restrição. Avisar quem consome o número.
- [ ] `DROP public.nps.ia_analise` (herdado, destravado desde 21/08)
- [ ] Agrupar as 13 áreas em 4-5 macro-temas para material executivo (herdado)

## Próximo passo

Nenhum trabalho em aberto. Se voltar ao assunto: confirmar com o JP se o NPS geral menor do 59 é aceito pelos consumidores do número, e decidir se os backups do 59 vão para o hub.
