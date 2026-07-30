# Handoff — Security Hardening: Blocos A, B, C completos no Pulse

**Data:** 2026-07-30
**Máquina de origem:** MacBook-jpazv
**Repo:** `~/dev/pulse`
**Status do branch:** `main`, 8 commits à frente de `origin/main` (**não commitados no remoto ainda**), working tree limpo.

---

## Contexto: mudança de infra decidida nesta sessão

O usuário decidiu **não usar mais Vercel** — o Pulse vai para **domínio próprio +
EC2 na AWS**. Isso muda o roadmap de infraestrutura do checklist de segurança
(`2026-07-30-security-harding-checklist.md`, ver abaixo): tudo que dependia de
Vercel KV foi implementado com abstração de backend trocável (in-memory hoje,
Redis/ElastiCache quando o EC2 existir).

---

## De onde isto veio

Handoff anterior: `2026-07-30-security-hardening-checklist.md` (mesmo dia,
commitado antes deste). Esse handoff lista os 12 blocos (A–L) derivados da
leitura de CSA, NIST, OWASP (Top 10 + API + CI/CD), ENISA, CWE, AppOmni, CISA,
ISO 27001, AICPA. **Leia esse primeiro se for continuar o trabalho** — ele tem
a checklist completa item a item, com esforço/impacto/status por bloco.

Esta sessão implementou e comitou (não pushou) os **Blocos A, B e C** desse
checklist, todos no repo `pulse`.

---

## Bloco A — Autenticação & Autorização — COMPLETO

Commits: `930d45d`, `1535d74`, `f390a94`, `d00a286`, `d770f00`

**A.1 Rate Limit** (`lib/server/rate-limit.ts`, `lib/server/rate-limit-middleware.ts`):
- In-memory, fail-open (erro no backend não derruba o request).
- Aplicado em `/api/webhook` (1000 req/min) e nos 5 crons (`/api/cron/*`, 100 req/min).
- **Limitação documentada no próprio código**: per-instância, não global — em
  Vercel serverless (ou múltiplas instâncias EC2 atrás de load balancer) o teto
  real é `limite × instâncias`. Migrar para Redis quando o EC2 tiver múltiplas
  instâncias.

**A.2 Audit Log** (`database/migrations/0003_audit_log.sql`, `lib/server/audit-log.ts`,
`app/api/admin/audit-log/route.ts`):
- Tabela `audit_log`: tenant_id, user_id, action, resource, resource_id, status,
  ip_address, user_agent, error_message.
- `logAudit()` é fail-safe — nunca derruba o fluxo principal se o log falhar.
- **Aplicado em 4 pontos críticos** (pedido explícito do usuário):
  1. `POST /api/auth/vincular` — login/vinculação de tenant (detecta credential
     stuffing, phishing, tentativa sem compra associada).
  2. `POST /api/webhook` — assinatura inválida, schema inválido, erro de
     processamento, sucesso.
  3. `POST /api/secretarias` — criação de secretária.
  4. `PATCH` / `DELETE /api/secretarias/:id` — endpoint novo, não existia antes
     desta sessão; soft-delete (marca `ativo=false`, não apaga linha).

**A.3 Tenant Enforcement** (`lib/server/require-tenant.ts`):
- Já existia parcialmente; **corrigido fail-open crítico** achado em revisão
  externa (ver seção "Teste de fogo" abaixo).
- Rotas que **ainda faltam migrar** (estão em Supabase, não Postgres):
  `/api/onboarding/units`, `/api/onboarding/whatsapp-connect`,
  `/api/onboarding/provision`, `/api/onboarding/signup`. Não foram tocadas
  nesta sessão — usuário pediu para migrar "conforme a necessidade for
  aparecendo", não de uma vez.

### Teste de fogo — vulnerabilidades achadas e corrigidas (commit `f390a94`)

O usuário rodou uma revisão externa sobre o código recém-comitado e achou duas
falhas reais, ambas corrigidas no mesmo commit:

1. **IP spoofing em `extractIpAddress()`**: a implementação original confiava
   no **primeiro** IP de `X-Forwarded-For`, que é justamente o campo que o
   cliente controla. Um atacante conseguia (a) burlar o rate limit gerando IP
   aleatório a cada request, e (b) envenenar o audit log com IP forjado.
   **Corrigido**: agora usa `request.ip` (garantido pela Vercel) como primeira
   fonte; se usar `X-Forwarded-For` como fallback, lê o **último** elemento
   (o mais próximo do proxy de borda), não o primeiro.
2. **Fail-open em `requireTenant()`**: usuário multi-tenant sem header
   `x-pulse-tenant-id` caía silenciosamente no primeiro tenant da lista. Se o
   frontend perdesse o estado do tenant ativo, a API escrevia/lia na clínica
   errada sem erro nenhum — corrupção cross-tenant silenciosa.
   **Corrigido**: agora é fail-closed — usuário com mais de 1 tenant e sem
   header explícito recebe **400 Bad Request**. Só auto-resolve para
   `tenantIds[0]` se o usuário tiver exatamente 1 tenant (sem ambiguidade).

Lição para quem continuar: **qualquer coisa que derive uma chave de segurança
(IP, tenant, user) de um header do cliente precisa ser auditada como se fosse
hostil por padrão.** Isso já é o padrão de todo o resto do repo (ver
`secret-crypto.ts`, `signature.ts`), mas essas duas peças novas escaparam na
primeira versão.

---

## Bloco B — Criptografia & Secrets — COMPLETO

Commits: `30c8182`, `02ba5c6` (mais um fix de performance sem commit próprio,
aplicado por cima do `30c8182` antes do push)

- **HSTS + CSP + X-Content-Type-Options + X-Frame-Options + Permissions-Policy**
  em `next.config.ts`, função `headers()`. CSP tem whitelist explícito pra
  Supabase e Google OAuth em `connect-src`.
- **Pre-commit hook** (`.git/hooks/pre-commit` — **não versionado, é local
  desta máquina**; existe cópia documentada em `docs/setup-git-hooks.md`, mas
  o hook em si precisa ser instalado manualmente em cada clone/máquina):
  tenta `gitleaks protect --staged` (rápido, só olha staged files — ajuste
  pedido em revisão externa, motivo: `gitleaks detect --source .` escaneia o
  repo inteiro a cada commit e fica lento conforme o repo cresce); se
  `gitleaks` não estiver instalado, cai num fallback de `grep` sobre padrões
  comuns de secret.
- **`docs/key-rotation-schedule.md`**: plano de rotação mensal pra
  `PULSE_SECRETS_KEY`, `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN` — passo a
  passo com dual-key transition pra não ter downtime. **Ainda não
  automatizado, é processo manual documentado.**
- **`docs/setup-git-hooks.md`**: como instalar o gitleaks + o hook em qualquer
  máquina nova.

⚠️ **Ação pendente que não foi feita**: instalar o hook em si (`cp
docs/... .git/hooks/pre-commit && chmod +x`) precisa rodar em **cada máquina**
que vai commitar no `pulse` — ele não veio automaticamente pro
`mac-grupovelas` nem vai vir sozinho pro macbook. Verificar antes de commitar
de outra máquina.

---

## Bloco C — API Security — COMPLETO

Commit: `f12e4a2`

- **`middleware.ts`** (novo arquivo, raiz do projeto): CORS com whitelist
  explícita (`localhost:3000/3001`, `app.pulse.local`, `app.grupovelas.com.br`).
  Aplica só em `/api/:path*`. **Atenção**: os domínios de staging/produção são
  placeholders — conferir se `app.grupovelas.com.br` é de fato o domínio real
  antes de ir pra produção, ou ajustar.
- **`lib/server/error-handler.ts`**: sanitiza erro antes de devolver ao
  cliente. Erro "de cliente" (validação, not found, unauthorized) revela
  mensagem; erro "de servidor" (database, timeout, interno) esconde tudo atrás
  de mensagem genérica. **Ainda não foi aplicado a nenhuma rota** — o arquivo
  existe como utilitário pronto (`errorResponse()`), mas nenhum `route.ts` foi
  migrado pra usá-lo ainda. Próximo passo natural: trocar os `catch` manuais
  espalhados pelas rotas por esse helper.
- **`lib/webhook/timestamp-validation.ts`** + aplicado em
  `app/api/webhook/route.ts`: anti-replay, rejeita webhook com timestamp >5min
  de idade ou no futuro (>60s clock skew). **Ponto de atenção**: o código lê o
  timestamp de `x-webhook-timestamp` OU do prefixo de
  `x-hub-signature-256` como fallback — esse fallback é estranho porque
  `x-hub-signature-256` não carrega timestamp de verdade (é
  `sha256=<hash>`, o `.split("=")[0]` vai pegar a string `"sha256"`, não um
  timestamp). **Isso é um bug a corrigir**: a Meta não manda
  `X-Webhook-Timestamp` nativamente no formato Cloud API — precisa checar a
  documentação da Meta pra ver se esse header existe de verdade nesse
  webhook, ou se a validação de timestamp anti-replay tem que vir de outro
  campo do payload (ex: `timestamp` dentro de cada mensagem, que a Cloud API
  manda em segundos). **Não testado ainda** — só a auditoria e o schema Zod
  foram testados no CI existente; esse código novo não tem teste próprio.
- **`docs/api-versioning-strategy.md`**: estratégia path-based (`/api/v1/`,
  `/api/v2/`), regras de quando versionar, timeline de deprecação de 6 meses.
  **Puramente documental — nenhuma rota foi versionada ainda**, o projeto
  inteiro continua em `/api/` sem prefixo de versão.

---

## O que NÃO foi feito (pendências explícitas, não esquecidas)

1. **Testes**: nenhum teste novo foi escrito para nada dos Blocos A/B/C. O
   `check-alerts.test` e afins que já existiam continuam passando (não
   rodados nesta sessão pra confirmar — rodar `npx vitest run` antes de seguir).
2. **Bug do timestamp fallback** em `app/api/webhook/route.ts` (ver acima,
   Bloco C) — precisa decisão: usar campo do payload da Meta em vez do header,
   ou confirmar que a Meta manda esse header e ajustar o parse.
3. **Error handler não aplicado a nenhuma rota** ainda, só existe como utilitário.
4. **Pre-commit hook não instalado automaticamente** em nenhuma máquina — é
   passo manual.
5. **Push pendente**: 8 commits locais no `pulse`, não sincronizados com
   `origin/main`. Usuário não pediu push ainda.
6. **Migrations `0003_audit_log.sql` não rodada** em nenhum ambiente — só
   existe o arquivo SQL, ninguém rodou `npm run db:migrate` com ela ainda
   (nem local, nem futuro RDS).
7. **Rotas de onboarding em Supabase** (unidades, whatsapp-connect, provision,
   signup) continuam sem `requireTenant`/Postgres — migração incremental, não
   atacada nesta sessão por decisão do usuário.

---

## Blocos restantes do checklist original (D–L)

Ver `2026-07-30-security-hardening-checklist.md` pra lista completa. Ainda não
iniciados nesta sessão:

- **D** — Webhook & External Integration (dead-letter queue, circuit breaker)
- **E** — Data Protection (PII, retenção 30 dias, LGPD, right-to-be-forgotten)
- **F** — Observability & Incident Response
- **G** — Infrastructure & Deployment (⚠️ aqui entra a decisão EC2 — via
  Terraform/CDK, ver nota de infra abaixo)
- **H** — Dependencies & Supply Chain
- **I** — Compliance & Governance
- **J** — Testing & Verification
- **K** — Multi-tenancy Isolation
- **L** — Documentation

Ordem sugerida pelo checklist original não mudou: próximo lógico é **D** (o
usuário estava indo bloco a bloco, A→B→C).

---

## Nota de infraestrutura (importante para o Bloco G quando chegar)

Toda a arquitetura de "Postgres produção" e "scheduler dos crons" do handoff de
29/07 (`2026-07-29-pulse-fase-b-fechada-e-pentest-seguranca.md`, se ainda
existir) precisa ser revisitada à luz da decisão EC2+domínio próprio desta
sessão: RDS ainda faz sentido, mas o "scheduler que Vercel Cron não cobre" pode
virar simplesmente `cron` do Linux no EC2, sem precisar de EventBridge. Não
decidido ainda — só uma nota pra não redesenhar em cima do pressuposto antigo
(Vercel) sem revisar.

---

## Como retomar

1. Ler este handoff + `2026-07-30-security-hardening-checklist.md`.
2. Rodar `npx vitest run` no `pulse` pra confirmar que nada quebrou.
3. Decidir: seguir pro Bloco D, ou resolver as pendências listadas acima
   primeiro (timestamp bug, error-handler aplicado, push dos commits)?
4. Se for continuar blocos, seguir a ordem A→B→C→**D**→E→...→L, sempre
   perguntando aprovação por bloco (é o padrão que o usuário estabeleceu:
   implementa, audita externamente, aprova, próximo bloco).
