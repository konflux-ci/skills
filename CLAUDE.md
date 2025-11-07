# Konflux Skills Repository

## Purpose

This repository contains Claude Code skills to help users work with the Konflux CI/CD platform. Skills provide quick reference materials, techniques, and patterns for common Konflux workflows.

**Target audience:** Developers and platform engineers using Konflux for continuous integration, testing, and release management.

## Repository Structure

```
.claude-plugin/
├── marketplace.json          # Marketplace manifest for Claude Code
skills/
├── understanding-konflux-resources/  # Each skill in its own directory
│   ├── SKILL.md             # Main skill file with YAML frontmatter
│   ├── README.md            # Skill documentation
│   └── tests/               # Test scenarios and results (TDD artifacts)
├── CLAUDE.md                # This file - development guidelines
└── README.md                # Project overview and status
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

- [ ] **Content Quality**
  - [ ] Core principle stated upfront
  - [ ] "When to Use" section with clear triggers
  - [ ] Quick reference table or decision tree
  - [ ] Real-world examples (Konflux-specific)
  - [ ] Common mistakes section
  - [ ] Keywords for Claude Search Optimization

- [ ] **Testing (TDD)**
  - [ ] Baseline tests run WITHOUT skill (RED phase)
  - [ ] All baseline failures documented in `tests/` directory
  - [ ] Skill addresses specific failures (GREEN phase)
  - [ ] Loopholes closed through iteration (REFACTOR phase)
  - [ ] All test scenarios passing with skill present
  - [ ] Test artifacts committed to `<skill-name>/tests/`

- [ ] **Integration**
  - [ ] Skill directory created: `<skill-name>/`
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
  "source": "your-skill-name",
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

Each skill must have test scenarios in `<skill-name>/tests/`:

**Required test artifacts:**
1. `test-scenarios-baseline.md` - Test scenarios with expected vs actual results
2. `baseline-results.md` - Documentation of failures WITHOUT the skill
3. `test-with-skill-results.md` - Results showing skill fixes the issues
4. `final-test-results.md` - Verification all scenarios pass

**Test scenario coverage:**
- Recognition tests (does agent know when to apply?)
- Application tests (can agent use the skill correctly?)
- Edge cases and common confusions
- Integration with other Konflux concepts

Minimum 3 scenarios, recommended 6+ for comprehensive skills.

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
