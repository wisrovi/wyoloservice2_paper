#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  Workflow de publicación IEEE usando opencode — modo paper-por-paper.
#  Procesa cada paper secuencialmente: solo avanza al siguiente cuando
#  el revisor IEEE aprobó el paper actual.
#
#  Uso:
#    ./run_workflow_opencode.sh                          # todos los papers
#    PAPER_FILTER=paper_3 ./run_workflow_opencode.sh     # solo paper_3
#    MAX_ROUNDS=5 ./run_workflow_opencode.sh             # max 5 rondas por paper
#    OPENCODE_AUTO=0 ./run_workflow_opencode.sh          # desactiva auto-aprobado
#
#  Requisitos: opencode instalado y con provider autenticado (opencode auth).
# ─────────────────────────────────────────────────────────────────────────────

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_CLI=opencode

# Define run_agent para opencode
run_agent() {
  local prompt_file="${1:?uso: run_agent <prompt_file>}"
  if [ "${OPENCODE_AUTO:-1}" = "1" ]; then
    opencode run --auto "$(cat "$prompt_file")"
  else
    opencode run "$(cat "$prompt_file")"
  fi
}
export -f run_agent
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
