# Development Roadmap

## Phase 0 — Planning

Tasks:

- inspect repository
- read all documentation
- confirm architecture
- create project structure

Do not build UI yet.

---

# Phase 1 — Infrastructure

Build:

- Docker Compose
- PostgreSQL
- Django
- DRF
- environment configuration
- React/Vite
- Tailwind
- basic project shell

Acceptance:

```text
docker compose up
```

works.

---

# Phase 2 — Authentication

Build:

- custom User
- login
- JWT
- protected routes
- logout
- current user endpoint

Acceptance:

Participant can log in and access the protected dashboard.

---

# Phase 3 — Event and Participants

Build:

- Event
- Participant
- admin participant management
- participant list

Acceptance:

Admin can create participants and participants can see eligible people.

---

# Phase 4 — Rating Categories

Build:

- RatingCategory
- admin CRUD
- ordering
- active/inactive
- required/optional

Seed the initial categories from `RATING_SYSTEM.md`.

---

# Phase 5 — Rating System

Build:

- rating UI
- 0–10 sliders
- rating submission
- validation
- duplicate protection
- self-rating protection
- edit support if enabled

Acceptance:

A participant can successfully rate another participant.

---

# Phase 6 — Anonymous Results

Build:

- aggregate calculation
- participant result page
- rating counts
- minimum sample threshold

Critical:

Verify evaluator identity is never exposed.

---

# Phase 7 — Memories

Build:

- memory submission
- anonymous display
- reporting
- moderation

---

# Phase 8 — Admin Dashboard

Build:

- participants
- categories
- event settings
- statistics
- moderation

---

# Phase 9 — Security

Perform explicit audit:

- authentication
- authorization
- IDOR
- XSS
- rate limiting
- data exposure
- evaluator privacy

---

# Phase 10 — Testing

Add:

- unit tests
- API tests
- privacy tests
- E2E tests

---

# Phase 11 — UI Polish

Improve:

- mobile UX
- RTL
- animations
- loading states
- empty states
- error states
- responsive layout

---

# Phase 12 — Production

Prepare:

- production environment
- Docker production configuration
- HTTPS
- database backups
- environment secrets
- logging
- monitoring

---

# Definition of MVP

MVP is complete when:

- participants can log in
- participants can see other participants
- participants can rate others on 0–10 scales
- participants can submit anonymous memories
- participants can see anonymous aggregate results about themselves
- participant identities are protected
- admin can manage participants/categories
- admin can moderate memories
- tests pass
- mobile UI works