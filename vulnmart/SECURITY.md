# Security Policy

## This app is vulnerable on purpose

VulnMart is a training lab, not production software. It contains four
deliberate vulnerabilities, documented in `README.md` and in the project
report:

1. SQL injection in the login form
2. Stored XSS in product reviews
3. IDOR on the order details page
4. Weak authentication (plaintext passwords, no rate limiting)

If you find one of these, that's expected, it's the point of the project.
Please don't open an issue for any of the four flaws listed above.

## Scope

- Run this only on `127.0.0.1`. Do not deploy it to a public server, a
  shared network, or any environment with real user data.
- Do not point any of these vulnerabilities at a system you don't own or
  don't have explicit permission to test.
