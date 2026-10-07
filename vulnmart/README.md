# VulnMart

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.x-black.svg)
![Status](https://img.shields.io/badge/status-lab%20only%2C%20not%20for%20production-red.svg)

An intentionally vulnerable e-commerce web app, built as a training lab for
the Final Assignment (Custom Vulnerable Lab option).

**Warning:** this application contains deliberate security vulnerabilities.
Run it locally only. Never deploy it to a public server, and never use real
personal or payment data with it.

## Vulnerabilities included

1. **SQL Injection** (login form). Raw string concatenated query, bypass
   with username `admin' --` and any password.
2. **Stored XSS** (product reviews). Review comments are rendered with the
   Jinja2 `|safe` filter, so any HTML or JavaScript submitted executes for
   every visitor.
3. **IDOR** (order details). `/order/<id>` never checks that the order
   belongs to the logged in user. Any authenticated user can view any order
   by changing the number in the URL.
4. **Weak authentication.** Passwords are stored in plain text, there's no
   rate limiting on `/login`, and the seeded accounts use predictable,
   personal data based passwords.

## Setup

```
pip install flask
python3 app.py
```

Visit `http://localhost:5055`. The database is created automatically on
first run (`vulnmart.db`), seeded with three demo users:

| Username | Password      |
|----------|---------------|
| admin    | password123   |
| sarah    | sarah1995     |
| devraj   | devraj_2001   |

## Files

- `app.py`, the Flask application. All four vulnerabilities live here, each
  clearly commented.
- `templates/`, the Jinja2 templates.
- `capture_demo.py`, a Playwright script that automatically demonstrates
  and screenshots each vulnerability. This is what generated the report's
  evidence, and it asserts each exploit actually worked rather than just
  taking a screenshot on faith.

## Fixing the vulnerabilities, for reference

- SQLi: use parameterized queries
  (`db.execute("... WHERE username = ?", (username,))`) instead of string
  formatting.
- XSS: drop the `|safe` filter and let Jinja2's default autoescaping do its
  job, or sanitize explicitly with something like `bleach`.
- IDOR: add `AND user_id = ?` to the order query, scoped to the session's
  logged in user.
- Weak auth: hash passwords with `werkzeug.security.generate_password_hash`,
  add rate limiting (Flask-Limiter works well), and enforce a minimum
  password policy.

## See also

- [SECURITY.md](SECURITY.md) for what counts as an intentional vulnerability versus an actual bug worth reporting.
- [LICENSE](LICENSE) for usage terms (MIT).
