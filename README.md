# AppSec Zero → Hero

A self-paced course that takes you from "what is HTTP?" to operating as a **senior application security engineer**: someone who finds and exploits bugs, fixes them at the root, threat-models whole systems, builds security into the SDLC, and runs an AppSec program.

> **Ethics first.** Every offensive technique here is for systems you own or are explicitly authorized to test (your own labs, CTFs, bug bounty programs within scope, pentest engagements with written authorization). Testing anything else is illegal in most jurisdictions and ends careers.

---

## How to use this course

1. **Go in order.** Each phase assumes the previous one.
2. **Do the labs.** Reading about SQL injection teaches you ~10%. Exploiting it, then fixing it, then writing a test that proves the fix, teaches you the rest.
3. **Answer the checkpoint questions out loud or in writing** before moving on. If you can't explain it simply, you don't know it yet.
4. **Keep a learning journal** (a private repo works well): notes, payloads that worked, write-ups of each lab. By Phase 4 this becomes your portfolio.
5. **Time-box.** Suggested pace is 8–12 hours/week. Total: roughly 9–14 months to the end of Phase 4; senior-level judgment then comes from applying it at work for a few years.

## Roadmap

| Phase | Level | Modules | Est. time |
|---|---|---|---|
| **0 — Foundations** | Absolute beginner | [01 How the Web Works](course/01-how-the-web-works.md) · [02 Linux, Programming & Tooling](course/02-linux-programming-tooling.md) · [03 Security Fundamentals](course/03-security-fundamentals.md) | 6–8 weeks |
| **1 — Breaking Web Apps** | Junior | [04 Injection](course/04-injection.md) · [05 XSS & Client-Side](course/05-xss-and-client-side.md) · [06 AuthN, Sessions & Access Control](course/06-authn-sessions-access-control.md) · [07 Server-Side Attacks](course/07-server-side-attacks.md) | 10–12 weeks |
| **2 — Building Secure Software** | Mid-level | [08 Secure Coding & Code Review](course/08-secure-coding-and-code-review.md) · [09 Applied Cryptography](course/09-applied-cryptography.md) · [10 API & Modern Architecture Security](course/10-api-security.md) | 8–10 weeks |
| **3 — Security at Scale** | Senior | [11 Threat Modeling](course/11-threat-modeling.md) · [12 DevSecOps & Supply Chain](course/12-devsecops-and-supply-chain.md) · [13 Cloud & Container Security](course/13-cloud-and-container-security.md) | 8–10 weeks |
| **4 — Expert** | Senior / Staff | [14 Advanced Exploitation & Research](course/14-advanced-exploitation.md) · [15 Building an AppSec Program](course/15-appsec-program.md) · [16 Senior Mindset, Leadership & Career](course/16-senior-mindset-and-career.md) | 8–10 weeks |
| **Capstone** | Proof | [Capstone Project](course/capstone.md) | 4–6 weeks |

Supporting material:
- [Lab Setup](course/lab-setup.md) — build your safe practice environment (do this first)
- [Resources & Reading List](course/resources.md)
- [Glossary](course/glossary.md)

## What "senior" means (your target)

| Skill | Junior | Mid | Senior |
|---|---|---|---|
| Finding bugs | Runs scanners, finds OWASP Top 10 with guidance | Finds bugs manually, chains two issues | Finds logic & design flaws, novel bug classes, chains across systems |
| Fixing bugs | Patches the reported line | Fixes the bug class in that service | Eliminates the class org-wide (secure defaults, frameworks, guardrails) |
| Code review | Checks a list | Reviews PRs in 1–2 languages confidently | Reviews any language; knows where to look first |
| Design | — | Comments on designs | Leads threat models, sets architecture patterns |
| Risk | "Everything is critical" | Uses CVSS | Speaks in business impact, prioritizes ruthlessly, accepts risk explicitly |
| Influence | Files tickets | Works with one team | Changes how the whole engineering org builds software; mentors |

## Progress tracker

Copy this into your journal and tick as you go.

```
[ ] Lab setup complete
[ ] 01  [ ] 02  [ ] 03            Phase 0
[ ] 04  [ ] 05  [ ] 06  [ ] 07    Phase 1
[ ] 08  [ ] 09  [ ] 10            Phase 2
[ ] 11  [ ] 12  [ ] 13            Phase 3
[ ] 14  [ ] 15  [ ] 16            Phase 4
[ ] Capstone
```
