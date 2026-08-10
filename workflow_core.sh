#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  MOTOR COMPARTIDO del bucle de publicación IEEE.
#  No se ejecuta directamente: cada run_workflow_<cli>.sh define AGENT_CLI y
#  run_agent(), y luego hace source de este archivo, que lanza el bucle.
# ─────────────────────────────────────────────────────────────────────────────

# Protección: este archivo no se ejecuta directamente
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "❌ workflow_core.sh no se ejecuta directamente." >&2
  echo "   Usa: run_workflow.sh, run_workflow_opencode.sh, run_workflow_freebuff.sh o run_workflow_agy.sh" >&2
  exit 1
fi

set -u

# El wrapper debe definir AGENT_CLI antes de hacer source
: "${AGENT_CLI:?Define AGENT_CLI antes de cargar workflow_core.sh}"

# Resuelve el directorio del proyecto (raíz del repo) y trabaja desde ahí
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_ROUNDS="${MAX_ROUNDS:-10}"
ROUND=1

WORKFLOW_STATE="$SCRIPT_DIR/WORKFLOW_STATE.md"
IEEE_VERDICT="$SCRIPT_DIR/IEEE_REVIEW_VERDICT.md"
REVISOR_PROMPT="$SCRIPT_DIR/.agy_prompts/revisor.md"
EDITOR_PROMPT="$SCRIPT_DIR/.agy_prompts/editor.md"

# --- Utilidades --------------------------------------------------------------

# Copia stdin al portapapeles si hay una herramienta disponible
copy_to_clipboard() {
  if command -v xclip >/dev/null 2>&1; then
    xclip -selection clipboard
  elif command -v wl-copy >/dev/null 2>&1; then
    wl-copy
  elif command -v pbcopy >/dev/null 2>&1; then
    pbcopy
  else
    return 1
  fi
}

# Comprueba el código de salida del agente tras una etapa
check_agent_exit() {
  local role="$1"
  local rc="$2"

  # agy/opencode son no-interactivos: cualquier fallo aborta
  if { [ "$AGENT_CLI" = "agy" ] || [ "$AGENT_CLI" = "opencode" ]; } && [ "$rc" -ne 0 ]; then
    echo "❌ El $role ($AGENT_CLI) falló en la ronda $ROUND. Revisa el error y reintenta." >&2
    exit 1
  fi

  # freebuff: 1=timeout/fallo, 2=otra instancia -> aborta; otros -> avisa
  if [ "$AGENT_CLI" = "freebuff" ]; then
    if [ "$rc" -eq 1 ]; then
      echo "❌ Freebuff ($role) terminó con error en la ronda $ROUND (timeout o fallo de la TUI)." >&2
      echo "   Revisa e reintenta, o usa FREEBUFF_MANUAL=1 para el modo interactivo." >&2
      exit 1
    fi
    if [ "$rc" -eq 2 ]; then
      echo "❌ No se pudo ejecutar Freebuff ($role): hay otra instancia activa. Ciérrala y reintenta." >&2
      exit 1
    fi
    if [ "$rc" -ne 0 ]; then
      echo "⚠️  La sesión de Freebuff ($role) terminó con código $rc; se comprobará el estado."
    fi
  fi
}

# --- Comprobaciones previas --------------------------------------------------
case "$AGENT_CLI" in
  agy|opencode)
    if ! command -v "$AGENT_CLI" >/dev/null 2>&1; then
      echo "❌ No se encontró el comando '$AGENT_CLI' (AGENT_CLI=$AGENT_CLI)." >&2
      echo "   Instálalo o usa otro run_workflow_*.sh." >&2
      exit 1
    fi
    ;;
  freebuff)
    if ! command -v freebuff >/dev/null 2>&1; then
      echo "❌ No se encontró el comando 'freebuff' (AGENT_CLI=$AGENT_CLI)." >&2
      echo "   Instálalo o usa otro run_workflow_*.sh." >&2
      exit 1
    fi
    if command -v tmux >/dev/null 2>&1 && [ "${FREEBUFF_MANUAL:-0}" != "1" ] && [ ! -x "$SCRIPT_DIR/run_freebuff_agent.sh" ]; then
      echo "❌ No se encontró el helper ejecutable: $SCRIPT_DIR/run_freebuff_agent.sh" >&2
      exit 1
    fi
    ;;
  *)
    echo "❌ AGENT_CLI inválido: '$AGENT_CLI' (usa 'opencode', 'freebuff' o 'agy')." >&2
    exit 1
    ;;
esac

for f in "$WORKFLOW_STATE" "$REVISOR_PROMPT" "$EDITOR_PROMPT"; do
  if [ ! -f "$f" ]; then
    echo "❌ No existe el archivo requerido: $f" >&2
    exit 1
  fi
done

if [ ! -w "$WORKFLOW_STATE" ]; then
  echo "❌ El archivo de estado no es escribible: $WORKFLOW_STATE" >&2
  exit 1
fi

# --- Bucle de rondas ----------------------------------------------------------
echo "🚀 Iniciando bucle de publicación IEEE con $AGENT_CLI"

while [ "$ROUND" -le "$MAX_ROUNDS" ]; do
  echo ""
  echo "=================================================="
  echo "  RONDA $ROUND / $MAX_ROUNDS: Evaluación Revisor IEEE"
  echo "=================================================="

  # Reinicia el estado de la ronda para evitar un "APPROVED" obsoleto de una ejecución anterior
  printf "STATUS: IN_REVIEW\nROUND: %s\n" "$ROUND" > "$WORKFLOW_STATE"

  # Ejecutar el Revisor (escribe STATUS: APPROVED si acepta)
  VERDICT_MTIME_BEFORE=$(stat -c %Y "$IEEE_VERDICT" 2>/dev/null || echo 0)
  run_agent "$REVISOR_PROMPT"
  check_agent_exit "Revisor" $?
  VERDICT_MTIME_AFTER=$(stat -c %Y "$IEEE_VERDICT" 2>/dev/null || echo 0)
  if [ "$VERDICT_MTIME_AFTER" = "$VERDICT_MTIME_BEFORE" ]; then
    echo "⚠️  El Revisor ($AGENT_CLI) no actualizó $IEEE_VERDICT en la ronda $ROUND."
  fi

  # Verificar si el Revisor aprobó el trabajo
  if grep -q "STATUS: APPROVED" "$WORKFLOW_STATE"; then
    echo ""
    echo "🎉 ¡EL PAPER HA SIDO ACEPTADO PARA PUBLICACIÓN EN LA IEEE!"
    echo "Revisa el informe final en $IEEE_VERDICT"
    exit 0
  fi

  echo ""
  echo "=================================================="
  echo "  RONDA $ROUND / $MAX_ROUNDS: Correcciones del Editor"
  echo "=================================================="

  # Ejecutar el Editor
  run_agent "$EDITOR_PROMPT"
  check_agent_exit "Editor" $?

  # Incrementar contador de rondas
  ROUND=$((ROUND + 1))
done

echo ""
echo "⚠️ Se alcanzó el límite de $MAX_ROUNDS rondas. Revisa '$IEEE_VERDICT' para ver el estado actual."
exit 1
