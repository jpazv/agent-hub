---
data: 2026-08-11
maquina: macbook-jpazv
projeto: Pulse / integracao Meta via parceiro (Scal) + acesso Google
status: pesquisa e documentos prontos; MCP do Google instalado mas SEM consentimento OAuth
proxima-acao: autenticar o MCP do Google e publicar a proposta como Google Doc
---

# Google MCP instalado + proposta de integracao Pulse × Scal pronta para virar Doc

## 0. A primeira coisa a fazer nesta sessao

**Gerar o Google Doc da proposta de integracao tecnica Pulse × Scal e mandar o
link para o JP.** O conteudo ja esta escrito e revisado — nao reescrever, nao
resumir, nao "melhorar". So publicar.

- **Fonte do conteudo:** `~/dev/pulse/docs/proposta-integracao-pulse-scal.md`
- **Titulo do Doc:** `Proposta de integracao tecnica — Pulse × Scal`
- **Destino:** Google Drive do JP (conta a confirmar com ele, ver §3)
- **Entrega:** o link do Doc, no chat.

O unico motivo de isso nao ter sido feito na sessao anterior: o MCP do Google
foi registrado **durante** aquela sessao, e ferramentas de MCP so entram no
registro na abertura da sessao. Nesta sessao elas devem existir. Confirmar com
uma busca por ferramentas `google-workspace` antes de qualquer outra coisa.

---

## 1. Estado do MCP do Google

### O que ja esta feito (nao refazer)

| Peca | Caminho | Estado |
|---|---|---|
| Credenciais OAuth | `~/.config/agents/google-oauth.env` | Criado, `chmod 600`, **fora de qualquer repo** |
| Wrapper do servidor | `~/.config/agents/google-workspace-mcp.sh` | Criado, executavel |
| Registro no Claude Code | `~/.claude.json` (escopo `user`) | `claude mcp add -s user google-workspace` feito |
| `uv` / `uvx` | `/opt/homebrew/bin` | Instalado (0.12.3) |
| Health check | — | `claude mcp list` → `google-workspace ✔ Connected` |
| Script de replicacao | `agent-hub/scripts/setup-google-mcp.sh` | Criado (para outras maquinas) |
| Regra no hub | `agent-hub/AGENT-HUB.md` | Secao "Google (Docs + Drive) — MCP no escopo `user`" |

Servidor: `uvx workspace-mcp --single-user --tools docs drive` (stdio).
Escopo deliberadamente limitado a **Docs e Drive** — nao Gmail, nao Calendar.

O `client_id` e do projeto Google Cloud `538719293602`. **O `client_secret` nao
esta neste handoff nem em nenhum arquivo do hub, de proposito** — vive so em
`~/.config/agents/google-oauth.env` nesta maquina.

### O que FALTA (o trabalho desta sessao)

1. **Consentimento OAuth — nunca foi feito.** Na primeira chamada o servidor
   devolve uma URL de autorizacao. Repassar a URL ao JP; ele autoriza no
   browser. O token fica cacheado localmente depois disso.
2. **Confirmar no Google Cloud Console que Docs API e Drive API estao
   habilitadas** no projeto `538719293602`. O JP foi avisado mas nao confirmou.
   Se nao estiverem, a criacao do Doc falha com mensagem pouco obvia (erro de
   API desabilitada, nao de permissao). Esse e o modo de falha mais provavel.
3. **Se o OAuth client for do tipo "Web application"** (nao confirmado — pode
   ser Desktop), adicionar `http://localhost:8000/oauth2callback` nos Authorized
   redirect URIs. Cliente Desktop aceita loopback sem registro previo.

---

## 2. O que foi produzido nesta sessao (contexto do documento)

Tres documentos novos. Os dois primeiros ficam no repo `pulse`, o terceiro e
este handoff.

### 2.1 `~/dev/pulse/docs/meta-app-review-e-onboarding-via-parceiro.md`

Pesquisa completa na documentacao oficial da Meta (a estrutura mudou para
`/documentation/business-messaging/whatsapp/…`). **Achado central:** existe um
caminho oficial para o arranjo Pulse-sob-app-do-parceiro chamado
**Multi-Partner Solution**, e ele dissolve o bloqueador do plano de 29/07.

Resumo do que muda:

- A WABA do cliente fica compartilhada com **os dois** business portfolios.
  Cada parceiro inscreve o **proprio** app nos webhooks e recebe os eventos
  assinados com o **proprio** App Secret → **nao precisamos mais do App Secret
  da Scal**.
- O token do cliente vem de `GET /{solution_id}/access_token?business_id=…`,
  sem a troca de `code` que exigiria as credenciais deles.
- Custo: exige Business Verification + App Review + Advanced Access
  (`whatsapp_business_management` e `whatsapp_business_messaging`) no **nosso**
  app. Ou seja, nao destrava imediatamente.
- **Prazo duro descoberto: Embedded Signup v2 e descontinuado em 15/10/2026.**
  Integracoes nao migradas para v4 quebram. Nosso front
  (`app/(dashboard)/configuracoes/whatsapp/page.tsx:78`) trata so
  `data.type === "WA_EMBEDDED_SIGNUP"` sem olhar o `event`; a v4 tem cinco
  finais, e `FINISH_ONLY_WABA` / `FINISH_GRANT_ONLY_API_ACCESS` sao onboarding
  **incompleto** que hoje passariam como sucesso.
- Dois problemas do override puro que nao sabiamos: (a) `account_update` **nao e
  overridavel** — webhooks de nivel de conta sempre vao para o callback padrao
  do app, entao nunca saberiamos por webhook que uma clinica concluiu o
  onboarding; (b) a assinatura continua sendo do app inscrito.

O documento tem a mecanica exata do `override_callback_uri` (endpoints, ordem de
precedencia, lista de campos cobertos, limite de 200 chars na URL), o checklist
do App Review, e a §7 mapeando item a item o que muda no
`docs/plan-onboarding-meta-partner-app.md` de 29/07.

### 2.2 `~/dev/pulse/docs/proposta-integracao-pulse-scal.md` ← **o que vira o Doc**

Proposta comercial/tecnica para a Scal. **Substitui** a proposta de 27/07
(`docs/proposta-parceiro-acesso-app.md`), que pedia o App Secret deles e uma
alteracao no roteador de webhook da Scal.

O pedido novo e muito menor: criar uma Multi-Partner Solution, definir o app do
Pulse como o autorizado a enviar mensagens, e nao assinar o campo `messages` nas
WABAs da solution. Some o App Secret, some a mudanca no roteador, e some a
liberacao do nosso dominio no SDK deles — que era o item que travava qualquer
teste.

Pontos que foram escritos com intencao e **nao devem ser suavizados** se alguem
editar o documento:

- **§4** admite abertamente que a Scal *poderia* assinar `messages` e receber as
  conversas das clinicas, e que **nao ha mecanismo tecnico nosso para impedir**.
  Pede compromisso escrito, com o argumento de LGPD art. 11 (dado de saude).
- **§7** admite que este caminho **nao destrava hoje** — depende do nosso App
  Review — enquanto o caminho antigo destravaria. E o trade-off honesto.
- **§8** mantem a alternativa (override) documentada, agora numa versao melhor
  que a de julho: com `override_callback_uri` a Scal nao precisa mexer no
  roteador nem nesse cenario. Mas ai sim precisariamos do App Secret.
- **§6** corrigiu erros factuais da proposta de julho: nao falar mais em "Row
  Level Security" (foi removida na migracao para Postgres puro — o isolamento e
  na aplicacao) nem em "Supabase Vault" (hoje e `pgcrypto` com chave injetada
  por transacao).

---

## 3. Perguntas abertas com o JP

1. **Em qual conta Google o Doc deve viver** — `isabellavfreirer@gmail.com`
   (a conta desta maquina) ou `@grupovelas.com.br`? Perguntado, nao respondido.
   Afeta so onde o arquivo nasce; se ele nao responder, criar na conta que o
   consentimento OAuth autorizar e avisar qual foi.
2. **hub-up pendente.** O hub tem tres alteracoes nao commitadas desta sessao:
   `.gitignore`, `AGENT-HUB.md`, `scripts/setup-google-mcp.sh` — mais este
   handoff. O JP foi perguntado e nao respondeu. **Nao commitar sem ele pedir.**
3. **O repo `pulse` tem dois arquivos novos nao commitados**
   (`docs/meta-app-review-e-onboarding-via-parceiro.md` e
   `docs/proposta-integracao-pulse-scal.md`). Mesma regra.

---

## 4. Nota de seguranca

O `client_id` e o `client_secret` do OAuth **foram colados pelo JP no chat** e
portanto estao no historico daquela conversa. Cliente do tipo Desktop: o proprio
Google nao trata esse secret como confidencial (o fluxo assume que ele e
extraivel do binario), entao nao e urgente. **Se o cliente for do tipo Web
application, vale rotacionar** depois que tudo estiver funcionando.

O `.gitignore` do hub cobria **so** `.DS_Store` ate hoje — um `git add .`
distraido bastava para vazar segredo no historico publico. Foi estendido para
`*.env`, `*-oauth.env` e `*credentials*.json`. Vale conferir o mesmo no
`mac-grupovelas`.

---

## 5. Contexto anterior que segue valendo

- O foco de agosto vinha sendo **BI / Metabase / LeadScore** (regua de
  expectativa, dash 270 Chapeco, grafico do LSV parado aguardando MV do chefe).
  Esta sessao foi um desvio deliberado para a frente Meta/Pulse — o JP abriu
  dizendo "vamos fazer algo completamente diferente".
- O **Pulse** segue com a Fase B do Postgres fechada e a Fase C (auth propria)
  nao iniciada. Nada de codigo foi tocado nesta sessao — so documentacao.
- O **kanban do GitHub nao abriu** nesta maquina:
  `gh project item-list 1 --owner Grupo-Velas` devolve
  `{"items":[],"totalCount":0}` porque o PAT do `macbook-jpazv` e fine-grained e
  nao tem o escopo `project`. O JP precisa rodar
  `gh auth refresh -h github.com -s project -c` no terminal dele — device flow
  nao funciona pelo bash do agente.
