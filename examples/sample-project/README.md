# ForgeFlow Sample Project

A minimal **example project** showing how to use ForgeFlow with your own codebase.

This is a **template** — copy it into your real project directory and modify the contents (workflow specs, artifact samples, etc.) to match your needs.

---

## Directory Structure

```
sample-project/
├── .forgeflow/                    # The ForgeFlow runtime root (copy this!)
│   ├── adapter/                   # LLM adapters per host
│   │   └── copilot/              # GitHub Copilot Chat prompts
│   │       ├── plan.prompt.md    # Plan workflow system prompt
│   │       ├── grill.prompt.md   # Grill workflow system prompt  
│   │       ├── solution.prompt.md
│   │       ├── slice.prompt.md
│   │       ├── tdd.prompt.md
│   │       └── review.prompt.md
│   ├── artifacts/                 # Generated workflow outputs (created at runtime)
│   │   └── planning.md           # Sample artifact showing output format
│   ├── protocol/                  # Protocol specification files
│   │   ├── artifact.md           # Artifact naming, metadata conventions
│   │   └── handoff.md            # Handoff block templates (FORWARD/RETURN/TERMINAL)
│   ├── rules/reviews/             # Plugin system for custom review rules
│   │   ├── security/
│   │   │   └── rules.md          # Security check checklist (editable)
│   │   └── coding-standard/
│   │       └── rules.md          # Code style checklist (editable)
│   └── workflow/                  # Workflow specification files
│       ├── plan.md                # Plan → Planning.md
│       ├── grill.md               # Grill → Requirement-*.md
│       ├── solution.md            # Solution → SolutionPlan.md
│       ├── slice.md               # Slice → SlicePlan-*.md
│       ├── tdd.md                 # TDD → TDDRecord-*.md
│       └── review.md              # Review → ReviewReport-*.md
└── README.md                      # This file (project-level documentation)
```

---

## How to Use This Example

### Step 1: Copy the .forgeflow/ Directory into Your Project

```bash
# Option A: Copy directly into an existing project
cp -r sample-project/.forgeflow/ /path/to/my-project/

# Option B: Clone and customize
git clone https://github.com/<your-org>/my-project.git
cd my-project
mkdir .forgeflow && cp -r sample-project/.forgeflow/* .forgeflow/
```

### Step 2: Customize the Prompt Files

Open `.forgeflow/adapter/copilot/<workflow>.prompt.md` and modify:
- The **context** you want the LLM to consider (e.g., specific codebase structure)
- The **constraints** for your project (languages, frameworks, policies)

Example: Replace generic instructions with your project's technology stack.

### Step 3: Define Your Own Workflows

Each `.md` file in `.forgeflow/workflow/` contains:
- A **contract table** (scope, artifact type, required inputs)
- **Process steps** (what the LLM must do)
- **Completion criteria** (when to mark READY vs BLOCKED)

Replace the sample content with your project's specific requirements.

### Step 4: Add Review Plugins

Create `.forgeflow/rules/reviews/<your-plugin>/rules.md` for custom checks:

```markdown
# My Plugin Rules

| Rule ID | Description | Check Criteria | Expected Result |
|---------|-------------|----------------|-----------------|
| MY-001 | No hardcoded secrets | Scan .env files for literal values | All keys use environment variables |
```

Then register it in `.forgeflow/rules/reviews/_index.md` (create if not exists).

---

## Quick Start Commands

Once your project is set up, run:

```bash
# 1. Initialize (if not already done)
forge init --adapter copilot

# 2. Run the full pipeline
forge run                        # auto-mode: loops until complete or blocked
forge run --reset                # clean artifacts/ before running

# 3. Check status at any time
forge status

# 4. View latest handoff (debug tool)
forge handoff
```

---

## What Each Artifact Represents

| File | Created By | Purpose |
|------|------------|---------|
| `planning.md` | Plan workflow | Project scope, feature list, exclusions |
| `requirement-feature-01.md` | Grill workflow | Feature-level behavior and acceptance criteria |
| `solution-plan.md` | Solution workflow | Engineering design, tech stack decisions |
| `slice-plan-feature-01.md` | Slice workflow | Decomposition into implementable slices |
| `tdd-feature-01-slice-01.md` | TDD workflow | Test-driven development records per slice |
| `review-feature-01-slice-01-attempt-01.md` | Review workflow | Quality gate pass/fail with findings table |

---

## Tips for Customization

1. **Keep prompts focused** — Don't add too much context; let the LLM reason from the contract
2. **Define clear completion criteria** — Use explicit conditions (not "when it feels right")
3. **Use sample artifacts as templates** — Modify field names, not structure
4. **Test plugins independently** — Run `forge status` to see which plugin rules are active

---

## License

This example project is MIT-licensed under the same terms as ForgeFlow itself.
