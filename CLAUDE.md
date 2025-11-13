# Konflux Skills Repository

## Purpose

This repository contains Claude Code skills to help users work with the Konflux CI/CD platform. Skills provide quick reference materials, techniques, and patterns for common Konflux workflows.

**Target audience:** Developers and platform engineers using Konflux for continuous integration, testing, and release management.

## Testing Approach: Realistic Skill Discovery with Parallel Execution

**Solution:** Tests verify that Claude will **discover and invoke** skills in realistic scenarios using isolated temp HOME directories per worker.

**How it works:**
1. Create N temp HOME directories (one per parallel worker)
2. Each worker HOME contains:
   - Symlink to skill in `~/.claude/skills/`
   - Copy of `.config/gcloud` (required for Claude Code API auth)
   - Skill-specific credentials from `copy_to_home` field (e.g., `.config/gh`)
3. Run `claude --print --allowed-tools=<tools>` with `HOME=/tmp/claude-worker-N/`
   - Parses `allowed-tools` from SKILL.md frontmatter
   - Always includes `Skill` tool plus any skill-specific tools
4. Each worker reuses its temp HOME across all test invocations
5. Cleanup all worker HOMEs after test completion

**Key insights:**
- Isolated temp HOMEs prevent file watcher conflicts between parallel workers
- Skills symlinked to `~/.claude/skills/` are discovered automatically
- **Tool permissions**: Test framework parses `allowed-tools` from SKILL.md frontmatter
- **Credentials**: Test framework copies paths from scenarios.yaml `copy_to_home` field
- `.config/gcloud` always copied for Claude Code API authentication
- Skill-specific credentials (gh, kubectl, etc.) declared per skill
- Worker HOMEs persist for the duration of the test run

**Benefits:**
- ✅ Tests real skill discovery (Claude loads skills from `~/.claude/skills/`)
- ✅ Works in `--print` mode (automated testing)
- ✅ **True parallel execution** (8 workers, isolated file watchers)
- ✅ Runs from `/tmp` to avoid loading `CLAUDE.md` from repository
- ✅ Each worker reuses setup (minimal overhead per test)

**Trade-offs:**
- Copies credentials once per worker (~10-50MB × 8 workers)
- Skills must explicitly declare tool and credential requirements
- Tests discovery + effectiveness together (can't isolate just effectiveness)
- Temp HOMEs persist during test run (cleaned up after)

**Current Findings (understanding-konflux-resources):**

Tests successfully reveal limitations in skill discovery and Claude's base knowledge:

1. **Skill discovery is inconsistent**
   - Works reliably for IntegrationTestScenario (ITS) queries
   - Fails to trigger for ReleasePlanAdmission (RPA) queries despite "In Konflux" context
   - Suggests description matching is unpredictable

2. **Claude's base knowledge includes incorrect Konflux information**
   - Claude believes RPA is "automatically created by system" (wrong)
   - Skill correctly states "Platform Engineer creates RPA in managed namespace"
   - When skill isn't invoked, Claude falls back on incorrect training data

3. **Description balance challenge**
   - Too strict: Won't trigger even with explicit Konflux context
   - Too loose: Triggers on generic abbreviations without Konflux context
   - Current approach: Simplified description mentioning key resource types

4. **Test results: 1/6 scenarios passing, 7/18 samples**
   - ✅ PASS: its-not-running (all 3 samples)
   - ❌ FAIL: rpa-creation-responsibility (0/3 - skill not invoked)
   - ❌ FAIL: rp-rpa-relationship (0/3 - missing tenant/managed terms)
   - ❌ FAIL: negative-rp-without-konflux (0/3 - triggers without Konflux keyword)

**Conclusion:** Test framework works correctly - it reveals real skill discovery limitations and demonstrates need for more reliable skill invocation mechanisms.

## Repository Structure

```
.claude-plugin/
├── marketplace.json          # Marketplace manifest for Claude Code
skills/
└── understanding-konflux-resources/  # Each skill in its own directory
    ├── SKILL.md             # Main skill file with YAML frontmatter
    ├── README.md            # Skill documentation
    └── tests/               # Test scenarios and results (TDD artifacts)
CLAUDE.md                    # This file - development guidelines
README.md                    # Project overview and status
```

## Skill Development Guidelines

### Process: Test-Driven Development for Documentation

All skills MUST follow the RED-GREEN-REFACTOR cycle from the `superpowers:writing-skills` methodology:

**RED Phase - Write Failing Test:**
1. Create 3-6 pressure test scenarios covering the skill's domain
2. Run scenarios with fresh subagents WITHOUT the skill
3. Document exact failures, rationalizations, and gaps verbatim
4. Identify patterns in what agents get wrong

**GREEN Phase - Write Minimal Skill:**
1. Write skill addressing ONLY the specific baseline failures
2. Focus on the gaps identified in RED phase
3. Don't add hypothetical content
4. Run scenarios WITH skill - verify agents now comply

**REFACTOR Phase - Close Loopholes:**
1. Test again and identify NEW rationalizations
2. Add explicit counters to skill
3. Strengthen weak areas
4. Re-test until all scenarios pass

**MANDATORY:** Never commit a skill without completing all three phases. Test artifacts should be saved in `<skill-name>/tests/` directory.

### Skill Creation Checklist

Before committing a new skill, verify:

- [ ] **YAML Frontmatter**
  - [ ] `name` uses only lowercase letters, numbers, and hyphens
  - [ ] `description` starts with "Use when..." and includes specific triggers
  - [ ] Total frontmatter < 1024 characters
  - [ ] Description written in third person
  - [ ] `allowed-tools` field added if skill needs specific tools (e.g., `Bash(gh pr:*)`)
    - Restricts tools during interactive use (security/safety)
    - Enables same tools during test generation (consistency)

- [ ] **Content Quality**
  - [ ] Core principle stated upfront
  - [ ] "When to Use" section with clear triggers
  - [ ] Quick reference table or decision tree
  - [ ] Real-world examples (Konflux-specific)
  - [ ] Common mistakes section
  - [ ] Keywords for Claude Search Optimization

- [ ] **Testing (TDD)**
  - [ ] Test scenarios defined in `tests/scenarios.yaml`
  - [ ] Baseline tests run WITHOUT skill (RED phase)
  - [ ] All baseline failures documented in YAML's `baseline_failure` field
  - [ ] Skill addresses specific failures (GREEN phase)
  - [ ] Loopholes closed through iteration (REFACTOR phase)
  - [ ] All test scenarios passing: `make test SKILL=<name>`
  - [ ] Test results generated and committed: `make generate SKILL=<name>`

- [ ] **Integration**
  - [ ] Skill directory created: `skills/<skill-name>/`
  - [ ] SKILL.md created with proper frontmatter
  - [ ] README.md created documenting the skill
  - [ ] Entry added to `.claude-plugin/marketplace.json`
  - [ ] Version number follows semver (start at 1.0.0)

- [ ] **Git Commit**
  - [ ] Commit message describes what problem the skill solves
  - [ ] Commit signed with GPG (`-S` flag)
  - [ ] Sign-off added (`-s` flag)
  - [ ] Co-authored-by Claude footer included

### Marketplace File Management

When adding a new skill, update `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-skill-name",
  "source": "./skills/your-skill-name",
  "description": "Same as SKILL.md description",
  "version": "1.0.0",
  "author": {
    "name": "Konflux CI Team"
  }
}
```

**Version bumping:**
- Patch (1.0.x): Bug fixes, typo corrections, minor clarifications
- Minor (1.x.0): New sections, new examples, significant additions
- Major (x.0.0): Breaking changes to skill structure or approach

### Skill Naming Conventions

**Use gerunds (verbs ending in -ing) for techniques:**
- ✅ `debugging-pipeline-failures`
- ✅ `configuring-integration-tests`
- ✅ `securing-supply-chain`

**Use nouns for references:**
- ✅ `understanding-konflux-resources` (knowledge/reference)
- ✅ `konflux-resource-reference` (alternative)

**Keep names:**
- Lowercase with hyphens only
- Specific to the task/problem
- No special characters or parentheses

### Testing Standards

**IMPORTANT: Never directly edit files in `<skill-name>/tests/results/`**
- Result files are auto-generated by `make generate`
- They contain a digest of the skill content to detect changes
- Manual edits will be overwritten on next generation
- To update results: modify the skill, then run `make generate`
- `make generate` invokes Claude in `--print` mode (non-interactive) which does not load CLAUDE.md

Each skill must have test scenarios in `<skill-name>/tests/scenarios.yaml`:

**Required configuration:**
```yaml
skill_name: your-skill-name
description: Brief test description

# Optional: Paths to copy from real HOME to test environment HOME
# Skills that need external credentials (gh, kubectl, etc.) should declare them here
copy_to_home:
  - .config/gh          # Example: GitHub CLI authentication
  - .kube/config        # Example: kubectl cluster configuration

test_scenarios:
  - name: test-name
    description: What this validates
    prompt: "User question to test"
    model: haiku              # Model to use for this scenario
    samples: 3                # Number of result samples to generate
    expected:
      contains_keywords: [keyword1, keyword2]
      does_not_contain: [wrong-term]
    baseline_failure: "What failed in RED phase"
```

**Tool Permissions (`allowed-tools` in SKILL.md frontmatter):**

Skills that use specific tools should declare them in SKILL.md frontmatter using the standard `allowed-tools` field:

```yaml
---
name: navigating-github-to-konflux-pipelines
description: Use when GitHub PR or branch has failing checks...
allowed-tools: Bash(gh pr:*), Bash(gh api:*), Bash(gh repo:*), Bash(grep:*), Bash(sed:*)
---
```

**Purpose:**
- **Interactive use**: Restricts which tools Claude can use when skill is active (security/safety)
- **Test generation**: Test framework parses this field and enables the same tools in `--print` mode

**Syntax:**
- Use parenthetical syntax to limit command scope: `Bash(gh pr:*)`
- Comma or space-separated list
- Tool names must match Claude Code tool names (Bash, Read, Edit, etc.)

**Credential Management (`copy_to_home` in scenarios.yaml):**

Skills that need to run commands requiring external authentication (e.g., `gh`, `kubectl`) should declare required credential paths in `copy_to_home`:

- `.config/gcloud` is **always copied** for Claude Code API authentication
- Add skill-specific paths for other credentials:
  - `.config/gh` - GitHub CLI authentication
  - `.kube/config` - kubectl cluster configuration
  - `.aws/credentials` - AWS CLI credentials
  - Any other `~/` relative path needed

**Example:**
```yaml
# Skills using gh commands need GitHub CLI auth
copy_to_home:
  - .config/gh
```

**Relationship between `allowed-tools` and `copy_to_home`:**
- `allowed-tools` (SKILL.md) - **Permission** to use tools
- `copy_to_home` (scenarios.yaml) - **Credentials** to authenticate those tools
- Both are needed for skills using authenticated external commands

**Test scenario coverage:**
- Recognition tests (does agent know when to apply?)
- Application tests (can agent use the skill correctly?)
- Edge cases and common confusions
- Integration with other Konflux concepts

Minimum 3 scenarios, recommended 6+ for comprehensive skills.

**Running tests:**
- `make generate` - Generate test results (invokes Claude with `--allowed-tools=Skill`)
- `make test` - Validate results against expectations
- Results stored in `<skill-name>/tests/results/`
- Debug logs stored as `<scenario-name>-<sample-num>.debug.txt` (gitignored)

**Debug logs:**
Debug logs are invaluable for understanding skill invocation behavior. Each test generates a `.debug.txt` file containing:
- Skill loading: Which skills were discovered and from where
- Tool registration: Which tools are enabled (e.g., "Skills and commands included in Skill tool")
- Skill execution: How the Skill tool processes and injects skill content
- Hooks and LSP info: Additional context about the test environment

Use debug logs to diagnose:
- Why a skill wasn't invoked (check "Loaded X unique skills")
- Whether the Skill tool is enabled (search for "Skill tool")
- How skill content is being injected (search for "processPromptSlashCommand")
- Any errors during skill loading or execution

### Konflux-Specific Guidelines

**Keep content current:**
- Reference actual Konflux CRD names (Application, Component, Snapshot, etc.)
- Use current architecture (Tekton-based pipelines, not deprecated systems)
- Align with konflux-ci.dev documentation when possible
- Note any experimental or preview features

**Common user pain points to address:**
- Resource confusion (Application vs Component vs Snapshot)
- Namespace placement (tenant vs managed)
- User-created vs system-created resources
- Pipeline debugging and troubleshooting
- Integration test configuration
- Supply chain security (SBOM, provenance, scanning)

**Avoid:**
- Inventing non-existent resource names
- Mixing OpenShift/Kubernetes concepts unless explicitly relevant
- Outdated terminology (check latest docs)
- Project-specific details (keep skills general to Konflux platform)

### Quality Standards

**Conciseness:**
- Reference skills: < 1500 words preferred
- Technique skills: < 1000 words preferred
- Frequently-loaded skills: < 500 words (critical for context efficiency)

**Clarity:**
- Use tables for quick reference
- Use ❌/✅ format for common confusions
- Provide decision trees for "which option" questions
- Include concrete examples, not abstract templates

**Searchability (CSO - Claude Search Optimization):**
- Include error messages users might see
- Use symptom-based language ("flaky tests", "stuck in pending")
- Add keywords section at the end
- Description field should match how users think about the problem

## Contributing New Skills

1. **Research the problem space**
   - Check Konflux docs, issues, ADRs
   - Identify common pain points
   - Understand user workflows

2. **Follow TDD cycle**
   - Create test scenarios FIRST
   - Run baseline tests WITHOUT skill
   - Write skill addressing failures
   - Iterate until all tests pass

3. **Document thoroughly**
   - Save all test artifacts in `<skill-name>/tests/`
   - Create README.md explaining the skill
   - Update marketplace.json

4. **Commit with standards**
   - GPG sign commits (`-S`)
   - Add sign-off (`-s`)
   - Descriptive commit message
   - Include Co-Authored-By footer

## Current Skills

1. **understanding-konflux-resources** (v1.0.0)
   - Reference for Konflux Custom Resources
   - Addresses Application vs Component confusion
   - Covers namespace placement and resource lifecycle
   - 6/6 test scenarios passing

## Planned Skills

Based on Konflux user pain points:

1. **debugging-pipeline-failures** - Systematic approach to trace pipeline failures
2. **configuring-integration-tests** - Setup and debug IntegrationTestScenarios
3. **securing-supply-chain** - SBOM, provenance, artifact scanning patterns
4. **multi-architecture-builds** - Configure and debug multi-arch component builds

## Questions or Issues?

For questions about Konflux itself: https://konflux-ci.dev/docs/
For issues with these skills: File an issue in this repository
