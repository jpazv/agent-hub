# Handoff — Pulse: baseline Postgres validada em Docker

**Data:** 2026-07-28  
**Maquina:** mac-grupovelas  
**Repo:** `/Users/grupovelas/dev/pulse`  
**Container:** `pulse-postgres-test`

---

## O que foi feito

Subido Postgres local em Docker:

```bash
docker run --name pulse-postgres-test \
  -e POSTGRES_USER=pulse \
  -e POSTGRES_PASSWORD=pulse \
  -e POSTGRES_DB=pulse \
  -p 5432:5432 \
  -d postgres:16
```

Validado readiness:

```bash
docker exec pulse-postgres-test pg_isready -U pulse -d pulse
```

Resultado:

```text
/var/run/postgresql:5432 - accepting connections
```

---

## Migration executada

Comando:

```bash
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npm run db:migrate
```

Resultado:

```text
Applying 0001_baseline.sql
```

Executado uma segunda vez para validar idempotencia/checksum. Segunda execucao
nao reaplicou a migration e terminou sem erro.

---

## Verificacoes no banco

Tabela de migrations:

```text
filename          | checksum_len
------------------+-------------
0001_baseline.sql | 64
```

Schemas/tabelas:

```text
app_auth     | 2
app_internal | 1
public       | 11
```

---

## Teste de pgcrypto

Criados tenant, unit e whatsapp_connection de teste.

Executado em transacao:

```sql
select set_config('pulse.secrets_key', 'chave-local-teste', true);
select set_whatsapp_secret('<connection_id>', 'access_token', 'token-secreto');
select get_whatsapp_secret('<connection_id>', 'access_token');
```

Resultado:

```text
token-secreto
```

Conclusao: funcoes `set_whatsapp_secret` e `get_whatsapp_secret` funcionam
com chave injetada por transacao via `set_config(..., true)`.

---

## Estado

Baseline Postgres puro esta validada em banco descartavel local.

## Continuidade — Fase B

### Subpasso 1 — leitura de isolamento/IDOR

Lidos:

- `lib/server/auth.ts`
- `lib/server/require-tenant.ts`
- `app/api/dashboard/conversa/route.ts`
- `app/api/dashboard/enviar-mensagem/route.ts`
- `tests/auth/vincular.integration.test.ts`

Achados:

- `requireTenant` ainda retorna o primeiro tenant do usuario autenticado.
- `conversa` filtra a conversa por `id + tenant_id`, mas a busca de mensagens
  usa apenas `conversation_id`.
- `enviar-mensagem` filtra a conversa por `id + tenant_id`, mas consultas/
  updates derivados ainda podem ganhar filtros redundantes por `tenant_id`
  para reduzir risco de IDOR quando a RLS sair.

### Subpasso 2 — hardening IDOR inicial

Arquivos alterados no `pulse`:

- `app/api/dashboard/conversa/route.ts`
- `app/api/dashboard/enviar-mensagem/route.ts`

Mudancas:

- Busca de mensagens da conversa agora filtra tambem por `tenant_id`.
- Busca de `whatsapp_connections` em envio manual agora filtra tambem por
  `tenant_id`.
- Releitura de mensagens para score agora filtra tambem por `tenant_id`.
- Update final de `conversations` em envio manual agora usa
  `id + tenant_id`.

Commit:

```text
6b1691c fix: tighten tenant filters on dashboard actions
```

Validacao:

```text
npx tsc --noEmit
npm test -- tests/cron/cron-auth.test.ts
```

Resultado: ambos passaram.

### Subpasso 3 — hardening de thresholds de alerta

Arquivo alterado no `pulse`:

- `app/api/alertas/thresholds/route.ts`

Mudanca:

- Update de `units.alert_thresholds_min` agora usa `id + tenant_id`.
- A rota ja validava a unidade por tenant antes; o update ficou redundante e
  defensivo para o cenario sem RLS.

Commit:

```text
c3f3894 fix: scope alert threshold updates by tenant
```

Validacao:

```text
npx tsc --noEmit
npm test -- tests/cron/cron-auth.test.ts
```

Resultado: ambos passaram.

### Subpasso 4 — teste mocado de escopo por tenant

Arquivo adicionado no `pulse`:

- `tests/dashboard/tenant-scope.test.ts`

Cobertura:

- `app/api/dashboard/conversa/route.ts`: garante que a query de `messages`
  usa `conversation_id + tenant_id`.
- `app/api/alertas/thresholds/route.ts`: garante que o update de `units`
  usa `id + tenant_id`.

Objetivo:

- Travar em teste unitario o padrao de isolamento que vai substituir a RLS
  quando a camada Supabase sair.

Commit:

```text
ee2fd69 test: cover tenant scope guards
```

Validacao:

```text
npm test -- tests/dashboard/tenant-scope.test.ts
npx tsc --noEmit
npm test
```

Resultado:

```text
9 test files passed, 12 skipped
65 tests passed, 45 skipped
typecheck passou
```

### Subpasso 5 — helper Postgres para segredos WhatsApp

Arquivos alterados/adicionados no `pulse`:

- `lib/server/db.ts`
- `lib/server/pg-meta-secrets.ts`
- `tests/server/pg-meta-secrets.integration.test.ts`

Mudancas:

- Criado helper paralelo `getWhatsappSecretPg` / `setWhatsappSecretPg`.
- Helper usa `PULSE_SECRETS_KEY` fora do banco.
- A chave e injetada por transacao com
  `set_config('pulse.secrets_key', $1, true)`.
- `lib/server/db.ts` ganhou `closePool()` para encerrar conexoes em testes.
- Runtime atual ainda nao foi trocado: `meta-secrets.ts` Supabase continua em
  uso ate as rotas serem portadas para `pg`.

Commit:

```text
78aef9e feat: add postgres whatsapp secret helpers
```

Validacao:

```text
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npm test -- tests/server/pg-meta-secrets.integration.test.ts
npx tsc --noEmit
npm test
```

Resultado:

```text
pg-meta-secrets integration: 2 passed
suite comum: 9 passed, 13 skipped
65 tests passed, 47 skipped
typecheck passou
```

Proximo passo recomendado:

1. Comecar Fase B pela camada de dados e testes de isolamento:
   - helper de tenant/sessao.
   - teste garantindo que uma request de tenant A nao acessa dados do tenant B.
2. Portar rotas com maior risco de IDOR primeiro:
   - `app/api/dashboard/conversa/route.ts`
   - `app/api/dashboard/enviar-mensagem/route.ts`
   - `app/api/alertas/thresholds/route.ts`
3. Portar `lib/server/meta-secrets.ts` para Postgres/pgcrypto usando
   `PULSE_SECRETS_KEY`.

---

## Comandos uteis

Parar container:

```bash
docker stop pulse-postgres-test
```

Remover container:

```bash
docker rm pulse-postgres-test
```

Conectar via psql:

```bash
docker exec -it pulse-postgres-test psql -U pulse -d pulse
```
