#!/usr/bin/env bash
# run_revisor.sh: Evalúa un paper específico con el prompt del revisor IEEE.

set -euo pipefail

PAPER_NAME=$1
if [ -z "$PAPER_NAME" ]; then
  echo "Uso: $0 <nombre_del_paper>"
  echo "Ejemplo: $0 paper_6_llm_reporting"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVISOR_PROMPT="$SCRIPT_DIR/.agy_prompts/revisor.md"

# Buscar el path del paper
PAPER_DIR=""
for dir in "$SCRIPT_DIR"/rnd_papers/"$PAPER_NAME" "$SCRIPT_DIR"/normal_papers/"$PAPER_NAME"; do
  if [ -d "$dir" ]; then
    PAPER_DIR="$dir"
    break
  fi
done

if [ -z "$PAPER_DIR" ]; then
  echo "❌ No se encontró el paper $PAPER_NAME"
  exit 1
fi

tmp=$(mktemp "/tmp/prompt_XXXXXX.md")
sed "s|__PAPER_DIR__|${PAPER_DIR}|g; s|__PAPER_NAME__|${PAPER_NAME}|g" "$REVISOR_PROMPT" > "$tmp"

echo "=================================================="
echo " Ejecutando Revisor IEEE para: $PAPER_NAME"
echo "=================================================="

opencode run -m ollama/qwen3-coder-next:latest "$(cat "$tmp")"
rm -f "$tmp"
