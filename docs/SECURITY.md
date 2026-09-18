# Security Requirements

## Authentication

Use Django's secure password hashing.

Never:

- store plaintext passwords
- log passwords
- return passwords
- expose password hashes through APIs

---

# Authorization

Every protected resource must verify:

1. authenticated user
2. active user
3. active participant
4. correct event
5. appropriate permission

---

# IDOR

Test all endpoints for IDOR.

For example:

A participant must not be able to change:

```text
/api/ratings/another-user/
```

by simply replacing an ID.

---

# Anonymous Feedback Protection

Never return evaluator identity through:

- REST responses
- nested serializers
- query parameters
- error messages
- debug endpoints
- frontend state
- React Query cache
- browser-visible network payloads

---

# Rate Limiting

Implement rate limiting for:

- login
- rating submission
- memory submission
- reporting

---

# Input Validation

Validate:

- score range
- text length
- participant ID
- category ID
- event status

---

# Text Content

User-generated memories must be safely rendered.

Never render arbitrary HTML.

Prevent XSS.

---

# Production

Disable:

```text
DEBUG=True
```

Use environment variables for:

- SECRET_KEY
- DATABASE_URL
- JWT settings
- allowed hosts
- CORS configuration

Never commit secrets.

---

# Security Checklist

Before production:

- [ ] DEBUG disabled
- [ ] HTTPS
- [ ] secure cookies where applicable
- [ ] secure JWT handling
- [ ] password hashing
- [ ] rate limiting
- [ ] authorization tests
- [ ] IDOR tests
- [ ] XSS tests
- [ ] SQL injection protection
- [ ] privacy audit
- [ ] error disclosure audit
- [ ] secret scanning