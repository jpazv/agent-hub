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
- Iniciando **Fase 2** (backend core): portar `leadScore`/`tpr`/`agendamentoDetector`/`transcricao` pra TS com testes, depois webhook (fix de assinatura), Embedded Signup idempotente, crons.

## Proximo passo recomendado

Continuar a Fase 2 direto no repo `https://github.com/jpazv/pulse` (`git pull`
antes de comecar, em qualquer maquina). Ver `docs/plan-reconstrucao.md` dentro
do proprio repo pro plano completo — nao depende mais do hub nem do iCloud
pra esse arquivo.
