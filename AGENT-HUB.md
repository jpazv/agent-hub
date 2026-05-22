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
8. so entao agir

## Fonte de verdade minima

Sempre carregar:

- `README.md`
- `ARCHITECTURE.md`
- `memory/current-state.md`
- `registry/machines.yaml`
- `registry/projects.yaml`
- `machine.toml` local da maquina

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
