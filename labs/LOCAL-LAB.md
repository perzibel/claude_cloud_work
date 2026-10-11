# Local Lab — Your Practice Environment and Your Own App

This lab runs entirely on your own computer and costs nothing. It has five parts, matched to the stages of the [Learning Trail](../LEARNING-TRAIL.md):

| Part | What you build | Trail stage |
|---|---|---|
| §1 | Your workstation: tools and a proxy-configured browser | Stage 0 |
| §2 | A "practice range": deliberately vulnerable apps in Docker | Stages 0–1 |
| §3 | API and Kubernetes practice targets | Stages 2–3 |
| §4 | **Your own web app, built securely** | Stage 2 |
| §5 | A CI/CD security pipeline for your app | Stage 3 |

---

## §1 — Workstation setup

### 1.1 Hardware and OS
- 16 GB RAM is comfortable. 8 GB works if you run one practice app at a time.
- macOS, Linux, or Windows with **WSL2** (Windows Subsystem for Linux). On Windows, do all terminal work inside WSL2 (Ubuntu). Most security tooling assumes a Linux shell.

### 1.2 Install the core tools

| Tool | What it's for | How to install |
|---|---|---|
| **Docker** | Runs every practice app in an isolated container, so nothing vulnerable is installed directly on your machine. | Docker Desktop (macOS/Windows) or `docker.io` + `docker-compose-plugin` packages (Linux). Check with `docker run hello-world`. |
| **Git** | Version control for your app and journal. | Package manager / git-scm.com |
| **Python 3.12+** | Scripting and the app you'll build in §4. | python.org or package manager. Check with `python3 --version`. |
| **VS Code** | Reading and writing code. | code.visualstudio.com |
| **Burp Suite Community Edition** | An *intercepting proxy*: sits between your browser and the app so you can see and modify every request. The central tool for web security work. | portswigger.net/burp/communitydownload |
| **Firefox** | A dedicated browser for testing, kept separate from your everyday browsing. | mozilla.org |
| **FoxyProxy** (Firefox add-on) | One-click switching of Firefox's traffic through Burp. | addons.mozilla.org |
| **curl** and **jq** | Send raw HTTP requests and read JSON in the terminal. | Package manager |

### 1.3 Connect Firefox to Burp (do this carefully once)

**Why:** HTTPS traffic is encrypted. For Burp to show it to you, your test browser must trust Burp's own certificate authority (CA). You install that trust *only* in the dedicated testing browser.

1. Start Burp → *Temporary project* → *Use Burp defaults*.
2. Go to **Proxy → Proxy settings** and confirm a listener on `127.0.0.1:8080`.
3. In Firefox, open FoxyProxy → *Options* → *Add*: type HTTP, host `127.0.0.1`, port `8080`, title "Burp". Select it.
4. Visit `http://burpsuite` in Firefox → click **CA Certificate** to download `cacert.der`.
5. Firefox → *Settings* → search "certificates" → *View Certificates* → *Authorities* → *Import* → choose the file → tick **"Trust this CA to identify websites"**.
6. Browse to any site. You should see the requests under **Proxy → HTTP history** in Burp.
7. In Burp, set **Proxy → Intercept** to *off* unless you want to pause requests one at a time. Leave it off most of the time and work from HTTP history.

**Habit to build now:** right-click any request → *Send to Repeater* → change something → *Send* → compare the responses. You'll use this loop constantly.

### 1.4 Start your journal
Create a private Git repository called `appsec-journal`. For every lab, add a Markdown file:

```markdown
# <Lab name> — <date>
## Goal
## What I did (including dead ends)
## What I found
## Root cause (which line of code / which design choice)
## The correct fix (and why that fix, not a different one)
## How I'd catch this earlier: code review? test? scanner rule?
## What I learned
```

The "root cause" and "how I'd catch this earlier" sections are what turn a lab into AppSec skill rather than CTF points.

---

## §2 — The practice range (deliberately vulnerable apps)

These apps are **intentionally insecure**. Rules:
- Bind them to `127.0.0.1` only, so nothing on your network can reach them.
- Never expose them to the internet or deploy them to the cloud outside of the controlled AWS lab.
- Stop them when you're not using them.

### 2.1 Create the range

```bash
mkdir -p ~/appsec-range && cd ~/appsec-range
```

Create `docker-compose.yml`:

```yaml
# Deliberately vulnerable training apps. Localhost only.
services:
  juice-shop:
    image: bkimminich/juice-shop:latest
    ports:
      - "127.0.0.1:3000:3000"
    restart: "no"

  webgoat:
    image: webgoat/webgoat:latest
    ports:
      - "127.0.0.1:8080:8080"   # WebGoat lessons at /WebGoat
      - "127.0.0.1:9090:9090"   # WebWolf helper at /WebWolf
    restart: "no"

  dvwa:
    image: vulnerables/web-dvwa:latest
    ports:
      - "127.0.0.1:8081:80"
    restart: "no"
```

> **Port clash:** Burp also listens on 8080. Either move Burp's listener to `127.0.0.1:8090` (and update FoxyProxy) or change WebGoat's host port to `127.0.0.1:8082:8080`.
>
> **Apple Silicon:** the DVWA image is built for x86. Add `platform: linux/amd64` under `dvwa:` if it fails to start.

### 2.2 Run it

```bash
docker compose up -d           # start everything in the background
docker compose ps              # check status
docker compose logs -f webgoat # watch one app's logs (Ctrl+C to exit)
docker compose down            # stop and remove everything
docker compose up -d juice-shop  # or start just one
```

### 2.3 What each app teaches and how to use it

| App | URL | What it is | How to use it well |
|---|---|---|---|
| **OWASP Juice Shop** | http://localhost:3000 | A realistic online shop (Node.js, Angular, REST API, SQLite) with 100+ hidden challenges ranked 1–6★. | Find the hidden **Score Board** first; that's the first challenge. Work through challenges by difficulty. Use the free companion book (https://pwning.owasp-juice.shop/) only after a real attempt. Because it's open source (https://github.com/juice-shop/juice-shop), you can **find the vulnerable source line** for each bug. Do that every time. |
| **OWASP WebGoat** | http://localhost:8080/WebGoat | A teaching app: each lesson explains a concept, then has you exercise it. Java/Spring backend. | Register a local user, then follow lessons in order. Read the explanations. Good for seeing how bugs look in Java. |
| **DVWA** | http://localhost:8081 | Classic PHP app with security levels *Low / Medium / High / Impossible*. | Log in with the default credentials shown in its README, click **Create / Reset Database**. The valuable part: each module has **View Source** for every level. Compare *Low* vs *Impossible* source to see exactly what the secure version does differently. |

### 2.4 Good practice routine
1. Read the matching Web Security Academy topic.
2. Solve its Academy labs.
3. Find the same class of bug in Juice Shop / DVWA.
4. Locate the vulnerable code in the app's source.
5. Write the fix in your journal and say *why* it's correct.

---

## §3 — API and Kubernetes practice targets

### 3.1 OWASP crAPI (Completely Ridiculous API)

**What it is:** a deliberately vulnerable microservices platform (a vehicle owner's app) built to teach the OWASP API Security Top 10. It's several services: identity, community, workshop, web front end, mail catcher, databases.

**Set it up:**
```bash
git clone https://github.com/OWASP/crAPI.git
cd crAPI
# Follow the current instructions in the repo's README / deploy/docker directory.
# They change between releases, so the README is the source of truth.
```
- It needs more RAM than the range above. Stop the §2 apps first (`docker compose down` in `~/appsec-range`).
- Make sure published ports are bound to `127.0.0.1` (edit the compose file's `ports:` if needed).
- crAPI includes a built-in mail catcher (MailHog). You'll need it to read sign-up and reset emails.

**How to use it:** proxy everything through Burp, map every API endpoint the front end calls, and study each one against the OWASP API Security Top 10 (https://owasp.org/API-Security/). Record in your journal which category each finding belongs to.

### 3.2 Kubernetes Goat (Stage 3)

**What it is:** a deliberately vulnerable Kubernetes cluster with guided scenarios on container and cluster security.

**Set it up:**
1. Install **kind** (Kubernetes in Docker; https://kind.sigs.k8s.io) and **kubectl** (https://kubernetes.io/docs/tasks/tools/).
2. Create a local cluster: `kind create cluster --name goat`.
3. Clone https://github.com/madhuakula/kubernetes-goat and follow its README to deploy into your *kind* cluster (never into a shared or work cluster).
4. Delete it when done: `kind delete cluster --name goat`.

**What you learn:** why RBAC, pod security settings, network policies, secrets handling and image hygiene matter, all of which you'll later check in real design reviews.

---

## §4 — Build your own app, securely ⭐

This is the most important part of the lab. Breaking apps teaches you what goes wrong; **building one securely teaches you what right looks like**, and that is the AppSec engineer's job.

You'll build **"SafeNotes"**: users register, log in, and create, edit, delete and view their own private notes.

Small, but it contains the core of almost every real app: authentication, sessions, authorization, a database, user input, and HTML output.

### 4.1 Stack and why

| Choice | Why |
|---|---|
| **Python + Flask** | Small and explicit. You see every security decision instead of a framework hiding it. |
| **SQLAlchemy** (ORM) | Builds parameterized queries for you. User input is never concatenated into SQL. |
| **Flask-WTF** | CSRF protection for every form. |
| **argon2-cffi** | Argon2id password hashing, the current recommendation in the OWASP Password Storage Cheat Sheet. |
| **Jinja2** templates | Auto-escapes output by default, so user content is rendered as text, not HTML. |
| **Gunicorn** in Docker | A production-style server, running as a non-root user. |

### 4.2 Security requirements (write these *before* coding)

Seniors define requirements first, then build to them. Take these from the OWASP Cheat Sheets and ASVS Level 1:

| # | Requirement | Source to read |
|---|---|---|
| R1 | Passwords hashed with Argon2id; minimum length 12; no maximum below 64 | Password Storage CS, Authentication CS |
| R2 | Login errors don't reveal whether the email exists | Authentication CS |
| R3 | Session cookie is `HttpOnly`, `Secure`, `SameSite=Lax`; session ID changes at login | Session Management CS |
| R4 | Every state-changing request is a POST protected by a CSRF token | CSRF Prevention CS |
| R5 | **Every note access checks that the note belongs to the logged-in user** | Authorization CS |
| R6 | All database access via the ORM / parameterized queries | Query Parameterization CS |
| R7 | All output auto-escaped; a strict Content-Security-Policy header | XSS Prevention CS, CSP CS |
| R8 | Login attempts rate-limited | Authentication CS |
| R9 | Secrets (like `SECRET_KEY`) come from environment variables, never from code | Secrets Management CS |
| R10 | Security events (login success and failure, logout) are logged, without passwords or tokens | Logging CS |

### 4.3 Project layout

```
safenotes/
├── app.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── notes.html
├── requirements.txt
├── Dockerfile
├── tests/
│   └── test_authz.py
└── .semgrep/
    └── rules.yml
```

### 4.4 `requirements.txt`

```
flask
flask-sqlalchemy
flask-wtf
flask-limiter
argon2-cffi
gunicorn
pytest
```

Once it works, pin exact versions (`pip freeze > requirements.txt`) so builds are reproducible and dependency scanners can check them.

### 4.5 `app.py`, annotated

```python
import functools
import logging
import os

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.update(
    # R9: secret from the environment. The app refuses to start without it.
    SECRET_KEY=os.environ["SECRET_KEY"],
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///safenotes.db"),
    # R3: cookie hardening. COOKIE_SECURE=0 only for local plain-HTTP development.
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "1") == "1",
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=64 * 1024,  # reject oversized request bodies
)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)  # R4: every POST form must carry a valid token
limiter = Limiter(get_remote_address, app=app)  # R8
ph = PasswordHasher()  # R1: Argon2id with library defaults
log = logging.getLogger("safenotes.security")
logging.basicConfig(level=logging.INFO)

# Used so login takes similar time whether or not the email exists (R2).
DUMMY_HASH = ph.hash("not-a-real-password-just-for-timing")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False, default="")


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "uid" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def get_owned_note(note_id: int) -> Note:
    """R5: the ONLY way to load a single note. The owner filter is part of the
    query itself, so a note belonging to someone else is simply "not found"."""
    note = db.session.execute(
        db.select(Note).filter_by(id=note_id, owner_id=session["uid"])
    ).scalar_one_or_none()
    if note is None:
        abort(404)  # 404 rather than 403: don't confirm the note exists
    return note


@app.after_request
def security_headers(resp):
    # R7: CSP allows only our own scripts/styles and blocks framing.
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10/hour", methods=["POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if "@" not in email or len(email) > 254 or not (12 <= len(password) <= 128):
            return render_template("register.html", error="Use a valid email and a 12–128 character password."), 400
        if db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none():
            # Real apps send a "you already have an account" email instead,
            # so the page itself doesn't reveal which emails are registered.
            return render_template("register.html", error="Could not register with those details."), 400
        db.session.add(User(email=email, password_hash=ph.hash(password)))
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5/minute", methods=["POST"])  # R8
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        try:
            ph.verify(user.password_hash if user else DUMMY_HASH, password)
            ok = user is not None
        except VerifyMismatchError:
            ok = False
        if not ok:
            log.info("login_failed ip=%s", request.remote_addr)  # R10: no password logged
            return render_template("login.html", error="Invalid email or password."), 401  # R2
        session.clear()  # R3: discard any pre-login session data
        session["uid"] = user.id
        log.info("login_success uid=%s ip=%s", user.id, request.remote_addr)
        return redirect(url_for("notes"))
    return render_template("login.html")


@app.post("/logout")
@login_required
def logout():
    log.info("logout uid=%s", session["uid"])
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@login_required
def notes():
    my_notes = db.session.execute(
        db.select(Note).filter_by(owner_id=session["uid"]).order_by(Note.id.desc())
    ).scalars().all()
    return render_template("notes.html", notes=my_notes)


@app.post("/notes")
@login_required
def create_note():
    title = request.form.get("title", "").strip()[:200]
    body = request.form.get("body", "")[:10_000]
    if not title:
        abort(400)
    # owner_id comes from the session, NEVER from the form.
    db.session.add(Note(owner_id=session["uid"], title=title, body=body))
    db.session.commit()
    return redirect(url_for("notes"))


@app.post("/notes/<int:note_id>/delete")
@login_required
def delete_note(note_id):
    db.session.delete(get_owned_note(note_id))
    db.session.commit()
    return redirect(url_for("notes"))


with app.app_context():
    db.create_all()
```

Add an edit route yourself, using `get_owned_note()` and the same validation as `create_note`.

**Why each design decision matters:**
- **`get_owned_note()` as the single access path.** Authorization bugs usually come from *one* route forgetting a check. Centralizing it, and enforcing that with a Semgrep rule (§4.9) and a test (§4.8), removes that whole class of mistake. This is "fix the class, not the instance", the senior way to fix things.
- **`owner_id` taken from the session**, never from the request, so a user can't create notes as someone else.
- **`session.clear()` at login** prevents session fixation.
- **`DUMMY_HASH`** keeps response time similar for existing and non-existing accounts.
- **404 instead of 403** for other people's notes avoids confirming that a note ID exists.

### 4.6 Templates

`templates/base.html`:
```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>SafeNotes</title></head>
<body>
  {% if session.uid %}
  <form method="post" action="{{ url_for('logout') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button>Log out</button>
  </form>
  {% endif %}
  {% block content %}{% endblock %}
</body>
</html>
```

`templates/notes.html`:
```html
{% extends "base.html" %}
{% block content %}
<h1>My notes</h1>
<form method="post" action="{{ url_for('create_note') }}">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <input name="title" maxlength="200" required>
  <textarea name="body"></textarea>
  <button>Save</button>
</form>
{% for n in notes %}
  <article>
    <h2>{{ n.title }}</h2>          {# auto-escaped: shown as text, never run as HTML #}
    <p>{{ n.body }}</p>
    <form method="post" action="{{ url_for('delete_note', note_id=n.id) }}">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <button>Delete</button>
    </form>
  </article>
{% endfor %}
{% endblock %}
```

Write `login.html` and `register.html` the same way: a POST form with the `csrf_token` hidden input, and `{{ error }}` displayed if set.

**Rules for templates:** never use the `|safe` filter or `Markup()` on user data, and keep JavaScript in separate `.js` files. Inline scripts are blocked by the CSP above, which is intentional.

### 4.7 Run it locally

```bash
cd safenotes
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
export COOKIE_SECURE=0          # local HTTP only; never in production
flask --app app run --debug     # debug mode: local development ONLY
```

Open http://localhost:5000/register, create two users (Alice and Bob) in two different browsers or private windows, and add notes as each.

Now **verify your own controls through Burp**: send the delete request to Repeater, swap in one of Bob's note IDs while logged in as Alice, and confirm you get a 404. Remove the CSRF token and confirm the request is rejected. Check the response headers for the CSP. You are confirming your requirements hold, which is exactly what a security reviewer does.

### 4.8 Write security regression tests

`tests/test_authz.py`:
```python
import os
os.environ.setdefault("SECRET_KEY", "test-only")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["COOKIE_SECURE"] = "0"

import pytest
from app import app, db, Note, User, ph


@pytest.fixture
def client():
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
    with app.app_context():
        db.drop_all(); db.create_all()
        alice = User(email="alice@example.com", password_hash=ph.hash("alice-password-123"))
        bob = User(email="bob@example.com", password_hash=ph.hash("bob-password-1234"))
        db.session.add_all([alice, bob]); db.session.commit()
        db.session.add(Note(owner_id=bob.id, title="bob's secret", body="x")); db.session.commit()
    return app.test_client()


def login(c, email, pw):
    return c.post("/login", data={"email": email, "password": pw})


def test_user_cannot_delete_another_users_note(client):
    login(client, "alice@example.com", "alice-password-123")
    with app.app_context():
        bobs_note = db.session.execute(db.select(Note)).scalar_one()
    assert client.post(f"/notes/{bobs_note.id}/delete").status_code == 404
    with app.app_context():
        assert db.session.get(Note, bobs_note.id) is not None  # still there


def test_notes_page_requires_login(client):
    assert client.get("/").status_code == 302


def test_security_headers_present(client):
    r = client.get("/login")
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
```

Run with `pytest -q`. **Security tests are what stop a fixed bug from coming back.** Write one for every requirement you can.

### 4.9 Write a custom Semgrep rule

`.semgrep/rules.yml`:
```yaml
rules:
  - id: safenotes-note-fetch-without-ownership
    languages: [python]
    severity: ERROR
    message: >-
      Load single notes via get_owned_note() so the ownership check (R5)
      is always applied.
    patterns:
      - pattern-either:
          - pattern: db.session.get(Note, ...)
          - pattern: Note.query.get(...)
          - pattern: db.select(Note).filter_by(id=...)
      - pattern-not-inside: |
          def get_owned_note(...):
              ...
```

```bash
pip install semgrep
semgrep scan --config .semgrep/rules.yml --config p/python --config p/flask .
```

**Test the rule:** on a throwaway branch, add a route that uses `db.session.get(Note, note_id)` directly. Semgrep should flag it, and your authz test should fail if you call that route as the wrong user. You now have *two* independent guardrails. This is how seniors make secure code the default.

### 4.10 Containerize it

`Dockerfile`:
```dockerfile
FROM python:3.12-slim

# Don't run as root inside the container.
RUN useradd --create-home --uid 10001 app
WORKDIR /home/app/safenotes

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .
USER app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
```

```bash
docker build -t safenotes .
docker run --rm -p 127.0.0.1:8000:8000 \
  -e SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -e COOKIE_SECURE=0 safenotes
```

Also add a `.dockerignore` containing `.venv`, `*.db`, `.git` and `__pycache__`, so local databases and history never end up in the image.

### 4.11 Assess your app like a reviewer
1. **ASVS Level 1:** go through the ASVS L1 requirements and mark each Pass / Fail / Not applicable. Fix what fails.
2. **Threat model:** draw SafeNotes in OWASP Threat Dragon (browser → app → database), mark the trust boundaries, and list STRIDE threats per element. Which requirements cover which threats? Anything uncovered?
3. **Extend it, with security reasoning:** add one feature at a time and write requirements for it first.
   - Password reset by email (token entropy, expiry, single use)
   - File attachments (type allow-list, size limits, storage outside the web root, random file names)
   - Sharing a note with another user (now authorization gets interesting)
   - A JSON API with token auth (see the OWASP API Security Top 10)

---

## §5 — CI/CD security pipeline

Push SafeNotes to a GitHub repository and add automated security checks that run on every push and pull request.

### 5.1 What each check does

| Check | Tool | Catches |
|---|---|---|
| Secrets scanning | **Gitleaks** | API keys, passwords or tokens committed to the repo |
| SAST (static analysis) | **Semgrep** (public rules + your custom rule) | Insecure code patterns before they run |
| SCA (dependency scanning) | **pip-audit** | Known-vulnerable versions of your dependencies |
| Container & config scanning | **Trivy** | Vulnerable OS packages in the image, Dockerfile misconfigurations |
| Unit / security tests | **pytest** | Regressions of your security requirements |
| DAST (dynamic scanning) | **OWASP ZAP baseline** | Missing headers, cookie flags and other runtime issues, by scanning the running app |

### 5.2 Workflow file

`.github/workflows/security.yml`:
```yaml
name: security

on:
  push:
  pull_request:

permissions:
  contents: read   # least privilege for the workflow token

jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # scan full history, not only the latest commit
      - name: Gitleaks
        run: |
          docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest \
            detect --source /repo --redact --exit-code 1

  sast-sca-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt semgrep pip-audit
      - name: Tests (including security tests)
        run: pytest -q
      - name: Semgrep
        run: semgrep scan --error --config .semgrep/rules.yml --config p/python --config p/flask .
      - name: Dependency audit
        run: pip-audit -r requirements.txt

  container-and-dast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t safenotes:ci .
      - name: Trivy image + config scan
        run: |
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
            image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed safenotes:ci
          docker run --rm -v "$PWD:/src" aquasec/trivy:latest \
            config --exit-code 1 --severity HIGH,CRITICAL /src
      - name: Start app
        run: |
          docker run -d --name app -p 8000:8000 \
            -e SECRET_KEY=ci-only-not-secret -e COOKIE_SECURE=0 safenotes:ci
          for i in $(seq 1 30); do curl -sf http://localhost:8000/login && break; sleep 1; done
      - name: ZAP baseline scan
        run: |
          mkdir -p zap && chmod 777 zap
          docker run --rm --network host -v "$PWD/zap:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
            zap-baseline.py -t http://localhost:8000/login -r zap-report.html
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: zap-report
          path: zap/zap-report.html
```

### 5.3 Make it real
- **Branch protection:** in the repository settings, require the `security` workflow to pass before merging to `main`.
- **Dependabot:** enable it in the repository's security settings so outdated dependencies get automatic pull requests.
- **Triage like a professional:** for every finding, decide *fix*, *accept the risk (with a written reason)*, or *false positive (suppress with a comment explaining why)*. Record those decisions in your journal. Senior AppSec work is mostly judgment about findings, not running tools.
- **Pin versions:** the `:latest` tags above keep the example simple. In a real pipeline, pin tool images and GitHub Actions to specific versions or commit SHAs so a compromised or changed upstream can't silently alter your build. That's a supply-chain control from Stage 3.
- **Tune ZAP:** generate a rules file (`zap-baseline.py ... -g zap.conf`), then mark known-acceptable alerts as `IGNORE` with a reason.

---

## Clean-up commands

```bash
cd ~/appsec-range && docker compose down       # stop the practice range
docker ps -a                                   # anything left running?
docker system prune                            # remove stopped containers and dangling images
kind delete cluster --name goat                # remove Kubernetes Goat cluster
```
