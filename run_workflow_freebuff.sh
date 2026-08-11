#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  Workflow de publicación IEEE usando Freebuff — modo paper-por-paper.
#  Procesa cada paper secuencialmente: solo avanza al siguiente cuando
#  el revisor IEEE aprobó el paper actual.
#
#  Uso:
#    ./run_workflow_freebuff.sh                          # todos los papers
#    PAPER_FILTER=paper_1 ./run_workflow_freebuff.sh     # solo paper_1
#    FREEBUFF_MANUAL=1 ./run_workflow_freebuff.sh        # modo interactivo
#
#  Requisitos: freebuff instalado, tmux (automático) o FREEBUFF_MANUAL=1.
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_CLI=freebuff

# Define run_agent para freebuff
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
  freebuff --cwd "$SCRIPT_DIR"
}
export -f run_agent
export -f copy_to_clipboard
export AGENT_CLI

# ── Recopilar papers ─────────────────────────────────────────────────────────
PAPERS=()
for dir in "$SCRIPT_DIR"/rnd_papers/paper_* "$SCRIPT_DIR"/normal_papers/paper_*; do
  if [ -d "$dir" ]; then
    # Filtro opcional por nombre (exacto: paper_1 o paper_1_* pero NO paper_10)
    if [ -n "${PAPER_FILTER:-}" ]; then
      _pname="$(basename "$dir")"
      case "${_pname}" in
        "${PAPER_FILTER}"|"${PAPER_FILTER}"_*) PAPERS+=("$dir") ;;
      esac
    else
      PAPERS+=("$dir")
    fi
  fi
done

if [ ${#PAPERS[@]} -eq 0 ]; then
  echo "❌ No se encontraron papers${PAPER_FILTER:+ que coincidan con '$PAPER_FILTER'} en rnd_papers/ ni normal_papers/"
  exit 1
fi

TOTAL=${#PAPERS[@]}
CURRENT=0
APPROVED_COUNT=0
FAILED_COUNT=0

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 Workflow IEEE — $AGENT_CLI — $TOTAL paper(s)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

for paper in "${PAPERS[@]}"; do
  CURRENT=$((CURRENT + 1))
  export PAPER_DIR="$paper"
  export PAPER_NAME="$(basename "$paper")"

  echo "┌───────────────────────────────────────────────────────────┐"
  echo "│  📚 [$CURRENT/$TOTAL] Paper: $PAPER_NAME"
  echo "└───────────────────────────────────────────────────────────┘"

  # Ejecuta workflow_core.sh en subshell para este paper
  bash "$SCRIPT_DIR/workflow_core.sh"
  rc=$?

  if [ $rc -eq 0 ]; then
    APPROVED_COUNT=$((APPROVED_COUNT + 1))
    echo "  ✅ $PAPER_NAME → APROBADO"
  else
    FAILED_COUNT=$((FAILED_COUNT + 1))
    echo "  ❌ $PAPER_NAME → NO APROBADO (max rondas alcanzado)"
  fi
  echo ""
done

# ── Resumen final ────────────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════"
echo "  📊 RESUMEN FINAL"
echo "═══════════════════════════════════════════════════════════════"
echo "  Total papers:  $TOTAL"
echo "  ✅ Aprobados:  $APPROVED_COUNT"
echo "  ❌ Rechazados: $FAILED_COUNT"
echo "═══════════════════════════════════════════════════════════════"

if [ $FAILED_COUNT -gt 0 ]; then
  exit 1
fi
exit 0
