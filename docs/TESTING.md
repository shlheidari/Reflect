# Testing Strategy

## Backend

Use Django/DRF testing tools.

Test:

### Authentication

- valid login
- invalid login
- disabled user
- expired token

### Participants

- participant list
- self exclusion
- inactive participant exclusion

### Ratings

- valid rating
- score 0
- score 10
- score below 0
- score above 10
- duplicate rating
- self-rating
- rating closed event
- unauthorized rating modification

### Aggregates

- correct average
- correct count
- minimum sample threshold
- no evaluator identity leakage

### Memories

- valid memory
- empty memory
- maximum length
- anonymous retrieval
- reporting
- hidden memory

---

# Privacy Tests

These are critical.

Test:

```text
Participant A creates rating for Participant B.
Participant B requests results.
```

Verify that response contains:

```text
average
count
category
```

but NOT:

```text
Participant A
A's ID
A's username
A's timestamp
```

---

# Frontend

Test:

- login
- protected routes
- participant list
- rating slider
- submission
- results
- memories
- reporting
- logout

---

# End-to-End

Create an E2E scenario:

```text
Admin creates event
↓
Admin creates participants
↓
Participant A logs in
↓
Participant A rates Participant B
↓
Participant B logs in
↓
Participant B sees aggregate result
↓
Participant B cannot discover Participant A
```

---

# Regression

Every bug fix should include a regression test when practical.