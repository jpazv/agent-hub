# Handoff — Security Hardening Checklist (Literatura: CSA, NIST, OWASP, ENISA, CWE, CISA, ISO 27001, AICPA)

**Data:** 2026-07-30  
**Máquina:** MacBook-jpazv (continuação de sessão)  
**Contexto:** Revisão de segurança baseada em frameworks de indústria. Este handoff lista **ações concretas** para implementação.

---

## Checklist de Implementações

### **A. Autenticação & Autorização** (OWASP A07, NIST AC-2/AC-3)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] API key versioning | Suportar múltiplos secrets em paralelo para rotação sem downtime | M | H | TODO |
| [ ] MFA/2FA dashboard | Two-factor auth (TOTP) para usuários admin/operacional | M | H | TODO |
| [ ] Audit log de acessos | Registrar quem acessou o quê, quando, de onde — queryable | M | H | TODO |
| [ ] Session timeout | Logout automático em 15-30 min inatividade (NIST padrão) | L | M | TODO |
| [ ] Rate limit global | Por usuário + por IP, Redis backed (não por instância) | M | H | TODO |
| [ ] Tenant context enforcement | Middleware valida `x-pulse-tenant-id` em TODA requisição | L | H | PARTIAL (em require-tenant.ts) |
| [ ] RLS policies | Postgres Row-Level Security para tenant isolation | M | H | TODO |

### **B. Criptografia & Secrets** (OWASP A02, NIST SC-13/SC-7)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Key rotation schedule | Rolar `PULSE_SECRETS_KEY` e `WHATSAPP_APP_SECRET` mensal | L | H | TODO |
| [ ] Encrypt-at-rest | RDS encryption enabled (AWS KMS key, não managed key) | L | H | TODO (pré-RDS) |
| [ ] Encrypt-at-transit | TLS 1.2+ enforcement, no fallback | L | M | PARTIAL (Vercel) |
| [ ] HSTS header | Strict-Transport-Security (max-age ≥ 31536000) | L | M | TODO |
| [ ] CSP header | Content-Security-Policy (whitelist scripts, styles) | M | M | TODO |
| [ ] Secrets scanning | Pre-commit hook (Gitleaks, git-secrets) | L | H | TODO |
| [ ] Key derivation | HKDF em vez de plaintext (NIST SP 800-135) | L | M | DONE (secret-crypto.ts) |

### **C. API Security** (OWASP API Top 10, NIST AC)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Input validation by field | Zod schemas com `.min()`, `.max()`, padrões (emails, phones) | M | H | PARTIAL (Zod existe) |
| [ ] Output encoding | JSON.stringify com sanitização, sem template injection | L | M | TODO |
| [ ] CORS whitelist | Explícito, sem `*`; whitelist por domínio | L | M | TODO |
| [ ] API versioning | Header ou path (`/api/v1/`, `/api/v2/`) com deprecation policy | M | M | TODO |
| [ ] Request signing | HMAC-SHA256 para requisições críticas (além do webhook) | M | M | TODO |
| [ ] Error handling | Erros sem stack trace / SQL / internals em produção | L | H | PARTIAL (check-alerts loga) |
| [ ] Timestamp validation | Anti-replay em webhooks (check "X-Timestamp" recente) | L | M | TODO |

### **D. Webhook & External Integration** (OWASP A06, NIST IR, CSA)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Signature validation | HMAC-SHA256 com constant-time compare | L | H | DONE (signature.ts) |
| [ ] Timestamp validation | Webhook não processa se timestamp > 5min | L | M | TODO |
| [ ] Idempotency tokens | Client envia nonce, server deduplica | M | M | PARTIAL (wa_message_id) |
| [ ] Dead-letter queue | Eventos falhados → fila de reprocessamento | M | H | TODO |
| [ ] Webhook delivery log | Tabela: received_at, phone_id, signature_valid, error | L | H | PLANNED (migration) |
| [ ] Circuit breaker | Falhas em Meta/Chatwoot não derrubam webhook | M | M | TODO |
| [ ] Webhook validation | GET challenge handshake logging + alerting | L | M | TODO |

### **E. Data Protection** (LGPD, GDPR, NIST SC-28, CSA)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Data classification | Marcar cada coluna: público / interno / confidencial / PII / PHI | L | M | TODO |
| [ ] PII pseudonymization | Hash ou criptografia de phone, email — não plaintext em logs | M | H | TODO |
| [ ] Data retention policy | Implementar delete automático em 30 dias (ou conforme law) | M | H | PLANNED (migrations) |
| [ ] Right to be forgotten | Endpoint POST `/api/tenant/{id}/gdpr/delete` + job assíncrono | M | H | TODO |
| [ ] Data residency | RDS em BR (São Paulo), confirmar localização | L | H | TODO (blocking) |
| [ ] Backup encryption | RDS backups encrypted com KMS, not default AWS key | L | H | TODO (pré-RDS) |
| [ ] Backup restoration test | Testar restore semanal de backup, documentar MTTR | M | H | TODO (ongoing) |

### **F. Observability & Incident Response** (NIST IR-4/IR-6, CISA)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Centralized logging | Não confiar em Vercel stdout; CloudWatch / ELK | M | H | TODO |
| [ ] Security event alerting | Alert em: unauthorized access, rate limit hits, signature failures | M | H | TODO |
| [ ] Anomaly detection | Spike em error rate, latência, 404s — alertar ops | M | M | TODO |
| [ ] Incident response playbook | Documento: escalation, communication, containment steps | L | H | TODO |
| [ ] On-call runbook | Como resolver: RDS down, webhook failing, DB full | M | M | TODO |
| [ ] Breach notification | Procedimento + templates para LGPD/GDPR (72h) | L | H | TODO |
| [ ] Log retention | 90 dias mínimo (auditoria), 1 ano para security events | L | M | TODO |

### **G. Infrastructure & Deployment** (OWASP Top 10 CI/CD, NIST CM)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] RDS provisioning | PostgreSQL 16+ em BR (VPC, not public) + backups | H | H | BLOCKING |
| [ ] RDS high-availability | Read replica + automated failover (Multi-AZ) | H | M | TODO (after RDS) |
| [ ] Secrets management | Vercel KV ou AWS Secrets Manager, not .env files | M | H | TODO |
| [ ] Infrastructure as Code | Terraform/CDK para RDS, KV, VPC — não manual console | M | M | TODO |
| [ ] Database encryption | RDS encryption enabled, key rotation policy | L | H | TODO (pré-RDS) |
| [ ] Staging environment | Clone de prod com masking de dados, full test antes de deploy | M | H | TODO |
| [ ] Build artifact signing | Sign docker images / deployables (cosign) | M | M | TODO |
| [ ] Secrets not in logs | Sanitize logs, no `PULSE_SECRETS_KEY` em error messages | L | H | PARTIAL (webhook.ts correto) |

### **H. Dependencies & Supply Chain** (OWASP C07, NIST SR, CISA)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] npm audit weekly | CI job: `npm audit --audit-level high` | L | H | TODO |
| [ ] Dependabot/Renovate | Auto-PR para updates, approve + merge semana 1 de cada release | L | M | TODO |
| [ ] Lock file pinning | `package-lock.json` committed, no semver ranges em prod | L | H | TODO |
| [ ] SCA tool | Snyk/WhiteSource scanning transitive deps | M | M | TODO |
| [ ] License compliance | FOSSA scan: não usar GPL em SaaS sem conformidade | L | M | TODO |
| [ ] Signed commits | Todos commits devem ter GPG signature (GitHub requirement) | M | L | TODO |
| [ ] Vendor risk assessment | Quarterly review: Supabase, Meta, Chatwoot SLAs + security posture | L | M | TODO |

### **I. Compliance & Governance** (ISO 27001, AICPA, CSA)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Privacy Policy | Conforme LGPD (direitos, coleta, retenção, cookies) | M | H | TODO |
| [ ] Terms of Service | Liability, retention, breach notification, SLA | M | H | TODO |
| [ ] Data Processing Agreement | DPA com clientes (obrigatório LGPD) | M | H | TODO |
| [ ] Access control matrix | Spreadsheet: role (admin/op/viewer) × feature, revisado 6m | L | M | TODO |
| [ ] Data owner assignment | Quem é responsável por qual dado (GDPR Art. 4) | L | M | TODO |
| [ ] Acceptable use policy | Proíbe scraping, brute force, abuso de API — enforcement automático | L | M | TODO |
| [ ] Annual security review | Audit interno: revisit this checklist, test recovery plans | M | M | TODO |

### **J. Testing & Verification** (NIST SP 800-115, OWASP)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Security test suite | Testes para OWASP Top 10: injection, auth bypass, etc | H | H | PARTIAL (pentests exist) |
| [ ] SAST | ESLint security rules + SonarQube CI | M | M | TODO |
| [ ] DAST | OWASP ZAP ou Burp Scanner agendado | M | M | TODO |
| [ ] Threat modeling | STRIDE para webhook + onboarding — document attack trees | M | H | TODO |
| [ ] Chaos engineering | Simular falhas: RDS down, Meta timeout, rate limit | H | M | TODO |
| [ ] Penetration test | Anual ou trimestral (terceirizado recomendado) | H | H | TODO |
| [ ] Cross-tenant test | Manual + automated: user A não consegue ler user B | H | H | CRITICAL |

### **K. Multi-tenancy Isolation** (NIST, CSA, AppOmni)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Data breach simulation | Penetration: pode user A ler conversations de unit B? | M | H | CRITICAL |
| [ ] Cache key isolation | Redis: `pulse:${tenantId}:key`, não global | L | H | TODO |
| [ ] Connection pooling | PgBouncer em transaction mode, tenant context por conexão | M | M | TODO |
| [ ] RLS policies | Postgres: forbid `select` sem `where tenant_id = current_setting('app.tenant_id')` | M | H | TODO |
| [ ] Tenant routing validation | Middleware: não deixa override casual de tenant_id | L | H | PARTIAL (require-tenant.ts) |
| [ ] Audit trail per tenant | Não misturar logs de tenants em mesmo table | M | M | TODO |
| [ ] Resource quota per tenant | Limite de: conexões, storage, requests/min | M | M | TODO |

### **L. Documentation** (NIST, ISO 27001)

| Item | Descrição | Esforço | Impacto | Status |
|---|---|---|---|---|
| [ ] Architecture Decision Records | ADRs: por quê Postgres em Node, por quê fail-closed webhook | M | M | PARTIAL |
| [ ] Security policies | Password policy, 2FA requirement, clean-desk, BYOD | M | M | TODO |
| [ ] Runbooks | Incident response, data loss, breach, service down | M | H | TODO |
| [ ] API documentation | OpenAPI/Swagger com security notes + auth examples | M | M | TODO |
| [ ] Threat model diagrams | Quem ataca o webhook, o dashboard, o Postgres | M | M | TODO |
| [ ] Change log | Releases com security fixes highlighted | L | M | TODO |
| [ ] Dependency graph | Bill of Materials (SBOM) em cada release (CISA recomenda) | M | L | TODO |

---

## Próximas Etapas

**Bloco A (Autenticação & Autorização):** Começar análise e plano de implementação.
