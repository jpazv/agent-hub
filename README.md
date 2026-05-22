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
