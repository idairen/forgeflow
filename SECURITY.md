# Security Policy

This document describes ForgeFlow's security posture and provides guidance for reporting vulnerabilities.

---

## Table of Contents

- [1. How To Report A Vulnerability](#1-how-to-report-a-vulnerability)
- [2. Supported Versions](#2-supported-versions)
- [3. What Constitutes A Vulnerability](#3-what-constitutes-a-vulnerability)
- [4. Security Considerations For Users](#4-security-considerations-for-users)
- [5. Security Features Built Into ForgeFlow](#5-security-features-built-into-forgeflow)
- [6. Incident Response Process](#6-incident-response-process)

---

## 1. How To Report A Vulnerability

### Reporting Process

If you discover a security vulnerability in ForgeFlow:

1. **Do NOT open a public GitHub issue** — vulnerabilities should be reported privately
2. Email the maintainers at: **[dairen@example.com](mailto:dairen@example.com)** (replace with real contact when ready)
3. Include a clear subject line: **"ForgeFlow Security Vulnerability Report"**
4. Provide as much detail as possible:
    - Description of the vulnerability
    - Steps to reproduce
    - Potential impact assessment
    - Suggested fix (optional but helpful)

### Response Timeline

| Stage | Target Timeframe | Action |
|-------|------------------|--------|
| Acknowledgment | Within 48 hours | Confirm receipt of report |
| Initial Assessment | Within 1 week | Classify severity and impact |
| Fix Development | Variable (P0: days, P3: months) | Develop patch |
| Public Disclosure | Coordinated with maintainers | Release fix + announcement |

### What To Expect

- A maintainer will respond within 48 hours acknowledging your report
- You may be asked for additional information or clarification
- The team will keep you updated throughout the fix process
- Credit will be given unless anonymity is requested

---

## 2. Supported Versions

ForgeFlow follows a **rolling release** model. Only the latest version receives security patches.

| Version | Status | End of Support |
|---------|--------|----------------|
| Latest (e.g., v0.2.0) | Active development, all patches applied | N/A |
| Previous minor versions | Bug fixes only, no new features | 6 months after latest release |
| Older versions | No longer supported | Discontinued |

**Recommendation:** Always stay on the latest version for security updates.

---

## 3. What Constitutes A Vulnerability

### Examples Of Security Vulnerabilities

| Type | Example | Severity |
|------|---------|----------|
| **Remote Code Execution** | LLM prompt injection leading to arbitrary code execution | P0 (Critical) |
| **Data Exfiltration** | Artifact files containing sensitive credentials sent to external API | P0 (Critical) |
| **Local File Read** | ForgeFlow reads files outside the project directory without authorization | P1 (High) |
| **Command Injection** | Unsafe shell execution in workflow commands | P1 (High) |
| **Dependency Vulnerability** | Outdated package with known CVE | P2 (Medium) |
| **Information Disclosure** | Sensitive metadata leaked in error messages | P2 (Medium) |

### Examples Of Non-Vulnerabilities

| Type | Example | Reason |
|------|---------|--------|
| Documentation typos | Wrong word in README.md | Not a security risk |
| Minor style inconsistencies | Inconsistent code formatting | Cosmetic, not security-relevant |
| Feature requests without security impact | "Add X feature" | Enhancement, not vulnerability |

---

## 4. Security Considerations For Users

### Important Notes About ForgeFlow's Architecture

ForgeFlow is a **Markdown-driven orchestration tool**. It does not directly execute code or make network requests. However, users should be aware of:

#### Risk #1: LLM Backend Communication

| Aspect | Detail | Mitigation |
|--------|--------|------------|
| Where data goes | Prompt content is sent to the configured LLM backend (OpenAI, Anthropic, etc.) | Only project-relevant Markdown is sent |
| What gets sent | Workflow prompts + user intent | No source code is automatically included unless explicitly referenced |
| Network dependency | Required for LLM API calls | Can be used offline with local models |

#### Risk #2: Artifact File Content

| Aspect | Detail | Mitigation |
|--------|--------|------------|
| Who writes artifacts | The LLM generates Markdown content for `planning.md`, `solution-plan.md`, etc. | Review generated content before trusting it |
| Where artifacts are stored | `.forgeflow/artifacts/` (local directory) | No external storage, no cloud sync |
| Can artifacts be modified? | Only the owning workflow can modify its artifact | Cross-workflow modification is prevented by design |

#### Risk #3: CLI Execution Safety

| Aspect | Detail | Mitigation |
|--------|--------|------------|
| Does `forge run` execute code? | **No** — it reads prompts and writes Markdown files | No shell commands are executed by the engine |
| Does `reset --force` delete files? | Yes — removes `.forgeflow/artifacts/` | Only project-local files; never deletes source code |

### Best Practices For Safe Usage

1. **Review LLM-generated content** before trusting it for production decisions
2. **Never store sensitive credentials** in artifact files (planning.md, solution-plan.md, etc.)
3. **Use version control** to track changes and revert if needed
4. **Limit LLM API access** — use tokens with minimum required permissions
5. **Keep ForgeFlow updated** — install the latest version for security fixes

---

## 5. Security Features Built Into ForgeFlow

ForgeFlow incorporates several design principles that inherently reduce security risk:

| Feature | How It Helps | Limitations |
|---------|-------------|-------------|
| **Local-first architecture** | All data stays on your machine; no cloud storage dependency | No built-in encryption for stored artifacts |
| **No external service calls** | ForgeFlow itself does not make HTTP requests | LLM backends (OpenAI, Anthropic) do communicate externally |
| **Artifacts are Markdown only** | No executable code is generated or executed by ForgeFlow | Users may place code in artifacts; review recommended |
| **Single data source (config.json)** | Centralized configuration reduces inconsistency attacks | Config file permissions not enforced by ForgeFlow |
| **Plugin system validation** | Plugin rules must follow checklist format | LLM executes rule interpretation; quality depends on user-written rules |

### Security By Design Principles

1. **Zero Trust**: Assume every LLM-generated artifact could contain incorrect or harmful content
2. **Least Privilege**: ForgeFlow only has read/write access to project-local files
3. **Fail Securely**: Handoff validation failures stop execution rather than proceeding with invalid state
4. **Audit Trail**: All artifacts are version-tracked (via git); resets create timestamped archives

---

## 6. Incident Response Process

When a security vulnerability is confirmed:

### Step 1: Classification

| Severity | Definition | Response Time |
|----------|------------|---------------|
| **P0 (Critical)** | RCE, data breach, arbitrary code execution, credential theft | Immediate — fix within hours/days |
| **P1 (High)** | Local file read, command injection, significant privilege escalation | Within days |
| **P2 (Medium)** | Information disclosure, minor privilege escalation, DoS vector | Within weeks |
| **P3 (Low)** | Cosmetic security concern, informational vulnerability, hardening suggestion | Next release cycle |

### Step 2: Patch Development

- Develop patch against `dev` branch
- Add regression test if applicable
- Self-review and peer-review required

### Step 3: Testing

| Test | Description |
|------|-------------|
| Unit test | Verify the fix resolves the vulnerability |
| Regression test | Ensure no existing functionality is broken |
| Integration test | End-to-end flow with `forge run --reset` |

### Step 4: Release

- Bump version in `pyproject.toml`
- Write changelog entry under "Security Fixes" section
- Merge to `dev`, then to `main`
- Publish release announcement with advisory details

---

## Quick Reference

### Reporting A Vulnerability — Checklist

- [ ] Do NOT open a public issue
- [ ] Email: dairen@example.com (subject: "ForgeFlow Security Vulnerability Report")
- [ ] Include description, reproduction steps, impact assessment
- [ ] Expect acknowledgment within 48 hours
- [ ] Stay updated through private communication channel

### Supported Versions

| Version | Support Status |
|---------|---------------|
| Latest | Active (all patches applied) |
| Previous minor | Bug fixes only |
| Older | No longer supported — upgrade immediately |

### Security Best Practices

1. Review LLM-generated artifacts before trusting
2. Never store credentials in artifact files
3. Keep ForgeFlow updated to latest version
4. Use local models when available for sensitive projects
5. Enable version control (git) for artifact tracking

---

Thank you for helping keep ForgeFlow secure!
