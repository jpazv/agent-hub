# Handoff — Security Hardening: Blocos D, E, F, H completos no Pulse

**Data:** 2026-07-30  
**Máquina:** MacBook-jpazv  
**Repo:** `~/dev/pulse`  
**Status:** `main`, 12 commits à frente de `origin/main` (push pendente nesta sessão), working tree limpo.

---

## Contexto

Continuação direta de `2026-07-30-security-blocos-abc-completos.md`.  
Blocos A, B, C já estavam completos. Esta sessão implementou D, E, F e H.  
**Bloco G (Infra/EC2) foi pulado** — será feito pelo chefe quando provisionar RDS + EC2.

---

## Bloco D — Webhook & External Integration — COMPLETO

Commit: `97efda4`

- **`database/migrations/0004_webhook_delivery_log.sql`**: tabelas `webhook_delivery_log` e `webhook_dead_letter`
- **`lib/server/circuit-breaker.ts`**: CLOSED/OPEN/HALF_OPEN, in-memory, configurável. Utilitário pronto — ainda não aplicado às chamadas em `webhook-processing.ts` (Meta/Chatwoot). Próximo passo natural.
- **`lib/server/webhook-dead-letter.ts`**: `enqueueDeadLetter()`, `fetchPendingDeadLetters()`, `resolveDeadLetter()`, `requeueDeadLetter()` com backoff exponencial (5m → 15m → 45m → 2h máx)
- **`app/api/cron/retry-dead-letter/route.ts`**: reprocessa DLQ, max 50 itens/ciclo
- **`app/api/webhook/route.ts`** (modificado): integra delivery log + DLQ; GET challenge auditado; **fix crítico**: fallback de timestamp que lia `x-hub-signature-256` e retornava `"sha256"` em vez de timestamp. Meta Cloud API não manda `X-Webhook-Timestamp` — header agora é opcional.
- **Fix colateral**: `secretarias/[id]/route.ts` — params async (Next.js 15), template literals corrigidos (artefato da sessão anterior com escapes incorretos)

---

## Bloco E — Data Protection (LGPD) — COMPLETO

Commit: `4cd0148`

- **`database/migrations/0005_data_protection.sql`**: `gdpr_deletion_requests` + `data_retention_log`
- **`lib/server/data-retention.ts`**: `runDataRetention()` — processa GDPR queue + purga >30d
  - `messages.conteudo` / `payload` → nullificados (métricas preservadas)
  - `conversations.lead_wa_id` → substituído por `[removido-lgpd]`
  - `webhook_delivery_log` → purgado em 90d
  - `audit_log` excluído da purga (obrigação legal LGPD Art. 37 — 5 anos mínimo)
- **`app/api/cron/purge-old-data/route.ts`**: executa retenção, registra em `data_retention_log`
- **`POST /api/tenant/gdpr/delete`**: solicitação assíncrona (202 Accepted), valida lead no tenant, bloqueia duplicata (409)
- **`docs/data-classification.md`**: catálogo PII/PHI/Confidencial/Interno por tabela+campo, base legal LGPD, retenção

**Pendência menor (auditada)**: `data_retention_log` não registra quantos `webhook_delivery_log` foram deletados — aceitável.

---

## Bloco F — Observability & Incident Response — COMPLETO

Commit: `15bb12d`

- **`lib/server/logger.ts`**: JSON estruturado por linha, nível `security` próprio, CloudWatch/ELK-ready
- **`lib/server/security-alert.ts`**: `checkSecurityEvents()` varre `audit_log` por spikes em janela de 5min
  - Assinaturas inválidas > 10 → alerta
  - Rate limit hits > 50 → alerta
  - Auth failures > 20 → alerta
  - Destino: `SECURITY_ALERT_WEBHOOK_URL` (Slack-compatible); silencioso se não configurado
  - Thresholds via env: `ALERT_SIGNATURE_FAILURES`, `ALERT_RATE_LIMIT_HITS`, `ALERT_AUTH_FAILURES`
- **`app/api/cron/anomaly-check/route.ts`**: roda a cada 5min
- **`docs/incident-response-playbook.md`**: P1–P4, contenção, erradicação, recuperação, queries SQL prontas
- **`docs/on-call-runbook.md`**: 6 cenários (RDS down, webhook travado, rate limit, assinatura inválida, retenção, backup restore)
- **`docs/breach-notification.md`**: templates ANPD + titular + interno, checklist 72h LGPD Art. 48

**Infra pendente**: CloudWatch agent no EC2 (Bloco G) é pré-requisito para ingestão dos logs JSON.

---

## Bloco G — Infrastructure & Deployment — PULADO

Responsabilidade do chefe. Não entrar neste bloco sem coordenação.  
O que precisa ser provisionado:
- RDS PostgreSQL 16+ em SA-EAST-1 (BR), VPC privada, Multi-AZ
- EC2 com Node, nginx, CloudWatch agent
- AWS Secrets Manager para `PULSE_SECRETS_KEY`, `WHATSAPP_APP_SECRET`, `DATABASE_URL`
- Staging environment com mascaramento de dados

---

## Bloco H — Dependencies & Supply Chain — COMPLETO

Commit: `c342f5b`

- **npm audit fix**: corrige `@hono/node-server` (GHSA-frvp-7c67-39w9, moderate, path traversal Windows)
- **ESLint 9→10**: resolve chain `brace-expansion` nos devDeps diretos
- **`.github/dependabot.yml`**: PRs semanais (segunda 9h BRT), agrupados por tipo; Next.js major ignorado (breaking frequente); Supabase **não ignorado** (migração Supabase→Postgres em curso, PR vai alertar)
- **`.github/workflows/security-audit.yml`**: CI com `npm audit --omit=dev --audit-level=high` + `tsc --noEmit`
- **`docs/accepted-risks.md`**: formaliza H-001 (postcss), H-002 (sharp), H-003 (brace-expansion em devDep) — todos build-time ou devDep, risco real zero em runtime

---

## Blocos restantes (I, J, K, L)

- **I** — Compliance & Governance: Privacy Policy, DPA, access control matrix
- **J** — Testing & Verification: suite de segurança, SAST, cross-tenant tests
- **K** — Multi-tenancy Isolation: RLS migrations, cache key isolation — migrations escritas aqui, aplicar em prod quando RDS estiver pronto
- **L** — Documentation: ADRs, OpenAPI docs, SBOM

---

## Migrations pendentes de rodar

| Migration | Status |
|---|---|
| `0003_audit_log.sql` | Não rodada (nenhum ambiente) |
| `0004_webhook_delivery_log.sql` | Não rodada |
| `0005_data_protection.sql` | Não rodada |

Rodar `npm run db:migrate` antes de subir qualquer ambiente.

---

## Variáveis de ambiente novas (não existiam antes desta sessão)

| Variável | Usado em | Padrão |
|---|---|---|
| `SECURITY_ALERT_WEBHOOK_URL` | `security-alert.ts` | — (sem alerta se ausente) |
| `ALERT_SIGNATURE_FAILURES` | `security-alert.ts` | 10 |
| `ALERT_RATE_LIMIT_HITS` | `security-alert.ts` | 50 |
| `ALERT_AUTH_FAILURES` | `security-alert.ts` | 20 |
| `DATA_RETENTION_DAYS` | `data-retention.ts` | 30 |
| `WDL_RETENTION_DAYS` | `data-retention.ts` | 90 |

---

## Como retomar

1. Ler este handoff + `2026-07-30-security-blocos-abc-completos.md` + `2026-07-30-security-hardening-checklist.md`
2. `npx vitest run` para confirmar que nada quebrou
3. Seguir para **Bloco I** (Compliance) — zero dependência de infra
4. Padrão estabelecido: implementa → audita → aprova → próximo bloco
