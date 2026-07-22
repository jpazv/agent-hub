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

## ✅ Atualização — Fase 0 concluída (mesmo dia, sessão seguinte)

O bloqueio do `supabase login` foi resolvido pelo usuário. Detalhe
importante: **a primeira tentativa de login autenticou numa conta Supabase
errada** (sem acesso à org `tnumeveypqsklzezdksf` "Grupo Velas jpazvOrg") —
`supabase projects list` não mostrava o `pulse-staging` e `supabase link`
falhava com `LegacyLinkProjectStatusError` (sem privilégios). Usuário
deslogou e logou de novo com a conta certa
(`jpazevedomoreiraa@grupovelas.com.br`), aí sim `pulse-staging` apareceu na
lista.

Depois disso:

1. `supabase link --project-ref fiswngbbjpezivneiete` — ok.
2. `supabase db push --password <PULSE_STAGING_DB_PASSWORD>` (senha lida de
   `.staging-supabase-credentials`) — **as 14 migrations aplicaram todas sem
   erro** no `pulse-staging`.
3. `supabase/.temp/` (cache local do CLI, sem segredos) adicionado ao
   `.gitignore`.
4. Commit `cf887a2`: "fase 0: linka staging Supabase e aplica migrations
   iniciais".

**Fase 0 do plano está concluída.** Scaffold Next.js, shadcn/ui, deps de
dados/teste, staging Supabase linkado e com as migrations do projeto antigo
aplicadas.

## ⚠️ Único bloqueio restante antes da Fase 1

**O plano completo (`wondrous-hopping-gizmo.md`) não está acessível no
macbook-jpazv.** Ele vive em `/Users/grupovelas/.claude/plans/` no
`mac-grupovelas`, pasta que **não sincroniza via iCloud** (diferente de
`~/Documents` e `~/Desktop`, que sincronizam). Confirmado via busca — não
existe cópia em `~/Documents` nem `~/Desktop` neste macbook.

Pra seguir com a Fase 1 (migrations novas: `tenant_members`, RLS policies
reais, mover secrets pra Vault, dropar índice obsoleto, validar isolamento
multi-tenant com 2 tenants sintéticos), alguém precisa trazer esse arquivo
pra uma pasta sincronizada — por exemplo movê-lo/copiá-lo pra dentro de
`~/Documents` no `mac-grupovelas`, ou colar o conteúdo diretamente numa
sessão.

## Task list desta sessão (não persiste entre sessões)

8 tasks no Claude Code, todas resolvidas exceto a última: npm install (✅),
shadcn init (✅), deps de dados/UI (✅), deps de teste (✅), supabase
login+link (✅, com o desvio de conta acima), copiar migrations (✅),
commit+handoff (✅), recuperar plano `wondrous-hopping-gizmo.md` (⏳
bloqueado, ver acima).
