#!/bin/zsh
# Instala o MCP google-workspace (Docs + Drive) nesta maquina, no escopo `user`
# do Claude Code — ou seja, disponivel em TODA sessao, de qualquer diretorio.
#
# Uso:
#   bash scripts/setup-google-mcp.sh
#
# PRE-REQUISITO (uma vez por maquina, feito a mao):
#   criar ~/.config/agents/google-oauth.env com:
#
#     export GOOGLE_OAUTH_CLIENT_ID="...apps.googleusercontent.com"
#     export GOOGLE_OAUTH_CLIENT_SECRET="GOCSPX-..."
#
#   e depois: chmod 600 ~/.config/agents/google-oauth.env
#
# Esse arquivo NAO vive no hub e NAO e versionado — de proposito. O hub
# carrega o roteiro; o segredo fica local em cada maquina.
#
# Do lado do Google Cloud Console, o projeto precisa de:
#   - Google Docs API e Google Drive API habilitadas
#   - tela de consentimento OAuth configurada
#   - um OAuth client ID do tipo "Desktop app"
#     (se for do tipo "Web application", adicionar
#      http://localhost:8000/oauth2callback nos Authorized redirect URIs)

set -e

ENV_FILE="$HOME/.config/agents/google-oauth.env"
WRAPPER="$HOME/.config/agents/google-workspace-mcp.sh"

if [ ! -f "$ENV_FILE" ]; then
  echo "Credenciais nao encontradas nesta maquina."
  echo
  echo "Pegue-as em: Google Cloud Console > APIs e servicos > Credenciais"
  echo "  projeto 538719293602 > OAuth 2.0 Client IDs > (o client Desktop)"
  echo "O client_secret pode ser lido de novo la a qualquer momento — nao"
  echo "precisa copiar de outra maquina, e nao deve trafegar por chat/git."
  echo

  printf 'GOOGLE_OAUTH_CLIENT_ID: '
  read -r CLIENT_ID
  printf 'GOOGLE_OAUTH_CLIENT_SECRET (nao aparece na tela): '
  read -rs CLIENT_SECRET
  echo

  if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo "ERRO: os dois valores sao obrigatorios."
    exit 1
  fi

  mkdir -p "$(dirname "$ENV_FILE")"
  umask 077
  cat > "$ENV_FILE" <<ENV_EOF
# Credenciais OAuth do Google para o MCP workspace-mcp
# Tipo de cliente: OAuth client ID (Desktop app)
# NUNCA commitar este arquivo. Ele vive fora do repo do hub de proposito.

export GOOGLE_OAUTH_CLIENT_ID="$CLIENT_ID"
export GOOGLE_OAUTH_CLIENT_SECRET="$CLIENT_SECRET"
ENV_EOF
  echo "Gravado em $ENV_FILE"
  echo
fi

chmod 600 "$ENV_FILE"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv nao encontrado — instalando via Homebrew..."
  brew install uv
fi

cat > "$WRAPPER" <<'WRAPPER_EOF'
#!/bin/zsh
# Wrapper do MCP google-workspace. Existe para que o client_secret viva num
# unico arquivo local em vez de ser copiado para dentro de ~/.claude.json.
set -e
source "$HOME/.config/agents/google-oauth.env"
export PATH="/opt/homebrew/bin:$PATH"
exec uvx workspace-mcp --single-user --tools docs drive "$@"
WRAPPER_EOF

chmod +x "$WRAPPER"

claude mcp remove -s user google-workspace 2>/dev/null || true
claude mcp add -s user google-workspace -- "$WRAPPER"

echo
echo "Pronto. Reinicie o Claude Code para as ferramentas aparecerem."
echo "Na primeira chamada o servidor devolve uma URL de consentimento —"
echo "abra no browser e autorize. O token fica cacheado localmente."
