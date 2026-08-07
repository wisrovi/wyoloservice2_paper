#!/usr/bin/env bash
# Workflow de publicación IEEE usando opencode (no-interactivo). Recomendado.
#   opencode run --auto "<prompt>"  (OPENCODE_AUTO=0 desactiva el auto-aprobado)
# Requisitos: opencode instalado y con provider autenticado (opencode auth).

AGENT_CLI=opencode

run_agent() {
  local prompt_file="${1:?uso: run_agent <prompt_file>}"
  if [ "${OPENCODE_AUTO:-1}" = "1" ]; then
    opencode run --auto "$(cat "$prompt_file")"
  else
    opencode run "$(cat "$prompt_file")"
  fi
}

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/workflow_core.sh"
