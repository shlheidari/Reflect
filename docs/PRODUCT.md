# Product Specification

## 1. Product Concept

A private graduation-event platform where participants anonymously rate each other and share memories.

The purpose is entertainment, nostalgia, and collecting anonymous impressions of classmates/colleagues.

The application is not intended to be a public social network.

---

# 2. Main User Journey

## Step 1 — Login

Participant receives:

```text
Username
Password
```

from the event administrator.

They log in.

---

## Step 2 — Home

After login, the participant sees:

- welcome message
- event name
- progress toward rating others
- number of people rated
- number of people remaining
- shortcut to "People"
- shortcut to "What people think about me"

---

# 3. People Page

Display all eligible participants except the current user.

Each card contains:

```text
[Avatar]

Name

18 ratings received

[Rate]
```

If the current participant already rated that person:

```text
✓ Rated
[View / Edit]
```

depending on event settings.

---

# 4. Rating Page

The participant sees the person's:

- name
- avatar
- optional short introduction

Then all rating categories.

Each category contains:

```text
Left characteristic

0 ───── 5 ───── 10

Right characteristic
```

The participant selects a score from 0 to 10.

All categories do not necessarily need to be answered if the event allows optional categories.

At the bottom:

```text
Memory / Story
[large text area]

Additional comment
[large text area]

[Submit]
```

---

# 5. Rating Submission

When submitted:

- validate authentication
- validate target participant
- prevent self-rating
- validate category IDs
- validate scores
- create/update rating
- create optional memory
- create optional comment
- return success

The evaluator identity is stored internally but is never returned to the target participant.

---

# 6. My Results

Participants can open:

```text
What do people think about me?
```

Display each category:

```text
خوش‌کشیک        7.8 / 10
████████░░

خوش‌فاز         8.2 / 10
████████░░

مسئولیت‌پذیر    7.1 / 10
███████░░░

...
```

Also display:

```text
Based on 18 anonymous ratings
```

Do not show individual votes.

---

# 7. Memories

Display anonymous memories in cards.

Example:

```text
"هیچ‌وقت اون کشیک شب عید رو یادم نمیره 😂"

Anonymous
```

The word "Anonymous" is optional in the UI; the important requirement is that no identifying information is exposed.

A participant may see many memories about themselves.

---

# 8. Rating Count

The People page displays how many ratings each participant has received.

Purpose:

- encourage participants to rate people who have fewer ratings
- reduce the chance that someone receives no feedback
- make participation more balanced

The count is not intended as a popularity score.

Do not sort people primarily by rating count in a way that creates a public ranking.

A neutral or randomized ordering is preferred.

---

# 9. Admin

Admin dashboard includes:

### Participants

- create
- edit
- disable
- reset password
- view participation status

### Event

- event name
- event status
- start/end time
- whether editing ratings is allowed
- whether memories are enabled
- minimum ratings required for displaying aggregates

### Categories

- create
- edit
- disable
- reorder

### Moderation

- reported memories
- reported comments
- hide content
- restore content

### Statistics

Show aggregate system-level statistics such as:

- total participants
- active participants
- total ratings
- average ratings per participant
- participation percentage
- memories submitted

Do not unnecessarily expose evaluator identities.

---

# 10. Event Lifecycle

An event has a status:

```text
DRAFT
OPEN
CLOSED
```

### DRAFT

Only admins can access event configuration.

### OPEN

Participants can rate and submit memories.

### CLOSED

Participants can view results if enabled, but cannot submit new ratings.

---

# 11. Empty States

Examples:

No ratings yet:

```text
هنوز نظری ثبت نشده.
اولین نفر باش که درباره بقیه نظر می‌دهی!
```

No memories:

```text
هنوز خاطره‌ای درباره شما ثبت نشده.
```

No people remaining:

```text
همه را ارزیابی کردی 🎉
```

---

# 12. Future Features

Potential future features:

- graduation countdown
- anonymous "superlatives"
- downloadable personal result card
- event QR code
- invite links
- avatar customization
- Persian/English/Arabic
- PWA installation
- real-time participation counter
- optional AI summarization of memories, only if privacy implications are carefully addressed