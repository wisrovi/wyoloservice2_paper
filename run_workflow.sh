#!/usr/bin/env bash

# Dispatcher del workflow de publicación IEEE.
#   ./run_workflow.sh                    -> opencode (recomendado, no-interactivo)
#   AGENT_CLI=opencode ./run_workflow.sh -> opencode
#   AGENT_CLI=freebuff ./run_workflow.sh -> freebuff (tmux automático)
#   AGENT_CLI=agy ./run_workflow.sh      -> agy (requiere cuota)
# También puedes ejecutar directamente: ./run_workflow_opencode.sh | _freebuff | _agy

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_CLI="${AGENT_CLI:-opencode}"

case "$AGENT_CLI" in
  opencode) TARGET="run_workflow_opencode.sh" ;;
  freebuff) TARGET="run_workflow_freebuff.sh" ;;
  agy)      TARGET="run_workflow_agy.sh" ;;
  *)
    echo "❌ AGENT_CLI inválido: '$AGENT_CLI' (usa 'opencode', 'freebuff' o 'agy')." >&2
    exit 1
    ;;
esac

if [ ! -x "$SCRIPT_DIR/$TARGET" ]; then
  echo "❌ No se encontró el script ejecutable: $SCRIPT_DIR/$TARGET" >&2
  exit 1
fi

exec "$SCRIPT_DIR/$TARGET"
