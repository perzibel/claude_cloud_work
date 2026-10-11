# AppSec Zero → Hero: Learning Trail & Labs

A self-study guide for going from beginner to senior application security engineer, built on **real, public, high-quality resources** plus **hands-on labs you build yourself**.

| File | What's in it |
|---|---|
| [**LEARNING-TRAIL.md**](LEARNING-TRAIL.md) | An ordered trail of websites, free courses, standards, tools and books, with what you learn from each and when you're done with it. Five stages: Foundations → Web Vulnerabilities → Building Secure Software → Security at Scale → Expert & Senior. |
| [**labs/LOCAL-LAB.md**](labs/LOCAL-LAB.md) | Your local practice environment: tools, Burp setup, a Docker "practice range" of deliberately vulnerable apps, API/Kubernetes targets, then **building your own app securely** (with security tests and custom Semgrep rules) and a **CI/CD security pipeline**. |
| [**labs/AWS-LAB.md**](labs/AWS-LAB.md) | A safe AWS environment: account lockdown, guardrails, logging and detection, deploying your app with Terraform and no inbound exposure, Prowler scanning, flAWS/CloudGoat practice, and finding your own activity in the logs. |

## How the pieces fit together

| Trail stage | Read / practice | Build |
|---|---|---|
| 0 — Foundations | MDN, Linux Journey, Bandit, TryHackMe, OWASP Top 10 | Local Lab §1–2 |
| 1 — Web vulnerabilities | PortSwigger Web Security Academy, Juice Shop, WebGoat, WSTG | Local Lab §2–3 |
| 2 — Secure software | OWASP Cheat Sheets, ASVS, Semgrep, API Top 10, Cryptopals | Local Lab §4 |
| 3 — Security at scale | Threat modeling, DevSecOps, SLSA, AWS Security Pillar, flAWS | Local Lab §5 + AWS Lab |
| 4 — Expert & senior | Expert labs, research, SAMM, BSIMM, LLM security | Extend everything; mentor others |

## Ground rules

- Only test what you own, your own labs, or targets that explicitly invite testing (CTFs, practice platforms, bug bounty programs within scope).
- Keep a learning journal. For every lab write the **root cause**, the **right fix**, and **how you'd catch it earlier**. That habit is what turns hacking practice into AppSec skill.
- Pace: about 8–12 hours a week. Stages 0–3 take roughly 8–11 months; senior judgment then grows by applying it on real systems.
