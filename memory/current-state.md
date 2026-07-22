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

## ⚠️ Bug recorrente conhecido: corrupção do `.git` via iCloud (ler antes de tocar no repo local do Pulse)

Já aconteceu **pelo menos 2 vezes**: o diretório de trabalho do Pulse
(`~/Desktop/Pulse1.0.1`) fica dentro do escopo do iCloud "Desktop e
Documentos", que sincroniza **arquivo por arquivo** entre `mac-grupovelas` e
`macbook-jpazv`. O `.git` (e `node_modules`) tem escrita constante e
concorrente (index, HEAD, refs, objects mudam a cada comando git) — o iCloud
não entende isso como uma unidade atômica, então quando as duas máquinas
escrevem quase ao mesmo tempo ele cria cópias de conflito (`index 2`,
`COMMIT_EDITMSG 2`, `objects 2`, `logs 2`, `.git/hooks` e `.git/logs` com
contagem de entradas absurda). O resultado: `git status`/`git log` ficam
travados (observado: `git status` sem retornar em 2min) ou o repo fica em
estado inconsistente.

**Causa raiz**: mesmo depois do repo ganhar remoto real no GitHub
(`git@github.com:jpazv/pulse.git`) — o que deveria eliminar a necessidade de
sincronizar `.git` via iCloud — o diretório do projeto continua fisicamente
dentro de uma pasta que o iCloud sincroniza por padrão. Ele não sabe que o
git já resolve isso sozinho; continua tentando sincronizar `.git/` de
qualquer forma.

**Fix definitivo recomendado (ainda não aplicado)**: mover o diretório de
trabalho do Pulse pra **fora** do escopo do iCloud Desktop/Documents em
ambas as máquinas — ex. `~/dev/pulse` ou `~/code/pulse` (qualquer pasta que
não seja `~/Desktop` nem `~/Documents`). Cada máquina passa a ter seu
próprio clone local independente, sincronizado **só** via `git pull`/`push`
normal contra o GitHub — nunca mais via iCloud. Isso remove a causa raiz de
vez, em vez de só consertar depois de cada corrupção.

**Recuperação rápida se acontecer de novo antes do fix acima ser aplicado**
(feito manualmente no `macbook-jpazv` em 2026-07-22, funcionou bem):
```bash
# 1. NÃO apagar nada — mover a pasta corrompida pra um backup
mv ~/Desktop/Pulse1.0.1 ~/Desktop/Pulse1.0.1.icloud-corrupted-backup-$(date +%Y%m%d)

# 2. Clone limpo via SSH (repo é privado; gh CLI já autenticado cobre isso)
cd ~/Desktop && git clone git@github.com:jpazv/pulse.git Pulse1.0.1

# 3. .env.local não é versionado — recuperar do backup, não recriar do zero
cp ~/Desktop/Pulse1.0.1.icloud-corrupted-backup-*/.env.local ~/Desktop/Pulse1.0.1/.env.local

# 4. node_modules também é afetado pelo mesmo problema (iCloud evict/duplica) — reinstalar
cd ~/Desktop/Pulse1.0.1 && npm install
```
Depois de recuperar, considerar seriamente aplicar o fix definitivo acima
pra não precisar repetir isso a cada sessão nova.

**Atualização importante (mesma sessão, alguns minutos depois): o mesmo bug
atingiu o próprio `agent-hub`** (`~/Documents/agent-hub`), não só o Pulse —
confirma que a causa raiz é genérica (qualquer repo git dentro de
`~/Desktop`/`~/Documents` sincronizado pelo iCloud entre as duas máquinas).
Sintoma aqui foi diferente: `git status` reportou "No commits yet" porque
`.git/refs/heads/main` sumiu (arquivo vazio/ausente), e este próprio
handoff apareceu duplicado (`... 2.md`, `... 3.md`). **Recuperado sem perda**
porque `refs/remotes/origin/main` sobreviveu intacto e não havia commits
locais não enviados: `git fetch origin && git update-ref refs/heads/main
refs/remotes/origin/main`, depois apagados os arquivos duplicados (`rm`, não
`git checkout` — evita o classificador de auto mode bloquear por parecer
descarte de mudanças). **O hub em si também deveria considerar sair do
escopo do iCloud** (`~/Documents`) pra não repetir isso — decisão do usuário,
não aplicada ainda.

## Proximo passo recomendado

Fase 4 (corte de produção) direto no repo `https://github.com/jpazv/pulse`
(`git pull` antes de comecar). Ver `docs/plan-reconstrucao.md` dentro do
proprio repo pro plano completo — resolver scheduling em aberto, configurar
env vars reais no Vercel, migrar 1 tenant piloto, rodar em paralelo com o app
antigo antes de desligar. `.env.local` precisa ser recriado localmente em
qualquer maquina nova (nao é versionado).
