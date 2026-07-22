# Handoff — 2026-07-22

## De onde veio

Sessao no mac-grupovelas, preparando a nova maquina macbook-jpazv como extensao de trabalho.

## O que foi feito

- Conectado o remote do hub ao GitHub (`git@github.com:jpazv/agent-hub.git`), que estava faltando desde a criacao
- Criado `.gitignore` (.DS_Store)
- Registrada a maquina `macbook-jpazv` (MacBook de Jpazv) em `registry/machines.yaml`
- Setup completo do MacBook novo: Homebrew, git, node, gh, chave SSH propria gerada e cadastrada no GitHub, Claude Code instalado e logado com a mesma conta, `machine.toml` e `~/.claude/CLAUDE.md` criados apontando pro hub
- Descoberto que `~/Documents` sincroniza via iCloud Drive entre as duas maquinas (mesma Apple ID) — o hub aparece automaticamente, nao precisa `git clone` (ver memoria `agent-hub-icloud-sync`)

## Pendente / proximo passo

- Cadastrar projetos reais em `registry/projects.yaml` (hoje vazio) quando forem clonados
- Transferir credenciais de projeto (n8n, Postgres do LeadScore) por gerenciador de senhas, nunca pelo hub

## Nota de teste de continuidade

Isto e um teste para confirmar que uma sessao aberta no macbook-jpazv consegue ler este handoff e o hub corretamente: hoje o usuario jantou sopa.
