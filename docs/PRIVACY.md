# Privacy Specification

## 1. Fundamental Requirement

All participant feedback is anonymous from the perspective of the person being evaluated.

The system internally knows who submitted a rating because authentication is required.

However, the evaluated participant must never be able to discover the evaluator's identity through the application.

---

# 2. Information Hidden From Participants

Participants must never see:

- evaluator username
- evaluator name
- evaluator ID
- evaluator email
- evaluator profile
- IP address
- user agent
- device information
- evaluator-specific timestamps
- database IDs that can be correlated with evaluators

---

# 3. Ratings

Internal database:

```text
evaluator_id
target_id
category_id
score
created_at
```

Participant-facing API:

```text
category
average
rating_count
```

Never return:

```text
evaluator_id
```

---

# 4. Memories

Internal database may contain:

```text
author_id
target_id
text
created_at
status
```

Participant-facing response:

```text
id
text
```

Never return:

```text
author_id
author_username
author_name
```

---

# 5. API Security

Do not rely on frontend hiding.

For every endpoint ask:

> Could the authenticated participant use this endpoint to discover who rated someone?

If yes, redesign the endpoint.

---

# 6. IDOR Prevention

A participant must not be able to modify the URL:

```text
/api/users/123/results
```

to access another participant's private information unless that information is explicitly public to participants.

Backend authorization must be based on authenticated user permissions.

Never trust IDs coming from the frontend.

---

# 7. Aggregates

Results should be aggregated server-side.

Example:

```json
{
  "category": "vibe",
  "average": 8.1,
  "count": 14
}
```

Do not send all individual scores to the frontend.

---

# 8. Minimum Count

Default minimum:

```text
3
```

Before displaying an aggregate.

If there are fewer than three ratings:

```text
نتیجه برای نمایش هنوز کافی نیست.
```

---

# 9. Rating Counts

The People page may display:

```text
12 ratings
```

This is acceptable because it does not reveal evaluator identity.

However:

- do not display timestamps
- do not display who has rated
- do not expose rating history
- do not allow filtering by evaluator

---

# 10. Memories and Identifiability

The application cannot guarantee that a participant will never recognize someone's writing style.

Therefore the UI should clearly communicate:

```text
خاطرات و توضیحات به‌صورت ناشناس نمایش داده می‌شوند.
```

Do not attempt to technically identify or reveal authors.

---

# 11. Admin Privacy

Administrators may manage the event and moderate content.

The admin interface should not casually expose evaluator identities.

If an administrative audit log is implemented later, it must be clearly separated from the normal participant experience and protected by strict permissions.

---

# 12. Analytics

Do not send personal feedback text to third-party analytics services.

Avoid third-party trackers by default.

---

# 13. Logging

Application logs must not contain:

- passwords
- JWT tokens
- full memory text
- unnecessary personal data

Do not log complete rating payloads in production.

---

# 14. Error Messages

Do not expose database objects, SQL errors, internal IDs, or stack traces to users.

---

# 15. Privacy Testing

Create automated tests proving:

1. Participant A cannot discover that Participant B submitted a rating.
2. Participant A cannot discover authors of memories.
3. Participant A cannot access evaluator-specific endpoints.
4. Participant A cannot access another participant's private account data.
5. Aggregate endpoints return only aggregate information.