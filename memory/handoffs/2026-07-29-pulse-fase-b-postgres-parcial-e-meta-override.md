# Handoff — Pulse: Fase B Postgres parcial + possível mudança para onboarding Meta override

**Data:** 2026-07-29  
**Maquina:** mac-grupovelas  
**Repo:** `/Users/grupovelas/dev/pulse`  
**Branch:** `main`  
**Estado git Pulse:** working tree limpo, `main` à frente de `origin/main` por 21 commits  
**Estado git hub:** havia alteração local anterior em `memory/handoffs/2026-07-28-pulse-postgres-docker-baseline-validada.md`; este handoff foi criado sem tocar nela.

---

## Contexto

Sessão focada em cumprir a Fase B da migração Supabase -> Postgres puro
para o Pulse Eco, com Postgres local já rodando em Docker:

```text
postgres://pulse:pulse@localhost:5432/pulse
```

O usuário sinalizou no fim que possivelmente vamos mudar algumas coisas para
deixar pronto o onboarding em outro app já registrado na Meta usando override
URL. Portanto, a próxima sessão pode não continuar diretamente nos crons
restantes; pode priorizar Embedded Signup/onboarding Meta.

---

## O que foi feito nesta sessão

### Dashboard e rotas operacionais portadas para `pg`

Commits:

```text
8edcbe0 feat: port dashboard overview to pg
72e66d0 feat: port dashboard conversations to pg
23054c8 feat: port dashboard conversation detail to pg
bad9f7c feat: port manual message sending to pg
6ea17c0 feat: port alert thresholds to pg
ddff27a feat: port alert settings to pg
ff7dcce feat: port secretaries to pg
4364f6d feat: port dashboard network trends to pg
```

Principais rotas/helpers agora em Postgres:

- `app/api/dashboard/espera/route.ts` (feito antes desta sessão, commit `f178496`)
- `app/api/dashboard/overview/route.ts`
- `app/api/dashboard/conversas/route.ts`
- `app/api/dashboard/conversa/route.ts`
- `app/api/dashboard/enviar-mensagem/route.ts`
- `app/api/alertas/thresholds/route.ts`
- `app/api/alertas/route.ts`
- `app/api/alertas/recipients/route.ts`
- `app/api/alertas/recipients/[id]/route.ts`
- `app/api/secretarias/route.ts`
- `app/api/secretarias/[id]/route.ts`
- `app/api/dashboard/trend/route.ts`
- `app/api/dashboard/rede/route.ts`
- `lib/server/live-stats.ts`

### Caminho tempo real do lead portado

Commit:

```text
23e87f6 feat: port webhook processing to pg
```

Arquivo:

- `lib/server/webhook-processing.ts`

O webhook agora usa `pg` para:

- localizar conexão por `phone_number_id`;
- criar/reusar conversa por `unit_id + lead_wa_id`;
- gravar mensagem idempotente por `wa_message_id`;
- recalcular score do lead em tempo real quando há consentimento;
- atualizar status de entrega;
- atualizar resposta de botão `compareceu`;
- usar `getWhatsappSecretPg` para áudio/transcrição.

### Crons já portados

Commits:

```text
76bdd56 feat: port daily rollup cron to pg
faeef16 feat: port lead scoring cron to pg
c601d56 feat: port appointment detection cron to pg
```

Crons portados:

- `app/api/cron/rollup-daily/route.ts`
- `app/api/cron/score-leads/route.ts`
- `app/api/cron/detect-agendamentos/route.ts`

Observação importante: o fluxo principal de análise de lead é o webhook em
tempo real. `score-leads` é rede de segurança para conversas onde
`scored_at` ficou ausente ou mais antigo que `ultima_mensagem_em`.

### Commit de front de outra sessão preservado

Commit do Claude no meio da fila:

```text
3a237e9 Front: responsividade mobile, redesenho de alertas e login com Google
```

Ele foi mantido. Não houve conflito real de branch; apenas reconciliação no
working tree.

---

## Testes novos adicionados

Integrações Postgres adicionadas:

- `tests/dashboard/overview-pg.integration.test.ts`
- `tests/dashboard/conversas-pg.integration.test.ts`
- `tests/dashboard/conversa-pg.integration.test.ts`
- `tests/dashboard/enviar-mensagem-pg.integration.test.ts`
- `tests/alertas/thresholds-pg.integration.test.ts`
- `tests/alertas/alertas-pg.integration.test.ts`
- `tests/secretarias/secretarias-pg.integration.test.ts`
- `tests/dashboard/trend-rede-pg.integration.test.ts`
- `tests/webhook/webhook-pg.integration.test.ts`
- `tests/cron/rollup-daily-pg.integration.test.ts`
- `tests/cron/score-leads-pg.integration.test.ts`
- `tests/cron/detect-agendamentos-pg.integration.test.ts`

Validações feitas ao longo da sessão:

```text
npx tsc --noEmit
npm test
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npm test -- <teste pg focado>
```

Última suíte comum observada antes dos commits finais:

```text
9 test files passed, demais integrações sem env foram skipped
```

---

## Onde estamos na Fase B

Fase A: concluída.  
Fase B: em andamento, bem avançada.  
Fase C auth própria: ainda não começou.

### Ainda usa Supabase / pendente na Fase B

Crons restantes:

- `app/api/cron/check-alerts/route.ts`
- `app/api/cron/ask-compareceu/route.ts`

Onboarding/Meta/WhatsApp:

- `app/api/onboarding/units/route.ts`
- `app/api/onboarding/whatsapp-connect/route.ts`
- `app/api/onboarding/provision/route.ts`
- `app/api/onboarding/signup/route.ts`

Auth atual ainda Supabase:

- `lib/server/auth.ts`
- `app/api/auth/vincular/route.ts`
- front/client auth (`lib/client/api.ts`, `lib/supabase-browser.ts`, `lib/client/use-session.ts`, páginas auth)

Legado de secrets Supabase:

- `lib/server/meta-secrets.ts`
- `lib/server/supabase-admin.ts`

Esses só devem sair de vez quando todos os chamadores tiverem sido portados.

---

## Próxima decisão provável

O usuário indicou:

> possivelmente vamos mudar algumas coisas pq precisamos deixar pronto pro onboarding em outro app ja registrado na meta usando override url

Antes de continuar mecanicamente os crons, a próxima sessão deve confirmar a
prioridade:

1. Continuar Fase B pelos crons restantes (`check-alerts`, `ask-compareceu`).
2. Ou mudar o foco para onboarding/Embedded Signup Meta com outro app já
   registrado e override URL.

Se for onboarding Meta, ler primeiro:

- `app/api/onboarding/whatsapp-connect/route.ts`
- `app/api/onboarding/provision/route.ts`
- `app/api/onboarding/signup/route.ts`
- `lib/server/meta-auth.ts`
- `tests/onboarding/whatsapp-connect.integration.test.ts`
- handoff anterior sobre Embedded Signup/Meta:
  `memory/handoffs/2026-07-27-pulse-embedded-signup-e-proposta-parceiro.md`

Também lembrar do contexto global:

- Embedded Signup estava bloqueado por Advanced Access da Meta.
- Havia achado de webhook override/proposta ao parceiro no handoff de
  2026-07-27.
- O usuário agora menciona outro app já registrado na Meta usando override URL,
  o que pode mudar a estratégia.

---

## Não fazer sem confirmar

- Não fazer deploy.
- Não alterar env vars de produção/Vercel.
- Não trocar webhook URL/override URL na Meta sem pedido explícito.
- Não fazer push automático sem o usuário pedir.
- Não iniciar Fase C auth própria antes de fechar/decidir onboarding e os
  pontos restantes da Fase B.

---

## Próximos comandos úteis

Ver estado:

```bash
cd /Users/grupovelas/dev/pulse
git status --short --branch
git log --oneline -20
```

Rodar validação geral:

```bash
npx tsc --noEmit
npm test
```

Rodar integrações Postgres focadas:

```bash
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npm test -- tests/webhook/webhook-pg.integration.test.ts
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npm test -- tests/cron/detect-agendamentos-pg.integration.test.ts
```
