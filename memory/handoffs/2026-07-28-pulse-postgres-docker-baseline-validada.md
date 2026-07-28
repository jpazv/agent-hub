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
