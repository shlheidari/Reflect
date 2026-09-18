# Graduation Rating Platform

A private web app for a graduation event: participants anonymously rate and
write memories about each other. See `docs/PRODUCT.md` for the full product
spec and `docs/ROADMAP.md` for build phases.

Stack: Django + DRF + PostgreSQL + JWT (backend), React + TypeScript + Vite +
Tailwind + TanStack Query (frontend), Docker Compose.

## Local development

```bash
cp .env.example .env
# edit .env if needed — defaults work out of the box for local dev
docker compose up
```

- Backend: http://localhost:8000 (API under `/api/`, admin at `/admin/`)
- Frontend: http://localhost:5173

Source is bind-mounted, so both the Django dev server and Vite's dev server
hot-reload on file changes.

### Database setup and migrations

The `db` service and its `postgres_data` volume are created automatically by
`docker compose up`. Apply migrations and seed the rating categories:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_rating_categories
docker compose exec backend python manage.py createsuperuser
```

After changing any model, create and apply a new migration the same way:

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### Tests

```bash
docker compose exec backend python manage.py test
docker compose exec frontend npm run test
```

### Lint and type-check (frontend)

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npx tsc -b
```

## Production build

```bash
docker compose exec frontend npm run build   # tsc -b && vite build -> frontend/dist
```

Docker images used in production (`backend/Dockerfile.prod`,
`frontend/Dockerfile.prod`) build this same way internally — see
**`docs/DEPLOYMENT.md`** for the full production deployment guide:
environment variables, `docker-compose.prod.yml` usage, migrations, health
checks, and database backup/restore.
