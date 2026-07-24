# Agent Integration Guide

Como integrar Claude Code, Codex, Gemini e outros agentes ao hub com boot automático.

## Arquitetura

```
~/.config/agents/machine.toml
  ↓
  └─→ ~/.claude/CLAUDE.md (Claude Code)
  └─→ ~/.codex/init.sh (Codex)
  └─→ ~/.gemini/init.sh (Gemini)
       ↓
       └─→ /dev/agent-hub/scripts/agent-boot.sh
            ↓
            └─→ Lê handoffs, carrega contexto
```

## 1. Machine Configuration

**Arquivo:** `~/.config/agents/machine.toml`

```toml
machine_id    = "seu-machine-id"
display_name  = "Seu Display Name"
role          = "interactive"

hub_path      = "/caminho/para/agent-hub"
projects_root = "/caminho/para/projetos"
```

**Campos obrigatórios:**
- `machine_id` — identificador único (ex: mac-grupovelas, linux-dev)
- `hub_path` — caminho absoluto do agent-hub (ex: `/Users/user/dev/agent-hub`)
- `projects_root` — onde projetos vivem (ex: `/Users/user/dev`)

## 2. Claude Code

**Configuração:** Nativa via `~/.claude/CLAUDE.md`

Arquivo já criado. Claude Code lê automaticamente no boot.

**Verificar:**
```bash
cat ~/.claude/CLAUDE.md | head -20
```

Deve mostrar "Hub Global Rule" e referenciar o agent-hub.

## 3. Codex (ou outro agente CLI)

**Arquivo:** `~/.codex/init.sh`

Pré-criado. Execute no terminal antes de usar Codex:

```bash
source ~/.codex/init.sh
```

Ou adicione ao seu shell profile (`~/.zshrc`, `~/.bashrc`):

```bash
# Agent Hub initialization
if [ -f ~/.codex/init.sh ]; then
  source ~/.codex/init.sh
fi
```

**Resultado esperado:**
```
⬇️  Sincronizando hub...
📖 Carregando fontes de verdade...
✅ Hub carregado
   HUB_PATH=/Users/grupovelas/dev/agent-hub
   MACHINE_ID=mac-grupovelas
```

## 4. Gemini (ou outro agente)

**Arquivo:** `~/.gemini/init.sh`

Mesmo padrão do Codex. Execute no terminal:

```bash
source ~/.gemini/init.sh
```

Ou adicione ao shell profile.

## 5. Script Universal de Boot

**Arquivo:** `/dev/agent-hub/scripts/agent-boot.sh`

Usado internamente por todos os agentes. Faz:
1. Valida `machine.toml`
2. `git pull` do hub
3. Carrega fontes de verdade
4. Detecta projeto (se aplicável)
5. Mostra handoff mais recente
6. Exporta variáveis de ambiente

**Uso direto:**
```bash
source /path/to/agent-hub/scripts/agent-boot.sh
```

## Fluxo de Boot Esperado

Quando você abre um agente:

1. **Machine.toml existe?** ✓
   - Sim → lê machine_id e hub_path
   - Não → aviso e aguarda configuração

2. **Hub existe em hub_path?** ✓
   - Sim → continua
   - Não → erro, sair

3. **Git pull** (hub-down) ✓
   - Sincroniza mudanças do GitHub

4. **Detectar projeto** ✓
   - Se `memory/project.md` existe → é um projeto
   - Senão → modo global

5. **Carregar handoff** ✓
   - Mostra últimas 30 linhas do handoff mais recente
   - (Agente deve ler completo)

6. **Exportar variáveis** ✓
   - `HUB_PATH`, `MACHINE_ID`, `CURRENT_PROJECT`
   - Disponíveis pra scripts subsequentes

## Troubleshooting

### `machine.toml não encontrado`
```bash
mkdir -p ~/.config/agents/
cat > ~/.config/agents/machine.toml << 'EOF'
machine_id    = "mac-seu-nome"
display_name  = "Seu Computer"
role          = "interactive"
hub_path      = "/Users/seu-nome/dev/agent-hub"
projects_root = "/Users/seu-nome/dev"
EOF
```

### `git pull` falha (offline)
Continua mesmo assim — usa cache local. Se offline persistir:
```bash
cd /path/to/agent-hub
git status  # verifica estado
```

### Handoff não aparece
Projeto não está registrado. Adicione em `agent-hub/registry/projects.yaml`:
```yaml
projects:
  - id: meu-projeto
    path: /Users/seu-nome/dev/meu-projeto
```

### Init script não executa automaticamente
Adicione ao shell profile:
```bash
# ~/.zshrc ou ~/.bashrc
[ -f ~/.codex/init.sh ] && source ~/.codex/init.sh
```

Restart terminal e abra novamente.

## Próximas Integrações

Mesmo padrão pode ser replicado para:
- **OpenAI Codex** → `~/.openai-codex/init.sh`
- **Anthropic Operator** → `~/.operator/init.sh`
- **Local Ollama** → `~/.local-ai/init.sh`

Copie `~/.codex/init.sh` e adapte conforme necessário.
