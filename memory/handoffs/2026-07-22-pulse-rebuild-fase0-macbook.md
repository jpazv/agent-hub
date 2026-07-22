# Handoff — 2026-07-22 — Pulse (continuação da Fase 0 no macbook-jpazv)

## De onde veio

Continuação de `memory/handoffs/2026-07-22-pulse-rebuild-fase0.md` (sessão no
`mac-grupovelas`). Ler aquele handoff primeiro se ainda não leu — ele tem o
contexto completo do plano, schema, staging Supabase etc.

## Confirmação do aviso do handoff anterior

`~/Desktop/Pulse1.0.1` **apareceu normalmente no `macbook-jpazv`** via iCloud
("Desktop e Documentos" sincroniza ambas as pastas juntas nesta conta) — git
local com o commit inicial, `.staging-supabase-credentials` e o scaffold
estavam todos intactos. Não foi necessário nenhum plano B (remoto GitHub ou
mover pra `~/Documents`).

## O que foi feito nesta sessão (macbook-jpazv)

Segui a lista de próximos passos do handoff anterior:

1. `npm install` no scaffold — 357 pacotes, ok (3 vulnerabilidades
   moderadas/altas reportadas pelo `npm audit`, não tratadas ainda —
   avaliar depois, não são bloqueantes pra Fase 0).
2. `npx shadcn@latest init -d` (defaults) — criou `components.json`,
   `components/ui/button.tsx`, `lib/utils.ts`, atualizou `app/globals.css`.
3. `npm install @supabase/supabase-js @supabase/ssr @tanstack/react-query recharts zod`
4. `npm install -D vitest @testing-library/react`
5. Copiei as 14 migrations de `~/Documents/tempo-resposta-app/supabase/migrations/`
   pra `~/Desktop/Pulse1.0.1/supabase/migrations/` (conferi que nenhuma tem
   segredo embutido — o comentário sobre `CRON_SECRET` em
   `20260716151500_pg_cron_extensions.sql` é só documentação de que o
   `cron.schedule` real é aplicado à parte, fora do arquivo).
6. Commitei tudo isso localmente em `~/Desktop/Pulse1.0.1` (commit
   `3c45f22`, "fase 0: shadcn init, deps de dados/UI/teste, migrations do
   projeto antigo"). Ainda sem remoto configurado.

## ⚠️ Bloqueado — precisa de ação do usuário

**`supabase login` não pôde ser automatizado neste macbook.** O CLI do
Supabase não estava instalado (instalei via `brew install supabase/tap/supabase`,
v2.109.1), mas o login em si exige fluxo interativo de navegador — falha em
ambiente não-TTY com `LegacyLoginMissingTokenError`. Precisa de um dos dois:

- Rodar `supabase login` manualmente num terminal interativo nesta máquina
  (abre o navegador pra autenticar), ou
- Gerar um access token em https://supabase.com/dashboard/account/tokens e
  exportar `SUPABASE_ACCESS_TOKEN` (ou usar `supabase login --token <token>`).

Depois disso, rodar (senha do banco de staging em
`.staging-supabase-credentials`, só existe nesta e na outra máquina, não vai
pro git):

```bash
cd ~/Desktop/Pulse1.0.1
supabase link --project-ref fiswngbbjpezivneiete
supabase db push   # aplica as 14 migrations já copiadas em supabase/migrations/
```

## Pendente / próximo passo imediato

1. Resolver o login/link do Supabase acima (bloqueado por ação do usuário).
2. `supabase db push` pra aplicar as migrations no staging.
3. Validar que as migrations aplicaram sem erro (elas foram escritas pro
   projeto antigo — checar se alguma depende de estado/dados que não existe
   num banco novo, ex. `secretaries`, RPCs de `rede_stats`).
4. Seguir pra **Fase 1 do plano** (migrations novas: `tenant_members`, RLS
   policies reais, mover secrets pra Vault, dropar índice obsoleto, validar
   isolamento multi-tenant com 2 tenants sintéticos em staging) — ver plano
   completo em `/Users/grupovelas/.claude/plans/wondrous-hopping-gizmo.md`
   (checar se esse arquivo está acessível neste macbook; se não, pedir pro
   usuário reexportar/copiar).

## Task list desta sessão (não persiste entre sessões)

7 tasks criadas no Claude Code: npm install (✅), shadcn init (✅), deps de
dados/UI (✅), deps de teste (✅), supabase login+link (⏳ bloqueado),
copiar migrations (✅ copiadas, mas `db push` ainda pendente — depende do
login), commit+handoff (✅ este arquivo).
