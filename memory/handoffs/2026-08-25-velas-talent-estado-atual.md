# Velas Talent — Estado Atual e Diagnóstico (2026-08-25)

## Resumo Executivo

O Velas Talent está **parcialmente funcional em produção** (`https://talent.grupovelas.com.br`, rodando há ~2 meses no servidor user1 @ `167.233.30.181`). A nova versão **MVP Lite foi refeita do zero** com tela de triagem, segurança, idempotência e worker da fila — **mas nenhuma mudança local foi enviada para produção ainda.**

Hoje descobrimos e diagnosticamos:
1. **Produção não estava lenta por token — era o worker local agressivo saturando o proxy n8n**
2. **O guard de autorização aceitava `undefined` como jobId** — corrigido, mas não deployado
3. ~~**O servidor está sem `.env`** (zero linhas)~~ — **CORRIGIDO na 2ª parte da sessão: o `.env` EXISTE e tem 24 linhas.** Ver secção 13.
4. **Main local está "ahead 19, behind 4" de origin/rebuild-1.0.2** — aqueles 4 commits removem pg.Pool fallback (mas ver correção na secção 13: o servidor está mais próximo do main local do que do rebuild-1.0.2)
5. **Package.json mudou breaking changes** que precisam ser testadas antes de deploy

> **LEIA A SECÇÃO 13 ANTES DE QUALQUER DEPLOY.** Ela corrige afirmações erradas
> deste handoff e documenta o que mataria a aplicação em produção.

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

---

# 13. ATUALIZAÇÃO — Investigação do servidor (2ª parte da sessão)

Esta secção **corrige** afirmações erradas das secções 1 e 7 e documenta o que
foi descoberto ao inspecionar o servidor de verdade. **Prevalece sobre o que está
escrito acima.**

## 13.1 — SSH deste servidor ignora comando por argumento

**Sintoma:** `ssh -i key user1@IP 'comando'` retorna `exit=0` **sem nenhuma saída**.
Não é erro de rede nem de chave — o comando simplesmente não roda.

**Causa:** o servidor força um shell que lê da entrada padrão e descarta o
argumento de comando do SSH.

**Como fazer funcionar — sempre use heredoc:**

```bash
K=~/Downloads/user1_key
ssh -i "$K" user1@167.233.30.181 << 'EOF'
pwd
ls -la /app
EOF
```

O aviso `Pseudo-terminal will not be allocated because stdin is not a terminal.`
é esperado e **não** indica falha.

Isso custou várias tentativas em falso nesta sessão. O usuário já tinha avisado
("ele vai retornar vazio se voce criar o comando ja com alguma instrução") — o
aviso estava certo.

## 13.2 — CORREÇÃO: o `.env` do servidor EXISTE

A secção 1 diz que o `.env` tem "zero linhas". **Está errado.** Aquele zero veio
de uma chamada SSH no formato que não executa (13.1).

**Realidade — `/app/.env` tem 24 linhas**, com pelo menos:

```
NODE_ENV, PORT, APP_FRONTEND_URL, CONNECT_VERIFY_JWT_URL, VELAS_INTERNAL_KEY,
QUICKIN_API_BASE_URL, QUICKIN_ACCOUNT_ID, QUICKIN_API_TOKEN,
GOOGLE_CALENDAR_API_KEY, GOOGLE_CLOUD_API_KEY, ...
```

## 13.3 — O RISCO REAL DO DEPLOY NÃO É APAGAR O `.env`. É SOBRESCREVER.

O `.env` **local** existe (1186 bytes, 21 linhas, valores de desenvolvimento
apontando para o proxy n8n).

O comando documentado em `docs/deploy/private-server-user1.md` exclui apenas
`node_modules` e `.git`. **Ele mandaria o `.env` de desenvolvimento por cima do
`.env` de produção.**

Estar no `.gitignore` **não protege** — rsync copia o diretório de trabalho, não
o que o git rastreia.

**Qualquer rsync para este servidor precisa de `--exclude '.env' --exclude '.env.*'`.**

## 13.4 — `--delete` MATA A APLICAÇÃO

`/app/index.js` é o ponto de entrada do processo (`node index.js`, PID 1, cwd `/app`)
e **NÃO existe no repositório**. É um wrapper criado à mão no servidor:

```js
import { createWriteStream, appendFileSync } from "node:fs";
appendFileSync("/app/app.log", `\n=== START ${new Date().toISOString()} ===\n`);
const logStream = createWriteStream("/app/app.log", { flags: "a" });
const origOut = process.stdout.write.bind(process.stdout);
const origErr = process.stderr.write.bind(process.stderr);
process.stdout.write = (...args) => { logStream.write(...args); return origOut(...args); };
process.stderr.write = (...args) => { logStream.write(...args); return origErr(...args); };
await import("./apps/api/dist/server.js");
```

Ele existe para capturar stdout/stderr em `/app/app.log` (não há gerenciador de
processo). `rsync --delete` **apagaria este arquivo** e a app não subiria no
próximo restart.

**Outros arquivos que só existem no servidor e seriam apagados:**

| Arquivo | O que é |
|---|---|
| `index.js` | **ponto de entrada — crítico** |
| `app.log`, `app.pid` | runtime |
| `tunnel.log`, `tunnel.pid` | runtime |
| `*.tgz` (4 arquivos) | backups feitos no servidor |
| `run-full-sync.mjs`, `_verify_fix.mjs`, `setup_bulk_invite_test.mjs` | scripts avulsos |

**Conclusão: `docs/deploy/private-server-user1.md` está PERIGOSO como escrito.**
O comando de lá deve ser corrigido antes de qualquer uso.

## 13.5 — Cadeia de execução em produção

```
node /app/index.js            (wrapper de log, PID 1, cwd /app)
  └─ import ./apps/api/dist/server.js    (API compilada)
```

Front: existem **duas** cópias — `/app/dist/` (assets, index.html, favicon.svg,
vt-logo.png) e `/app/apps/web/dist/`. Ainda **não confirmado** qual é a servida —
verificar `SERVE_WEB`/`APP_BASE_PATH` no `server.js` antes de publicar o front.

## 13.6 — CORREÇÃO: quão atrasado está o servidor, de verdade

A secção 1 diz "produção está 19 commits atrás". **Impreciso.**

O `package.json` do servidor tem:

```
"start:private": "SERVE_WEB=true PORT=3000 APP_BASE_PATH=/app1 npm --workspace @velas-talent/api run start"
```

Essa linha é **idêntica à do main local** e **diferente** da de
`origin/rebuild-1.0.2`. Ou seja: **o servidor foi publicado a partir de algo
próximo do main local, não do rebuild-1.0.2.**

O que está confirmado como ausente em produção é apenas o trabalho de hoje:
`grep "jobId invalido" /app/apps/api/dist/modules/jobs/jobs.repo.js` → não encontra.

**Não repetir a afirmação "19 commits atrás" sem reverificar.** A relação entre
`main` e `origin/rebuild-1.0.2` é de *unrelated histories* (git merge recusa), o
que torna a contagem ahead/behind pouco significativa.

## 13.7 — Build local: corrigida e passando

A build falhava com:

```
tsconfig.app.json: error TS5101: Option 'baseUrl' is deprecated ...
```

**Causa:** `apps/web/tsconfig.app.json` tinha `"ignoreDeprecations": "5.0"`,
mas o `tsc` do projeto é **6.0.3**, que exige `"6.0"`.

Primeira tentativa minha inseriu uma segunda chave `ignoreDeprecations` no topo
do objeto — **não funcionou**, porque em JSON a última chave repetida vence e a
`"5.0"` de baixo continuava valendo. A correção certa foi **alterar o valor
existente**, não adicionar outro.

**Estado:** `npm run build:private:user1` passa. `apps/web/dist/` gerado,
incluindo `TriagemPage-DWAde-UK.js`. O guard está compilado em
`apps/api/dist/modules/jobs/jobs.repo.js`.

**Não commitado ainda:**
```
 M apps/api/src/modules/jobs/jobs.repo.ts     (guard UUID fail-closed)
 M apps/web/tsconfig.app.json                 (ignoreDeprecations 5.0 -> 6.0)
```

## 13.8 — Nota: rsync da árvore inteira é lento aqui

Um `--dry-run` da árvore completa não terminou em 2 minutos e travou o SSH
concorrente. A árvore local tem **480 MB**, dos quais **383 MB** são
`node_modules`. Mesmo excluído, o rsync percorre a árvore local inteira.

Preferir sync cirúrgico dos diretórios compilados.

## 13.9 — PLANO DE DEPLOY SEGURO (substitui o da secção 7)

**Nunca** usar o comando como está na doc. Usar:

```bash
cd ~/dev/velas-talent
K=~/Downloads/user1_key

# 1) Backup no servidor (heredoc!)
ssh -i "$K" user1@167.233.30.181 << 'EOF'
cp /app/.env /app/.env.bak.$(date +%s)
cp /app/index.js /app/index.js.bak.$(date +%s)
tar czf /tmp/api-dist-backup.tgz /app/apps/api/dist 2>/dev/null
ls -la /app/.env.bak.* /app/index.js.bak.* | tail -4
EOF

# 2) Sync cirúrgico — SEM --delete, SEM .env, só o compilado
rsync -avz --no-perms --no-owner --no-group \
  -e "ssh -i $K" \
  apps/api/dist/ user1@167.233.30.181:/app/apps/api/dist/

rsync -avz --no-perms --no-owner --no-group \
  -e "ssh -i $K" \
  apps/web/dist/ user1@167.233.30.181:/app/apps/web/dist/

# 3) Verificar que o guard chegou e reiniciar (heredoc!)
ssh -i "$K" user1@167.233.30.181 << 'EOF'
grep -c "jobId invalido" /app/apps/api/dist/modules/jobs/jobs.repo.js
ls -la /app/index.js /app/.env
EOF
```

**Antes de rodar isto, resolver:**

- [ ] Confirmar de qual pasta o front é servido (13.5) — senão o front novo não aparece
- [ ] Descobrir **como reiniciar** o processo: não há gerenciador; PID 1 roda
      `node index.js`. Matar o PID 1 num container **encerra o container**.
      Verificar se há restart automático antes de matar qualquer coisa.
- [ ] Confirmar se `npm install` é necessário (mudou alguma dependência?)

## 13.10 — Erros meus nesta parte da sessão

1. **Declarei ".env do servidor está vazio" sem verificar o formato do SSH.**
   O `wc -l` retornou 0 porque o comando não executou (13.1), não porque o
   arquivo estivesse vazio. Construí um plano de deploy inteiro em cima disso.

2. **Disse que o risco era o `--delete` apagar o `.env`.** O risco real era a
   *sobrescrita* pelo `.env` de desenvolvimento — mecanismo diferente, e que o
   `--exclude` do `--delete` não resolveria sozinho.

3. **Tentei silenciar o TS5101 adicionando uma chave duplicada** em vez de
   corrigir a existente. Não funcionou e me custou uma rodada de build.

4. **"19 commits atrás"** foi afirmado com mais confiança do que a evidência
   suportava (13.6).

Padrão comum aos quatro: concluir a partir do primeiro sinal, sem confirmar o
mecanismo. O usuário tinha avisado sobre o comportamento do SSH antes de eu
esbarrar nele duas vezes.

## 14 — Continuidade: diagnóstico funcional e hardening de convites (2026-08-25)

### Decisões de escopo

- Não incluir o legado Lite, nem como tela servida nem como fallback.
- Preservar os commits positivos recentes; não reescrever layout.
- Não alterar schema/banco salvo necessidade comprovada.
- Prioridade: triagem segura, fallback, fila sem sobreposição, idempotência,
  slots compreensíveis e agenda confiável para pelo menos 10 usuários.
- Login real via VelasConnect confirmado pelo usuário como funcionando.
- A API usa o proxy n8n (`N8N_DB_WEBHOOK_URL`); não assumir acesso direto ao
  Neon sem confirmar a credencial do workflow.

### Verificações realizadas

- `npm run verify`: passou; 58 testes da API e 14 do domínio.
- `npm run build:private:user1`: passou.
- Smoke local: `/app1/api/health` 200, frontend 200, rota protegida sem sessão
  401.
- Produção: health público 200, mas artefatos compilados continuam de julho e
  não contêm o guard UUID novo. Nenhum deploy recente foi concluído.

### Alterações locais ainda não publicadas

1. `apps/api/src/modules/email-templates/email-templates.routes.ts`
   - Templates, logs e teste de envio agora exigem `superadmin`, `gestor_dho`,
     `diretor` ou `rh`. Recrutador comum não pode editar HTML pela API.

2. `apps/api/src/modules/email-templates/email-log.repo.ts`
   - Reserva idempotente permite retry quando o envio anterior terminou em
     `failed`; envio já `sent` continua bloqueado.

3. `apps/api/src/modules/screening/screening.booking.ts`
   - Convite individual reutiliza convite `pending`, token e slots existentes.
   - Os dois fluxos em lote consultam convite `pending` antes de inserir, para
     evitar registros duplicados em corrida simultânea.
   - Ainda falta fluxo explícito para reenviar lote cujo convite `pending`
     ficou salvo após falha; não considerar isso resolvido.

### Riscos encontrados para a próxima etapa

- Vagas delegadas: `canUserAccessJob` filtra a lista e as rotas de triagem,
  mas `GET /jobs/:jobId` não chama o guard de acesso.
- A movimentação valida acesso à vaga, mas ainda não confirma que `placementId`
  pertence ao `jobId` informado. Isso pode permitir cruzamento de kanban por IDOR.
- Review por `resultId` e convite individual por `resultId` não recebem `jobId`
  na rota; precisam validar a vaga do resultado antes de alterar/enviar.
- Quickin possui endpoints administrativos amplos; revisar se recrutador deve
  sincronizar ou consultar dados fora do escopo da vaga delegada.
- Agendamento chama Google Calendar dentro do fluxo de reserva. A falha externa
  vira `calendar_pending`, mas ordem e reconciliação ainda precisam ser validadas.

### Próximo passo recomendado

Fechar primeiro o isolamento de vagas delegadas: proteger `GET /jobs/:jobId`,
amarrar `placementId` ao `jobId` na movimentação e validar o job dos resultados
antes de review/convite. Depois voltar ao reenvio de convites pendentes e à
reconciliação de calendário. Não fazer deploy antes dessa revisão.

## 15 — Reinício de produção e pesquisa operacional (2026-08-25)

### Estado confirmado

- Acesso Docker não está disponível dentro do ambiente remoto.
- Não foi encontrado `systemd`, `supervisord` ou outro gerenciador acessível.
- O processo principal é `node index.js`, PID 1, em `/app`.
- `/app/index.js` é wrapper manual que importa `./apps/api/dist/server.js` e grava
  logs em `/app/app.log`.
- `/app/api/health` responde 200 enquanto o processo está ativo.
- Nenhum comando destrutivo foi executado; produção não foi reiniciada nesta
  investigação.

### Pesquisa de reinício forçado

- Políticas Docker (`always`/`unless-stopped`) são configuradas no host e podem
  recuperar um container parado: [Docker restart policies](https://docs.docker.com/engine/containers/start-containers-automatically/).
- Montar ou expor `/var/run/docker.sock` para reiniciar de dentro não é aceitável:
  acesso ao socket equivale a acesso root ao host, conforme alerta do mantenedor
  do Moby: [Moby discussion](https://github.com/moby/moby/discussions/46682).
- `SIGHUP` não é solução para este app: não há handler de reload confirmado e
  módulos Node já carregados não são substituídos.
- `kill -TERM 1` ou `kill -KILL 1` somente deve ser usado depois de confirmar,
  no host, que existe política automática de restart. Sem isso, derruba produção
  sem mecanismo de retorno.

### Próximo passo operacional

Obter acesso ao host/orquestrador ou confirmação do operador sobre a política de
restart. No host, verificar primeiro:

```bash
docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' <container>
```

Só com política confirmada executar `docker restart -t 30 <container>` ou, como
último recurso, terminar o PID 1 e deixar o runtime recuperar o processo. Não
usar `docker.sock` como atalho. O deploy continua pendente até haver restart
controlado e smoke test de `/api/health`, login, triagem e convite.

## 16 — Emails, OpenRouter e verificações locais (2026-08-25)

### Emails

- O JSON `~/Downloads/Produção D-1 — Relatório Diário-2.json` contém HTML e uma
  chamada HTTP para `sub-enviar-email`, mas **não contém credenciais**; apenas
  referencia `httpHeaderAuth` do n8n.
- O shell visual VelasConnect foi reaproveitado em `corporate-email.ts`:
  fundo azul escuro, logo Grupo Velas, cabeçalho azul, conteúdo central e rodapé.
- Foi criado `apps/api/src/integrations/email/email.delivery.ts`:
  - Gmail API direto é primário quando `GMAIL_REFRESH_TOKEN` + OAuth existem.
  - Provider HTTP compatível com payload Resend é alternativa direta quando
    `EMAIL_HTTP_API_KEY` + `EMAIL_FROM` existem.
  - n8n permanece fallback.
  - `EMAIL_TEST_OVERRIDE` também vale para o caminho direto.
- Convite, confirmação, negativa e alerta de banco de talentos usam o adaptador.
- Criado `npm run email:sink`: sink local em `127.0.0.1:8787` que valida Bearer,
  payload e grava em `/tmp/velas-talent-email-sink.jsonl`, sem enviar email.
- O remetente direto é `EMAIL_FROM`; `jp@grupovelas.com.br` ainda não está
  configurado. Gmail exige OAuth com escopo `gmail.send`.

### Testes executados

- `npm run verify`: **58 testes API + 14 domínio, todos passando**.
- `npm run build:private:user1`: passou.
- `npx tsc --noEmit -p apps/api/tsconfig.json`: passou.
- Smoke local: `/api/health` = `200`, rota protegida sem sessão = `401`.
- Sink de email local = `202`.
- Dez requisições simultâneas ao health: `10/10` = `200`.
- OpenRouter smoke sintético: `200`, modelo `google/gemini-2.5-flash`, 15 tokens,
  custo aproximado de `US$0,0000067`.
- OpenRouter com dez chamadas simultâneas no formato do app: **10/10 passaram**,
  tempo total `2,216s`, latência individual entre `1,632s` e `2,204s`, nenhum
  `429`, consumo de 18–19 tokens por chamada.

### Limitações e incidentes de teste

- Ainda não houve carga completa do worker com currículo, persistência no banco e
  movimento no Quickin.
- Ao iniciar a API local, o `.env` carregou o proxy n8n e o worker iniciou sozinho;
  houve timeouts e logs de itens presos devolvidos à fila. O processo foi parado.
  Próxima melhoria: flag explícita para iniciar o worker desligado em testes.
- Consulta somente leitura ao proxy para selecionar 20 currículos retornou:
  `count=1`, `withResumeUrl=0`, `withQuickinRaw=0`, `jobIds=1`. Portanto **não
  foi feita carga com 20 currículos** e nenhum currículo foi enviado ao OpenRouter.
- Não foi chamado Gmail real, n8n real, endpoint de confirmação real ou DAST/pentest.

### Estado do trabalho local

Além das alterações de segurança/convites das secções anteriores, ficaram locais:

- `.env.example`, `package.json`;
- `apps/api/src/config/env.ts`;
- `apps/api/src/integrations/email/email.delivery.ts`;
- `apps/api/src/integrations/n8n/corporate-email.ts`;
- `apps/api/src/integrations/n8n/n8n.email.ts`;
- `apps/api/src/integrations/n8n/n8n.rejection.ts`;
- `apps/api/src/integrations/n8n/n8n.talent-bank.ts`;
- `scripts/email-http-sink.mjs`;
- mudanças anteriores em autorização de vagas, convites/idempotência e templates.

### Próximos passos

1. Criar flag `SCREENING_WORKER_ENABLED=false` para testes locais.
2. Corrigir/confirmar a consulta de currículos e identificar por que só um placement
   sem URL foi retornado.
3. Só então executar carga controlada com 20 currículos, com autorização explícita
   para enviar PII ao OpenRouter e sem persistir resultados reais.
4. Obter OAuth de `jp@grupovelas.com.br` com `gmail.send` e testar Gmail direto.

## 17 — Tentativa de carga com duas vagas (2026-08-25)

O usuário pediu carga concorrente simulando dois recrutadores, com 10 currículos
por vaga. A execução foi bloqueada antes de enviar qualquer currículo ao
OpenRouter:

- Consulta de placements com `resume_url`/`quickin_raw` retornou `count=1`,
  `withResumeUrl=0`, `withQuickinRaw=0`, `jobIds=1`.
- Consulta agregada por vaga voltou `[{}]`, sem colunas úteis.
- Consulta simples de até 25 placements também voltou `count=1` com um objeto
  vazio.
- Inferência: o webhook/proxy n8n atual está limitando, transformando ou
  descartando os resultados, ou o banco acessível não contém a base esperada.
  Não concluir ainda que não existem currículos.
- Nenhum currículo real foi impresso, persistido localmente ou enviado ao
  OpenRouter nesta tentativa.
- A carga 10x10 continua pendente até corrigir/validar o retorno do proxy ou
  disponibilizar uma fonte de leitura confiável. Não contornar o proxy com
  acesso não autorizado ao Neon.

## 18 — Diagnóstico do proxy e carga real 10x10 (2026-08-25)

- Causa encontrada para o retorno anterior vazio: o workflow n8n responde o
  contrato como `[{ rows, rowCount }]`, mas `proxy-pool.ts` tratava o array
  externo como se cada item fosse uma linha. O app recebia um objeto embrulhado
  em vez dos placements.
- `apps/api/src/shared/db/proxy-pool.ts` foi ajustado para desembrulhar esse
  formato antes de retornar `rows`. TypeScript passou.
- Após o ajuste, a leitura retornou dados reais: as vagas escolhidas tinham
  148 e 132 placements, respectivamente, com currículos disponíveis.
- Carga autorizada executada sem persistir resultados de triagem nem mover
  candidatos: duas vagas em paralelo, 10 currículos por vaga, 20 chamadas reais
  ao OpenRouter.
- Resultado: **16/20 passaram**; vaga `a748...c0c2f9`: **10/10**; vaga
  `db004...1bf1d0`: **6/10**. Quatro falhas foram `AbortSignal.timeout` de
  50 segundos. Nenhum `429` foi observado.
- Latência total da carga: aproximadamente 60 segundos. As falhas ocorreram
  somente na segunda vaga e devem ser investigadas no caminho de download/
  extração de PDFs e na tolerância de concorrência, antes de considerar 10
  usuários simultâneos suportados.
- A carga não gravou `screening_results`; apenas `insertTokenUsage` pode ter
  enviado telemetria assíncrona pelo proxy. Nenhum e-mail foi enviado.

## 19 — Proteção contra timeouts e concorrência (2026-08-25)

- Timeout de download de currículo ficou configurável por
  `SCREENING_RESUME_FETCH_TIMEOUT_MS`, padrão 15s.
- Extração PDF ganhou timeout próprio de 20s.
- OpenRouter ficou configurável por `SCREENING_AI_TIMEOUT_MS`, padrão 45s.
- Timeout/rede indisponível no OpenRouter agora gera resultado de fallback com
  recomendação obrigatória `revisao_humana`, sem eliminar candidato e sem
  travar permanentemente a fila.
- Worker passou a processar até duas vagas em paralelo por passada, controlado
  por `SCREENING_WORKER_JOB_CONCURRENCY` (máximo aceito 4), mantendo uma única
  passada global para evitar sobreposição.
- `npx tsc --noEmit -p apps/api/tsconfig.json` e `git diff --check` passaram.
- Nova carga ainda pendente; precisa confirmar que os quatro casos anteriores
  viram fallback controlado em vez de erro.

## 20 — Estratégia final de fallback (2026-08-25)

- Decisão: manter o modelo principal e o modelo fallback no mesmo pedido do
  OpenRouter; o provedor já pode alternar sem expor currículo novamente.
- Falhas de rede/timeout devem continuar como resultado de revisão humana, sem
  eliminação automática.
- A fila existente já reencaminha item retryable para `pending` enquanto
  `attempts < max_attempts`; a ordenação por `updated_at` coloca a tentativa
  no fim dos pendentes, evitando bloquear os demais candidatos.
- Depois do limite de tentativas, o item permanece `failed` para revisão e não
  entra em loop.
- Não alterar banco nem layout para essa estratégia.

## 21 — Ambiente local e E2E básico (2026-08-25)

- API local iniciada em `http://127.0.0.1:3001` com
  `SCREENING_WORKER=off` para evitar triagem automática durante inspeção.
- Frontend Vite iniciado em `http://127.0.0.1:5174`; a porta 5173 já estava
  ocupada por outro processo local.
- Corrigido bootstrap de ambiente: `bootstrap-env.ts` carrega `.env` antes de
  importar `app` e repositorios. Antes disso, módulos de email tentavam
  inicializar sem `N8N_DB_WEBHOOK_URL`, apesar de a variável existir.
- E2E básico passou: `/api/health` = 200, frontend `/api/health` via proxy =
  200, rota protegida sem token = 401, headers de segurança presentes.
- `npm run build:private:user1` passou e `npx tsc --noEmit -p
  apps/api/tsconfig.json` passou.
- E2E autenticado, inspeção visual e teste de rotas protegidas com sessão real
  ainda dependem de executar o login Connect no navegador.

---

# 14. PRODUÇÃO ESTÁ FALHANDO HÁ SEMANAS (descoberta no fim da sessão)

Achado ao ler `/app/app.log`. **Isto é mais grave do que tudo acima** e não tinha
sido detectado porque `/api/health` responde `200` mesmo com a app sem banco.

## 14.1 — O log

`/app/app.log` tem **7,8 MB**. Processo de pé desde `=== START 2026-07-07T20:46:57Z ===`
(~7 semanas). Contagem de erros acumulados:

| Ocorrências | Erro |
|---:|---|
| 13.010 | `[proxy-pool] n8n respondeu 404: "The requested webhook \"POST talent-db\" is not registered"` |
| 623 | `[proxy-pool] n8n respondeu 500: {"message":"Workflow execution failed"}` |
| 276 | `relation "talent.candidates" does not exist` |
| 193 | `[proxy-pool] n8n respondeu 40x: Authorization data is wrong!` |
| 191 | `fetch failed` |
| 18 | `Nao foi possivel buscar candidatos no Quickin.` |

Por cron: **7.610** `[sync-candidates] erro`, **6.705** `[sync-calendar-cancellations] erro`.

## 14.2 — Leitura dos três erros principais

**`404 ... is not registered` (13.010, o dominante)** — não havia **nenhum**
workflow ativo no path `talent-db`. Produção ficou sem acesso ao banco.
**Já não aparece nas últimas 200 linhas** → é histórico, foi resolvido.

**`Authorization data is wrong!` (193)** — assinatura do node Webhook com
`authentication: headerAuth` **sem credencial vinculada**. É exatamente o modo de
falha do `Talent DB Proxy — CORRIGIDO.json`. Confirma o diagnóstico daquele
incidente, agora com evidência do log de produção.

**`relation "talent.candidates" does not exist` (276)** — **bug separado e não
investigado.** O código consulta uma tabela que não existe no banco. Pode ser
schema errado (`talent.` vs `rh.`) ou migration não aplicada. **Investigar.**

## 14.3 — Estado ATUAL (últimas 500 linhas do log)

```
36 × n8n respondeu 403
24 × n8n respondeu 500
 0 × 404 not registered
```

Ou seja: o webhook **voltou a existir**, mas as chamadas de produção ainda são
recusadas — agora com **403** e **500**.

**Contradição não resolvida:** meu `curl` manual de hoje, com
`x-webhook-key: gv_talent_db_2026`, devolveu **200 com linhas**. E o `.env` de
produção tem `N8N_DB_WEBHOOK_KEY=gv_tal…` (bate). Mesmo assim prod leva 403/500.

Hipóteses a testar na próxima sessão (nenhuma verificada):
1. Há **mais de um workflow** no path `talent-db` e o roteamento é inconsistente
   (o n8n aceita ativar só um; o outro pode estar respondendo em `/webhook-test/`)
2. O workflow ativo é o `CORRIGIDO` (headerAuth sem credencial) → 403, e meu curl
   acertou outro
3. Prod monta o header com nome/caixa diferente do que o Code node lê
   (`x-webhook-key`)
4. As requisições que falham são as que enviam SQL que o `Auth + Validate` rejeita
   (ex.: `sql` ausente) → 500 legítimo

**Teste que separa as hipóteses:** rodar o mesmo `curl` que funcionou e, em
paralelo, olhar a lista de execuções no n8n para ver qual workflow atendeu.

## 14.4 — O bug do `undefined` está VIVO em produção

Última linha útil do log:

```
[requireAuth] GET /jobs/undefined/results {
```

Sessão **autenticada** mandando `undefined`. É o mesmo bug corrigido hoje pelo
guard em `canUserAccessJob` — e mais uma razão para publicá-lo.

## 14.5 — Reiniciar o processo é PERIGOSO (bloqueio de deploy)

```
PID   PPID  COMMAND
    1     0 node index.js
```

- **`node index.js` é o PID 1.** Não há s6, supervisor nem systemd.
- Matar o PID 1 **encerra o container**. Se não houver política de restart no
  orquestrador (fora do container, não visível daqui), a app **não volta**.
- `/app/docker-compose.yml` não tem `restart:` (grep vazio) — mas não é
  necessariamente o compose que subiu este container.
- `/app/app.pid` contém `10172`, **PID que não existe** — arquivo obsoleto,
  não confiar nele.

**NÃO reiniciar sem antes descobrir quem sobe o container.** Perguntar ao
responsável pela infra, ou achar a policy no host.

## 14.6 — Detalhe de configuração

`DATABASE_URL` **não está** em `/app/.env` — vem do **ambiente do container**
(aparece em `env`, não no arquivo). Ao mexer no `.env`, isso não é afetado.

## 14.7 — Ordem recomendada para a próxima sessão

A ordem abaixo inverte a prioridade das secções 7 e 13.9: **não faz sentido
publicar código novo numa produção que não fala com o banco.**

1. **Resolver o proxy n8n primeiro.** Descobrir por que prod leva 403/500 (14.3).
   Garantir **um único** workflow ativo no path `talent-db`, com credencial
   Postgres vinculada. Validar com `curl` **e** confirmando no log de produção
   que os erros pararam:
   ```
   tail -50 /app/app.log | grep -c 'proxy-pool'   # esperado: 0
   ```
2. **Investigar `relation "talent.candidates" does not exist`** (14.2).
3. **Só então** avaliar o deploy do guard + tela nova, pelo plano de 13.9,
   e **depois** de responder como reiniciar o processo (14.5).

## 14.8 — Por que isto passou despercebido

`/api/health` devolve `200 {"status":"ok"}` mesmo com o banco inacessível — o
healthcheck não toca o banco. A app "está no ar" e falhando ao mesmo tempo.

**Melhoria a considerar:** um `/api/health/deep` que faça um `select 1` pelo
proxy e falhe de verdade quando o banco não responder.
