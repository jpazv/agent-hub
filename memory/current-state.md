# Current State

Last updated: 2026-07-22

## Onde estamos

| No | Status |
|---|---|
| mac-grupovelas | ✅ operacional |
| macbook-jpazv | ✅ operacional — `~/Desktop/Pulse1.0.1` confirmado acessivel via iCloud, trabalho continuado no projeto pulse |

## O que foi feito nesta sessao (2026-07-22)

- Primeiro projeto real cadastrado no hub: `pulse` (`registry/projects.yaml`) — reconstrução full-stack do SaaS `tempo-resposta-app` (WhatsApp/tempo de resposta)
- Auditoria completa do codigo atual + plano de reconstrucao aprovado (plan mode) em `/Users/grupovelas/.claude/plans/wondrous-hopping-gizmo.md`
- Projeto Supabase de staging criado (`pulse-staging`, regiao Sao Paulo)
- Scaffold inicial do novo app (Next.js+TS+Tailwind) criado e commitado localmente em `~/Desktop/Pulse1.0.1` (sem remoto ainda)
- Handoff detalhado com estado exato e proximos comandos: `memory/handoffs/2026-07-22-pulse-rebuild-fase0.md`
- **Continuado no macbook-jpazv**: `~/Desktop/Pulse1.0.1` confirmado sincronizado via iCloud. `npm install`, `shadcn init`, deps de dados/UI (supabase-js/ssr, tanstack-query, recharts, zod) e deps de teste (vitest, testing-library) instaladas. Migrations do projeto antigo copiadas pra `supabase/migrations/`. Tudo commitado localmente (`3c45f22`). Ver `memory/handoffs/2026-07-22-pulse-rebuild-fase0-macbook.md`.

## Trabalho em andamento

- **Pulse**: Fase 0 e Fase 1 do plano **concluidas**. Fase 1: `tenant_members` (multi-usuario por tenant), RLS policies reais, secrets movidos pro Supabase Vault, indice obsoleto dropado — tudo validado em staging com script de teste (2 tenants sinteticos, isolamento confirmado). Um bug real foi encontrado e corrigido durante a validacao: recursao infinita numa policy de RLS (`tenant_members_select`). Ver `memory/handoffs/2026-07-22-pulse-rebuild-fase1.md`.
- **Mudanca estrutural**: `~/Desktop/Pulse1.0.1` corrompeu o `.git` local (iCloud sincronizando `.git/objects` entre as duas maquinas simultaneamente) e depois `node_modules` (mesma causa raiz). Ambos corrigidos. O projeto agora tem remoto real no GitHub (`https://github.com/jpazv/pulse`, privado) — dev daqui pra frente usa `git pull`/`push` normal, nao depende mais do iCloud pra sincronizar o `.git` entre maquinas. O plano completo tambem foi movido pra dentro do repo (`docs/plan-reconstrucao.md`), resolvendo o bloqueio anterior de ele estar numa pasta nao-sincronizada.
- **Fase 2 (backend core) concluida**: scoring puro, webhook (fix de assinatura), Embedded Signup idempotente (portado mas SEM teste live — usuario ainda aguarda Advanced Access da Meta, decisao explicita de nao testar contra a Graph API real agora), 5 crons portados (rollup-daily, score-leads, check-alerts, detect-agendamentos, ask-compareceu). 81 testes, tsc/eslint/build limpos. Ver `memory/handoffs/2026-07-22-pulse-rebuild-fase2.md`.
- **Fase 3 (frontend) concluida**: auth multi-usuario, dashboard completo (Rede, Espera, Conversas+CRM, Alertas real — dívida da auditoria resolvida, Secretarias CRUD novo, conexao WhatsApp). shadcn nesta versao usa Base UI, nao Radix (prop `render`, nao `asChild`). 96 testes, tsc/eslint/build limpos. Ver `memory/handoffs/2026-07-22-pulse-rebuild-fase3.md`.
- **Polimento pos-Fase-3 + deploy**: verificacao visual real com Playwright (achou e corrigiu bug de redirect 404 e bordas quase invisiveis no design system), insight de qualidade de atendimento revelado com sutileza (checklist expansivel + toast de descoberta), modo demo (`NEXT_PUBLIC_DEMO_MODE`, dashboard le de JSON estatico, zero latencia), e **deploy em produção no Vercel**: https://pulse-app-steel-tau.vercel.app (login demo@pulse.local/demo12345). Ver `memory/handoffs/2026-07-22-pulse-mvp-instant-demo-e-deploy.md`.
- Decisoes/pendencias abertas (nao bloqueiam): scheduling de score-leads/detect-agendamentos/ask-compareceu e do pg_cron do check-alerts; env vars de producao real (Meta/cron/Groq) ainda nao configuradas no Vercel (só o modo demo funciona lá); conta Vercel sem GitHub conectado (deploy é manual via `vercel --prod`, nao automatico em push). Tudo pra Fase 4.

## Proximo passo recomendado

Fase 4 (corte de produção) direto no repo `https://github.com/jpazv/pulse`
(`git pull` antes de comecar). Ver `docs/plan-reconstrucao.md` dentro do
proprio repo pro plano completo — resolver scheduling em aberto, configurar
env vars reais no Vercel, migrar 1 tenant piloto, rodar em paralelo com o app
antigo antes de desligar. `.env.local` precisa ser recriado localmente em
qualquer maquina nova (nao é versionado).
