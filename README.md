# Konflux Skills - First Skill Complete

## Completed: understanding-konflux-resources

### What It Does
Provides a quick reference for Konflux CI/CD Custom Resources (Applications, Components, Snapshots, IntegrationTestScenarios, ReleasePlans, etc.) to help users understand:
- Which resource to use for different tasks
- Who creates each resource (user vs system)
- Where resources belong (tenant vs managed namespace)
- Common confusions and how to avoid them

### Why This Skill First
Based on research into Konflux architecture, documentation, and issue tracker, the most common user pain points are:
1. **Resource confusion** - Not knowing Application vs Component vs Snapshot
2. **Namespace placement** - Wrong namespace for ReleasePlan/ReleasePlanAdmission
3. **Manual vs automatic** - Trying to create resources that are auto-created
4. **Workflow understanding** - Not knowing what happens when code is pushed

This skill (#3 from initial proposal) was chosen as the first because it's foundational - users need to understand resources before they can debug pipelines, configure tests, or set up releases.

### Development Process (TDD for Documentation)

Following the writing-skills methodology:

**RED Phase - Baseline Testing:**
- Created 6 pressure test scenarios
- Ran with fresh agents WITHOUT the skill
- Documented exact failures and rationalizations
- Key findings: Agents invented resource names, confused Application/Component, thought Snapshots were manual

**GREEN Phase - Write Minimal Skill:**
- Wrote skill addressing specific baseline failures
- Quick reference table with "Who Creates" column
- Common Confusions section with ❌/✅ format
- Decision tree for resource selection

**REFACTOR Phase - Close Loopholes:**
- Round 1: Agents still inventing resource names → Added explicit warning
- Round 2: Agents confused Application/Component → Strengthened with Q&A format
- Round 3: Added multiple redundant explanations ("NO git URL" for Application)
- Final: All 6 scenarios passing

### Test Results

| Scenario | Baseline | Final | Status |
|----------|----------|-------|--------|
| 1. Resource selection (which CR for building) | ❌ Invented "ApplicationSource" | ✅ Component | PASSING |
| 2. Namespace placement (tenant vs managed) | ❌ Wrong namespace | ✅ Correct placement | PASSING |
| 3. Snapshot lifecycle (auto-creation) | ❌ Said create manually | ✅ Auto-created | PASSING |
| 4. Application/Component (microservices) | ✅ Already correct | ✅ Still correct | PASSING |
| 5. Resource flow (code push workflow) | ⚠️ Mixed terminology | ✅ Correct flow | PASSING |
| 6. Integration testing (security scans) | ✅ Already correct | ✅ Still correct | PASSING |

### Metrics

- **Word count:** 1,297 words (reasonable for domain-specific reference)
- **Frontmatter:** 326 characters (< 1024 limit)
- **Test coverage:** 6/6 scenarios passing
- **Refactor iterations:** 3 rounds to bulletproof
- **Time invested:** Full RED-GREEN-REFACTOR cycle with proper testing

### Key Learnings

1. **❌/✅ format extremely effective** - Agents respond well to explicit wrong/right examples
2. **Redundancy is good** - Same concept explained multiple ways catches more cases
3. **Negative space matters** - "NO git URL" clarifies what something ISN'T
4. **Q&A decision trees > statements** - More concrete than abstract rules
5. **Test early, test often** - Each refactor iteration revealed new loopholes

### Files

```
understanding-konflux-resources/
├── SKILL.md          # Main skill (273 lines)
└── README.md         # Skill documentation

Test artifacts (not committed):
├── baseline-results.md           # Baseline test failures
├── test-scenarios-baseline.md    # Test scenarios
├── test-with-skill-results.md    # Round 1 results
└── final-test-results.md         # Final verification
```

### Next Steps

Recommended next skills based on original research:

1. **debugging-pipeline-failures** (HIGH PRIORITY)
   - Most common issue in bug tracker
   - Systematic approach to trace pipeline failures
   - Similar to superpowers:root-cause-tracing but Konflux-specific

2. **configuring-integration-tests** (HIGH PRIORITY)
   - Complex workflow with third-party integrations
   - Critical for CI/CD success
   - Builds on understanding-konflux-resources

3. **securing-supply-chain** (MEDIUM PRIORITY)
   - SBOM, provenance, artifact scanning
   - Aligns with Konflux's security focus
   - Multiple ADRs support this area

4. **multi-architecture-builds** (LOWER but strategic)
   - Specific, complex workflow
   - Feature request in issue tracker
   - Prevents arch-specific pitfalls

### Development and Validation

Before committing changes to this repository, ensure the marketplace schema is valid:

```bash
# Run validation using Make (recommended)
make validate

# Or run directly with Docker/Podman
docker run --rm -v $(pwd):/workspace:Z -w /workspace ghcr.io/stbenjam/claudelint:latest --strict
```

The validation checks:
- ✅ Marketplace schema validity
- ✅ Plugin source paths (must start with `./`)
- ✅ Required fields in marketplace.json
- ✅ JSON syntax correctness

**CI/CD**: GitHub Actions automatically validates all PRs and commits to main using claudelint in strict mode.

### Repository Status

- ✅ First skill committed and signed
- ✅ Follows TDD for documentation
- ✅ All tests passing
- ✅ Automated validation via GitHub Actions
- ✅ Ready for users
- 🎯 Foundation for future Konflux skills
