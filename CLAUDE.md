# Ayneh (آینه) — Anonymous Group Feedback Platform — Claude Code Instructions

## 1. Project Overview

Build a private web application (named **Ayneh / آینه**) for any closed group or event (graduation party, class, team, camp, workplace…) where participants can anonymously rate and write memories about other participants.

The application is intended for a closed group of people attending the same event; graduation is only one example, so avoid occasion-specific wording in code and UI.

Each participant receives a username and password from the administrator.

After logging in, a participant can:

1. See the list of other participants.
2. Select people they want to rate.
3. Rate each selected person across multiple 0–10 bipolar scales.
4. Write an optional anonymous memory/story about that person.
5. Write optional additional comments.
6. See the aggregate results about themselves.
7. See memories/comments written about themselves.
8. Never see who submitted any specific rating, memory, or comment.

The administrator can manage participants, rating categories, event settings, moderation, and the overall system.

---

# 2. Core Principles

## Privacy First

The identity of the person submitting a rating must never be exposed to the rated person.

The UI must never display:

- evaluator username
- evaluator name
- evaluator ID
- submission timestamp in a way that identifies the evaluator
- any technical identifier that could reveal the evaluator

The backend must enforce this privacy model as well.

Do not rely only on hiding information in the frontend.

---

# 3. Technology Stack

Use:

### Backend
- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT authentication

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query

### Infrastructure
- Docker
- Docker Compose

Use clean REST APIs between frontend and backend.

Keep backend and frontend separated.

---

# 4. Development Philosophy

Do not try to build the entire project in one step.

Work incrementally.

Before implementing a feature:

1. Read the relevant documentation in `/docs`.
2. Inspect the current codebase.
3. Identify existing architecture.
4. Implement the smallest complete version.
5. Run tests.
6. Fix errors.
7. Only then move to the next feature.

Do not rewrite working parts of the project unnecessarily.

Do not introduce additional frameworks without a clear reason.

Prefer simple, maintainable solutions.

---

# 5. Required Documentation

Before coding, read:

- `docs/PRODUCT.md`
- `docs/UX.md`
- `docs/RATING_SYSTEM.md`
- `docs/PRIVACY.md`
- `docs/DATABASE.md`
- `docs/API.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `docs/ROADMAP.md`

These files define the intended product behavior.

If implementation conflicts with the documentation, stop and identify the conflict rather than silently changing the product requirements.

---

# 6. Main User Roles

There are two roles.

## ADMIN

The administrator can:

- create participants
- edit participants
- disable participants
- reset passwords
- view participation statistics
- manage rating categories
- moderate memories/comments
- configure the event
- view system statistics

The administrator must NOT automatically be able to see which participant submitted a specific anonymous rating unless an explicit future security/audit feature is introduced.

## PARTICIPANT

A participant can:

- log in
- see eligible participants
- rate other participants
- edit their own unfinished/submitted ratings if the event configuration allows it
- write memories
- see anonymous aggregate results about themselves
- see anonymous memories about themselves
- log out

A participant must not be able to rate themselves.

---

# 7. Rating Model

Ratings use a bipolar 0–10 scale.

For example:

0 = completely left-side characteristic
5 = balanced / middle
10 = completely right-side characteristic

The exact labels and descriptions are defined in `docs/RATING_SYSTEM.md`.

Use sliders or an equivalent highly understandable UI.

Always display both endpoints.

Example:

`خوش‌کشیک ───────────── بدکشیک`

The user should be able to understand what 0 and 10 represent.

---

# 8. Anonymous Results

Participants can see results about themselves.

For each category show:

- average score
- number of submitted ratings
- optionally distribution/histogram if enabled
- category label

Example:

```text
خوش‌کشیک ←→ بدکشیک

Average: 7.4
Ratings: 18
```

Do not show:

- individual scores
- evaluator names
- evaluator usernames
- evaluator identities

---

# 9. Memories

Each participant has a section containing anonymous memories/comments written about them.

Each memory should show:

- text
- optional category/type
- moderation status internally

Do not show author identity.

The participant must not be able to infer the author through frontend data.

---

# 10. Participation Selection

The initial rating screen should show the list of other participants.

For every participant show:

- name
- profile/avatar if enabled
- whether the current user has already rated them
- number of ratings received by that participant

The rating count exists partly to encourage participation and prevent someone from receiving zero feedback.

Example:

```text
Ali Rezaei
18 ratings received
[Rate]
```

Do not expose evaluator identities.

Do not create a public competitive leaderboard.

---

# 11. Anti-Abuse Requirements

Because participants are rating real people, the system must include moderation safeguards.

Required:

- admin moderation for reported memories/comments
- report button for inappropriate memories
- ability to hide/remove inappropriate content
- no public leaderboard
- no ranking participants by score
- no display of individual evaluator scores
- rate limiting
- authentication
- authorization checks
- server-side validation

Avoid UI patterns that encourage harassment or humiliation.

---

# 12. Authentication

Participants receive credentials from the administrator.

Initial version:

- username
- password

Passwords must be stored securely using Django's password hashing.

Never store plaintext passwords.

JWT authentication should be used for the API.

The frontend should protect authenticated routes.

---

# 13. Backend Requirements

Use:

- Django
- Django REST Framework
- PostgreSQL
- JWT

Recommended application structure:

```text
backend/
├── config/
├── apps/
│   ├── accounts/
│   ├── participants/
│   ├── ratings/
│   ├── memories/
│   ├── moderation/
│   └── events/
└── manage.py
```

Keep business logic out of serializers where possible.

Use service functions/classes for complex operations.

---

# 14. Frontend Requirements

Use:

- React
- TypeScript
- Vite
- Tailwind
- React Router
- TanStack Query

Required pages:

- Login
- Participant Home
- People List
- Rating Page
- My Results
- Memories About Me
- Profile/Account
- Admin Dashboard
- Admin Participants
- Admin Rating Categories
- Admin Moderation

Mobile-first responsive design is required.

The application should work particularly well on phones because participants will likely use their phones at the event.

---

# 15. UI Language

Primary language:

Persian

Use RTL layout.

The codebase should still be structured so English/Arabic localization can be added later.

Use Persian-friendly typography.

Avoid hard-coding text directly into complex components when practical.

---

# 16. Design Direction

The product should feel:

- modern
- fun
- friendly
- group-event oriented (not tied to any one occasion)
- lightweight
- mobile-first

It should not feel like a medical or corporate survey application.

Use cards, sliders, progress indicators, avatars, and subtle animations where appropriate.

Avoid excessive animations.

---

# 17. Data Integrity

Every rating submission must be associated internally with:

- evaluator
- target participant
- event
- rating category
- score
- creation timestamp

However, evaluator identity must never be returned in participant-facing result APIs.

Use backend serializers/querysets that explicitly prevent accidental exposure.

---

# 18. Important Privacy Rule

NEVER create an API response such as:

```json
{
  "evaluator": {
    "id": 12,
    "username": "..."
  }
}
```

for participant-facing endpoints.

Instead:

```json
{
  "category": "good_shift",
  "average": 7.4,
  "rating_count": 18
}
```

For memories:

```json
{
  "id": 123,
  "text": "...",
  "created_at": "..."
}
```

No author information.

---

# 19. Testing

Write automated tests for:

- authentication
- authorization
- self-rating prevention
- rating creation
- rating updates
- aggregate calculations
- anonymous result APIs
- memory creation
- memory privacy
- moderation
- disabled accounts
- rate limiting
- participant visibility rules

Especially test that one participant can NEVER retrieve another participant's evaluator identities.

---

# 20. Security

Before considering the MVP complete, audit:

- IDOR vulnerabilities
- authorization bypass
- JWT handling
- password handling
- CSRF where applicable
- XSS
- SQL injection
- rate limiting
- excessive API data exposure
- enumeration attacks
- accidental evaluator identity leakage

---

# 21. Development Workflow

Follow this order:

1. Project initialization
2. Docker/PostgreSQL
3. Django configuration
4. User/authentication system
5. Participant model
6. Event model
7. Rating categories
8. Rating submission
9. Aggregate calculations
10. Anonymous memories
11. Participant dashboard
12. Admin dashboard
13. Moderation
14. Security hardening
15. Tests
16. UI polish
17. Production configuration

Do not skip tests.

---

# 22. Definition of Done

A feature is not complete until:

- backend implementation exists
- API is tested
- frontend is implemented
- loading/error/empty states exist
- authorization is enforced
- privacy implications are checked
- automated tests exist where appropriate
- the application runs successfully

---

# 23. Claude Code Behavior

When working on this project:

- Explain the plan before major architectural changes.
- Inspect existing files before modifying them.
- Do not delete functionality without justification.
- Do not fabricate requirements.
- If a requirement is ambiguous, choose the simplest safe implementation and document the assumption.
- Keep documentation synchronized with implementation.
- After each meaningful milestone, run tests and verify the application.
- Report exactly what was changed.
- Report remaining issues honestly.

Never claim that something works without testing it.