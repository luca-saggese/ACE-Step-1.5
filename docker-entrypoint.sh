#!/usr/bin/env sh
set -e

CHECKPOINTS_DIR="/app/checkpoints"

if [ ! -d "$CHECKPOINTS_DIR/acestep-v15-turbo" ] || [ ! -d "$CHECKPOINTS_DIR/vae" ]; then
  echo "Models not found. Download starting..."
  uv run acestep-download --dir "$CHECKPOINTS_DIR"
else
  echo "Models found in $CHECKPOINTS_DIR"
fi

exec uv run acestep --server-name 0.0.0.0 --port 7860 --enable-api
