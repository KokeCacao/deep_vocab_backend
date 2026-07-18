#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT"

if [[ ! -x .venv/bin/gunicorn ]]; then
    printf 'ERROR: run ./install.sh before starting DeepVocab.\n' >&2
    exit 1
fi

exec .venv/bin/gunicorn \
    --workers 1 \
    --threads 8 \
    --log-level debug \
    --worker-class gthread \
    --bind "${DEEPVOCAB_BIND:-127.0.0.1:5000}" \
    --no-control-socket \
    wsgi:app
