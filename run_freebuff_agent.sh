#!/usr/bin/env bash

# Ejecuta una etapa del workflow dentro de Freebuff de forma automática usando tmux.
# El prompt se inyecta en la TUI como un pegado (paste-buffer) y el script espera
# a que el agente cree el marcador .freebuff_done en la raíz del proyecto.
#
# Uso: run_freebuff_agent.sh <archivo_prompt> [directorio_proyecto]
#
# Códigos de salida:
#   0  -> el agente completó la tarea (marcador .freebuff_done creado)
#   1  -> error (sin tmux/freebuff, TUI no arrancó, timeout)
#   2  -> hay otra instancia de Freebuff activa (el llamador decide)

set -u

PROMPT_FILE="${1:?uso: run_freebuff_agent.sh <prompt_file> [project_dir]}"
PROJECT_DIR="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

MARKER="$PROJECT_DIR/.freebuff_done"
TIMEOUT="${FREEBUFF_TIMEOUT:-1800}"   # segundos máximos de espera por etapa
POLL_INTERVAL=5
READY_ATTEMPTS=30                     # ~30s para que arranque la TUI
SESS="fbwf_$(basename "$PROMPT_FILE" .md)_$$"

rm -f "$MARKER"

# --- Requisitos --------------------------------------------------------------
if ! command -v tmux >/dev/null 2>&1; then
  echo "❌ [freebuff-agent] No se encontró 'tmux'. Usa el modo manual (FREEBUFF_MANUAL=1)." >&2
  exit 1
fi
if ! command -v freebuff >/dev/null 2>&1; then
  echo "❌ [freebuff-agent] No se encontró 'freebuff'." >&2
  exit 1
fi

# Limpieza garantizada (sesión tmux y marcador) pase lo que pase
cleanup() {
  tmux kill-session -t "$SESS" 2>/dev/null
  rm -f "$MARKER"
}
trap cleanup EXIT

# --- Lanzar Freebuff en una sesión tmux oculta -------------------------------
tmux new-session -d -s "$SESS" -x 220 -y 50 "freebuff --cwd '$PROJECT_DIR'" || {
  echo "❌ [freebuff-agent] No se pudo crear la sesión tmux '$SESS'." >&2
  exit 1
}
if ! tmux has-session -t "$SESS" 2>/dev/null; then
  echo "❌ [freebuff-agent] La sesión tmux '$SESS' no existe tras el lanzamiento." >&2
  exit 1
fi
echo "[freebuff-agent] Sesión tmux '$SESS' creada; esperando a que la TUI arranque..."

# Esperar a que la TUI termine la fase "Connecting…"
READY=0
for _ in $(seq 1 "$READY_ATTEMPTS"); do
  sleep 1
  PANE=$(tmux capture-pane -t "$SESS" -p 2>/dev/null)
  if ! echo "$PANE" | grep -q "Connecting"; then
    READY=1
    break
  fi
done

if [ "$READY" -ne 1 ]; then
  echo "❌ [freebuff-agent] La TUI de Freebuff no arrancó a tiempo." >&2
  exit 1
fi

# Freebuff solo permite una instancia: detectar el diálogo "already running"
# (recapturar el pane: el diálogo puede aparecer justo después de "Connecting…")
PANE=$(tmux capture-pane -t "$SESS" -p 2>/dev/null)
if echo "$PANE" | grep -qi "already running"; then
  echo "⚠️  [freebuff-agent] Se detectó otra instancia de Freebuff activa." >&2
  echo "   Cierra la otra sesión de Freebuff y vuelve a ejecutar el workflow." >&2
  exit 2
fi

# --- Inyectar el prompt como pegado + Enter ----------------------------------
tmux set-buffer -b fbprompt "$(cat "$PROMPT_FILE")"
tmux paste-buffer -b fbprompt -t "$SESS"
tmux send-keys -t "$SESS" Enter
echo "[freebuff-agent] Prompt inyectado. Esperando al agente (timeout ${TIMEOUT}s)..."

# --- Esperar a que el agente cree el marcador ---------------------------------
ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  if [ -f "$MARKER" ]; then
    echo "[freebuff-agent] ✅ Marcador detectado: el agente terminó la etapa."
    exit 0
  fi
  sleep "$POLL_INTERVAL"
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

echo "❌ [freebuff-agent] Timeout tras ${TIMEOUT}s sin que el agente terminara." >&2
exit 1
