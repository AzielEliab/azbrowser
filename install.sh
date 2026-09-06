#!/usr/bin/env bash
# AZBrowser one-click install. Counted download via this project's Worker.
# Usage: curl -fsSL https://azbrowser-download-tracker.vibelock.workers.dev/install.sh | bash
set -euo pipefail

HOST="${AZBROWSER_HOST:-https://azbrowser-download-tracker.vibelock.workers.dev}"
ASSET="${AZBROWSER_ASSET:-azbrowser-0.1.0.tar.gz}"
WORKDIR="${AZBROWSER_HOME:-$HOME/azbrowser}"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "Downloading counted tarball from ${HOST}/download (User-Agent Mozilla/5.0)…"
curl -fsSL -A 'Mozilla/5.0' "${HOST}/download?asset=${ASSET}" -o "${ASSET}"

tar -xzf "${ASSET}"
DIR="$(find . -maxdepth 1 -type d -name 'azbrowser-*' | head -n 1)"
if [ -n "${DIR}" ]; then
  cd "${DIR}"
fi

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

echo
echo "Installed AZBrowser."
echo "Run: azbrowser ui"
echo "Then open http://127.0.0.1:8878 (loopback only)"
echo "Phase 1 research shell — not Chromium. Author: Aziel Eliab."
