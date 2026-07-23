# Handoff — Onboarding do Pulse Eco (compra → provisiona → acesso) + rebranding

**Data:** 2026-07-23
**Máquina:** mac-grupovelas
**Continua em:** macbook-jpazv

## O que foi feito nesta sessão

### 1. Rebranding e apresentação do Eco na landing (`raiox-mvp-html`)
- "Raio-X" → **Pulse Lume** em todo o texto visível de `index.html` e
  `comprar.html` (títulos, botões, meta tags). IDs internos de JS
  (`navRaioxLink` etc.) e URLs de domínio ficaram como estavam de propósito
  — são internos/infra, não texto visível.
- Card do "Eco" (antes "Tempo médio de resposta") na landing renomeado e com
  CTA "Assinar o Eco" apontando pra `comprar-eco.html`.

### 2. Onboarding completo: compra → provisiona → acesso por email
Decisão confirmada com o usuário: **sem conta Stripe ainda**, então o
"pagamento" do Eco é **simulado** — o objetivo era validar o fluxo completo
ponta a ponta (landing → compra → conta criada → email → login → app),
não processar dinheiro de verdade.

- **`raiox-mvp-html`** (landing):
  - `comprar-eco.html` — formulário de compra do Eco (nome + email, R$
    197,00/mês, aviso claro de "ambiente de simulação").
  - `api/pulse-eco-checkout.js` (novo) — recebe a "compra", chama
    `/api/onboarding/provision` no repo `pulse` (segredo compartilhado
    `PULSE_PROVISIONING_SECRET`), e manda o email de acesso via o mesmo
    webhook interno "Connect" que já envia o resultado do Lume
    (`lib/send-email.js`, extraído de `api/send-email.js` pra reaproveitar).
- **`pulse`** (o app/Eco em si):
  - `app/api/onboarding/provision/route.ts` (novo) — cria tenant +
    `tenant_members` (owner) + unit "Matriz", gera link de convite via
    `supabase.auth.admin.generateLink` (tipo `invite` na primeira vez, tipo
    `recovery` em reenvio — usuário já existe nesse caso). **Idempotente por
    email**: uma segunda "compra" com o mesmo email não duplica tenant, e
    agora **reenvia** um novo link/email em vez de ficar silenciosa (bug que
    o usuário pediu pra corrigir).
  - `app/(auth)/convite/page.tsx` (novo) — trata o link do email (Supabase
    detecta a sessão pelo hash da URL automaticamente), deixa definir senha,
    redireciona pra `/configuracoes/whatsapp`. Se o link já foi usado/
    expirou, orienta login (`/login`) ou pedir novo acesso — antes só dizia
    "convite inválido" sem saída.
  - `lib/server/provisioning-auth.ts` (novo) — checagem de
    `PULSE_PROVISIONING_SECRET`, fail-closed (sem bypass se a env var não
    estiver setada, diferente do `verifyCronSecret`).
  - `tests/onboarding/provision.integration.test.ts` (novo) — 3 testes
    passando contra staging real (rejeita sem segredo, cria tenant/unit/
    membership + `action_link`, idempotência com reenvio de `action_link`
    diferente).

## ⚠️ Pendências reais (não resolvidas)

1. **Deploy do `pulse-app` na Vercel falhou — causa raiz identificada.**
   3 tentativas de `vercel --prod` ficaram "penduradas" em background por
   40+ minutos cada e todas terminaram com o **mesmo erro real**, só visível
   quando o processo finalmente retornou:
   ```json
   { "status": "error", "reason": "deploy_failed", "message": "Not authorized" }
   ```
   Ou seja: não é limite de build concorrente nem demora — é **autorização**
   negada especificamente pro projeto `pulse-app` (a `raiox-mvp-html`
   deployou normal com a mesma conta/CLI na mesma sessão). O usuário viu
   "Blocked" no dashboard, consistente com isso. Hipóteses a checar no
   macbook: permissão da conta/time na Vercel mudou pra esse projeto
   especificamente, alguma integração Git conectada ao projeto conflitando
   com deploy via CLI, ou billing/limite de plano específico do projeto.
   **Próximo passo: abrir
   `vercel.com/jpazevedomoreiraa-1824s-projects/pulse-app`, ver o deploy
   marcado como "Blocked"/"Not authorized" e a razão exata que a Vercel dá
   na UI (geralmente mais detalhada que a CLI), resolver a permissão, tentar
   `vercel --prod` de novo.**
2. **`raiox-mvp-html` já foi deployado com sucesso** (rebranding + checkout
   simulado do Eco no ar em `https://raiox-mvp-html.vercel.app`), mas as
   env vars novas (`PULSE_APP_URL`, `PULSE_PROVISIONING_SECRET`) só fazem
   efeito de verdade quando o deploy do `pulse-app` (item 1) também subir —
   até lá, o botão "Assinar o Eco" da landing vai falhar ao chamar o
   provisionamento (endpoint não existe na versão em produção do app ainda).
3. **Falta configurar a redirect URL no Supabase Auth** (não é possível via
   API/CLI disponível pra mim — só dashboard):
   `Authentication → URL Configuration → Redirect URLs` em
   `https://supabase.com/dashboard/project/fiswngbbjpezivneiete/auth/url-configuration`,
   adicionar `https://pulse-app-steel-tau.vercel.app/convite`. Sem isso, o
   link do email de convite cai em `localhost:3000` em vez do app real —
   confirmado em teste local (o mecanismo funciona, só o redirect erra).
4. Env vars **já configuradas** na Vercel (confirmado nesta sessão):
   - Projeto `pulse-app`: `PULSE_PROVISIONING_SECRET` ✅
   - Projeto `raiox-mvp-html`: `PULSE_APP_URL`, `PULSE_PROVISIONING_SECRET` ✅
     (`CONNECT_INTERNAL_KEY` e `STRIPE_SECRET_KEY` já existiam de antes)
   - Segredo compartilhado (mesmo valor nos dois lados):
     `6e7dab9859fdc6465aa08088a708d6b46007e91769cc19efc8c0bc61e781859f`
     (também salvo em `~/dev/pulse/.env.local` pra dev local)
5. `checkpulse.com.br` está associado (alias) ao projeto `raiox-mvp-html`
   na Vercel, mas **o DNS não resolve** — usuário não tem acesso ao DNS
   desse domínio ainda. Continuar usando as URLs `.vercel.app` até resolver.

## Git — estado dos repos

- **`~/dev/pulse`** — commit `618eddf` pushado pra
  `https://github.com/Grupo-Velas/pulse` (branch `main`, sem pendência).
- **`~/Documents/raiox-mvp-html`** — **nunca tinha git antes desta sessão**.
  Inicializado agora, primeiro commit `d74a85d`, novo repo criado e
  pushado: `https://github.com/Grupo-Velas/raiox-mvp-html`. ⚠️ Continua
  dentro de `~/Documents` (iCloud) — mesmo risco de corrupção já visto 3x
  nesta sessão com Pulse/agent-hub. Considerar mover pra `~/dev/raiox-mvp-html`
  como já foi feito com os outros dois, numa sessão futura.

## Próximos passos recomendados (ordem)

1. Resolver o deploy travado do `pulse-app` (item 1 acima).
2. Confirmar que `pulse-app-steel-tau.vercel.app` está servindo o build
   novo (`/api/onboarding/provision` deve responder 401 sem segredo, não
   404).
3. Adicionar a redirect URL no Supabase (item 3).
4. Testar o fluxo real: `comprar-eco.html` → email chega → link funciona →
   define senha → cai em `/configuracoes/whatsapp`.
5. Mover `raiox-mvp-html` pra fora do iCloud (`~/dev/raiox-mvp-html`), igual
   já foi feito com `pulse` e `agent-hub`.
6. Fase 4 do plano original do Pulse (corte de produção) continua pendente,
   agora com o onboarding comercial pronto pra alimentar tenants reais.
