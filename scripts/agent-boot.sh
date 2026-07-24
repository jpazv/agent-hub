#!/bin/bash
# Agent Hub Bootstrap
# Execute isto no começo de qualquer sessão pra carregar contexto correto
#
# Uso: source agent-boot.sh
# ou:  bash agent-boot.sh (vai exportar vars, use source pra elas persistirem)

set -e

# 1. Detectar máquina
MACHINE_TOML="$HOME/.config/agents/machine.toml"
if [ ! -f "$MACHINE_TOML" ]; then
  echo "❌ Erro: $MACHINE_TOML não encontrado"
  echo "   Crie com: mkdir -p ~/.config/agents/ && cat > ~/.config/agents/machine.toml << 'EOF'"
  echo "   machine_id = \"seu-id\""
  echo "   hub_path = \"/path/to/agent-hub\""
  echo "   EOF"
  exit 1
fi

# 2. Ler config local
HUB_PATH=$(grep 'hub_path' "$MACHINE_TOML" | cut -d'"' -f2)
MACHINE_ID=$(grep 'machine_id' "$MACHINE_TOML" | cut -d'"' -f2)

if [ -z "$HUB_PATH" ] || [ -z "$MACHINE_ID" ]; then
  echo "❌ machine.toml inválido (faltam hub_path ou machine_id)"
  exit 1
fi

# 3. Verificar hub existe
if [ ! -d "$HUB_PATH" ]; then
  echo "❌ Hub não encontrado em: $HUB_PATH"
  exit 1
fi

# 4. Hub-down (git pull)
echo "⬇️  Sincronizando hub..."
cd "$HUB_PATH"
git pull origin main --quiet 2>/dev/null || echo "⚠️  git pull falhou (offline?)"

# 5. Ler fontes de verdade obrigatórias
echo "📖 Carregando fontes de verdade..."

for file in AGENT-HUB.md ARCHITECTURE.md README.md; do
  if [ ! -f "$HUB_PATH/$file" ]; then
    echo "⚠️  $file não encontrado"
  fi
done

# 6. Detectar projeto (se estiver em um)
PROJECT_PATH=$(pwd)
PROJECT_FOUND=false

if [ -f "$PROJECT_PATH/memory/project.md" ]; then
  PROJECT_NAME=$(basename "$PROJECT_PATH")
  PROJECT_FOUND=true
  echo "📁 Projeto detectado: $PROJECT_NAME"

  # Ler handoff mais recente
  LATEST_HANDOFF=$(ls -t "$PROJECT_PATH/memory/handoffs/"*.md 2>/dev/null | head -1)
  if [ -n "$LATEST_HANDOFF" ]; then
    HANDOFF_NAME=$(basename "$LATEST_HANDOFF")
    echo "📄 Handoff mais recente: $HANDOFF_NAME"
    echo ""
    echo "--- HANDOFF ---"
    head -30 "$LATEST_HANDOFF"
    echo "..."
    echo "--- (leia $LATEST_HANDOFF completo) ---"
  fi
else
  echo "🌍 Modo global (sem projeto)"
fi

# 7. Export pra uso em scripts
export HUB_PATH
export MACHINE_ID
export CURRENT_PROJECT="$PROJECT_NAME"

echo ""
echo "✅ Hub carregado"
echo "   HUB_PATH=$HUB_PATH"
echo "   MACHINE_ID=$MACHINE_ID"
echo "   CURRENT_PROJECT=${CURRENT_PROJECT:-none}"
echo ""
echo "📋 Próximo: leia os handoffs completos e AGENT-HUB.md"
