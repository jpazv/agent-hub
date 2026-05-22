# Architecture

Arquitetura do hub de agentes.

## Objetivo

Permitir que Claude Code, Codex, Antigravity e outros agentes operem com:

- contexto compartilhado sem depender de chat anterior
- isolamento entre projetos
- continuidade entre maquinas
- handoff padronizado

## Camadas

### 1. control plane

Onde mora a arquitetura global, os contratos e a memoria compartilhada.

- este repositorio (hub)
- versionado no GitHub
- sincronizado entre maquinas via hub-down / hub-up

### 2. interactive plane

Onde voce trabalha no dia a dia e conversa com os agentes.

- maquinas locais
- editores e terminais
- sessoes de Claude Code, Codex, Antigravity

### 3. runtime plane

Onde os projetos e automacoes executam de fato.

- servidores
- pipelines de CI/CD
- automacoes agendadas

## Fonte de verdade por camada

### Global

Fica no hub.

Inclui:

- regras de boot
- registry de projetos e maquinas
- memoria global minima

### Projeto

Fica dentro do repositorio do projeto.

Inclui:

- `memory/project.md`
- `memory/current-state.md`
- `memory/decisions.md`
- `memory/handoffs/`

### Local da maquina

Fica fora do Git.

Inclui:

- `machine.toml`
- segredos
- tokens
- credenciais

## Regra mestra de memoria

Chats sao efemeros.

Continuidade real deve estar em:

- memoria global curta
- memoria por projeto
- handoffs padronizados
- machine config

## Papeis recomendados por agente

### Claude Code

- exploracao
- trabalho interativo
- arquitetura
- leitura ampla de codebase

### Codex

- execucao tecnica
- alteracoes precisas
- manutencao estruturada de codigo

### Antigravity

- edicao visual
- trabalho integrado ao editor
- contexto de arquivo atual
