# Handoff — 2026-07-22 — Pulse (Fase 3 concluída: Frontend)

## De onde veio

Continuação de `memory/handoffs/2026-07-22-pulse-rebuild-fase2.md`. Repo:
`https://github.com/jpazv/pulse` (privado) — `docs/plan-reconstrucao.md` tem
o plano completo, não depende mais do hub.

## O que foi feito (Fase 3 completa — 3 checkpoints, todos commitados/pushed)

**1/3 — Fundação + auth + Rede:**
- shadcn/ui nesta versão usa **Base UI, não Radix** — descoberta importante:
  `Trigger`/`Close` usam prop `render={<Elemento/>}`, não `asChild` com
  children. Vale pra qualquer componente novo (Dialog, Select, DropdownMenu
  já usados assim).
- TanStack Query com polling de 20s (decisão do plano: Realtime só depois de
  validar RLS multi-tenant em produção).
- `app/(auth)/{login,signup}` como páginas de verdade (antes era 1 componente
  com toggle).
- Backend de onboarding (`signup`, `units`) portado pro modelo
  `tenant_members`.
- Todos os endpoints de `lib/dashboardHandlers.js` portados como Route
  Handlers separados (não precisa mais do hack de 1 arquivo só pra caber no
  limite de 12 functions do Hobby).
- Página Rede: KPIs, hero chart de tendência, histograma, heatmap, ranking
  por unidade — direção visual PostHog.

**2/3 — Espera, Conversas+CRM, Alertas real, Secretárias:**
- Espera: fila com urgência por bucket de tempo.
- Conversas: lista paginada + `/conversas/[id]` com chat (bolhas) e resposta
  manual (vira CRM).
- **`/api/alertas/*`**: endpoint novo — fecha a dívida que a auditoria
  encontrou (`AlertasPage` era só visual antes). GET config, PATCH
  thresholds, POST/DELETE recipients.
- **`/api/secretarias/*`**: CRUD novo — antes só existia a contagem no RPC,
  sem forma de cadastrar pelo produto.

**3/3 — Conexão WhatsApp (Embedded Signup):**
- Port de `ConnectWhatsApp.jsx`, consumindo o backend idempotente já pronto
  da Fase 2. Env vars agora `NEXT_PUBLIC_META_APP_ID`/`NEXT_PUBLIC_META_CONFIG_ID`/
  `NEXT_PUBLIC_WHATSAPP_EMBEDDED_SIGNUP_ENABLED`.

**Estado final da Fase 3**: 96 testes (unit + integração real contra
staging), `tsc`/`eslint`/`next build` limpos em cada commit. Fluxo completo
signup→login→dashboard validado via HTTP real contra o dev server (não só
chamada direta de função nos testes).

## Pendências conhecidas, deixadas explícitas (não esquecidas)

- **Embedded Signup sem teste live** — código pronto, aguardando Advanced
  Access da Meta (decisão do usuário na Fase 2, ainda vale).
- **Scheduling de `score-leads`/`detect-agendamentos`/`ask-compareceu`** —
  ainda não decidido, fica pra Fase 4.
- **`pg_cron` do `check-alerts`** — migration template no repo, não aplicado
  (falta URL real de produção).
- Sem testes de componente React (Vitest+RTL) — cobertura é toda na camada
  de API/backend, que é onde está a lógica crítica; UI é presentational
  sobre dados já validados. Gap conhecido, não bloqueador.
- `.env.local` (staging keys) existe só localmente, gitignored — precisa
  recriar em qualquer máquina nova (valores nos handoffs anteriores/no
  Supabase dashboard do projeto `pulse-staging`).

## Próximo passo: Fase 4 (corte de produção)

Ver seção "Fase 4" em `docs/plan-reconstrucao.md`: resolver as pendências de
scheduling acima, migrar 1 tenant piloto de baixo risco, rodar em paralelo
com o app antigo (`~/Documents/tempo-resposta-app`, que continua em produção
até aqui), desligar o antigo só depois de confirmar estabilidade.
