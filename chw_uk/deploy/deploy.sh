#!/usr/bin/env bash
# Run on the server as the `deploy` user:  /srv/chw/app/deploy/deploy.sh
set -euo pipefail

APP=/srv/chw/app
VENV=/srv/chw/venv

cd "$APP"
git pull --ff-only
"$VENV/bin/pip" install --quiet -r requirements.txt
"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py collectstatic --noinput --verbosity 0
sudo systemctl restart chw
sleep 2
systemctl is-active --quiet chw && echo "chw is running — deploy OK" || { echo "chw FAILED to start: journalctl -u chw -n 50"; exit 1; }
