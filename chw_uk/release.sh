#!/usr/bin/env bash
# Run on YOUR computer (Git Bash / WSL / macOS / Linux):
#   ./release.sh "what changed"
# Builds Tailwind, commits, pushes to GitHub. Set DEPLOY_HOST to also update the live server:
#   DEPLOY_HOST=deploy@YOUR_SERVER_IP ./release.sh "what changed"
set -euo pipefail
cd "$(dirname "$0")"

[ -d node_modules ] || npm install --no-audit --no-fund
npm run build

git add -A
if git diff --cached --quiet; then
  echo "Nothing new to commit."
else
  git commit -m "${1:-Update site}"
fi
git push

if [ -n "${DEPLOY_HOST:-}" ]; then
  ssh "$DEPLOY_HOST" "/srv/chw/app/deploy/deploy.sh"
fi
