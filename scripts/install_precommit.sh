#!/usr/bin/env bash
set -euo pipefail

echo "Installing pre-commit hooks..."
command -v pre-commit >/dev/null 2>&1 || {
  echo "pre-commit not found, installing via pip into venv..."
  ./venv/bin/pip install pre-commit
}

./venv/bin/pre-commit install
echo "pre-commit installed."
