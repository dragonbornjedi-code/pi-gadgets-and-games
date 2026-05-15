#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -x ".venv/bin/python3" ]; then
  exec .venv/bin/python3 main.py --windowed
fi

exec python3 main.py --windowed
