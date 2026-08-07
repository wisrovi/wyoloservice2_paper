#!/usr/bin/env bash
# Workflow de publicación IEEE usando Freebuff.
#   Automático: lanza Freebuff en una sesión tmux (run_freebuff_agent.sh), inyecta
#   el prompt y espera al marcador .freebuff_done.
#   Fallback manual (sin tmux o FREEBUFF_MANUAL=1): imprime/copia el prompt y abre la TUI.
#   FREEBUFF_RUN=1: hook para una futura versión de Freebuff con modo no-interactivo.

AGENT_CLI=freebuff

run_agent() {
  local prompt_file="${1:?uso: run_agent <prompt_file>}"

  # Hook futuro: 'freebuff run --instructions' no-interactivo
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
}

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/workflow_core.sh"
