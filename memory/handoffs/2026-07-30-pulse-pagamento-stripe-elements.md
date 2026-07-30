# Handoff — Pulse: Pagamento Stripe Elements (white-label)

**Data:** 2026-07-30  
**Repo:** `~/dev/pulse`  
**Próxima máquina:** macbook-jpazv

---

## Decisão tomada

Checkout white-label com **Stripe + Stripe Elements**.

**Por quê:**
- Cliente nunca vê "Stripe" — formulário de cartão renderiza no domínio `pulse.grupovelas.com.br`
- Stripe.js tokeniza o cartão direto no browser (PCI compliance — número nunca passa pelo servidor)
- Suporta BRL, assinaturas recorrentes nativas, webhook confiável com HMAC
- Conta ativa em minutos (sem processo comercial como Iugu)

---

## O que já existe no repo

- `database/migrations/0007_iugu_subscription.sql` — adiciona `iugu_customer_id` e `iugu_subscription_id` nos tenants. **Reaproveitar** renomeando para `stripe_customer_id` e `stripe_subscription_id` (ou criar 0008 que altera as colunas).
- `lib/server/iugu.ts` — cliente Iugu. **Substituir** por `lib/server/stripe.ts`.
- `app/api/webhooks/iugu/route.ts` — webhook handler Iugu. **Substituir** por `app/api/webhooks/stripe/route.ts`.

---

## O que precisa ser construído

### 1. Conta e configuração Stripe

- Criar conta em stripe.com (sem processo comercial, ativa na hora)
- Pegar `STRIPE_SECRET_KEY` (server) e `STRIPE_PUBLISHABLE_KEY` (client — `NEXT_PUBLIC_`)
- Criar produto + plano recorrente mensal no Stripe Dashboard → Products
- Anotar o `price_id` do plano (ex: `price_xxx`) — usado na criação da subscription
- Configurar webhook no Stripe Dashboard → Developers → Webhooks:
  - URL: `https://pulse.grupovelas.com.br/api/webhooks/stripe`
  - Eventos: `invoice.payment_succeeded`, `invoice.payment_failed`, `customer.subscription.deleted`, `customer.subscription.updated`
  - Pegar o `STRIPE_WEBHOOK_SECRET` (começa com `whsec_`)

### 2. Migration `0008_stripe_subscription.sql`

```sql
ALTER TABLE tenants
  RENAME COLUMN iugu_customer_id     TO stripe_customer_id;
ALTER TABLE tenants
  RENAME COLUMN iugu_subscription_id TO stripe_subscription_id;
```

### 3. `lib/server/stripe.ts`

```typescript
import Stripe from "stripe";
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: "2024-06-20" });

// createCustomer(email, name) → stripe.customers.create
// createSubscription(customerId, priceId) → stripe.subscriptions.create
// createPaymentIntent ou createSetupIntent para capturar cartão
```

Instalar: `npm install stripe`

### 4. `app/api/checkout/create-subscription/route.ts`

Fluxo server-side:
1. Recebe `{ email, nome_clinica, payment_method_id }` do front
2. Cria ou recupera customer no Stripe por email
3. Atualiza `defaultPaymentMethod` do customer
4. Cria subscription com `payment_behavior: "default_incomplete"` → retorna `client_secret`
5. Front usa `stripe.confirmCardPayment(client_secret)` para confirmar

### 5. Página de checkout `app/(public)/assinar/page.tsx`

- Rota pública (fora do dashboard auth)
- Carrega Stripe.js via `@stripe/stripe-js` + `@stripe/react-stripe-js`
- `<CardElement>` ou `<PaymentElement>` do Stripe — aparece como campo do seu site
- Formulário: Nome, Email, campo de cartão, botão "Assinar"
- Ao confirmar: chama `/api/checkout/create-subscription` → recebe `client_secret` → `stripe.confirmCardPayment()`
- Sucesso: mostra tela de "aguardando confirmação" (webhook vai provisionar)

### 6. `app/api/webhooks/stripe/route.ts`

Stripe assina webhooks com HMAC — verificar com `stripe.webhooks.constructEvent(body, sig, STRIPE_WEBHOOK_SECRET)`.

| Evento | Ação |
|---|---|
| `invoice.payment_succeeded` + subscription nova | Provisionar tenant + enviar email de acesso |
| `invoice.payment_succeeded` + subscription existente (renovação) | `status = active` |
| `invoice.payment_failed` | `status = paused` |
| `customer.subscription.deleted` | `status = canceled` |
| `customer.subscription.updated` | Atualizar conforme novo status |

---

## Variáveis de ambiente novas

| Variável | Tipo | Descrição |
|---|---|---|
| `STRIPE_SECRET_KEY` | Secrets Manager | `sk_live_...` (prod) / `sk_test_...` (dev) |
| `STRIPE_WEBHOOK_SECRET` | Secrets Manager | `whsec_...` — gerado no Stripe Dashboard |
| `STRIPE_PRICE_ID` | Secrets Manager | `price_...` — ID do plano mensal |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | `.env.production` (build time) | `pk_live_...` |

---

## Pacotes a instalar

```bash
npm install stripe @stripe/stripe-js @stripe/react-stripe-js
```

---

## Ordem de implementação recomendada

1. Criar conta Stripe + produto + plano + webhook → pegar as 4 variáveis acima
2. `npm install stripe @stripe/stripe-js @stripe/react-stripe-js`
3. Migration 0008 (renomear colunas iugu → stripe)
4. `lib/server/stripe.ts`
5. `app/api/checkout/create-subscription/route.ts`
6. `app/(public)/assinar/page.tsx` com Stripe Elements
7. `app/api/webhooks/stripe/route.ts`
8. Testar fluxo completo com cartão de teste Stripe (`4242 4242 4242 4242`)

---

## Contexto da sessão anterior

- Auth Postgres puro concluído (sem Supabase)
- Banco Neon configurado em dev (`ep-withered-cherry-aclgcbg7-pooler.sa-east-1.aws.neon.tech`)
- Migrations 0001–0007 aplicadas no Neon
- Fluxo completo validado: landing → provision → convite → dashboard
- Google OAuth corrigido (JWKS verify)
- Crons: todos 8 adicionados ao `vercel.json` (6 nunca tinham rodado)
- Variáveis de ambiente completas documentadas em `2026-07-30-pulse-variaveis-ambiente.md`
