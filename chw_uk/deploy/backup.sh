#!/usr/bin/env bash
# Nightly backup of the database and uploads. Run as the `deploy` user (see DEPLOY.md, cron).
set -euo pipefail
DEST=/srv/backups/chw
STAMP=$(date +%F)
mkdir -p "$DEST"

# Database (reads credentials from the app's .env)
set -a; . /srv/chw/app/.env; set +a
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$DEST/db-$STAMP.sql.gz"

# Uploaded programmes / images
tar -czf "$DEST/media-$STAMP.tar.gz" -C /srv/chw/app media 2>/dev/null || true

# Keep 14 days
find "$DEST" -type f -mtime +14 -delete
