#!/bin/sh
# Dumps the production Postgres database to a timestamped, gzipped file.
# Usage (from the repo root, with .env.prod already filled in):
#   ./scripts/backup_db.sh
# See docs/DEPLOYMENT.md for restore instructions and a suggested cron entry.
set -eu

cd "$(dirname "$0")/.."

ENV_FILE="${1:-.env.prod}"
if [ ! -f "$ENV_FILE" ]; then
    echo "Env file not found: $ENV_FILE" >&2
    exit 1
fi
# shellcheck disable=SC1090
. "$ENV_FILE"

mkdir -p backups
timestamp=$(date +%Y%m%d_%H%M%S)
outfile="backups/reflect_${timestamp}.sql.gz"

docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" exec -T db \
    pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$outfile"

echo "Backup written to $outfile"
