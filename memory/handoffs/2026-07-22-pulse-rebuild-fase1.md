# Handoff — 2026-07-22 — Pulse (Fase 1 concluída)

## De onde veio

Continuação de `memory/handoffs/2026-07-22-pulse-rebuild-fase0-macbook.md`
(Fase 0 concluída no macbook-jpazv). Esta sessão foi no `mac-grupovelas`.

## ⚠️ Mudança estrutural importante: projeto agora tem remoto no GitHub

`~/Desktop/Pulse1.0.1` corrompeu o `.git` local durante esta sessão — causa
raiz: **git + iCloud sync simultâneo em duas máquinas é uma combinação
perigosa** (o iCloud sincroniza arquivos individuais do `.git/objects`,
quebrando a integridade do object store; achamos um blob órfão, erro 42P07-like
a nível de git). O histórico antigo (2 commits triviais) foi descartado e
recriado a partir do estado atual dos arquivos (nenhum trabalho perdido, só
histórico). **Repo agora tem remoto real**: `https://github.com/jpazv/pulse`
(privado). Dev daqui pra frente: `git pull`/`git push` normalmente — não
depender do iCloud para sincronizar o `.git` entre `mac-grupovelas` e
`macbook-jpazv` nunca mais. O working tree continua em `~/Desktop/Pulse1.0.1`
(iCloud sync dos arquivos de trabalho é inofensivo, só o `.git` interno é o
problema).

Nota lateral: `node_modules` também ficou corrompido pelo iCloud (só 20MB de
664MB esperado) — sem relação com o git, mesma causa raiz (muitos arquivos
pequenos). Resolvido com reinstall limpo. Isso é esperado tolerar: rodar
`npm install` de novo em cada máquina, nunca confiar no `node_modules`
sincronizado.

Também: `~/.claude/plans/wondrous-hopping-gizmo.md` (o plano aprovado) foi
copiado pra `~/Desktop/Pulse1.0.1/docs/plan-reconstrucao.md` — está commitado
no repo agora, acessível em qualquer máquina via git, não depende mais de
pasta sincronizada nem do arquivo original em `~/.claude/plans/`.

## O que foi feito nesta sessão (Fase 1 do plano)

Ver `docs/plan-reconstrucao.md` no repo pro plano completo. Migrations novas
em `supabase/migrations/`, aplicadas e **validadas** em staging
(`pulse-staging`, ref `fiswngbbjpezivneiete`):

1. `20260722140000_tenant_members.sql` — tabela `tenant_members` (multi-usuário
   por tenant: owner/admin/secretaria, escopo opcional por unidade), função
   `current_tenant_ids()` (security definer), migração de dados de
   `tenants.auth_user_id`.
2. `20260722150000_rls_policies.sql` — RLS policies de leitura em
   tenants/units/conversations/messages/alert_recipients; `whatsapp_connections`
   trancada na tabela base (`using (false)`), exposta só via view
   `whatsapp_connections_public` (sem colunas sensíveis); `data_deletion_requests`
   com RLS habilitado sem policy (deny-all — era a única tabela sem RLS).
3. `20260722160000_secrets_vault.sql` — `access_token`/`register_pin` movidos
   pro Supabase Vault. Funções `set_whatsapp_secret`/`get_whatsapp_secret`
   (security definer, só `service_role` executa). Colunas antigas em texto
   puro **dropadas** (staging não tinha nenhuma linha real ainda).
4. `20260722170000_drop_obsolete_index.sql` — dropado
   `idx_conversations_aguardando` (achado da auditoria, obsoleto desde
   `aguardando_desde`).
5. `20260722180000_fix_tenant_members_recursion.sql` — **bug encontrado e
   corrigido durante a validação**: a policy `tenant_members_select` fazia
   subquery direta na própria `tenant_members`, causando recursão infinita
   de RLS (erro `42P17`) que quebrava em cascata `conversations`/`units`. Fix:
   usar `current_tenant_ids()` (que bypassa RLS por ser security definer) em
   vez de subquery correlacionada direta.

## Verificação feita (bate com a seção "Verificação" do plano)

`scripts/test-rls-isolation.mjs` — cria 2 tenants sintéticos + 2 usuários reais
via Supabase Auth, confirma via client `authenticated` (não `service_role`):
tenant A vê o próprio tenant e a própria conversation, NÃO vê nada do tenant B,
`select` sem filtro só retorna dado do próprio tenant, `whatsapp_connections`
(tabela base) retorna vazio, INSERT direto em `tenants` é bloqueado. **Todos
os 7 testes passaram** (depois do fix da recursão — antes dele, os testes de
`conversations` falhavam com 0 resultados mesmo pro próprio tenant, foi assim
que o bug foi pego).

`scripts/test-vault.mjs` — roundtrip de secret via `set_whatsapp_secret`/
`get_whatsapp_secret`, confirma que as colunas antigas não existem mais e que
o secret salvo é recuperado corretamente. Passou.

Ambos os scripts precisam de `PULSE_STAGING_ANON_KEY`/`PULSE_STAGING_SERVICE_KEY`
como env var pra rodar de novo (chaves do projeto `pulse-staging`, buscar via
`supabase projects api-keys --project-ref fiswngbbjpezivneiete` — não estão
salvas em nenhum arquivo do repo).

## Estado do staging (`pulse-staging`)

Todas as migrations (as 15 originais do projeto antigo + as 5 novas da Fase 1)
aplicadas e confirmadas. **Nota cosmética não-bloqueante**: `supabase migration
list` mostra duas linhas duplicadas com "Remote" vazio pra
`20260716142142`/`20260717160000` — resíduo de checksum drift de quando essas
migrations foram copiadas de forma diferente entre macbook/Mac mini via
iCloud antes do fix. Não afeta nada (schema real está correto, confirmado
pelos testes), só faz `db push` pedir `--include-all` se você tentar re-rodar
essas duas migrations específicas — não precisa, elas já estão aplicadas.

## Próximo passo: Fase 2 do plano (Backend core)

Ver seção "Fase 2" em `docs/plan-reconstrucao.md`: portar funções puras
(`leadScore`, `tpr`, `agendamentoDetector`, `transcricao`) pra TS com testes
Vitest primeiro (baixo risco), depois webhook (corrigindo bypass de
assinatura), depois Embedded Signup com idempotência real, depois crons.
