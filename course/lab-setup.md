# Lab Setup — Your Safe Practice Environment

Set this up before Module 01. Everything runs locally; you never need to touch a system you don't own.

## 1. Base machine

- A computer with ≥16 GB RAM is comfortable (8 GB works with fewer containers running at once).
- **Docker** (Docker Desktop on macOS/Windows, Docker Engine on Linux).
- Optional: a Linux VM (Ubuntu or Kali) via VirtualBox/UTM if you're on Windows and want a native Linux shell. WSL2 is also fine.

## 2. Core tools

| Tool | Why | Install |
|---|---|---|
| **Burp Suite Community** | Intercepting proxy — the #1 web testing tool | portswigger.net/burp |
| **OWASP ZAP** | Free alternative proxy + scanner | zaproxy.org |
| **Firefox** + FoxyProxy | Dedicated testing browser routed through Burp | addons.mozilla.org |
| **curl**, **jq** | Raw HTTP and JSON from the terminal | package manager |
| **Python 3** + `requests` | Writing exploits and automation | python.org |
| **VS Code** | Code review & editing | code.visualstudio.com |
| **Semgrep** | Static analysis (Module 08/12) | `pip install semgrep` |
| **git** | Everything | package manager |

## 3. Vulnerable practice targets (all intentionally insecure — run locally only)

```bash
# OWASP Juice Shop — modern Node/Angular app, 100+ challenges
docker run -d --name juice -p 3000:3000 bkimminich/juice-shop

# DVWA — classic PHP vulns with difficulty levels
docker run -d --name dvwa -p 8081:80 vulnerables/web-dvwa

# crAPI — OWASP's deliberately vulnerable API platform (Module 10)
# https://github.com/OWASP/crAPI  (docker compose)

# WebGoat — Java lessons with explanations
docker run -d --name webgoat -p 8080:8080 -p 9090:9090 webgoat/webgoat
```

Bind to localhost only if you're on a shared network: `-p 127.0.0.1:3000:3000`.

## 4. Online labs (free tiers are enough to start)

- **PortSwigger Web Security Academy** — the single best free web security curriculum. Each module here maps to its labs.
- **OWASP Juice Shop** (above) — track your progress on its scoreboard.
- **HackTheBox / TryHackMe** — broader skills; TryHackMe is gentler for Phase 0.
- **flAWS / flAWS2** (flaws.cloud) — AWS misconfiguration (Module 13).
- **Kubernetes Goat** — container/K8s (Module 13).

## 5. Configure Burp + browser (do it once, properly)

1. Start Burp → Proxy → listener on `127.0.0.1:8080`.
2. In Firefox, FoxyProxy → add proxy `127.0.0.1:8080`, enable it.
3. Browse to `http://burp`, download the CA cert, import into Firefox (Settings → Certificates → Authorities, trust for websites).
4. Visit `http://localhost:3000` (Juice Shop). You should see requests in Burp's **HTTP history**.
5. Try: send a request to **Repeater** (Ctrl+R), modify a parameter, resend. This loop — *intercept, modify, observe* — is 80% of web testing.

## 6. Journal template

```markdown
# Lab: <name>   Date: <date>   Module: <nn>
## Goal
## What I tried (including what failed)
## Working payload / request
## Root cause (the line of code or design decision)
## Fix
## How I'd detect this in code review / with tooling
## What I learned
```
