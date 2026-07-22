# Handoff — 2026-07-22 — Pulse (Fase 2 concluída: Backend core)

## De onde veio

Continuação de `memory/handoffs/2026-07-22-pulse-rebuild-fase1.md`. Nota
importante: o plano completo agora vive dentro do próprio repo do projeto
(`docs/plan-reconstrucao.md` em `https://github.com/jpazv/pulse`), não mais
só em `~/.claude/plans/` — qualquer sessão em qualquer máquina só precisa
clonar/pullar esse repo pra ter o plano completo. O hub deixou de ser
necessário pra continuidade deste projeto especificamente (mas o handoff
ainda é útil como registro cronológico entre sessões).

## Decisão de escopo tomada nesta sessão

Usuário decidiu **não portar o Embedded Signup pra teste live agora** —
ainda está aguardando acesso (via empresa parceira ou App Review próprio) pra
ter Advanced Access aprovado na Meta. Instrução: portar o código e deixá-lo
pronto ("assentado"), mas sem validação ponta a ponta contra a Graph API real
— só testado com mocks. Isso está registrado no topo do arquivo
`app/api/onboarding/whatsapp-connect/route.ts`.

## O que foi feito (Fase 2 completa — 5/5 etapas do plano)

Todos os commits estão em `https://github.com/jpazv/pulse` (main), um por
etapa, com mensagens detalhadas. Resumo:

1. **Lógica pura de scoring** (`lib/scoring/`): `lead-score.ts`, `tpr.ts`,
   `agendamento-detector.ts` — port 1:1 do JS original, com tipos.
2. **Webhook** (`app/api/webhook/route.ts`): Route Handler, com o fix real
   do bug de assinatura (P0 da auditoria — antes aceitava payload não
   assinado se `WHATSAPP_APP_SECRET` não estivesse configurado, agora falha
   fechado). Payload validado com Zod. `access_token` lido do Vault.
3. **Embedded Signup** (`app/api/onboarding/whatsapp-connect/route.ts`):
   portado com idempotência real (cada etapa da Graph API persiste antes de
   seguir pra próxima) — **sem teste live**, só mocks (ver decisão acima).
4. **3 crons ativos** (`rollup-daily`, `score-leads`, `check-alerts`) como
   Route Handlers.
5. **Funil de comparecimento** (`detect-agendamentos`, `ask-compareceu`):
   usuário decidiu portar agora (não deixar como backlog), scheduling ainda
   em aberto.

**Estado final**: 81 testes (unitários + integração real contra staging com
Graph API mockada), `tsc`/`eslint`/`next build` limpos em cada commit.

## Achados/decisões importantes que sobrevivem além do código

- **Scheduling de `score-leads`, `detect-agendamentos`, `ask-compareceu`
  ainda não decidido** — precisam rodar mais de 1x/dia (Vercel Cron gratuito
  só permite diário), e o padrão antigo (n8n externo) foi flagado pela
  auditoria como não-versionado. Decisão explícita fica pra Fase 4, junto
  com a decisão de subir o Vercel pro plano Pro.
- **`check-alerts` pg_cron**: migration template criada
  (`supabase/migrations/20260722190000_check_alerts_pg_cron.sql`), mas
  **NÃO aplicada** — falta a URL real de produção (só existe a partir da
  Fase 4). Ficou versionada no git em vez de "só na cabeça de alguém"
  (era o achado P0 da auditoria), mas o agendamento de fato só acontece
  depois do deploy.
- Todos os secrets (`access_token`, `register_pin`) já vêm do Supabase Vault
  em todo código novo — nenhum lugar novo usa coluna em texto puro.

## Próximo passo: Fase 3 (Frontend)

Ver seção "Fase 3" em `docs/plan-reconstrucao.md`: auth multi-usuário,
dashboard com TanStack Query (Realtime só depois de validar RLS com múltiplos
tenants em produção), `AlertasPage` conectada de fato ao motor real, CRUD de
`secretaries`. Direção visual: PostHog como âncora (já registrado no plano).
