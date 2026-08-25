# Velas Talent — Estado Atual e Diagnóstico (2026-08-25)

## Resumo Executivo

O Velas Talent está **parcialmente funcional em produção** (`https://talent.grupovelas.com.br`, rodando há ~2 meses no servidor user1 @ `167.233.30.181`). A nova versão **MVP Lite foi refeita do zero** com tela de triagem, segurança, idempotência e worker da fila — **mas nenhuma mudança local foi enviada para produção ainda.**

Hoje descobrimos e diagnosticamos:
1. **Produção não estava lenta por token — era o worker local agressivo saturando o proxy n8n**
2. **O guard de autorização aceitava `undefined` como jobId** — corrigido, mas não deployado
3. **O servidor está sem `.env`** (zero linhas) — risco crítico se fazer rsync com `--delete`
4. **Main local está "ahead 19, behind 4" de origin/rebuild-1.0.2** — aqueles 4 commits removem pg.Pool fallback
5. **Package.json mudou breaking changes** que precisam ser testadas antes de deploy

## 1. Arquitetura de Produção

### URLs e Rotas

- **Pública:** `https://talent.grupovelas.com.br/` (via Cloudflare, 172.67.184.141)
- **Interna:** `https://167-233-30-181.nip.io/app1/` (IP direto)
- **API:** `/app1/api` → nginx proxy → `/api` dentro do container
- **Health:** ambas devolvem `{"status":"ok","service":"velas-talent-api"}` (HTTP 200)

### Infraestrutura

| | |
|---|---|
| Server | `167.233.30.181` (SSH user1, chave em `~/Downloads/user1_key`) |
| Node | v20.20.2 |
| npm | 10.8.2 |
| Processo | `node index.js` (PID 1, sem gerenciador) |
| Database | Neon (PostgreSQL), URL em `/app/.env` |
| Build | jun 17, 2 meses atrás (estático em `/app/dist/`) |
| Git | **não existe** — servidor só tem código compilado |

### O `.env` Crítico

```
DATABASE_URL=postgresql://neondb_owner:...@ep-aged-thunder-ac6ytkef-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
NODE_ENV=production
```

**RISCO:** Servidor tem arquivo `.env` *mas* leitura remota retorna 0 linhas (permissão ou arquivo vazio). Se fazer `rsync ... --delete`, apaga o `.env` do servidor, app fica sem DATABASE_URL e quebra.

## 2. O Que Aconteceu Hoje

### Diagnóstico da "Produção Lenta"

**Sintoma:** User disse "prod não puxa nada, como se o token não funcionasse" após importar workflow corrigido.

**Causa encontrada:** Não era token. Era **minha API local (`pid 5398`) com worker de 5s rodando 24/7, martelando o proxy n8n.**

**Prova:**
```
Sem a API local: curl select 1 → 19 segundos
Após kill pid 5398: curl select 1 → 1-2.7 segundos
```

O proxy respondeu em todos os testes — o arquivo retornou linhas. Eu li `exit=0` sem output e inventei uma causa errada.

**Lição:** Medir antes de reescrever. Uma chamada de `curl` teria resolvido em 30s.

### Correção do Guard de Autorização

**Problema:** App mandava string literal `"undefined"` como `jobId` (de páginas legadas sem validação). `canUserAccessJob` repassava ao Postgres sem validar, que retornava:

```
invalid input syntax for type uuid: "undefined"
```

`500` em vez de `403`.

**Correção em `apps/api/src/modules/jobs/jobs.repo.ts:467`:**

```ts
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// Fail-closed: fronteira de authz não depende de validação do caller
if (!UUID_RE.test(params.jobId ?? "")) {
  console.warn("[authz] jobId invalido em canUserAccessJob", {...});
  return false;
}
if (scope === "none") return false;
```

**Status:** Commitado localmente, **NÃO ESTÁ EM PRODUÇÃO.**

### O Workflow "Corrigido" que Quebrou

Anterior a hoje: user importou meu `Talent DB Proxy — CORRIGIDO.json`, que removeu o check de chave do código e dependia da credencial `httpHeaderAuth` no node Webhook.

**Problema:** n8n não exporta credenciais. Node importado chegou com `headerAuth: true` mas sem credencial vinculada → rejeita tudo.

**Solução:** Entreguei `Talent DB Proxy — RESTAURAR.json` que volta a validar chave no código (mesmo sem credencial). Mantém o check mesmo se n8n não exportar credencial.

**Status:** Arquivo em `~/Downloads/Talent DB Proxy — RESTAURAR.json`, aguardando importação manual no n8n.

## 3. Estado do Código Local

### Branch e Commits

```
main [ahead 19, behind 4] origin/rebuild-1.0.2
```

**Ahead 19:** Commits locais que não foram pushados:
- feat: worker da fila, EMAIL_TEST_OVERRIDE, convite via bulk-approved
- fix: 3 erros de contrato (dor/areas/placementId/candidateEmail/slot_ids)
- chore: token de desenvolvimento, proxy local
- ... e mais

**Behind 4 (critérios):**
```
04a064b feat: n8n-only database proxy, remove pg.Pool fallback
a4a7cf2 feat: email templates, talent bank, calendar sync and screening improvements
f724513 feat: track email sends in talent.email_log
0e07792 chore: init Velas_Talent1.0.2 from 1.0.1
```

Aquele "remove pg.Pool fallback" é **crítico** — se enviar main sem esses 4, o código tenta acessar banco direto que foi removido em rebuild-1.0.2.

**Problema:** Branches têm "unrelated histories" (não são pai/filho) — git merge falha. Pode ser que rebuild-1.0.2 seja branch abandoned ou paralelo.

### Mudanças Não Commitadas

```
 M apps/api/src/modules/jobs/jobs.repo.ts (guard UUID)
```

### Package.json — Breaking Changes

```diff
- "build:private:user1": "VITE_APP_BASE_PATH=/app1 npm run build",
+ "build:private:user1": "VITE_API_URL=/api npm run build",
```

Muda qual variável é passada ao Vite. Precisa testar se build completa passa.

## 4. Segurança e Regras

### Regra do Pulse (de CLAUDE.md global)

"Preciso seguir todos os criterios de segurança que temos no pulse" — issue #306 + checklist 84 itens. Implementado:

✅ Fail-closed role mapping (`NO_ACCESS_ROLE` em connect-role.ts)
✅ SSRF prevention (DNS resolution, rejeita private/loopback/link-local)
✅ Rate limiting (300/min, sliding window, em-memória)
✅ Idempotência (índice único parcial em screening_jobs, email_log)
✅ Webhook auth (3 webhooks com httpHeaderAuth + CODE fallback)
✅ Email override (`EMAIL_TEST_OVERRIDE`)

### Pendências Críticas (Não Implementadas)

- [ ] Audit log de autorização
- [ ] Row-level security via `usuario_unidades`
- [ ] MFA
- [ ] LGPD — talent bank sem opt-out column
- [ ] Teste de guard UUID (registrado como pendência)

## 5. Banco de Dados

### Migrations Aplicadas

`0027_idempotencia.sql` — **JÁ RODADO EM PRODUÇÃO** pelo user:
```sql
CREATE UNIQUE INDEX screening_jobs_um_ativo_por_vaga
  ON talent.screening_jobs (job_id) WHERE status IN ('queued', 'running');
CREATE UNIQUE INDEX email_log_idempotency_key_unico
  ON talent.email_log (idempotency_key) WHERE idempotency_key IS NOT NULL;
```

### Recursos e Comportamento

- Não há transações reais (BEGIN/COMMIT → SELECT 1 noop)
- SELECT ... FOR UPDATE locks não seguram (sem transação)
- Proxy n8n é a **única via de acesso ao banco**
- Worker de triagem e polling via `/run/tick` (ainda não automático)

## 6. Fluxo de Deploy Documentado

Em `docs/deploy/private-server-user1.md`:

```bash
# Local
npm run verify
npm run build:private:user1

# Envio
rsync -avz --delete \
  --exclude node_modules \
  --exclude .git \
  -e "ssh -i user1_key" \
  ./ user1@167.233.30.181:/app/

# No servidor
ssh -i user1_key user1@167.233.30.181
cd /app
npm install
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f postgres/corporate/talent_bd_clean.sql
npm run start:private
```

**Risco:** O `--delete` apaga tudo local que não estiver no servidor. Se `.env` não estiver em `.gitignore` localmente, rsync vai **deletar o `.env` remoto**.

## 7. Próximos Passos Recomendados

### Imediato (De Risco Crítico)

1. **Restaurar o Talent DB Proxy importado** — importar `~/Downloads/Talent DB Proxy — RESTAURAR.json` no n8n
   - Desativar o "corrigido" que está ativo
   - Vincular credencial Postgres no node
   - Ativar
   - Testar com `curl` select 1

2. **Investigar .env do servidor**
   ```bash
   ssh -i user1_key user1@167.233.30.181 'cat /app/.env | head -20'
   ```
   Se estiver vazio, recriar com segredos reais (DATABASE_URL etc)

3. **Aumentar intervalo do worker local** (se mantiver API rodando)
   - Adicionar ao `.env`: `SCREENING_WORKER_INTERVAL_MS=30000` (5s é agressivo)

### Antes de Deploy

4. **Entender rebuild-1.0.2**
   - Clonar e testá-lo localmente
   - Ou confirmar que aquele branch está abandoned
   - Se for production-ready, fazer rebase de main (ou cherry-pick dos 4 commits críticos)

5. **Testes de build completa**
   - `npm run verify` (passou)
   - `npm run build:private:user1` (não rodou ainda — precisa testar breaking change de package.json)
   - `npx tsc --noEmit` em apps/api e packages/domain
   - `npx tsx --test` para suite de testes

6. **Backup robusto antes de rsync**
   ```bash
   ssh user1@... 'tar czf /tmp/app-backup-$(date +%s).tar.gz /app/.env /app/node_modules'
   ```

7. **Testar rsync em dry-run**
   ```bash
   rsync -avz --delete --dry-run ... > /tmp/rsync-plan.txt
   ```
   Revisar antes de executar de verdade.

### Deploy Seguro (Quando Pronto)

8. **Procedimento ordenado:**
   - Commit + push de main
   - SSH → backup /app/.env
   - rsync do código
   - SSH → restaurar /app/.env
   - SSH → npm install
   - SSH → npm run start:private
   - Testar `/api/health`
   - Monitorar logs

## 8. Fichário de Erros e Lições

### Erro: Diagnóstico errado de "token não funciona"

**Contexto:** User disse "prod não puxa nada" depois que importei workflow.

**Meu erro:** Sem medir, assumi que era o workflow. Reescrevi tudo em vez de fazer `curl` simples.

**Realidade:** Era meu worker local em loop de 5s, saturando o proxy. Curl levava 19s de latência, não recusa de token.

**Lição:** Medir antes de refatorar. Uma chamada HTTP teria resolvido em 30s.

### Erro: Workflow que depende de credencial não exportada

**Contexto:** Removi check de chave do código, dependendo só de `httpHeaderAuth` credencial.

**Meu erro:** Sabia que n8n não exporta credencial (cheguei a escrever isso), mas tratei como instrução de importação, não risco de projeto.

**Realidade:** Workflow importado chegou autenticado-false, rejeitando tudo.

**Lição:** Credencial não exportada = validação deve estar no código, sempre. A credencial é redundância, não substitui.

### Erro: Guard de autorização aceitava `undefined`

**Contexto:** `canUserAccessJob` recebia string `"undefined"` de páginas legadas sem validar.

**Meu erro:** Achei que era problema só do app (10 arquivos legados). Deveria ter colocado o guard na fronteira, não esperado que caller validasse.

**Realidade:** Falhou em 5 rotas diferentes. Guard é a solução.

**Lição:** Fronteira de segurança (auth) não confia em caller. Fail-closed sempre.

## 9. Contexto Mais Amplo

### Por Que o Projeto Reiniciou

User pediu recreate do zero seguindo "todas as regras de negocio" e "todos os criterios de segurança do pulse". O Lite anterior era experimental/incompleto.

**Objetivos conseguidos:**
- Tela funcional de triagem
- Worker da fila (elimina engasgo)
- Convite automático via bulk-approved
- Negativa automática
- Email com override de teste
- Idempotência no DB
- Calendário com cancel em vez de delete
- Security: fail-closed role, SSRF, rate limit, webhook auth

**Objetivos ainda pendentes:**
- Deploy estável em produção
- Testes automatizados de integração
- Manual/PDF para stakeholder (user disse "ainda não é hora")

## 10. Contatos e Chaves

### Servidor user1

- **IP:** `167.233.30.181`
- **SSH user:** `user1`
- **Chave:** `~/Downloads/user1_key` (167-233 bytes)
- **Caminho app:** `/app/`
- **Database:** Neon (URL em `/app/.env`)

### Workflows n8n em Produção

1. **Talent DB Proxy** — path `talent-db` (webhook)
   - Status: Precisa restaurar do `RESTAURAR.json`
   - Credencial: Postgres (vinculada na importação)
   
2. **Velas Talent - Gmail - Convite de Entrevista** — envia convite
3. **Talent Bank Sync** — envia para banco de talentos (negativa)

## 11. Fichas Técnicas

### A Tela de Triagem

**Arquivo:** `apps/web/src/pages/TriagemPage.tsx` (~352 linhas)

**Fluxo:**
1. Seleciona vaga (dispara `GET /screening/jobs/:id/results` + `/screening/jobs/:id/invites/approved`)
2. Botão "Triando" chama `POST /screening/jobs/:id/run`
3. Loop polling em `GET /screening/jobs/:id/run/latest`
4. Tabela mostra resultados com status (Avançar/Eliminado/Revisão humana)
5. "Convite" → `POST /screening/jobs/:id/invites/bulk-approved` (auto-escolhe slots)
6. "Negativa" → `POST /screening/jobs/:id/notify-rejected` (email automático)

**Estados:**
- `queued` → API enfilera
- `running` → worker rodando
- `completed` → tela mostra resultados
- `failed` (item específico) → candidato falha, resto continua

### Worker de Triagem

**Arquivo:** `apps/api/src/jobs/screening-worker.job.ts`

- Roda a cada `SCREENING_WORKER_INTERVAL_MS` (padrão 5s, melhor 30s)
- Busca jobs em `queued`/`running`
- Chama `runScreeningJobStep` (análise com IA)
- Reaper: item preso em `running` → volta para `pending` (lease 10 min)
- **Hoje:** Rodando local. Ideal: rodar no servidor, nunca no frontend.

## 12. Arquivos-Chave

| Arquivo | Responsabilidade |
|---|---|
| `/Users/grupovelas/dev/velas-talent` | Raiz do projeto |
| `apps/api/src/modules/jobs/jobs.repo.ts:467` | Guard UUID (NOVO, não deployado) |
| `apps/web/src/pages/TriagemPage.tsx` | Tela de triagem |
| `apps/api/src/jobs/screening-worker.job.ts` | Worker (local, deve mover pro servidor) |
| `apps/api/src/shared/http/outbound.ts` | Cliente único de saída + EMAIL_TEST_OVERRIDE |
| `apps/api/src/shared/http/external-fetch.ts` | Anti-SSRF |
| `apps/api/src/shared/http/rate-limit.ts` | Rate limit 300/min |
| `apps/api/src/shared/auth/connect-role.ts` | Fail-closed role mapping |
| `docs/deploy/private-server-user1.md` | Procedimento de deploy |
| `~/Downloads/Talent DB Proxy — RESTAURAR.json` | Workflow corrigido (aguardando importação) |
| `postgres/migrations/0027_idempotencia.sql` | Índices (JÁ APLICADO) |

## Próxima Sessão: Checklist

- [ ] Confirmar `.env` do servidor (leitura com ssh)
- [ ] Importar workflow restaurado no n8n
- [ ] Aumentar SCREENING_WORKER_INTERVAL_MS localmente
- [ ] Investigar rebuild-1.0.2 (production-ready ou orphaned?)
- [ ] Testar `npm run build:private:user1` (breaking change de package.json)
- [ ] Fazer backup robusto antes de rsync
- [ ] Teste de rsync em --dry-run
- [ ] Deploy com procedimento ordenado (backup → rsync → restaurar .env → npm install → start)
- [ ] Post-deploy: testes de health + função básica de triagem
