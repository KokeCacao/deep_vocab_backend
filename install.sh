#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT"

UV_BIN=${UV_BIN:-}
if [[ -z $UV_BIN ]] && command -v uv >/dev/null 2>&1; then
    UV_BIN=$(command -v uv)
elif [[ -z $UV_BIN && -x /opt/kokecacao/bin/uv ]]; then
    UV_BIN=/opt/kokecacao/bin/uv
fi

if [[ -z $UV_BIN || ! -x $UV_BIN ]]; then
    printf 'ERROR: uv is required; install it or set UV_BIN.\n' >&2
    exit 1
fi

"$UV_BIN" sync --frozen
.venv/bin/python -m unittest discover -s tests -v
