#!/usr/bin/env bash
# Runner for Streamlit on port 3000 bound to 0.0.0.0 for AI Studio container
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYLIBS_DIR="$SCRIPT_DIR/__pypackages__"
if [ -d "$PYLIBS_DIR" ]; then
  export PYTHONPATH="$PYLIBS_DIR:${PYTHONPATH:-}"
  export PATH="$PYLIBS_DIR/bin:$PATH"
fi

# Ensure dependencies are importable; bootstrap pip if missing and install into __pypackages__
if ! python3 -c "import streamlit, google.genai, dotenv, gtts, PIL.Image, pypdf" 2>/dev/null; then
  echo "Python dependencies not found. Bootstrapping and installing from requirements.txt..."
  if ! python3 -m pip --version >/dev/null 2>&1; then
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
    python3 /tmp/get-pip.py --break-system-packages --no-warn-script-location
    rm -f /tmp/get-pip.py
  fi
  mkdir -p "$PYLIBS_DIR"
  python3 -m pip install --no-cache-dir --target "$PYLIBS_DIR" -r "$SCRIPT_DIR/requirements.txt"
  export PYTHONPATH="$PYLIBS_DIR:${PYTHONPATH:-}"
  export PATH="$PYLIBS_DIR/bin:$PATH"
fi

exec python3 -m streamlit run "$SCRIPT_DIR/app.py" \
  --global.developmentMode=false \
  --server.port=3000 \
  --server.address=0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.headless=true
