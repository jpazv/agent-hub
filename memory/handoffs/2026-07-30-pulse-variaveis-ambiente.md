# Handoff — Pulse: Variáveis de ambiente completas

**Data:** 2026-07-30  
**Repo:** `~/dev/pulse`

---

## Segredos — AWS Secrets Manager (`pulse/prod`)

Lidos em runtime via IAM role. Não precisam estar no build.

| Variável | Como obter |
|---|---|
| `DATABASE_URL` | `postgresql://pulse_app:<senha>@localhost:5432/pulse_prod` — senha definida ao criar o user Postgres no EC2 |
| `PULSE_SECRETS_KEY` | `openssl rand -hex 32` |
| `PULSE_PROVISIONING_SECRET` | `openssl rand -hex 32` — **mesmo valor** configurado no raiox-mvp-html |
| `CRON_SECRET` | `openssl rand -hex 32` |
| `WHATSAPP_APP_SECRET` | Meta for Developers → seu app → App Secret |
| `WHATSAPP_VERIFY_TOKEN` | Qualquer string aleatória — você define e coloca igual no painel Meta (Webhook → Verify Token) |
| `META_APP_ID` | Meta for Developers → App ID (versão server-side, usada na troca de token OAuth) |
| `META_APP_SECRET` | Meta for Developers → App Secret — **mesmo valor que `WHATSAPP_APP_SECRET`** |
| `GOOGLE_CLIENT_ID` | Google Cloud Console → Credentials → OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console → Credentials → OAuth 2.0 Client Secret |
| `RESEND_API_KEY` | resend.com → API Keys |
| `GROQ_API_KEY` | console.groq.com → API Keys |
| `SECURITY_ALERT_WEBHOOK_URL` | URL webhook Slack/Teams para alertas de segurança — opcional |
| `PULSE_APP_URL` | `https://pulse.grupovelas.com.br` — define domínio dos links de email e OAuth |
| `WHATSAPP_ALERT_TEMPLATE_NAME` | Nome do template de alerta aprovado no Meta |
| `WHATSAPP_COMPARECEU_TEMPLATE_NAME` | Nome do template de confirmação de comparecimento |

---

## Variáveis públicas — precisam estar no `.env.production` antes do `npm run build`

> ⚠️ São `NEXT_PUBLIC_` — embutidas no bundle em build time. O Secrets Manager não resolve isso.  
> Precisam estar no arquivo `.env.production` no EC2 antes de rodar `npm run build`.

| Variável | O que é | Onde achar |
|---|---|---|
| `NEXT_PUBLIC_META_APP_ID` | ID do app Meta — inicializa o FB SDK no browser | Meta for Developers → App ID |
| `NEXT_PUBLIC_META_CONFIG_ID` | ID da configuração do Embedded Signup | Meta for Developers → WhatsApp → Embedded Signup → ID da configuração |
| `NEXT_PUBLIC_WHATSAPP_EMBEDDED_SIGNUP_ENABLED` | Feature flag do botão "Conectar número" | Colocar `"true"` só após App Review da Meta ser aprovado |

---

## Com padrão — só configurar se quiser mudar

| Variável | Padrão |
|---|---|
| `DATA_RETENTION_DAYS` | `30` |
| `WDL_RETENTION_DAYS` | `90` |
| `ALERT_SIGNATURE_FAILURES` | `10` |
| `ALERT_RATE_LIMIT_HITS` | `50` |
| `ALERT_AUTH_FAILURES` | `20` |

---

## Não colocar em produção

| Variável | Motivo |
|---|---|
| `NEXT_PUBLIC_DEMO_MODE` | Só para dev local — ativa dados fake no dashboard |
| `NODE_ENV` | Next.js define automaticamente como `production` no build |

---

## Pendências externas obrigatórias antes de ir a prod

- **Google Cloud Console** → adicionar redirect URI autorizado: `https://pulse.grupovelas.com.br/api/auth/google/callback`
- **Resend** → verificar domínio `grupovelas.com.br` (SPF/DKIM) — sem isso emails de convite caem em spam
- **Meta** → App Review aprovado para liberar `NEXT_PUBLIC_WHATSAPP_EMBEDDED_SIGNUP_ENABLED=true`
- **Meta** → Webhook configurado apontando para `https://pulse.grupovelas.com.br/api/webhook`

---

## Crons — não rodam automaticamente no EC2

No EC2 não existe `vercel.json`. Usar o crontab em `docs/ec2-crontab.md`.  
O `vercel.json` foi corrigido com todos os 8 crons (estava com apenas 1 — os outros 7 nunca rodaram na Vercel).
