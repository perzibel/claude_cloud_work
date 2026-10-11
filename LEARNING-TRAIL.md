# The AppSec Learning Trail

A curated, ordered path through real online resources, from your first HTTP request to working as a senior application security engineer. Each stop says **where to go**, **what you'll learn there**, and **when you're done with it**.

Do the stops roughly in order. Run the labs from [`labs/`](labs/) alongside them; each stage says which lab work fits it.

> Only test systems you own, your own lab environment, or targets that explicitly invite testing (CTFs, practice platforms, bug bounty programs within their published scope).

---

## Stage 0 — Foundations (≈ 6–8 weeks)

Goal: understand how the web, Linux, and code actually work. Security is built on these.

| # | Resource | URL | What you learn | Done when… |
|---|---|---|---|---|
| 0.1 | **MDN — An overview of HTTP** | https://developer.mozilla.org/en-US/docs/Web/HTTP | Requests/responses, methods, status codes, headers, cookies, caching, CORS. The authoritative reference you'll keep returning to. | You can write a raw HTTP request by hand and explain every header in it. |
| 0.2 | **MDN — Web security** | https://developer.mozilla.org/en-US/docs/Web/Security | Same-origin policy, HTTPS, cookies security attributes, CSP, the browser's security model. | You can explain what an "origin" is and why it matters. |
| 0.3 | **Linux Journey** | https://linuxjourney.com | Command line, filesystem, permissions, processes, networking basics. Gentle and well-structured. | You're comfortable in a terminal without a GUI. |
| 0.4 | **OverTheWire: Bandit** | https://overthewire.org/wargames/bandit/ | Practical Linux through a game: ssh, file searching, permissions, pipes, basic scripting. | You've finished level 20+. |
| 0.5 | **Python docs tutorial** (or any language course) | https://docs.python.org/3/tutorial/ | Enough programming to read code and write small scripts. AppSec engineers read far more code than they write. | You can write a script that sends HTTP requests with `requests` and parses JSON. |
| 0.6 | **TryHackMe — Pre Security & Web Fundamentals paths** | https://tryhackme.com | Guided, browser-based intro to networking, web basics, and security vocabulary. Very beginner friendly. | Both paths complete. |
| 0.7 | **Hacksplaining** | https://www.hacksplaining.com | Short, animated explanations of the most common web vulnerabilities. A good first map of the field before going deep. | You can name the major vulnerability classes and give one sentence on each. |
| 0.8 | **OWASP Top 10 (current edition)** | https://owasp.org/www-project-top-ten/ | The industry's shared list of the most important web app risk categories. Read each category page, including "How to prevent". | You know all 10 categories and one example of each. |

**Lab work for this stage:** [Local Lab §1–2](labs/LOCAL-LAB.md): install the tools, set up Burp with your browser, run your first practice apps.

---

## Stage 1 — Web Vulnerabilities, Hands-On (≈ 10–14 weeks)

Goal: find and understand vulnerabilities yourself. This stage is the core of the junior skill set.

| # | Resource | URL | What you learn | Done when… |
|---|---|---|---|---|
| 1.1 | **PortSwigger Web Security Academy** ⭐ | https://portswigger.net/web-security | The best free web security curriculum that exists. Every topic has written material plus interactive labs: SQL injection, XSS, CSRF, authentication, access control, SSRF, XXE, file upload, path traversal, OS command injection, business logic, deserialization, JWTs, OAuth, CORS, clickjacking, request smuggling, cache poisoning, and more. | All **Apprentice** labs, and most **Practitioner** labs, are solved. |
| 1.2 | **Web Security Academy — Learning paths** | https://portswigger.net/web-security/learning-paths | A suggested order through the Academy if the topic list feels overwhelming. | Use as your sequencing guide for 1.1. |
| 1.3 | **OWASP Juice Shop** + its free companion book | https://owasp.org/www-project-juice-shop/ · https://pwning.owasp-juice.shop/ | A realistic modern app (Node/Angular/REST) with 100+ challenges and a built-in scoreboard. Teaches you to find bugs in an app that looks real, not in an isolated exercise. | 3★ challenges done; work into 4★–5★ over time. |
| 1.4 | **OWASP WebGoat** | https://owasp.org/www-project-webgoat/ | Lesson-based, with explanations in the app. Java backend, useful for seeing how bugs look in Java code. | Main lesson categories finished. |
| 1.5 | **OWASP Web Security Testing Guide (WSTG)** | https://owasp.org/www-project-web-security-testing-guide/ | The methodology professionals use: a structured checklist of what to test, test-case by test-case. Turns "poking around" into a systematic process. | You've used it as a checklist against Juice Shop. |
| 1.6 | **Hacker101** (HackerOne) | https://www.hacker101.com | Free video lessons plus CTF levels, aimed at aspiring bug hunters. Good second explanation of the same topics. | Watched the core videos; solved several CTF flags. |
| 1.7 | **HackerOne Hacktivity** | https://hackerone.com/hacktivity | Publicly disclosed real-world bug reports. Shows how real bugs look, how they're reported, and how companies respond. | You read 2–3 disclosed reports per week as a habit. |
| 1.8 | **PortSwigger Research** | https://portswigger.net/research | Original research on new attack classes. Too advanced right now; skim titles and come back in Stage 4. | Bookmark it. |

**Lab work for this stage:** [Local Lab §2–3](labs/LOCAL-LAB.md). Run Juice Shop, WebGoat and DVWA locally. For every bug you find, write a journal entry: root cause, fix, how you'd catch it in code review.

---

## Stage 2 — Building Secure Software (≈ 8–10 weeks)

Goal: shift from finding bugs to preventing them. This is what separates AppSec engineers from pentesters.

| # | Resource | URL | What you learn | Done when… |
|---|---|---|---|---|
| 2.1 | **OWASP Cheat Sheet Series** ⭐ | https://cheatsheetseries.owasp.org | Concise, practical "how to do X securely" guides: authentication, session management, password storage, input validation, output encoding, query parameterization, file upload, logging, secrets, Docker, Node.js, and dozens more. This is your daily defensive reference. | You've read the ~15 core cheat sheets and applied them to your own app (Local Lab §4). |
| 2.2 | **OWASP ASVS** (Application Security Verification Standard) | https://owasp.org/www-project-application-security-verification-standard/ | A detailed list of security requirements at three levels. Used to define "what secure looks like" for an app and to structure reviews. | You've assessed your own app against ASVS Level 1. |
| 2.3 | **CWE Top 25** | https://cwe.mitre.org/top25/ | MITRE's ranking of the most dangerous software weakness types. CWE IDs are the shared vocabulary used by scanners, CVEs and reports. | You can map a finding to its CWE ID. |
| 2.4 | **Semgrep — Learn & Docs** | https://semgrep.dev/learn · https://semgrep.dev/docs | Static analysis: how to run rules on a codebase and **write your own rules** to catch a bug pattern everywhere at once. | You've written a custom rule that catches an insecure pattern in your own app. |
| 2.5 | **CodeQL documentation** | https://codeql.github.com/docs/ | Semantic code analysis (data flow from sources to sinks), used heavily by GitHub. Steeper than Semgrep; very powerful. | You've run CodeQL on a repo and understood one data-flow result. |
| 2.6 | **OWASP API Security Top 10** | https://owasp.org/API-Security/ | API-specific risks: broken object-level authorization (BOLA), broken auth, mass assignment, rate limiting, inventory issues. APIs are where most modern bugs live. | You know all 10 and have practiced on crAPI (Local Lab §3). |
| 2.7 | **Crypto 101** (free book) | https://www.crypto101.io | Practical cryptography for developers: what primitives do, how they're misused. | You can explain hashing vs. encryption vs. MAC vs. signature. |
| 2.8 | **Cryptopals challenges** | https://cryptopals.com | Hands-on coding challenges that show *why* crypto misuse breaks things. Teaches respect for "don't roll your own crypto". | Sets 1–2 done (more is a bonus). |
| 2.9 | **Book: *Alice and Bob Learn Application Security*** (Tanya Janca) | publisher / bookstores | Readable overview of secure SDLC, secure design, testing, and building a program. Good bridge from junior to mid. | Read cover to cover. |

**Lab work for this stage:** [Local Lab §4](labs/LOCAL-LAB.md). Build your own small web app securely, then review your own code with Semgrep and the cheat sheets.

---

## Stage 3 — Security at Scale: Design, Pipelines, Cloud (≈ 8–10 weeks)

Goal: secure systems, not just code. This is the start of senior-level work.

### Threat modeling & design

| # | Resource | URL | What you learn |
|---|---|---|---|
| 3.1 | **Threat Modeling Manifesto** | https://www.threatmodelingmanifesto.org | The four key questions (What are we working on? What can go wrong? What are we going to do about it? Did we do a good job?) and the values behind good threat modeling. Short; read it first. |
| 3.2 | **OWASP Threat Modeling Cheat Sheet** | https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html | Practical how-to: data flow diagrams, trust boundaries, STRIDE. |
| 3.3 | **OWASP Threat Dragon** | https://owasp.org/www-project-threat-dragon/ | Free tool for drawing threat models. Use it on your own app. |
| 3.4 | **Book: *Threat Modeling: Designing for Security*** (Adam Shostack) | publisher / bookstores | The standard text on threat modeling. |
| 3.5 | **Google — *Building Secure and Reliable Systems*** (free online) | https://sre.google/books/ | How a large company designs for security: least privilege, defense in depth, design reviews, recovery. Senior-level thinking. |

### DevSecOps & software supply chain

| # | Resource | URL | What you learn |
|---|---|---|---|
| 3.6 | **OWASP DevSecOps Guideline** | https://owasp.org/www-project-devsecops-guideline/ | Where each security check fits in a CI/CD pipeline: secrets scanning, SAST, SCA, IaC scanning, DAST. |
| 3.7 | **SLSA** (Supply-chain Levels for Software Artifacts) | https://slsa.dev | Framework for build integrity: provenance, hardened builds, tamper resistance. |
| 3.8 | **NIST SSDF (SP 800-218)** | https://csrc.nist.gov/projects/ssdf | The US government's secure software development framework. Common in compliance-driven organizations. |
| 3.9 | **CISA Secure by Design** | https://www.cisa.gov/securebydesign | The "eliminate bug classes with secure defaults" philosophy. Shapes how senior engineers think about fixes. |
| 3.10 | **Tool docs: Gitleaks, Trivy, OWASP ZAP** | https://github.com/gitleaks/gitleaks · https://github.com/aquasecurity/trivy · https://www.zaproxy.org/docs/ | Secrets scanning, dependency/container/IaC scanning, and automated dynamic scanning. You'll wire these into CI in Local Lab §5. |

### Cloud & containers

| # | Resource | URL | What you learn |
|---|---|---|---|
| 3.11 | **AWS Well-Architected — Security Pillar** | https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html | AWS's own best practices: identity, detection, infrastructure protection, data protection, incident response. |
| 3.12 | **AWS Skill Builder** (free courses) | https://skillbuilder.aws | Official training, including security fundamentals. Free tier is enough. |
| 3.13 | **flAWS & flAWS2** | http://flaws.cloud · http://flaws2.cloud | Free, hosted challenges teaching common AWS mistakes (S3, IAM, metadata, keys). flAWS2 has both attacker and defender paths. No AWS account needed. |
| 3.14 | **CloudGoat** (Rhino Security Labs) | https://github.com/RhinoSecurityLabs/cloudgoat | Deploys vulnerable-by-design AWS scenarios into **your own** account. See [AWS Lab](labs/AWS-LAB.md). |
| 3.15 | **Prowler** | https://github.com/prowler-cloud/prowler | Open-source AWS security posture scanner. Learn what "misconfigured" looks like by scanning your own account. |
| 3.16 | **Kubernetes docs — Security** | https://kubernetes.io/docs/concepts/security/ | Pod security, RBAC, network policies, secrets. |
| 3.17 | **Kubernetes Goat** | https://github.com/madhuakula/kubernetes-goat | Vulnerable-by-design Kubernetes cluster for local practice. |
| 3.18 | **CIS Benchmarks** | https://www.cisecurity.org/cis-benchmarks | Hardening baselines for AWS, Docker, Kubernetes, OSes. Used by scanners and auditors. |

**Lab work for this stage:** [Local Lab §5](labs/LOCAL-LAB.md) (CI/CD pipeline) and the full [AWS Lab](labs/AWS-LAB.md).

---

## Stage 4 — Expert & Senior (ongoing)

Goal: depth, research, judgment, and influence across an organization.

### Deepening technical skill

| # | Resource | URL | What you learn |
|---|---|---|---|
| 4.1 | **Web Security Academy — Expert labs** | https://portswigger.net/web-security | The hardest labs: request smuggling, advanced cache poisoning, prototype pollution, race conditions. |
| 4.2 | **PortSwigger Research** (now, for real) | https://portswigger.net/research | How new vulnerability classes are discovered. Read the long-form papers. |
| 4.3 | **PentesterLab** (paid, excellent) | https://pentesterlab.com | Many short exercises, including code-review exercises and real CVE reproductions. Great for building code-review instinct. |
| 4.4 | **Book: *Real-World Bug Hunting*** (Peter Yaworski) | publisher / bookstores | Real disclosed bugs dissected, with an emphasis on how they were found. |
| 4.5 | **Book: *Serious Cryptography*** (Jean-Philippe Aumasson) | publisher / bookstores | Deeper crypto for engineers who review crypto designs. |
| 4.6 | **OWASP Top 10 for LLM Applications / GenAI Security Project** | https://genai.owasp.org | Prompt injection, insecure output handling, excessive agency, data leakage. An increasingly common part of senior AppSec work. |
| 4.7 | **MITRE ATT&CK** | https://attack.mitre.org | Attacker behaviors after initial access. Helps you connect app bugs to real-world impact and detection. |
| 4.8 | **CVSS v4.0 specification** | https://www.first.org/cvss/ | How severity is scored, and its limits. Seniors use it, then explain business impact beyond it. |

### Running an AppSec program

| # | Resource | URL | What you learn |
|---|---|---|---|
| 4.9 | **OWASP SAMM** | https://owasp.org/www-project-samm/ | A maturity model to assess and improve an organization's software security practices. The backbone of a program roadmap. |
| 4.10 | **BSIMM** | https://www.blackduck.com/services/security-program/bsimm-maturity-model.html (search "BSIMM report" if the URL has moved) | Data on what real software security programs actually do. Good for benchmarking and for making a case to leadership. |
| 4.11 | **OWASP Security Champions Guide** | https://owasp.org/www-project-security-champions-guidebook/ | How to scale security through embedded developer champions. |
| 4.12 | **Book: *Agile Application Security*** (Bell, Brunton-Spall, Smith, Bird) | publisher / bookstores | Fitting security into fast-moving engineering teams without being a blocker. |

### Staying current (weekly habits)

| Resource | URL | Why |
|---|---|---|
| **tl;dr sec newsletter** (Clint Gibler) | https://tldrsec.com | The best weekly digest of AppSec, cloud security and tooling news. |
| **Awesome AppSec list** | https://github.com/paragonie/awesome-appsec | Large curated index of further resources. |
| **OWASP Global AppSec conference talks** (YouTube) | https://www.youtube.com/@OWASPGLOBAL | Free recordings of talks from practitioners. |
| **NVD / CVE feeds** | https://nvd.nist.gov | Track vulnerabilities in the stacks you work with. |
| **HackerOne Hacktivity** | https://hackerone.com/hacktivity | Keep reading real reports. |

---

## Suggested weekly rhythm (8–12 h/week)

| Time | Activity |
|---|---|
| 40% | Hands-on labs (Academy, Juice Shop, your own app, AWS lab) |
| 25% | Reading the current stage's main resources |
| 20% | Writing: journal entries, write-ups, your own Semgrep rules / docs |
| 15% | Habits: newsletter, 2–3 disclosed reports, one conference talk |

## Milestones that show you've leveled up

- **Junior:** Most Web Security Academy Apprentice + Practitioner labs solved; Juice Shop 3★ complete; you can explain each OWASP Top 10 item with an example.
- **Mid:** Your own app passes ASVS L1; you've written custom Semgrep rules; you've reviewed real PRs (open-source or at work) and found real issues.
- **Senior:** You've threat-modeled a multi-service system; built a CI security pipeline; completed the AWS lab with detections; can make a prioritized, business-framed case for security work; you mentor others.
