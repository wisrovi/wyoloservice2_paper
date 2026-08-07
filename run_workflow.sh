#!/usr/bin/env bash

set -u  # Falla si se usa una variable sin definir

# CLI del agente que ejecuta las instrucciones (revisor/editor).
#   AGENT_CLI=freebuff (por defecto): lanza Freebuff automáticamente en una sesión
#     tmux (inyecta el prompt y espera al agente). Sin tmux, o con FREEBUFF_MANUAL=1,
#     cae al modo interactivo manual (imprime/copia el prompt y abre la TUI).
#   AGENT_CLI=opencode  : no-interactivo (opencode run "<prompt>"). Necesita auth de opencode.
#     OPENCODE_AUTO=0 desactiva el auto-aprobado de permisos (por defecto 1).
#   AGENT_CLI=agy        : ejecución con agy run --instructions (requiere cuota activa y TTY).
AGENT_CLI="${AGENT_CLI:-freebuff}"

# Resuelve el directorio donde vive este script y trabaja desde ahí,
# para que el flujo (y el agente) sea independiente del CWD del usuario
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_ROUNDS=10
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
  if { [ "$AGENT_CLI" = "agy" ] || [ "$AGENT_CLI" = "opencode" ]; } && [ "$rc" -ne 0 ]; then
    echo "❌ El $role ($AGENT_CLI) falló en la ronda $ROUND. Revisa el error y reintenta." >&2
    exit 1
  fi
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

# Ejecuta el agente con las instrucciones del prompt indicado
run_agent() {
  local prompt_file="${1:?uso: run_agent <prompt_file>}"

  case "$AGENT_CLI" in
    agy)
      agy run --instructions "$prompt_file"
      ;;

    opencode)
      # opencode run es no-interactivo: ejecuta el prompt y termina solo
      if [ "${OPENCODE_AUTO:-1}" = "1" ]; then
        opencode run --auto "$(cat "$prompt_file")"
      else
        opencode run "$(cat "$prompt_file")"
      fi
      ;;

    freebuff)
      # Si una versión futura de Freebuff soporta 'run --instructions', actívalo con FREEBUFF_RUN=1
      if [ "${FREEBUFF_RUN:-0}" = "1" ]; then
        freebuff run --instructions "$prompt_file"
        return
      fi

      # Modo automático: Freebuff en una sesión tmux (inyecta el prompt y espera al agente)
      if command -v tmux >/dev/null 2>&1 && [ "${FREEBUFF_MANUAL:-0}" != "1" ]; then
        "$SCRIPT_DIR/run_freebuff_agent.sh" "$prompt_file" "$SCRIPT_DIR"
        return
      fi

      # Modo interactivo manual (sin tmux o FREEBUFF_MANUAL=1):
      # Freebuff (v0.0.142) no acepta prompts por CLI, así que mostramos/copiamos
      # las instrucciones y abrimos la TUI para pegarlas a mano.
      echo ""
      echo "══════════════════════════════════════════════════════════"
      echo "📋 INSTRUCCIONES PARA FREEBUFF — pega este prompt en la sesión"
      echo "══════════════════════════════════════════════════════════"
      cat "$prompt_file"
      echo "══════════════════════════════════════════════════════════"
      echo ""
      if copy_to_clipboard < "$prompt_file" 2>/dev/null; then
        echo "✅ Prompt copiado al portapapeles (pega con Ctrl+V en Freebuff)."
      else
        echo "⚠️  No se pudo copiar al portapapeles; cópialo manualmente."
      fi
      echo ""
      echo "Abriendo Freebuff en $SCRIPT_DIR ..."
      echo "Cuando el agente termine, cierra la sesión para continuar el bucle."
      echo "(Si Freebuff ya está abierto, elige 'Take over' para usar esa sesión.)"
      freebuff --cwd "$SCRIPT_DIR"
      ;;

    *)
      echo "❌ AGENT_CLI desconocido: '$AGENT_CLI' (usa 'agy' o 'freebuff')." >&2
      return 1
      ;;
  esac
}

# --- Comprobaciones previas --------------------------------------------------
case "$AGENT_CLI" in
  agy)
    if ! command -v agy >/dev/null 2>&1; then
      echo "❌ No se encontró el comando 'agy' (AGENT_CLI=$AGENT_CLI)." >&2
      echo "   Instálalo o cambia AGENT_CLI=freebuff." >&2
      exit 1
    fi
    ;;
  opencode)
    if ! command -v opencode >/dev/null 2>&1; then
      echo "❌ No se encontró el comando 'opencode' (AGENT_CLI=$AGENT_CLI)." >&2
      echo "   Instálalo o cambia AGENT_CLI=freebuff." >&2
      exit 1
    fi
    ;;
  freebuff)
    if ! command -v freebuff >/dev/null 2>&1; then
      echo "❌ No se encontró el comando 'freebuff' (AGENT_CLI=$AGENT_CLI)." >&2
      echo "   Instálalo o cambia AGENT_CLI=agy." >&2
      exit 1
    fi
    if command -v tmux >/dev/null 2>&1 && [ "${FREEBUFF_MANUAL:-0}" != "1" ] && [ ! -x "$SCRIPT_DIR/run_freebuff_agent.sh" ]; then
      echo "❌ No se encontró el helper ejecutable: $SCRIPT_DIR/run_freebuff_agent.sh" >&2
      exit 1
    fi
    ;;    *)
      echo "❌ AGENT_CLI inválido: '$AGENT_CLI' (usa 'freebuff', 'opencode' o 'agy')." >&2
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

echo "🚀 Iniciando bucle de publicación IEEE con $AGENT_CLI"

while [ "$ROUND" -le "$MAX_ROUNDS" ]; do
  echo ""
  echo "=================================================="
  echo "  RONDA $ROUND / $MAX_ROUNDS: Evaluación Revisor IEEE"
  echo "=================================================="

  # Reinicia el estado de la ronda para evitar un "APPROVED" obsoleto de una ejecución anterior
  printf "STATUS: IN_REVIEW\nROUND: %s\n" "$ROUND" > "$WORKFLOW_STATE"

  # Ejecutar el Revisor (escribe STATUS: APPROVED si acepta)
  run_agent "$REVISOR_PROMPT"
  check_agent_exit "Revisor" $?

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
