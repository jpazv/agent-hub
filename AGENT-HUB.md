# Agent Hub Boot Rule

Este arquivo define a regra global de entrada para qualquer agente operando neste hub.

## Regra mestra

Nenhum agente deve assumir que o chat atual e a unica fonte de verdade.

Antes de agir, o agente deve:

1. identificar a maquina atual
2. localizar o hub
3. ler `machine.toml`
4. ler a memoria global minima do hub
5. identificar se esta operando em um projeto ou no modo global
6. se houver projeto, ler a memoria do projeto
7. se houver handoff recente, ler o handoff mais recente
8. conectar ao kanban e reportar as tasks abertas do JP
9. so entao agir

## Fonte de verdade minima

Sempre carregar:

- `README.md`
- `ARCHITECTURE.md`
- `memory/current-state.md`
- `memory/best-practices.md`
- `registry/machines.yaml`
- `registry/projects.yaml`
- `machine.toml` local da maquina

## Kanban — conectar em TODA sessao

Toda sessao comeca conectada ao kanban do GitHub e abre reportando as tasks
abertas do JP. Nao esperar o usuario pedir.

Board: org `Grupo-Velas`, project `1` (Produtividade BI e Dev).

```bash
gh project item-list 1 --owner Grupo-Velas --format json --limit 400
```

Como identificar as tasks do JP (o board nao usa assignee de forma confiavel):

- titulo casando `[JP]` ou `JP:`
- OU corpo contendo `jpazv`

Status a mostrar, nesta ordem:

1. Em andamento
2. Em validacao
3. Solicitada
4. Triagem/Backlog

**Nunca listar `Concluida`.** `Bloqueada` so se o JP pedir.

Sinalizar prazo vencido comparando `### Prazo desejado` com a data de hoje.

### Requisito de token

Exige o escopo `project` no `gh`. Conferir com `gh auth status`. Se faltar:

```bash
gh auth refresh -h github.com -s project -c
```

O device flow **nao funciona** pelo bash do agente (a saida com o codigo nao
aparece) — o JP precisa rodar num terminal proprio. O codigo e impresso pelo
`gh` no terminal, nao vem de app de celular.

## Google (Docs + Drive) — MCP no escopo `user`

O acesso ao Google Workspace e um MCP instalado por maquina, no escopo `user` do
Claude Code (carrega em toda sessao, de qualquer diretorio).

Instalar numa maquina nova:

```bash
bash scripts/setup-google-mcp.sh
```

Pre-requisito: `~/.config/agents/google-oauth.env` com
`GOOGLE_OAUTH_CLIENT_ID` e `GOOGLE_OAUTH_CLIENT_SECRET`, `chmod 600`.

**Esse arquivo nunca entra no hub.** O `.gitignore` do repo so cobre `.DS_Store`
— qualquer segredo commitado aqui vai para o GitHub e fica no historico. O hub
carrega o roteiro; o segredo fica local em cada maquina.

## Se estiver em um projeto

Carregar tambem:

- `memory/project.md`
- `memory/current-state.md`
- `memory/decisions.md`
- ultimo arquivo em `memory/handoffs/`, se existir

## Se nao estiver em um projeto

Operar em modo global do hub. Nao inventar contexto de projeto.

## Comportamento esperado

- preservar isolamento entre projetos
- tratar segredos como locais
- usar handoff estruturado em vez de depender de memoria de conversa

## Regra de sync

- hub-down = consumir do GitHub (git pull)
- hub-status = verificar estado local (git status)
- hub-up = guardar no GitHub (git add + commit + push)
