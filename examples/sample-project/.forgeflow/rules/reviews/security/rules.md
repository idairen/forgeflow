# Security Review Rules — Sample

## Overview

This plugin checks for common security vulnerabilities. Copy this template and modify the rules for your project's needs.

| Rule ID | Description | Check Criteria | Expected Result |
|---------|-------------|----------------|-----------------|
| SEC-001 | No hardcoded passwords | Scan all .py files for literal password strings in assignments | All credentials from env vars or vault |
| SEC-002 | SQL Injection Prevention | Check database query patterns | Use parameterized queries only |

## Notes

- This is a **sample** plugin. Replace with your own rules.md content.
- Add more rows to the table for additional checks.
- Each rule should be specific and testable by an LLM.
