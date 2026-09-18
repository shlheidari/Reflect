# API Specification

Base:

```text
/api/
```

---

# Authentication

## POST

```text
/api/auth/login/
```

Request:

```json
{
  "username": "ali",
  "password": "password"
}
```

Response contains JWT tokens and safe user information.

Never return password.

---

# Current User

## GET

```text
/api/me/
```

Returns current participant information.

---

# Participants

## GET

```text
/api/participants/
```

Returns eligible participants for the current event.

Do not include private account data.

Example:

```json
{
  "id": 12,
  "display_name": "Ali",
  "avatar": null,
  "rating_count": 18,
  "rated_by_me": true
}
```

---

# Rating Categories

## GET

```text
/api/rating-categories/
```

Returns active categories for the current event.

---

# Submit Ratings

## POST

```text
/api/ratings/
```

Example:

```json
{
  "target_id": 12,
  "ratings": [
    {
      "category_id": 1,
      "score": 8
    },
    {
      "category_id": 2,
      "score": 6
    }
  ],
  "memory": "یاد اون کشیک..."
}
```

---

# Update Rating

If enabled:

## PUT/PATCH

```text
/api/ratings/{target_id}/
```

Only the evaluator's own ratings may be changed.

---

# My Results

## GET

```text
/api/me/results/
```

Example:

```json
{
  "rating_count": 18,
  "categories": [
    {
      "category_id": 1,
      "left_label": "خوش‌کشیک",
      "right_label": "بدکشیک",
      "average": 7.4,
      "count": 18
    }
  ]
}
```

Never return evaluator information.

---

# Memories About Me

## GET

```text
/api/me/memories/
```

Example:

```json
{
  "items": [
    {
      "id": 123,
      "text": "یاد اون مورنینگ..."
    }
  ]
}
```

Never return author information.

---

# Report Memory

## POST

```text
/api/memories/{id}/report/
```

Request:

```json
{
  "reason": "inappropriate"
}
```

---

# Admin Participants

## GET

```text
/api/admin/participants/
```

Admin only.

---

# Admin Categories

CRUD:

```text
/api/admin/rating-categories/
```

Admin only.

---

# Admin Moderation

## GET

```text
/api/admin/reports/
```

Admin only.

---

# Statistics

## GET

```text
/api/admin/statistics/
```

Admin only.

---

# API Security Rules

Every endpoint must have:

- authentication where required
- authorization
- serializer-level filtering
- object-level permission checks

Never rely on the frontend.

---

# Pagination

Use pagination for:

- participants
- memories
- reports
- admin tables

---

# Error Format

Use consistent JSON:

```json
{
  "detail": "Human readable message",
  "code": "validation_error"
}
```

Do not expose stack traces.