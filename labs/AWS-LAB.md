# AWS Lab — A Safe Cloud Security Environment

This lab teaches cloud security the way you'll meet it at work: you **set up an AWS account properly**, **deploy your own app securely**, **turn on detection**, **scan for misconfigurations**, and **practice on deliberately vulnerable scenarios**, all inside an account that holds nothing but lab resources.

It matches Stage 3 of the [Learning Trail](../LEARNING-TRAIL.md). Finish [Local Lab §4](LOCAL-LAB.md) first; you'll deploy SafeNotes here.

| Part | What you do | Why it matters |
|---|---|---|
| §0 | Understand cost and safety rules | Cloud labs can cost real money if left running |
| §1 | Create and lock down a dedicated lab account | Account setup is the foundation of all cloud security |
| §2 | Add guardrails (region limits, budgets) | Preventive controls, the senior way |
| §3 | Turn on logging and detection | You can't defend what you can't see |
| §4 | Deploy SafeNotes securely with Terraform | Secure-by-default infrastructure as code |
| §5 | Scan your account with Prowler | Learn what "misconfigured" looks like |
| §6 | Practice with flAWS and CloudGoat | Learn common AWS mistakes hands-on |
| §7 | Review your own activity in the logs | Connect attacker actions to detection |
| §8 | Tear down and verify cost | Professional hygiene |

---

## §0 — Cost and safety rules (read before you start)

1. **Use a dedicated AWS account for this lab.** Never use a work account, or any account with real data or real workloads.
2. **Set budget alerts first** (§1.4). They're the safety net if you forget something running.
3. **Destroy what you create when you finish a session.** Everything here is built with Terraform or CloudGoat, so it can be recreated in minutes.
4. **Some services cost money even when idle**: NAT gateways, load balancers, AWS Config rules, Security Hub checks, RDS databases, Elastic IPs not attached to a running instance. This lab avoids most of them; §3 says which ones to switch off afterwards.
5. **Check current pricing yourself.** AWS's free-tier model changes over time, so look at the pricing page for any service before you rely on it being free.
6. **Expected cost** if you follow the teardown steps: typically a few US dollars a month. Leaving things running is what makes it expensive.
7. **Vulnerable scenarios (CloudGoat) are deliberately insecure.** Only deploy them with the IP allow-list it sets up, and destroy them the same day.
8. **AWS's penetration-testing policy** allows testing your own resources for many services without pre-approval, but it lists prohibited activities (for example, denial-of-service testing). Read it once: search "AWS penetration testing policy".

---

## §1 — Create and lock down the lab account

### 1.1 Create the account

**Recommended setup (teaches multi-account practice):**
1. Create an AWS account. This becomes your **management account**: use it only for billing and organization settings.
2. In it, open **AWS Organizations** → *Create organization*.
3. *Add an AWS account* → *Create an AWS account* named `appsec-lab`, with a distinct email address (for example, a `+lab` alias if your provider supports it).
4. All lab work happens in `appsec-lab`.

**Why:** real companies separate workloads into accounts so a compromise of one doesn't reach the others, and so guardrails (§2) can apply to member accounts. The management account can't be restricted by those guardrails, which is exactly why you keep it empty.

**Simpler option:** a single standalone account works too. You'll just skip the Service Control Policy in §2.1.

### 1.2 Secure the root user (in every account you create)

The root user can do anything, including closing the account, and can't be restricted by IAM. Treat it like a fire extinguisher: locked away, used almost never.

1. Sign in as root → account menu → **Security credentials**.
2. **Assign MFA**: a hardware security key or passkey is best, an authenticator app is acceptable.
3. Make sure there are **no access keys** for root. Delete any that exist.
4. Use a long, unique password stored in a password manager.
5. Under **Account** settings, set alternate contacts (security, billing) to an address you read.

For member accounts created through Organizations, recent AWS features let the management account manage member-account root access centrally ("root access management" in IAM). If available, enable it so member accounts have no standing root credentials.

### 1.3 Create your everyday admin identity with IAM Identity Center

Don't use root or long-lived IAM user access keys for daily work. Use **IAM Identity Center** (formerly AWS SSO), which gives you short-lived credentials.

1. In the management account, open **IAM Identity Center** → *Enable*.
2. *Users* → *Add user* (yourself) → set up MFA when you first sign in.
3. *Permission sets* → *Create* → predefined **AdministratorAccess** (for this lab) and a second one with **ReadOnlyAccess**.
4. *AWS accounts* → select `appsec-lab` → *Assign users* → yourself → both permission sets.
5. Note the **AWS access portal URL** shown on the Identity Center dashboard.

Use **ReadOnly** for exploring and reviewing, and switch to Admin only when you need to change something. That habit of least privilege for yourself is worth building early.

### 1.4 Budget alerts (do this now, not later)

In the management account (or standalone account):
1. **Billing and Cost Management** → **Budgets** → *Create budget* → *Monthly cost budget*.
2. Amount: for example **$10**. Alerts at **50%, 80%, 100%** of actual spend, plus **100% forecasted**, emailed to you.
3. Create a second budget at **$25** as a "something is badly wrong" alarm.
4. **Cost Anomaly Detection** → create a monitor for AWS services with email alerts.

### 1.5 Command-line access with short-lived credentials

Install the **AWS CLI v2** (https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and **Terraform** (https://developer.hashicorp.com/terraform/install).

```bash
aws configure sso
#  SSO session name: lab
#  SSO start URL:    <your AWS access portal URL>
#  SSO region:       <region where you enabled Identity Center>
#  -> a browser opens; approve; pick the appsec-lab account and AdministratorAccess
#  Profile name:     lab

aws sso login --profile lab
export AWS_PROFILE=lab
aws sts get-caller-identity     # confirm: account = appsec-lab, role = AdministratorAccess
```

Credentials expire automatically after a few hours. Run `aws sso login` again when they do. **No access keys are stored on your disk**, which removes one of the most common real-world causes of cloud breaches: leaked keys.

---

## §2 — Guardrails (preventive controls)

### 2.1 Restrict the lab to one region (Organizations only)

**Why:** attackers who get credentials often launch resources in regions nobody watches. A Service Control Policy (SCP) blocks that outright, for every identity in the account, including admins.

In the management account: **Organizations** → *Policies* → *Service control policies* → *Enable* → *Create policy*:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyOutsideLabRegion",
      "Effect": "Deny",
      "NotAction": [
        "iam:*", "organizations:*", "sts:*", "sso:*", "account:*",
        "support:*", "budgets:*", "ce:*", "health:*", "trustedadvisor:*",
        "cloudfront:*", "route53:*", "waf:*", "globalaccelerator:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": { "aws:RequestedRegion": ["us-east-1"] }
      }
    }
  ]
}
```

- Replace `us-east-1` with your chosen lab region.
- The `NotAction` list exempts **global services**, which always operate through `us-east-1` or have no region, so they keep working.
- Attach the policy to the `appsec-lab` account (not to the root of the organization while you're learning).
- **Test it:** `aws ec2 describe-instances --region eu-west-1` should now return *AccessDenied* (explicit deny in a service control policy).

**Lesson:** SCPs set the maximum permissions an account can ever have. Even an `AdministratorAccess` identity can't exceed them. That is defense in depth at the organization level.

### 2.2 Account-level S3 Block Public Access

In `appsec-lab`: **S3** → *Block Public Access settings for this account* → turn **all four on**. Public S3 buckets are one of the most common cloud data leaks; this makes "public" impossible unless someone deliberately reverses an account-wide setting.

### 2.3 Default EBS encryption

**EC2** → *Settings* (under *EC2 Dashboard → Account attributes → Data protection and security*) → **EBS encryption** → *Always encrypt new EBS volumes* → enable, for your lab region.

---

## §3 — Logging and detection

| Service | What it does | Cost note |
|---|---|---|
| **CloudTrail** | Records every API call: who did what, when, from where. The basis of all AWS investigations. | Management events in one trail: free (you pay for S3 storage, which is tiny). |
| **GuardDuty** | Threat detection: unusual API calls, credential misuse, crypto-mining, known-bad IPs. | Free trial period, then usage-based. Disable after the lab if cost matters. |
| **IAM Access Analyzer** | Finds resources shared outside your account (buckets, roles, keys) and unused access. | External access analyzer: free. |
| **Security Hub** | Runs best-practice checks (e.g. *AWS Foundational Security Best Practices*, CIS) and collects findings. | Free trial period, then per check. Requires AWS Config. |
| **AWS Config** | Records resource configuration over time; Security Hub depends on it. | Charged per configuration item recorded. Disable after the lab. |

### 3.1 Enable them (in `appsec-lab`, lab region)

1. **CloudTrail** → *Create trail* → name `lab-trail` → new S3 bucket → enable **log file validation** → management events: Read and Write. *(Event history in the console shows 90 days of management events even without a trail, but a trail is what you'd have in production and lets you query logs with Athena.)*
2. **GuardDuty** → *Get started* → *Enable*.
3. **IAM** → **Access analyzer** → *Create analyzer* → zone of trust: current account.
4. **Security Hub** → *Go to Security Hub* → enable, with **AWS Foundational Security Best Practices** checked. Accept the prompt to enable AWS Config.

### 3.2 Explore before building anything
- Open **CloudTrail → Event history**. Find your own `ConsoleLogin` and the `CreateTrail` call. Note the fields: `userIdentity`, `sourceIPAddress`, `eventName`, `errorCode`.
- After a few hours, open **Security Hub → Controls** and read every failed control. For each one, write in your journal what it protects against and how you'd fix it.

---

## §4 — Deploy SafeNotes securely with Terraform

You'll deploy the app from [Local Lab §4](LOCAL-LAB.md) with **zero inbound internet exposure**: no SSH, no public ports. You reach it through an encrypted **SSM Session Manager port forward**. That is a real pattern for admin tools and internal services.

### 4.1 Architecture

```
Your laptop ──(aws ssm start-session, port forward)──► AWS Systems Manager
                                                          │
                                                          ▼
                     ┌──────────── EC2 instance (no inbound rules) ────────────┐
                     │  IMDSv2 required, encrypted disk, IAM role (least priv) │
                     │  docker run -p 127.0.0.1:8000:8000 safenotes            │
                     └───────────────┬────────────────────────┬────────────────┘
                                     │ pulls image            │ reads SECRET_KEY
                                     ▼                        ▼
                                  Amazon ECR       SSM Parameter Store (SecureString)
```

### 4.2 Security decisions and why

| Decision | Threat it addresses |
|---|---|
| Security group with **no inbound rules** | Nothing on the internet can connect at all. No SSH to brute-force, no exposed app. |
| **Session Manager** instead of SSH | No SSH keys to manage or leak; every session is authorized by IAM and logged in CloudTrail. |
| **IMDSv2 required**, hop limit 1 | Makes it much harder for an SSRF bug in the app to steal the instance's role credentials from the metadata service. The hop limit of 1 also stops the container itself from reaching the metadata service. |
| **Instance role with minimal permissions** | If the instance is compromised, the attacker gets only "pull this image, read this one parameter". |
| **Secret in Parameter Store (SecureString)**, read at boot | No secrets in code, AMIs, Terraform files or the image. |
| **Encrypted root volume** | Data at rest protection. |
| **Image from your private ECR repo with scan-on-push** | Known vulnerabilities in the image are flagged automatically. |
| **App bound to 127.0.0.1 on the host** | Even if a security group rule were added by mistake, the app isn't listening on the network interface. |

### 4.3 Build and push the image to ECR

```bash
export AWS_PROFILE=lab AWS_REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

aws ecr create-repository --repository-name safenotes \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability IMMUTABLE

aws ecr get-login-password | docker login --username AWS --password-stdin \
  "$ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com"

cd safenotes
docker build --platform linux/amd64 -t "$ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/safenotes:v1" .
docker push "$ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/safenotes:v1"
```

`IMMUTABLE` tags mean `v1` can never be silently replaced with different contents. Check **ECR → safenotes → Images → v1 → Vulnerabilities** for the scan results.

### 4.4 Store the secret

```bash
aws ssm put-parameter --name /safenotes/secret_key --type SecureString \
  --value "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

### 4.5 Terraform

Create `infra/main.tf`:

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.region
  default_tags { tags = { Project = "appsec-lab", Owner = "me" } }
}

variable "region"    { default = "us-east-1" }
variable "image_tag" { default = "v1" }

data "aws_caller_identity" "me" {}
data "aws_vpc" "default" { default = true }

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

locals {
  registry  = "${data.aws_caller_identity.me.account_id}.dkr.ecr.${var.region}.amazonaws.com"
  param_arn = "arn:aws:ssm:${var.region}:${data.aws_caller_identity.me.account_id}:parameter/safenotes/secret_key"
}

# --- Network: no inbound access at all; outbound HTTPS only (ECR, SSM, packages)
resource "aws_security_group" "app" {
  name        = "safenotes-no-inbound"
  description = "SafeNotes: no inbound, HTTPS egress only"
  vpc_id      = data.aws_vpc.default.id

  egress {
    description = "HTTPS to AWS APIs and package repos"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Identity: least-privilege instance role
data "aws_iam_policy_document" "assume_ec2" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app" {
  name               = "safenotes-instance"
  assume_role_policy = data.aws_iam_policy_document.assume_ec2.json
}

# Lets Session Manager manage the instance (replaces SSH)
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

data "aws_iam_policy_document" "app" {
  statement {
    sid       = "ReadOnlyThisSecret"
    actions   = ["ssm:GetParameter"]
    resources = [local.param_arn]
  }
  statement {
    sid       = "EcrAuth"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]  # this action does not support resource-level scoping
  }
  statement {
    sid       = "PullOnlyThisRepo"
    actions   = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
    resources = ["arn:aws:ecr:${var.region}:${data.aws_caller_identity.me.account_id}:repository/safenotes"]
  }
}

resource "aws_iam_role_policy" "app" {
  name   = "safenotes-minimal"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app.json
}

resource "aws_iam_instance_profile" "app" {
  name = "safenotes-instance"
  role = aws_iam_role.app.name
}

# --- Compute
resource "aws_instance" "app" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = "t3.micro"
  iam_instance_profile   = aws_iam_instance_profile.app.name
  vpc_security_group_ids = [aws_security_group.app.id]

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # IMDSv2 only
    http_put_response_hop_limit = 1           # containers can't reach IMDS
  }

  root_block_device {
    encrypted = true
  }

  user_data = <<-EOF
    #!/bin/bash
    set -euo pipefail
    dnf install -y docker
    systemctl enable --now docker
    aws ecr get-login-password --region ${var.region} \
      | docker login --username AWS --password-stdin ${local.registry}
    SECRET_KEY=$(aws ssm get-parameter --region ${var.region} \
      --name /safenotes/secret_key --with-decryption \
      --query Parameter.Value --output text)
    docker run -d --restart unless-stopped --name safenotes \
      -p 127.0.0.1:8000:8000 \
      -e SECRET_KEY="$SECRET_KEY" -e COOKIE_SECURE=0 \
      ${local.registry}/safenotes:${var.image_tag}
  EOF

  tags = { Name = "safenotes" }
}

output "instance_id" { value = aws_instance.app.id }
```

> **Why `COOKIE_SECURE=0` here?** You reach the app through an encrypted SSM tunnel on `http://localhost`, and browsers won't store `Secure` cookies over plain HTTP on that path. In a real public deployment you'd put HTTPS in front (for example an Application Load Balancer with an ACM certificate on your own domain) and keep `COOKIE_SECURE=1`. Write this trade-off in your journal; documenting accepted risk is a senior habit.
>
> The secret ends up as a container environment variable, which anyone with Docker access on the host can read. Note that as a known limitation, and as an extension, change the app to fetch the parameter itself at startup.

Deploy:
```bash
cd infra
terraform init
terraform plan      # READ the plan: every resource, every permission
terraform apply
```

### 4.6 Connect to the app

Install the **Session Manager plugin** for the AWS CLI (search "Install the Session Manager plugin for the AWS CLI"), wait 2–3 minutes for the instance to boot, then:

```bash
aws ssm start-session --target "$(terraform output -raw instance_id)" \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8000"],"localPortNumber":["8000"]}'
```

Open http://localhost:8000/register. Your app is running in AWS with no inbound internet exposure.

For a shell on the instance (troubleshooting): `aws ssm start-session --target <instance-id>`, then `sudo docker logs safenotes`.

### 4.7 Verify your controls like a reviewer
1. **EC2 → Instances → safenotes → Security**: confirm no inbound rules. Check the role.
2. **IAM → Roles → safenotes-instance**: open the policy, then use **IAM Policy Simulator** to confirm the role *cannot* do `s3:ListAllMyBuckets` or read other parameters.
3. **EC2 → Instance → Actions → Instance settings → Modify instance metadata options**: confirm IMDSv2 is *Required*.
4. **CloudTrail → Event history**: find the `StartSession` event for your port forward. Who, when, from which IP.
5. **Security Hub**: after a few hours, check which controls pass or fail for the new instance.

### 4.8 Extensions (each one is a design exercise)
- Add an **S3 bucket** for note attachments: Block Public Access, default encryption, versioning, a bucket policy that denies non-TLS requests (`aws:SecureTransport = false`), and access only from the instance role, limited to one prefix.
- Scan your Terraform with **Trivy** (`trivy config infra/`) or **Checkov** before every `apply`, and add it to the CI pipeline from Local Lab §5.
- Add **VPC Flow Logs** for the default VPC and look at what the instance talks to.
- Replace the default VPC with your own VPC with private subnets and **VPC endpoints** for SSM, ECR and S3, so the instance needs no internet route at all. (VPC interface endpoints cost money per hour; destroy them after.)

---

## §5 — Scan your account with Prowler

**What it is:** an open-source tool that checks your AWS account against hundreds of security best practices and frameworks (CIS, AWS FSBP, and others).

```bash
pip install prowler
export AWS_PROFILE=lab
aws sso login --profile lab
prowler aws --region us-east-1        # outputs CSV/JSON/HTML reports to ./output
```

Open the HTML report. For your journal:
1. Pick the **10 most important failed checks**, not the 10 most numerous. Explain your ranking. Ranking by real risk is a core senior skill.
2. Fix them **in Terraform** where possible (not by clicking), re-run Prowler and confirm.
3. For anything you choose not to fix, write a one-paragraph **risk acceptance**: what the risk is, why it's acceptable *in this lab*, and what would change your mind.

---

## §6 — Practice on deliberately vulnerable scenarios

### 6.1 flAWS and flAWS2 (no account needed)

- http://flaws.cloud: a sequence of levels covering common AWS mistakes around S3, credentials and EC2.
- http://flaws2.cloud: has an **Attacker** path and a **Defender** path. Do both; the Defender path teaches you to investigate with CloudTrail logs.

These run in the creator's environment and are designed to be played by anyone. Do them before CloudGoat.

### 6.2 CloudGoat (in your own lab account)

**What it is:** Rhino Security Labs' "vulnerable by design" AWS deployment tool. Each scenario uses Terraform to create a small, deliberately misconfigured environment in your account, with a goal to reach.

**Setup:**
1. Clone https://github.com/RhinoSecurityLabs/cloudgoat and follow its README for the current installation method (it has changed between versions).
2. Configure it to use your lab profile, and let it whitelist your current public IP. The scenarios' exposed resources then only accept connections from you. Typical commands (check the README for the exact form):
   ```bash
   cloudgoat config profile        # enter: lab
   cloudgoat config whitelist --auto
   cloudgoat create <scenario_name>
   cloudgoat destroy <scenario_name>   # ALWAYS, at the end of the session
   ```
3. Each scenario prints starting credentials or a starting point, and its directory contains a README with the goal plus a **cheat sheet / walkthrough**. Try first; read after.

**Suggested order:** start with the smallest IAM-focused scenarios listed as *easy* in the README, then move to scenarios involving EC2, Lambda and S3. The README lists each scenario's size and difficulty.

**How to get the most out of it:**
- **Before** looking at the solution, write down which AWS services and permissions are involved.
- **After** solving it, write the *root-cause misconfiguration* and the *Terraform change* that would have prevented it.
- **Then** go to §7 and find your own actions in the logs.

---

## §7 — Purple-team yourself: find your own activity in the logs

This exercise connects the offensive view to the defensive one, and it's what makes cloud security knowledge useful in an organization.

After each CloudGoat scenario:
1. **CloudTrail → Event history**, filtered by *User name* or *Access key* for the scenario's starting identity. Reconstruct the timeline of every API call you made.
2. **GuardDuty → Findings**: did any of your actions trigger a finding? Which ones didn't, and why not?
3. Write in your journal:
   - The **timeline** (time, identity, API call, result).
   - Which steps were **detected**, which were **not**.
   - A **detection idea** for one undetected step. For example: "alert when `iam:CreatePolicyVersion` with `setAsDefault=true` is called by a non-admin role". Express it as a CloudTrail filter or an EventBridge rule pattern.
4. Stretch goal: create the EventBridge rule (`source: aws.iam`, matching `eventName`) that sends that event to an SNS topic emailing you, re-run the scenario, and confirm you get the email.

---

## §8 — Tear down and verify

At the end of **every** session:

```bash
# Vulnerable scenarios
cloudgoat destroy all

# Your app
cd infra && terraform destroy

# Image and secret (if you're done with them)
aws ecr delete-repository --repository-name safenotes --force
aws ssm delete-parameter --name /safenotes/secret_key
```

At the end of the **lab overall** (or if costs concern you):
- **Security Hub** → *Settings* → *Disable Security Hub*.
- **AWS Config** → *Settings* → stop the recorder.
- **GuardDuty** → *Settings* → *Suspend* or *Disable*.
- Keep **CloudTrail** and **budgets**; they're cheap and protect you.

**Verify nothing is left:**
- **Billing → Bills**: check charges by service for the current month.
- **Resource Explorer** (or **Tag Editor**, searching for tag `Project = appsec-lab`) across all regions.
- **EC2 dashboard** in your lab region: instances, volumes, Elastic IPs, load balancers, NAT gateways all at zero.

---

## What you'll be able to say after this lab

- "I set up a multi-account AWS environment with SSO, MFA, SCP region restrictions and budget guardrails."
- "I deployed an application with no inbound exposure, IMDSv2, a least-privilege role and managed secrets, all in Terraform."
- "I ran Prowler and Security Hub, prioritized findings by risk, and fixed them as code."
- "I exploited deliberately vulnerable AWS scenarios in my own account, then found my own activity in CloudTrail and built a detection for it."

Those are senior-level cloud security statements. Each one is backed by journal entries and code you can show.
