#!/usr/bin/env bash
# Simple helper to run the Gradio app in the repo venv
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$REPO_ROOT/venv"
if [ ! -d "$VENV" ]; then
  echo "No venv found at $VENV. Create it with: python -m venv venv && ./venv/bin/pip install -r requirements.txt"
  exit 1
fi
# Use the venv python to run the app so we don't need to 'activate'
"$VENV/bin/python" "$REPO_ROOT/ui/app_gradio.py" "$@"
