#!/bin/bash
# Instala os arquivos nativos de cada IA (Claude, Codex, Gemini) a partir do
# template portavel do hub. Rode isto UMA vez por maquina depois do git pull.
#
# Uso:  bash "$HUB"/scripts/setup-agents.sh
set -e

# Descobrir hub_path a partir do machine.toml (nao depende de caminho fixo)
MACHINE_TOML="$HOME/.config/agents/machine.toml"
if [ ! -f "$MACHINE_TOML" ]; then
  echo "❌ $MACHINE_TOML nao encontrado. Crie-o primeiro (machine_id + hub_path)."
  exit 1
fi
HUB=$(grep '^hub_path' "$MACHINE_TOML" | cut -d'"' -f2)
TEMPLATE="$HUB/agents/AGENTS.md"

if [ ! -f "$TEMPLATE" ]; then
  echo "❌ Template nao encontrado: $TEMPLATE (rode 'git pull' no hub)"
  exit 1
fi

# Codex  -> ~/.codex/AGENTS.md   (arquivo nativo do Codex)
# Gemini -> ~/.gemini/GEMINI.md  (arquivo nativo do Gemini)
# Claude -> ~/.claude/CLAUDE.md  (arquivo nativo do Claude)
install_one () {
  local dir="$1" dest="$2" label="$3"
  if [ -d "$dir" ] || mkdir -p "$dir" 2>/dev/null; then
    cp "$TEMPLATE" "$dir/$dest"
    echo "✅ $label -> $dir/$dest"
  else
    echo "⚠️  $label pulado ($dir nao existe e nao pude criar)"
  fi
}

echo "📦 Instalando config de agentes a partir de: $TEMPLATE"
install_one "$HOME/.codex"  "AGENTS.md" "Codex"
install_one "$HOME/.gemini" "GEMINI.md" "Gemini"
install_one "$HOME/.claude" "CLAUDE.md" "Claude"

echo ""
echo "✅ Pronto. Cada IA vai auto-carregar seu arquivo nativo em toda sessao,"
echo "   descobrindo o hub via ~/.config/agents/machine.toml (portavel)."
