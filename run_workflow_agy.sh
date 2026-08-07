#!/usr/bin/env bash
# Workflow de publicación IEEE usando agy.
#   agy run --instructions "<prompt_file>"
# Requisitos: agy instalado y con cuota activa (actualmente requiere suscripción).

AGENT_CLI=agy

run_agent() {
  local prompt_file="${1:?uso: run_agent <prompt_file>}"
  agy run --instructions "$prompt_file"
}

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/workflow_core.sh"
