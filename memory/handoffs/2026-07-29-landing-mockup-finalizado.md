# Handoff — Landing do Pulse: mockup do Hero finalizado + próximo passo (migração Postgres)

**Data:** 2026-07-29
**Repo da landing:** `~/dev/raiox-mvp-html` (`checkpulse.com.br`)
**Repo do produto/banco:** `~/dev/pulse`
**Status da landing:** trabalho concluído nesta sessão. **Nada commitado ainda** — aguardando confirmação do usuário.

---

## Parte 1 — Landing: o que foi feito nesta sessão

Handoff anterior (`2026-07-29-landing-mockup-nao-ficou-bom.md`) registrou que a
primeira tentativa de mockup (CSS puro) não ficou boa e foi interrompida a
pedido do usuário. Esta sessão refez tudo do zero, com resultado aprovado.

### 1. Copy e estrutura — 7 seções

Landing reduzida de 10 para 4 seções (Hero/Dor/Prova/Fechamento), copy nova
aplicando Kahneman, Kane, Dooley, Miller (Grunt Test + StoryBrand 2.0), Fogg,
Kotler 6.0, Bridger (neuromarketing) e Cialdini — síntese própria, nada citado
literalmente. Depois, a pedido do usuário, voltou a **7 seções**: Hero, Dor, 3
seções novas sobre as "duas frentes" do produto (tempo de resposta, qualidade
do atendimento, temperatura do lead — WhatsApp/Lead Score, além da frente
financeira original), Prova, Fechamento. Copy 100% reescrita a pedido do
usuário ("não gostei de nenhuma").

Bug real corrigido: `body.landing-mode .intro-hero { display: none; }` era CSS
legado do design de 10 seções que escondia o Hero inteiro silenciosamente.
Corrigido para `display: grid`.

### 2. Paywall removido do produto de verdade (não é só cosmético de screenshot)

O usuário pediu inicialmente para tirar o blur só para tirar um print, depois
confirmou explicitamente: **"Remover do produto de verdade"**. Eram 3 camadas
independentes no dashboard Lume, todas removidas:

- `.dashboard-locked-content { filter: blur(7px); ... }` — blur removido.
- `.dashboard-unlock` (card "Desbloquear relatório completo") — `display: none`.
- 3 pontos no JS onde um booleano `locked` substituía valores reais por texto
  placeholder ("Detalhe reservado", "Projeção parcial" etc.) — os 3 agora usam
  `const locked = false`. **Importante:** remover só o CSS de blur não bastava,
  esses 3 booleanos JS precisavam mudar também, senão o texto placeholder
  continuava aparecendo mesmo sem blur visual.

Isso é uma decisão de produto/monetização, não só de UI — o usuário foi
avisado do trade-off antes de confirmar.

### 3. Mockup MacBook + iPhone no Hero — com prints reais do produto

Usado um mockup flattened fornecido pelo usuário (`Downloads/Untitled-1.png`,
6000×4171, sem transparência) e compostos nele screenshots reais do dashboard
Lume (já sem paywall) via automação Playwright (wizard completo até o
dashboard) + Python/Pillow:

- Recorte preciso das telas por varredura de transição de cor (não por preview
  reduzido).
- Fundo removido por **flood-fill / connected-component** (`scipy.ndimage.label`),
  mantendo transparente só o componente que toca a borda da imagem — uma
  primeira tentativa com threshold global de branco furou buracos no conteúdo
  branco *dentro* das telas (cards, fundos de UI) e foi descartada.
- Borda do recorte suavizada com `GaussianBlur(radius=4)` só no canal alpha
  (não reintroduz buraco no miolo, só amacia a transição de borda) — resolve
  o "corte mal feito" que o usuário reportou por último.
- Quantização para PNG leve preservando alpha: `Image.FASTOCTREE` (obrigatório
  para RGBA; `MEDIANCUT` dá erro).
- Asset final: `assets/hero-mockup.png`, 2400×1529, ~127KB.

Depois de embutido no Hero, 3 bugs de acabamento foram corrigidos:
- Fundo não transparente → corrigido junto com o flood-fill acima.
- Mockup pequeno demais → aumentado em 2 rodadas: primeiro 35%, depois "bem
  mais" a pedido do usuário — o gargalo real não era o `width` do próprio
  `.hero-mockup`, e sim a **coluna do CSS Grid** que o contém
  (`grid-template-columns`); mudar só o `width` do elemento não tinha efeito
  até a coluna ser alargada também. Estado final: container split em
  `min(1600px,100%)` com colunas `.62fr / 1.38fr`, mockup renderizando a
  ~1076×686px em viewport largo (era ~546×346 originalmente).
- Sombra/smudge indesejada no texto do H1 → era `text-shadow` herdado de uma
  versão anterior de fundo escuro; neutralizado com override em
  `body.landing-mode h1.intro-title`.
- Sombra ao redor do mockup para disfarçar a borda do recorte → `filter` com
  **dois** `drop-shadow` empilhados (curto+denso e longo+difuso), que dissolve
  visualmente qualquer aresta residual do PNG.

Tudo verificado via Playwright pilotando o Chrome do sistema
(`chromium.launch({channel:"chrome"})`, evita o download do Chromium do
Playwright que falha por timeout de rede nesta máquina) — screenshots reais
conferidos a cada mudança, nunca assumido visualmente sem checar.

### Estado do repo da landing

```
M  index.html
?? assets/hero-mockup.png
?? docs/briefing-copy.md
```

**Nada commitado.** Prática desta sessão: sempre confirmar com o usuário antes
de `git commit`/`git push` (dois conflitos de push anteriores já foram
resolvidos assim, com `--force-with-lease` só após confirmação explícita).
Próxima sessão: perguntar ao usuário se pode commitar/dar push agora que o
mockup está aprovado.

---

## Parte 2 — Próximo passo: migração Supabase → Postgres puro (`~/dev/pulse`)

O usuário pediu explicitamente para este handoff apontar a continuidade para a
frente de banco de dados. Contexto resumido (detalhe completo em
`memory/handoffs/2026-07-28-migracao-postgres-puro.md` e no plano
`~/.claude/plans/delightful-sprouting-karp.md`):

**Decisão vigente:** Pulse sai do Supabase para Postgres puro em AWS RDS. SQL
puro com `pg` (sem ORM), auth própria em schema `app_auth` com sessão por
token opaco (não JWT), isolamento multi-tenant **na aplicação** (RLS removida),
segredos via `pgcrypto` com chave fora do banco.

**Progresso já registrado** (ver
`2026-07-28-pulse-postgres-fase-a-iniciada.md` e
`2026-07-28-pulse-postgres-docker-baseline-validada.md`): Fase A iniciada,
baseline de schema validado contra Postgres em Docker, testes de isolamento
tenant A / tenant B já cobrindo estatísticas do dia, buckets, fila e filtro por
`unit_id`.

**Próximo passo recomendado (Fase B):**
1. Helper de tenant/sessão + teste de isolamento cross-tenant como
   pré-requisito, antes de portar mais rotas.
2. Portar por ordem de risco de IDOR primeiro:
   - `app/api/dashboard/conversa/route.ts`
   - `app/api/dashboard/enviar-mensagem/route.ts`
   - `app/api/alertas/thresholds/route.ts`
3. Portar `lib/server/meta-secrets.ts` para Postgres/pgcrypto usando
   `PULSE_SECRETS_KEY` (Vault → pgcrypto, ver riscos no handoff da migração:
   a chave não pode viver no banco, precisa ser injetada por transação com
   `set_config(..., true)` por causa do PgBouncer em transaction mode).

**Risco de maior alcance ainda não mitigado em todo lugar:** coerção de tipos
do driver `pg` (numeric → string, timestamptz/date → objeto `Date`, diferente
do que o PostgREST devolvia) — só `lib/server/live-stats.ts:30` está blindado
hoje. Resolver com `setTypeParser` global + cast `::float8` explícito nas
queries antes de portar mais rotas, não depois.

**Pendências abertas, não afetadas pela migração:**
- Rotacionar `META_APP_SECRET` (circulou em texto plano).
- `WHATSAPP_VERIFY_TOKEN`/`WHATSAPP_APP_SECRET` setadas no Vercel mas não
  deployadas.
- Embedded Signup bloqueado por Acesso Avançado da Meta (`#2655111`).
- Responsividade mobile implementada, não verificada visualmente em aparelho
  real (safe-area-inset zera no devtools).
