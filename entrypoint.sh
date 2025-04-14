#!/bin/bash
set -e

# Check for API key in environment, generate if not set
if [ -z "$ACTION_SERVER_API_KEY" ]; then
  export ACTION_SERVER_API_KEY=$(openssl rand -base64 32)
  echo "[entrypoint] No API key set, generated: $ACTION_SERVER_API_KEY"
else
  echo "[entrypoint] Using provided API key."
fi

exec action-server start \
  --api-key "$ACTION_SERVER_API_KEY" \
  --address 0.0.0.0 \
  --port 8087 \
  --verbose \
  --datadir=/action-server/datadir \
  --actions-sync=false
