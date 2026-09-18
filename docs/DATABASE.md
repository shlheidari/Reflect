# Database Design

## 1. Event

```text
Event
-----
id
name
status
start_at
end_at
results_enabled
memories_enabled
allow_rating_edit
minimum_ratings_for_results
created_at
updated_at
```

Status:

```text
DRAFT
OPEN
CLOSED
```

---

# 2. User

Use Django's custom user model.

```text
User
----
id
username
password
is_active
is_staff
created_at
updated_at
```

Do not create a second authentication system.

---

# 3. Participant

```text
Participant
-----------
id
user_id
display_name
avatar
event_id
is_active
created_at
updated_at
```

A participant belongs to an event.

---

# 4. RatingCategory

```text
RatingCategory
--------------
id
event_id
key
left_label
right_label
description
order
required
active
created_at
updated_at
```

---

# 5. Rating

```text
Rating
------
id
event_id
evaluator_id
target_id
category_id
score
created_at
updated_at
```

Constraints:

```text
score >= 0
score <= 10
```

Unique constraint:

```text
evaluator + target + category + event
```

This prevents duplicate ratings for the same category.

---

# 6. Memory

```text
Memory
------
id
event_id
author_id
target_id
text
status
created_at
updated_at
```

Status:

```text
VISIBLE
REPORTED
HIDDEN
```

---

# 7. Report

```text
Report
------
id
event_id
reporter_id
memory_id
reason
status
created_at
resolved_at
```

Status:

```text
OPEN
RESOLVED
DISMISSED
```

---

# 8. Optional Comment

If comments are separated from memories:

```text
Comment
-------
id
event_id
author_id
target_id
text
status
created_at
updated_at
```

For MVP, Memory can contain both story and comment content unless the UX needs separate fields.

---

# 9. Indexes

Create appropriate indexes for:

- event_id
- evaluator_id
- target_id
- category_id
- target_id + category_id
- memory target_id
- report status

---

# 10. Deletion Policy

Prefer soft deletion/deactivation for participants.

Do not casually hard-delete ratings because this can corrupt aggregate statistics.

If an event must be permanently deleted, implement an explicit administrative data deletion workflow.