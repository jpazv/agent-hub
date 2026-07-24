# Agent Hub

Hub de agentes de IA com contexto compartilhado, memoria persistente e handoff padronizado.

## Principios

1. **Chats sao efemeros. Arquivos sao permanentes.**
2. **Uma fonte de verdade global, isolamento por projeto.**
3. **Segredos nunca entram no hub.**
4. **Cada IA tem seu proprio ponto de entrada.**
5. **Handoff estruturado em vez de resumo informal.**

## Estrutura

```
agent-hub/
  AGENT-HUB.md                ← regra mestra
  README.md                   ← este arquivo
  ARCHITECTURE.md             ← arquitetura do ecossistema
  memory/
    current-state.md          ← estado atual
  registry/
    machines.yaml             ← maquinas participantes
    projects.yaml             ← projetos registrados
  agents/
  templates/
  scripts/
```

## Fluxo minimo de uma sessao

1. IA abre → le o cerebro global
2. Cerebro aponta para o hub → IA le AGENT-HUB.md e memory/current-state.md
3. IA identifica o projeto pelo diretorio atual
4. IA le a memoria do projeto e o handoff mais recente
5. IA age com contexto completo
6. Ao encerrar: escreve handoff se houve trabalho relevante

## Agentes operando aqui

- **Claude Code** (~/.claude/CLAUDE.md) — exploração, arquitetura, decisões
- **Codex** (~/.codex/AGENTS.md) — execução precisa, refactoring, testes
- **Gemini** (~/.gemini/GEMINI.md) — análise rápida, busca de padrões

Cada IA le seu arquivo NATIVO em toda sessao, de qualquer diretorio. O
conteudo vem de um template unico e portavel: `agents/AGENTS.md`.

Veja [AGENTS.md](AGENTS.md) pra fluxo de colaboração entre agentes.

## Setup em uma maquina nova (ou depois de mudar os arquivos de agente)

Os arquivos nativos das IAs moram no home (`~/.codex/`, `~/.gemini/`,
`~/.claude/`), FORA do git — o `git pull` traz o template, e o script instala:

```bash
cd <hub> && git pull            # hub-down: traz template + script atualizados
bash scripts/setup-agents.sh    # instala nos 3 lugares nativos
```

Pre-requisito: `~/.config/agents/machine.toml` com `machine_id` e `hub_path`
corretos da maquina.

### Atalho (opcional): comando `hub-setup`

Adicione ao seu `~/.zshrc` (ou `~/.bashrc`) pra nao decorar o caminho:

```bash
# Agent Hub
alias hub-setup='bash "$(grep "^hub_path" ~/.config/agents/machine.toml | cut -d\" -f2)"/scripts/setup-agents.sh'
alias hub-down='cd "$(grep "^hub_path" ~/.config/agents/machine.toml | cut -d\" -f2)" && git pull'
```

Depois, em qualquer maquina nova: `hub-down && hub-setup`.
