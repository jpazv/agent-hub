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

- **Pulse**: Fase 0 do plano **concluida**. Staging (`pulse-staging`) linkado e com as 14 migrations do projeto antigo aplicadas sem erro. Login do Supabase exigiu atencao: a primeira tentativa autenticou numa conta sem acesso a org `tnumeveypqsklzezdksf`; resolvido relogando com `jpazevedomoreiraa@grupovelas.com.br`.
- **Bloqueio unico pra Fase 1**: o plano completo (`wondrous-hopping-gizmo.md`) esta em `/Users/grupovelas/.claude/plans/` no `mac-grupovelas`, pasta que **nao sincroniza via iCloud**. Precisa ser trazido pra uma pasta sincronizada (`~/Documents` ou `~/Desktop`) antes de continuar no `macbook-jpazv`.

## Proximo passo recomendado

Trazer `wondrous-hopping-gizmo.md` pra uma pasta sincronizada e iniciar a
Fase 1 do plano (migrations novas: `tenant_members`, RLS policies reais,
mover secrets pra Vault, dropar indice obsoleto, validar isolamento
multi-tenant com 2 tenants sinteticos em staging). Ver
`memory/handoffs/2026-07-22-pulse-rebuild-fase0-macbook.md` pro estado exato.
