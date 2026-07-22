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

- **Pulse**: Fase 0 quase concluida — falta so `supabase login`/`link`/`db push` pra aplicar as migrations no staging. **Bloqueado por acao do usuario**: CLI do Supabase instalado (brew) mas `supabase login` exige fluxo interativo de navegador, nao automatizavel em sessao nao-TTY. Precisa rodar `supabase login` manualmente ou fornecer `SUPABASE_ACCESS_TOKEN`. Ver handoff mais recente pra comandos exatos.

## Proximo passo recomendado

Resolver o bloqueio do `supabase login` (acao do usuario) e rodar
`supabase link --project-ref fiswngbbjpezivneiete` + `supabase db push`
seguindo `memory/handoffs/2026-07-22-pulse-rebuild-fase0-macbook.md`. Depois
seguir pra Fase 1 do plano (tenant_members, RLS real, secrets no Vault).
