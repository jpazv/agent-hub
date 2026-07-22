# Current State

Last updated: 2026-07-21

## Onde estamos

| No | Status |
|---|---|
| mac-grupovelas | ✅ operacional |
| macbook-jpazv | 🔄 em preparacao (registrado no registry, setup local pendente) |

## O que foi feito nesta sessao (2026-07-21)

- repositorio do hub conectado de fato ao GitHub (remote estava faltando desde a criacao): `git@github.com:jpazv/agent-hub.git`
- `.gitignore` criado (.DS_Store)
- nova maquina `macbook-jpazv` (MacBook de Jpazv) registrada em `registry/machines.yaml`, role interactive

## Trabalho em andamento

- setup do MacBook novo (`macbook-jpazv`): instalar ferramentas base, gerar SSH key propria, clonar o hub, criar `machine.toml` local e `~/.claude/CLAUDE.md`

## Proximo passo recomendado

Finalizar o boot do `macbook-jpazv`: apos clonar o hub, rodar `hub-status` para validar e registrar qualquer trabalho com `hub-up`. Depois, conectar o primeiro projeto ao hub (`registry/projects.yaml` ainda esta vazio).
