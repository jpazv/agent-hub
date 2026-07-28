# Handoff — Pulse: Postgres puro Fase A iniciada

**Data:** 2026-07-28  
**Maquina:** mac-grupovelas  
**Repo:** `/Users/grupovelas/dev/pulse`  
**Base:** handoff `2026-07-28-migracao-postgres-puro.md`

---

## O que foi feito

### 1. `CRON_SECRET` corrigido para fail-closed

Commit no `pulse`:

```text
1af1740 fix: fail closed cron secret verification
```

Mudancas:

- `lib/server/cron-auth.ts` nao aceita mais ausencia de `CRON_SECRET`.
- Comparacao do bearer token agora usa `crypto.timingSafeEqual`.
- Adicionado `tests/cron/cron-auth.test.ts`.
- Ajustado `tests/cron/rollup-daily.integration.test.ts` para enviar secret
  correto nos casos positivos e cobrir rejeicao sem env.

Importante operacional:

- Antes de deployar esse commit em ambiente onde crons reais rodam,
  `CRON_SECRET` precisa estar configurado na Vercel.
- Sem essa env, os crons passam a retornar 401 de proposito.

### 2. Fundacao Postgres puro criada

Commit no `pulse`:

```text
ff38645 feat: add postgres migration foundation
```

Mudancas:

- Adicionado `pg` e `@types/pg`.
- Criado `lib/server/db.ts`:
  - Pool singleton com `DATABASE_URL`.
  - Parser de `int8` para number.
  - Parser de `date`, `timestamp` e `timestamptz` para string.
  - `numeric` fica default do driver (`string`), para casts explicitos no SQL.
- Criado `scripts/migrate.mjs`:
  - Le `database/migrations/*.sql`.
  - Valida nomes com regex `0001_nome.sql`.
  - Usa `app_internal.schema_migrations`.
  - Usa checksum SHA-256 e falha se migration aplicada mudar.
  - Usa advisory lock transacional.
- Adicionado script:

```text
npm run db:migrate
```

- Criada baseline:

```text
database/migrations/0001_baseline.sql
```

Baseline remove dependencias Supabase:

- Sem `auth.users`.
- Sem RLS.
- Sem policies.
- Sem `supabase_vault`.
- Sem `pg_net` / `pg_cron`.

Baseline inclui:

- `app_auth.users`
- `app_auth.sessions`
- `tenants`
- `units`
- `tenant_members`
- `whatsapp_connections`
- `secretaries`
- `conversations`
- `messages`
- `tpr_daily_rollup`
- `alert_recipients`
- `alerts_sent`
- `data_deletion_requests`
- `set_whatsapp_secret`
- `get_whatsapp_secret`
- `conversas_para_scorear`
- `rede_stats`

Segredos WhatsApp:

- `access_token_ciphertext bytea`
- `register_pin_ciphertext bytea`
- Cifra via `pgcrypto`.
- Chave vem de `current_setting('pulse.secrets_key', true)`.
- App deve setar a chave por transacao antes de chamar funcoes de segredo.

---

## Validacao feita

No repo `pulse`:

```text
npm test -- tests/cron/cron-auth.test.ts
npx tsc --noEmit
node --check scripts/migrate.mjs
npm test
```

Resultado:

```text
8 test files passed, 12 skipped
63 tests passed, 45 skipped
typecheck passou
```

Os testes de integracao continuam pulados sem env de staging, como antes.

---

## Estado local observado

O repo `pulse` ainda tem mudancas nao feitas nesta sessao, preservadas fora
dos commits:

- Auth/UI/dashboard/client API modificados.
- Novos arquivos em `app/(auth)/entrando/`, `app/api/auth/`, `tests/auth/`.
- Docs de proposta/email parceiro.

Nao foram revertidas nem commitadas por esta sessao.

---

## Proximos passos recomendados

1. Configurar `CRON_SECRET` na Vercel antes de deployar os commits.
2. Rodar `npm run db:migrate` contra um Postgres descartavel primeiro.
3. Se a baseline aplicar limpa, criar `DATABASE_URL` real do RDS.
4. Comecar Fase B pela camada de dados mais central:
   - helpers de query/seed/sessao para testes.
   - `requireTenant` e teste de isolamento entre tenants.
   - rotas de dashboard com risco de IDOR.
5. Portar `meta-secrets.ts` para usar `pgcrypto` com chave por transacao.

---

## Alertas tecnicos

- A baseline ainda nao foi executada contra um Postgres real nesta sessao
  porque nao havia `DATABASE_URL` fornecida.
- `npm install` reportou 14 vulnerabilidades no grafo de dependencias
  (2 moderate, 12 high). Nao foi rodado `npm audit fix`, para evitar mudancas
  indiretas fora do escopo.
- O corte para Postgres puro ainda nao removeu Supabase do codigo de runtime.
  Isso e esperado: Fase A criou fundacao; Fase B porta chamadas `.from(...)`.
