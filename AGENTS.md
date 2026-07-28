# Agentes Operando no Hub

Este hub coordena **três agentes de IA** operando na mesma máquina, lendo a mesma fonte de verdade.

## Agentes

### Claude Code
- **Função**: exploração, arquitetura, design, decisões complexas
- **Força**: visão ampla de codebase, síntese de contexto, design patterns
- **Entrada**: `~/.claude/CLAUDE.md`
- **Melhor pra**: "Como devemos estruturar isso?", leitura ampla, brainstorming com contexto

### Codex
- **Função**: execução técnica precisa, refactoring, alterações estruturadas
- **Força**: mudanças de código precisas, testes, manutenção
- **Entrada**: `~/.codex/AGENTS.md` (arquivo nativo que o Codex auto-carrega em toda sessao)
- **Melhor pra**: "Muda a assinatura dessa função em 3 arquivos", refactorings, testes

### Gemini
- **Função**: análise rápida, busca de padrões, resumos técnicos
- **Força**: velocidade, detecção de inconsistências, resumos
- **Entrada**: `~/.gemini/GEMINI.md`
- **Melhor pra**: "Que padrões inconsistentes vê aqui?", análise rápida, busca

## Fluxo esperado

1. **Claude Code** começa — lê contexto amplo, propõe arquitetura
2. **Gemini** valida padrões — busca inconsistências que Claude talvez perdeu
3. **Codex** executa — faz as mudanças precisas
4. **Claude Code** valida e documenta — escreve handoff

## Fonte de verdade compartilhada

Todos os três leem:
- `AGENT-HUB.md` (regra mestra)
- `ARCHITECTURE.md` (como o hub funciona)
- `memory/current-state.md` (estado atual)
- `memory/best-practices.md` (boas praticas globais)
- `registry/machines.yaml` (máquinas participantes)
- `registry/projects.yaml` (projetos)
- `memory/handoffs/` (últimas decisões)

Cada um tem seu próprio arquivo de configuração em `~/.{agent}/`:
- `~/.claude/CLAUDE.md`
- `~/.codex/AGENTS.md`
- `~/.gemini/GEMINI.md`

## Isolamento e privilégios

- **Claude Code**: permissão total (lê/escreve, planeja)
- **Codex**: executa alterações específicas (restrições de escopo)
- **Gemini**: lê, analisa (sem escrita em arquivos de projeto)

## Como chamar cada um

Quando estiver em um projeto:

```bash
# Quero explorar e pensar sobre arquitetura
→ Abra Claude Code, ele lê ~/.claude/CLAUDE.md

# Quero que analise padrões e inconsistências
→ Abra Gemini, ele lê ~/.gemini/GEMINI.md

# Quero que execute uma mudança precisa
→ Abra Codex, ele lê ~/.codex/AGENTS.md
```

Cada um vai ler `memory/project.md` e `memory/handoffs/` automaticamente se existirem.

## Exemplo de fluxo real

1. Claude Code: "Vou estruturar onboarding do Eco. Lendo memory/handoffs/, vejo que provisioning precisa ser idempotente. Vou desenhar um plano."
   → Escreve `memory/handoffs/2026-07-24-eco-onboarding-plan.md`

2. Gemini: "Vou buscar padrões de idempotência no código existente."
   → Grep por `idempotent`, acha que `sign-up` já tem pattern, aponta inconsistência

3. Codex: "Vou refazer o provision endpoint seguindo o padrão do sign-up."
   → Altera `app/api/onboarding/provision/route.ts`, roda testes

4. Claude Code: "Valido, testes passam. Escrevo handoff de conclusão."
   → Escreve `memory/handoffs/2026-07-24-eco-onboarding-done.md`

## Contratos

Cada agente respeita:
- **Escopo**: não inventar tarefas fora do que foi pedido
- **Handoff**: escrever handoff quando terminar trabalho relevante
- **Isolamento**: não mexer em projetos que não foram autorizados
- **Sync**: `hub-up` antes de sair, `hub-down` ao entrar
