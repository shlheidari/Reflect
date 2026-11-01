# Deployment (Production)

This complements `docs/SECURITY.md`'s production checklist with the concrete
steps and files that implement it.

## 1. Architecture

Production runs three containers (`docker-compose.prod.yml`), built from
`Dockerfile.prod` in each app directory instead of the dev `Dockerfile`s:

- **db** — the same `postgres:16-alpine` image as dev, but not published to
  the host; only `backend` can reach it.
- **backend** — Gunicorn serving Django/DRF, static admin assets via
  WhiteNoise, `DEBUG=False`. Listens on 8000.
- **frontend** — the Vite production build (`npm run build`) served as
  static files by nginx. Listens on 80.

Unlike dev, there are **no bind-mounted source volumes** — each image is
self-contained, and code changes require a rebuild (`--build`), not a hot
reload.

This app is a small, private, single-event tool, not an internet-scale
service — the choices below are deliberately practical, not maximal. Two
things are explicitly **not** included and would need to be added before a
larger or longer-lived deployment:

- **TLS termination.** `backend`/`frontend` speak plain HTTP; put a reverse
  proxy or load balancer in front of them (Caddy, nginx-on-the-host, or a
  cloud provider's LB) that terminates HTTPS and forwards
  `X-Forwarded-Proto`. Once that's in place, set `DJANGO_BEHIND_HTTPS_PROXY`,
  `DJANGO_SECURE_SSL_REDIRECT`, and `DJANGO_SECURE_HSTS_SECONDS` in
  `.env.prod` (see `.env.prod.example`).
- **External error monitoring** (e.g. Sentry). Errors currently go to
  container stdout/stderr (`docker compose logs`), which is enough at this
  scale but won't page anyone.

## 2. First-time setup

```bash
cp .env.prod.example .env.prod
# edit .env.prod: real secret key, real DB password, real domain(s)
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Build and start:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

`--env-file .env.prod` is required (not just `env_file:` in the compose
file) — it's what lets `${POSTGRES_DB}` etc. resolve inside
`docker-compose.prod.yml` itself, in addition to being passed into the
backend container.

Static assets are collected automatically on container start
(`backend/docker-entrypoint.prod.sh`). Migrations are **not** automatic —
run them explicitly, the first time and after every deploy that adds one:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec backend python manage.py migrate
```

Create the first admin user:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec backend python manage.py createsuperuser
```

## 3. Redeploying after a code change

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.prod exec backend python manage.py migrate
```

## 4. Health checks

`GET /api/health/` returns `{"status": "ok"}` and requires no auth — used by
the backend container's own Docker healthcheck, and can be pointed to by an
external uptime monitor or load balancer probe.

## 5. Database backups

`scripts/backup_db.sh` dumps and gzips the database via `pg_dump` (run from
the repo root, with `.env.prod` present):

```bash
./scripts/backup_db.sh
```

Writes to `backups/reflect_<timestamp>.sql.gz` (gitignored). Schedule it
with cron for regular backups, e.g. nightly:

```cron
0 3 * * * cd /path/to/reflect && ./scripts/backup_db.sh >> backups/backup.log 2>&1
```

**Restore** (destructive — confirm you're restoring into the intended
environment first):

```bash
gunzip -c backups/reflect_<timestamp>.sql.gz | \
  docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db \
  psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

## 6. Media files

Participant avatars live on the `backend_media` named Docker volume (see
`docker-compose.prod.yml`), so they survive container rebuilds/redeploys.
They are not included in `scripts/backup_db.sh` — back up that volume
separately if avatar loss would matter:

```bash
docker run --rm -v reflect_backend_media:/data -v "$PWD/backups":/backup \
  alpine tar czf /backup/media_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

## 7. Logging

Both containers log to stdout/stderr in plain text (`docker compose logs -f
backend` / `frontend`). Per `docs/SECURITY.md`, request bodies, passwords,
and tokens are never logged — Django/DRF don't log those by default, and
nothing in this app's code logs raw request data.
