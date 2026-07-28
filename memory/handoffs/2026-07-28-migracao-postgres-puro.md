# Handoff — Pulse: migração Supabase → Postgres puro (AWS RDS)

**Data:** 2026-07-28
**Máquina:** mac-grupovelas
**Repo:** `~/dev/pulse` (Vercel `pulse-app`)
**Plano completo:** `~/.claude/plans/delightful-sprouting-karp.md`

---

## FASE ATUAL: migração para Postgres puro

**Decisão tomada em 28/07/2026.** O Pulse sai do Supabase para Postgres
gerenciado próprio no AWS RDS. Não é volume que motiva (43 conversas, 78
mensagens; projeção de ~2 GB com 100 clínicas) — é decisão de infraestrutura.

Toda sessão nova deve assumir **Postgres puro** como destino, não Supabase. O
`docs/plan-reconstrucao.md` dentro do repo `pulse` está desatualizado nesse
ponto: ele assume Supabase como banco + Auth na premissa da linha 18 e na
linha 31. Não seguir aquele documento para decisões de infraestrutura.

## Escolhas de arquitetura

| Tema | Decisão |
|---|---|
| Acesso a dados | SQL puro com `pg` (node-postgres). **Sem ORM.** |
| Autenticação | Própria, no Postgres (schema `app_auth`). Google OAuth continua. |
| Sessão | Token opaco em tabela, **não JWT** (revogação é requisito). |
| Senha | `@node-rs/argon2` (prebuilt, sem node-gyp). |
| Isolamento | **Na aplicação.** RLS e as 7 policies são removidas. |
| Segredos do WhatsApp | Coluna cifrada com `pgcrypto`, chave FORA do banco. |
| Schema | Baseline consolidado; as 21 migrations viram histórico. |
| Corte | Seco, sem migrar dado — o atual é de teste. |
| Usuários | Recriados do zero (não migrar hashes). |
| Hospedagem do app | Fica na Vercel por ora. Decisão separada, depois do banco. |

## Ordem das fases

**A — Fundação.** Handoff (este arquivo), camada `pg`, runner de migrations,
baseline de schema, correção do `verifyCronSecret`.

**B — Camada de dados.** Porte das 81 chamadas `.from(...)` (27 arquivos),
Vault → pgcrypto, agendamento dos crons.

**C — Autenticação.** Por último, deliberadamente: é o maior risco, e chegar
nela com a camada de dados estável significa que os 13 testes de integração já
estarão rodando contra o Postgres novo.

## Bloqueadores duros (não existem no RDS)

- **`supabase_vault`** — `whatsapp_connections` tem 2 colunas com FK física para
  `vault.secrets(id)`, e `20260722160000_secrets_vault.sql` usa
  `vault.create_secret()` e a view `vault.decrypted_secrets`. **É por isso que
  replay das migrations é impossível** — não é inconveniência, é bloqueador
  absoluto. Daí o baseline consolidado.
- **`pg_net`** — proprietário do Supabase. Consequência prática: **o banco não
  pode chamar HTTP**, então agendamento de cron dentro do banco está fora.
- **Supabase Auth** — 8 métodos em uso e 2 FKs para `auth.users`
  (`tenant_members.user_id` e o legado `tenants.auth_user_id`, nunca dropado).
- `auth.uid()` em 6 linhas de policy; roles `authenticated`/`anon`/`service_role`.

## O risco silencioso de maior alcance

**O driver `pg` devolve tipos diferentes do PostgREST para as mesmas colunas.**
Não gera erro de TypeScript, não quebra na hora, aparece três telas depois:

| Caso | PostgREST devolvia | `pg` devolve |
|---|---|---|
| `numeric` (`tpr_minutos`, `temperatura_lead`, `qualidade_atendimento`, toda `tpr_daily_rollup`) | `number` | **`string`** |
| `count(*)` (int8) | `number` | **`string`** |
| `timestamptz` / `date` | string ISO | **objeto `Date`** |

`lib/server/live-stats.ts:30` já faz `Number(...)` e é o **único** ponto
blindado — o que dá falsa sensação de segurança.

Tratamento: `setTypeParser` no bootstrap fixando `date`/`timestamptz` como
string e `int8` como número; `numeric` **não** convertido globalmente, mas com
cast `::float8` explícito no SQL onde o consumidor quer número.

Outros dois modos de falha silenciosa:
- **`join` interno onde o PostgREST devolvia `null` faz a linha desaparecer.**
  Usar `join` só onde a FK é `not null`; caso contrário `left join`.
- **`on conflict do nothing` sem coluna explícita** engole violação de qualquer
  constraint única. No dedup de retry da Meta
  (`lib/server/webhook-processing.ts:119`), especificar `(wa_message_id)`.

## Achados de segurança que entram de carona

**`verifyCronSecret` tem bypass aberto.** `lib/server/cron-auth.ts:14`:
`if (!cronSecret) return true`. Corrigir para fail-closed com comparação
constant-time. ⚠️ Antes de mergear, `CRON_SECRET` precisa existir nos ambientes
da Vercel — virar o fail-closed sem a env faz os 5 crons retornarem 401
**silenciosamente**, e alertas e scoring param sem erro visível.

**Não existe teste de isolamento entre clínicas.** Hoje a RLS pode estar
mascarando um bug de aplicação. Depois de removê-la, `requireTenant` é a única
defesa. O teste é **pré-requisito** da remoção de RLS, não tarefa de
acompanhamento.

**Rotas `[id]` e IDOR.** Com o isolamento saindo para a aplicação, todo
`UPDATE/DELETE ... where id = $1` precisa ganhar `and tenant_id = $2`.

**`email_verificado` é o item mais fácil de perder na tradução.** É a guarda que
impede reivindicar a clínica de um cliente conhecendo só o email dele. Precisa
valer em `signup` e no callback do Google (`email_verified === true` do
`id_token`).

**A chave do pgcrypto não pode viver no banco.** É a propriedade que o Vault
dava: dump vazado não deve decifrar nada. Injetada por transação com
`set_config('pulse.secrets_key', $1, true)` — o `true` é essencial porque `SET`
de sessão não sobrevive a PgBouncer em transaction mode.

## Dívidas que a migração obriga a resolver

- **Não existe runner de migrations.** Sem `config.toml`, sem CI, sem script;
  aplicação manual. Há migration duplicada byte-a-byte
  (`20260717160000_rede_stats_tendencia 2.sql`, sufixo do Finder). O runner novo
  valida o nome com regex e falha — o problema desaparece por construção.
- **`check-alerts` nunca foi agendado em nenhum ambiente.** Precisa rodar a cada
  ~5 min. `20260722190000_check_alerts_pg_cron.sql` é 100% comentário. Só
  `rollup-daily` está agendado, no `vercel.json`. Destino: EventBridge Scheduler.
- `lib/types/database.ts` (843 linhas) é output de `supabase gen types` commitado
  à mão, sem script de regeneração. Será descartado.
- 5 rotas de dashboard sem teste algum (`conversas`, `rede`, `espera`,
  `conversa`, `enviar-mensagem`).

## Rede de segurança

13 arquivos `*.integration.test.ts` batem em banco real e cobrem os contratos
HTTP de quase todas as rotas. 7 unitários puros não mudam. Os de integração
confiam em `ON DELETE CASCADE` para limpeza — que sobrevive intacto ao baseline.

Estratégia: extrair helpers de seed e de sessão **antes** de portar (o setup está
duplicado nos 13), e trocar a origem do token sem tocar nos `expect`. Se
`/api/dashboard/overview` continua 200 com token nosso e 401 sem, a substituição
está certa.

Durante o porte haverá **duas bases vivas ao mesmo tempo** — parte dos testes
contra o RDS, parte contra o Supabase. É andaime, não estado final.

## Pendências anteriores que seguem abertas

- **Rotacionar `META_APP_SECRET`** — circulou em texto plano no chat e no
  histórico do shell. Depois de rotacionar, atualizar no Vercel do `pulse-app` e
  do `tempo-resposta-app`; o webhook para de validar assinatura até isso.
- `WHATSAPP_VERIFY_TOKEN` e `WHATSAPP_APP_SECRET` estão setadas no Vercel mas
  **não deployadas** — o webhook rejeita tudo até o próximo deploy.
- Embedded Signup segue bloqueado por Acesso Avançado da Meta (`#2655111`). Ver
  handoff de 2026-07-27. Nada disso muda com a migração de banco.
- Responsividade mobile foi implementada mas **não verificada visualmente**.
