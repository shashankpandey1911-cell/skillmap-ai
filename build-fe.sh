#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/frontend"

echo "→ building frontend for production..."
npm run build
echo "✓ frontend build complete"
