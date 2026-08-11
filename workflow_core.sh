#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  MOTOR COMPARTIDO del bucle de publicación IEEE (modo paper-por-paper).
#  Llamado desde run_workflow_<cli>.sh vía bash (subshell) para cada paper.
#
#  Requiere variables de entorno (exportadas por el wrapper):
#    AGENT_CLI  — "agy" | "opencode" | "freebuff"
#    PAPER_DIR  — ruta absoluta al directorio del paper a procesar
#    PAPER_NAME — nombre legible del paper (opcional, se deriva de PAPER_DIR)
#    run_agent() — función que ejecuta el agente IA con un prompt
# ─────────────────────────────────────────────────────────────────────────────

set -u

# El wrapper debe definir AGENT_CLI y PAPER_DIR antes de invocar
: "${AGENT_CLI:?Define AGENT_CLI antes de cargar workflow_core.sh}"
: "${PAPER_DIR:?Define PAPER_DIR (ruta al directorio del paper) antes de cargar workflow_core.sh}"

# Resuelve el directorio del proyecto (raíz del repo) y trabaja desde ahí
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Nombre legible del paper
PAPER_NAME="${PAPER_NAME:-$(basename "$PAPER_DIR")}"

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
    echo "❌ El $role ($AGENT_CLI) falló en la ronda $ROUND para '$PAPER_NAME'. Revisa el error y reintenta." >&2
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

for f in "$REVISOR_PROMPT" "$EDITOR_PROMPT"; do
  if [ ! -f "$f" ]; then
    echo "❌ No existe el archivo requerido: $f" >&2
    exit 1
  fi
done

if [ ! -d "$PAPER_DIR" ]; then
  echo "❌ No existe el directorio del paper: $PAPER_DIR" >&2
  exit 1
fi

if [ ! -w "$WORKFLOW_STATE" ]; then
  echo "❌ El archivo de estado no es escribible: $WORKFLOW_STATE" >&2
  exit 1
fi

# --- Utilidades para prompts con placeholders ---------------------------------
# Sustituye __PAPER_DIR__ y __PAPER_NAME__ en un prompt y escribe a un temp
render_prompt() {
  local src="$1"
  local tmp
  tmp=$(mktemp "/tmp/prompt_XXXXXX.md")
  sed "s|__PAPER_DIR__|${PAPER_DIR}|g; s|__PAPER_NAME__|${PAPER_NAME}|g" "$src" > "$tmp"
  echo "$tmp"
}

# --- Bucle de rondas (un solo paper) ------------------------------------------
echo "🚀 Iniciando bucle de publicación IEEE con $AGENT_CLI para: $PAPER_NAME"

# Renderiza prompts con el paper específico
RENDERED_REVISOR=$(render_prompt "$REVISOR_PROMPT")
RENDERED_EDITOR=$(render_prompt "$EDITOR_PROMPT")
# Limpieza al salir
trap "rm -f '$RENDERED_REVISOR' '$RENDERED_EDITOR'" EXIT

while [ "$ROUND" -le "$MAX_ROUNDS" ]; do
  echo ""
  echo "=================================================="
  echo "  [$PAPER_NAME] RONDA $ROUND / $MAX_ROUNDS: Evaluación Revisor IEEE"
  echo "=================================================="

  # Reinicia el estado de la ronda para evitar un "APPROVED" obsoleto
  printf "STATUS: IN_REVIEW\nROUND: %s\nPAPER: %s\n" "$ROUND" "$PAPER_NAME" > "$WORKFLOW_STATE"

  # Ejecutar el Revisor (escribe STATUS: APPROVED si acepta)
  VERDICT_MTIME_BEFORE=$(stat -c %Y "$IEEE_VERDICT" 2>/dev/null || echo 0)
  run_agent "$RENDERED_REVISOR"
  check_agent_exit "Revisor" $?
  VERDICT_MTIME_AFTER=$(stat -c %Y "$IEEE_VERDICT" 2>/dev/null || echo 0)
  if [ "$VERDICT_MTIME_AFTER" = "$VERDICT_MTIME_BEFORE" ]; then
    echo "⚠️  El Revisor ($AGENT_CLI) no actualizó $IEEE_VERDICT en la ronda $ROUND."
  fi

  # Verificar si el Revisor aprobó el trabajo
  if grep -q "STATUS: APPROVED" "$WORKFLOW_STATE"; then
    echo ""
    echo "🎉 ¡'$PAPER_NAME' HA SIDO ACEPTADO PARA PUBLICACIÓN EN LA IEEE!"
    echo "Revisa el informe final en $IEEE_VERDICT"
    exit 0
  fi

  echo ""
  echo "=================================================="
  echo "  [$PAPER_NAME] RONDA $ROUND / $MAX_ROUNDS: Correcciones del Editor"
  echo "=================================================="

  # Ejecutar el Editor
  run_agent "$RENDERED_EDITOR"
  check_agent_exit "Editor" $?

  # Incrementar contador de rondas
  ROUND=$((ROUND + 1))
done

echo ""
echo "⚠️ Se alcanzó el límite de $MAX_ROUNDS rondas para '$PAPER_NAME'. Revisa '$IEEE_VERDICT' para ver el estado actual."
exit 1
