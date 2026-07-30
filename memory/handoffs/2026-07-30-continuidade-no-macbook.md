# Handoff — continuidade no MacBook: tudo sincronizado, próximo passo é onboarding Meta

**Data:** 2026-07-30
**Máquina de origem:** mac-grupovelas
**Motivo:** usuário vai continuar de outra máquina (macbook-jpazv)

---

## Estado: os três repos estão sincronizados com o GitHub

Nada mais preso em máquina nenhuma. Antes de começar, rodar `hub-down` (git pull)
nos três:

| Repo | HEAD | Estado |
|---|---|---|
| `~/dev/agent-hub` | `1490267` + este handoff | limpo, sincronizado |
| `~/dev/pulse` | `630d7b8` | limpo, sincronizado |
| `~/dev/raiox-mvp-html` (landing) | `5499ce6` | limpo, sincronizado |

⚠️ Havia uma alteração local em
`memory/handoffs/2026-07-28-pulse-postgres-docker-baseline-validada.md` que **não
é minha** (nunca commitei). Se ela importa, ver no `mac-grupovelas`; deixei
intocada de propósito em todos os commits.

---

## O que foi fechado na sessão de 29/07

Detalhe completo em
`memory/handoffs/2026-07-29-pulse-fase-b-fechada-e-pentest-seguranca.md` —
**ler esse antes de mexer no `pulse`.** Resumo:

- **Fase B da migração Postgres concluída.** Todas as rotas operacionais e os 5
  crons ativos usam Postgres puro. 138 testes passando, 21 deles pentests.
- **Banco partido no caminho do lead corrigido** — onboarding gravava a connection
  no Supabase e o webhook lia do Postgres, então mensagem de lead real era
  descartada em silêncio.
- **2 vulnerabilidades ALTAS corrigidas, provadas por exploit**: sequestro de
  conexão de WhatsApp entre clínicas (IDOR, pré-existente e reproduzida por mim
  ao portar 1:1) e o consentimento de conteúdo que era cosmético (texto de
  paciente persistido na coluna `payload` e despejado no log com o telefone).
- **Endurecimento**: chave-mestra de cifra saiu do banco (AES-256-GCM no Node),
  resolvida a ambiguidade das duas implementações de cripto, idempotência de
  reentrega de webhook, tenant ativo determinístico, comparações constant-time,
  rate limit em `signup`/`provision`.

**Landing** (`5499ce6`, commitada agora): mockup do Hero com iPhone em ângulo e
print real do dashboard composto na tela, moldura por cima do conteúdo, fundo
transparente; e as 3 seções de pilares alinhadas à esquerda. Aprovado
visualmente, verificado via Playwright.

---

## Setup no MacBook antes de rodar o `pulse`

O Postgres de teste é um container Docker **local de cada máquina** — não vem no
git. No MacBook precisa existir um equivalente:

```bash
docker run -d --name pulse-postgres-test \
  -e POSTGRES_USER=pulse -e POSTGRES_PASSWORD=pulse -e POSTGRES_DB=pulse \
  -p 5432:5432 postgres:16

cd ~/dev/pulse
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npm run db:migrate
```

O runner aplica `0001_baseline.sql` e `0002_drop_secret_sql_functions.sql`.

Validar:

```bash
npx tsc --noEmit
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npx vitest run
DATABASE_URL="postgres://pulse:pulse@localhost:5432/pulse" npx vitest run tests/security/
```

Esperado: **138 passando, 45 skipped** (as skipped são integrações Supabase sem
env — normal). Se os pentests em `tests/security/` falharem, **parar e
investigar**: eles cobrem regressão de isolamento entre clínicas e de dado
sensível de paciente.

`PULSE_SECRETS_KEY` não está no `.env.local`; os testes que precisam dela a
definem sozinhos. Para rodar a app de verdade localmente, ela precisa existir.

---

## Próximo passo: onboarding Meta via app do parceiro

Plano completo (commitado): **`~/dev/pulse/docs/plan-onboarding-meta-partner-app.md`**
— arquitetura, mudanças de banco, endpoints, fluxo de Embedded Signup, riscos,
dependências do parceiro, critérios de sucesso, 5 fases e checklist do que precisa
estar pronto antes de testar com WABA real.

**Fase 1 pode começar já** (não depende do parceiro nem de infra):
- Migration com a tabela `meta_app_credentials` (app_id + app_secret cifrado, no
  mesmo padrão de `lib/server/secret-crypto.ts`) e as colunas novas em
  `whatsapp_connections` (`meta_app_credential_id`,
  `override_callback_verified_at`, `override_callback_uri`, `subscribed_at`).
- Helper `lib/server/pg-meta-app-credentials.ts`.

**Fase 3 está BLOQUEADA** pela resposta do parceiro. Motivo (seção 6 do plano): a
Meta assina o webhook com o App Secret do app **inscrito na WABA**, que seria o do
parceiro. Sem esse secret compartilhado, `isValidSignature` falha para toda
conexão feita via app do parceiro. **Não escrever código da Fase 3 antes disso** —
é bloqueador, não detalhe.

---

## Pendências de segurança em aberto (precisam de decisão, não de código)

Todas detalhadas no handoff de 29/07, seção 6:

1. **Evento perdido em falha transitória** — erro no processamento → responde 200
   → a Meta não retenta → sem dead-letter, o evento morre. Decidir entre devolver
   5xx ou persistir payload cru. (Mitiguei o pior caso: um evento não mata o lote.)
2. **Rate limit é por instância** — em serverless o teto efetivo é
   (limite × instâncias). Limite global exige Redis ou tabela.
3. `.max()` nos arrays do Zod em `lib/webhook/parse.ts` (baixa).
4. `updateConversation` aceita `Record<string, unknown>` e interpola nome de
   coluna — **não explorável hoje** (verificado: todas as chaves vêm de literais),
   mas a assinatura permite um call site futuro inseguro.

---

## Para "dar o webhook" ainda faltam 3 itens

1. **Não existe Postgres de produção** — só o Docker local. Precisa provisionar
   (RDS ou equivalente) e rodar `npm run db:migrate`.
2. **Configurar e DEPLOYAR no Vercel**: `DATABASE_URL`, `PULSE_SECRETS_KEY`, e as
   já setadas-mas-não-deployadas `WHATSAPP_APP_SECRET` / `WHATSAPP_VERIFY_TOKEN`
   (até o deploy, o webhook rejeita tudo).
3. **App Secret do parceiro** — depende deles.

Pendências operacionais que seguem: rotacionar `META_APP_SECRET` (circulou em
texto plano); `check-alerts` precisa rodar a cada ~5 min e **não tem scheduler em
nenhum ambiente** (só `rollup-daily` está no `vercel.json`).

---

## Não fazer sem confirmar

- Não fazer deploy nem alterar env var de produção/Vercel.
- Não trocar webhook/override URL na Meta.
- Não iniciar Fase C (auth própria no Postgres) antes de fechar onboarding.
- **Não "portar 1:1" sem auditar.** Dois defeitos da sessão de 29/07 vieram
  exatamente de reproduzir fielmente o comportamento antigo (o sequestro de
  conexão veio junto no port) ou de confiar num teste que nunca foi visto
  falhando.
- **Todo teste de segurança precisa ser verificado nos dois sentidos** — falhar
  sem a correção, passar com ela. Um pentest meu passou vacuamente na sessão
  passada e só apareceu porque desliguei a proteção de propósito para conferir.
