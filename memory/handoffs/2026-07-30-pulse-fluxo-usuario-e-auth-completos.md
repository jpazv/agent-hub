# Handoff — Pulse: Fluxo de usuário validado + Auth Postgres puro

**Data:** 2026-07-30  
**Máquina:** mac-grupovelas  
**Repo:** `~/dev/pulse`  
**Banco (dev/staging):** Neon — `ep-withered-cherry-aclgcbg7-pooler.sa-east-1.aws.neon.tech`

---

## O que foi feito nesta sessão

### 1. Migração Supabase Auth → Postgres puro (concluída)

- `app_auth.users` com `password_hash` (bcrypt 12), `google_id`, `email_confirmed`, `session_version`
- JWT HS256 (jose), cookie httpOnly `pulse_session`, blacklist `app_auth.revoked_tokens`
- `session_version` para logout multi-dispositivo (`POST /api/auth/logout-all`)
- Google OAuth manual: JWKS verify contra `googleapis.com/oauth2/v3/certs` (fix crítico — estava usando `decodeJwt` sem verificar assinatura)
- Todos os imports de `@supabase/ssr` e `@supabase/supabase-js` removidos do runtime

### 2. Fluxo completo validado

```
Landing (raiox-mvp-html)
  └─ Compra → POST /api/onboarding/provision
       └─ Email "Seu acesso ao Pulse está pronto" (Resend)
            └─ /convite?token=xxx → set-password → JWT cookie → /
                 └─ Dashboard (KPIs de tempo de resposta)

Retorno:
  /login → email/senha → /
  /login → Google OAuth → JWKS → /
  /login → Esqueci senha → /recuperar → email → /convite?token=xxx → /
```

### 3. Banco Neon configurado

- `.env.local` aponta para Neon (substituiu variáveis Supabase)
- Migrations 0001–0006 aplicadas no Neon
- Migration 0006 atualizada para dropar schema legado da 0001 antes de recriar

---

## Pendências de infra (fora do código)

### Google Cloud Console — OBRIGATÓRIO antes de ir a prod

- [ ] Adicionar redirect URI autorizado: `https://pulse.grupovelas.com.br/api/auth/google/callback`
- [ ] Confirmar que `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` estão no AWS Secrets Manager (`pulse/prod`)

Sem isso, o Google OAuth falha em produção com erro `redirect_uri_mismatch`.

### AWS Secrets Manager (`pulse/prod`) — variáveis necessárias

Todas as variáveis abaixo precisam existir no secret antes do primeiro deploy:

| Chave | Observação |
|---|---|
| `DATABASE_URL` | Postgres local no EC2: `postgresql://pulse_app:<senha>@localhost:5432/pulse_prod` |
| `PULSE_SECRETS_KEY` | `openssl rand -hex 32` |
| `WHATSAPP_APP_SECRET` | Painel Meta for Developers |
| `WHATSAPP_VERIFY_TOKEN` | Qualquer string, gravar |
| `META_APP_ID` | Painel Meta |
| `META_APP_SECRET` | Painel Meta |
| `CRON_SECRET` | `openssl rand -hex 16` |
| `PULSE_PROVISIONING_SECRET` | Mesmo valor configurado no raiox-mvp-html |
| `PULSE_APP_URL` | `https://pulse.grupovelas.com.br` — **crítico**, define o domínio dos links de email e OAuth |
| `GROQ_API_KEY` | console.groq.com |
| `RESEND_API_KEY` | resend.com/api-keys |
| `GOOGLE_CLIENT_ID` | console.cloud.google.com |
| `GOOGLE_CLIENT_SECRET` | console.cloud.google.com |
| `SECURITY_ALERT_WEBHOOK_URL` | Opcional — webhook Slack para alertas de segurança |

### Domínio Resend — OBRIGATÓRIO para email não cair em spam

- [ ] Verificar domínio `grupovelas.com.br` no Resend (DNS SPF/DKIM)
- Emails saem de `noreply@grupovelas.com.br` — sem verificação DNS caem em spam

---

## Correções aplicadas nesta sessão

| Arquivo | O que foi corrigido |
|---|---|
| `app/api/auth/google/callback/route.ts` | `decodeJwt` → `jwtVerify` com JWKS (assinatura verificada) |
| `app/api/auth/login/route.ts` | Adicionado `auth_login_success` no audit log |
| `app/api/auth/set-password/route.ts` | Validação de rowCount (não falha silenciosamente) |
| `app/api/auth/logout/route.ts` | Revoga jti antes de limpar cookie |
| `app/api/auth/logout-all/route.ts` | Novo endpoint — incrementa `session_version` |
| `app/api/auth/request-recovery/route.ts` | Novo endpoint — envia email de recovery |
| `app/api/onboarding/provision/route.ts` | Fallback URL `app.grupovelas.com.br` → `pulse.grupovelas.com.br` |
| `middleware.ts` | CORS `app.grupovelas.com.br` → `pulse.grupovelas.com.br` |
| `app/(auth)/convite/page.tsx` | Suspense + redirect `/configuracoes/whatsapp` → `/` |
| `app/(auth)/entrando/page.tsx` | Suspense adicionado |
| `app/(auth)/login/page.tsx` | Suspense + leitura de `?erro=oauth_*` com mensagens legíveis |
| `app/(auth)/recuperar/page.tsx` | Nova página de recuperação de senha |
| `lib/server/email.ts` | Templates HTML completos (botão, estrutura, anti-spam) |
| `database/migrations/0006_auth_users.sql` | DROP IF EXISTS do schema legado + restaura FK tenant_members |

---

## Blocos de segurança ainda pendentes (do checklist original)

- **I** — Compliance & Governance (Privacy Policy, DPA, access control matrix)
- **J** — Testing & Verification (suite de segurança, SAST, cross-tenant tests) — depende de ambiente
- **K** — Multi-tenancy Isolation (RLS) — migrations escritas, aplicar quando EC2 estiver pronto
- **L** — Documentation (ADRs, OpenAPI, SBOM)

Referência: `2026-07-30-security-hardening-checklist.md`

---

## Como retomar

1. Ler este handoff
2. Para continuar hardening: ir para **Bloco I** (zero dependência de infra)
3. Para ir a prod: resolver as pendências de infra acima primeiro (Google Console + Resend DNS + Secrets Manager)
4. `npx tsc --noEmit` — confirma zero erros antes de qualquer mudança
