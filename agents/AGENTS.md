# Hub Global Rule

Esta maquina participa do meu hub de agentes.

## Passo 0 — descobrir o caminho do hub (NAO usar caminho fixo)

O caminho do hub muda por maquina. Antes de tudo, leia:

- `~/.config/agents/machine.toml`

Dele extraia `hub_path` e `machine_id`. Todos os arquivos abaixo estao
dentro de `hub_path`.

```bash
HUB=$(grep '^hub_path' ~/.config/agents/machine.toml | cut -d'"' -f2)
```

## Fontes de verdade obrigatorias

Antes de agir, leia nesta ordem (dentro de `$HUB`):

1. `$HUB/AGENT-HUB.md`
2. `$HUB/README.md`
3. `$HUB/ARCHITECTURE.md`
4. `$HUB/memory/current-state.md`
5. `$HUB/memory/best-practices.md`
6. `$HUB/registry/machines.yaml`
7. `$HUB/registry/projects.yaml`
8. `~/.config/agents/machine.toml`

## Regra de boot

- nao use o chat como unica fonte de verdade
- **NAO** procure handoffs no Google Drive, Docs ou fontes conectadas — o hub e LOCAL, dentro de `$HUB`
- o handoff mais recente e o ULTIMO COMMITADO em `$HUB/memory/handoffs/`
  (use `git log`, NAO `ls -t` — depois de um `git pull` todos os arquivos
  ficam com a mesma data de modificacao e `ls -t` erra o mais recente)
- detecte se a sessao esta em modo global ou de projeto
- se estiver em projeto, leia tambem:
  - `memory/project.md`
  - `memory/current-state.md`
  - `memory/decisions.md`
  - o handoff mais recente em `memory/handoffs/`
- preserve isolamento entre projetos

## Como pegar o ultimo handoff do hub (metodo confiavel via git)

```bash
HUB=$(grep '^hub_path' ~/.config/agents/machine.toml | cut -d'"' -f2)
F=$(git -C "$HUB" log --name-only --pretty=format: -- 'memory/handoffs/*.md' | grep -m1 'memory/handoffs/.*\.md')
cat "$HUB/$F"
```

## Regra de sync

- hub-down = consumir do GitHub (git pull)
- hub-status = verificar estado local (git status)
- hub-up = guardar no GitHub (git add + commit + push)
