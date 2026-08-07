#!/usr/bin/env bash

set -u  # Falla si se usa una variable sin definir

# Resuelve el directorio donde vive este script y trabaja desde ahí,
# para que el flujo (y el agente agy) sea independiente del CWD del usuario
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_ROUNDS=3
ROUND=1

WORKFLOW_STATE="$SCRIPT_DIR/WORKFLOW_STATE.md"
IEEE_VERDICT="$SCRIPT_DIR/IEEE_REVIEW_VERDICT.md"
REVISOR_PROMPT="$SCRIPT_DIR/.agy_prompts/revisor.md"
EDITOR_PROMPT="$SCRIPT_DIR/.agy_prompts/editor.md"

# --- Comprobaciones previas --------------------------------------------------
if ! command -v agy >/dev/null 2>&1; then
  echo "❌ No se encontró el comando 'agy' (Antigravity CLI)." >&2
  echo "   Instálalo o añádelo al PATH antes de ejecutar el workflow." >&2
  exit 1
fi

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

echo "🚀 Iniciando bucle de publicación IEEE con Antigravity CLI (agy)"

while [ "$ROUND" -le "$MAX_ROUNDS" ]; do
  echo ""
  echo "=================================================="
  echo "  RONDA $ROUND / $MAX_ROUNDS: Evaluación Revisor IEEE"
  echo "=================================================="

  # Reinicia el estado de la ronda para evitar un "APPROVED" obsoleto de una ejecución anterior
  printf "STATUS: IN_REVIEW\nROUND: %s\n" "$ROUND" > "$WORKFLOW_STATE"

  # Ejecutar agy con las instrucciones del Revisor (el revisor escribe STATUS: APPROVED si acepta)
  agy run --instructions "$REVISOR_PROMPT"
  if [ $? -ne 0 ]; then
    echo "❌ El Revisor (agy) falló en la ronda $ROUND. Revisa el error y reintenta." >&2
    exit 1
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

  # Ejecutar agy con las instrucciones del Autor/Editor
  agy run --instructions "$EDITOR_PROMPT"
  if [ $? -ne 0 ]; then
    echo "❌ El Editor (agy) falló en la ronda $ROUND. Revisa el error y reintenta." >&2
    exit 1
  fi

  # Incrementar contador de rondas
  ROUND=$((ROUND + 1))
done

echo ""
echo "⚠️ Se alcanzó el límite de $MAX_ROUNDS rondas. Revisa '$IEEE_VERDICT' para ver el estado actual."
exit 1
