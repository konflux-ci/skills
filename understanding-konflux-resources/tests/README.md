# Testing Guide for understanding-konflux-resources Skill

This directory contains test scenarios and results for the shortname discovery feature.

## Test Files

- **shortname-discovery-test.md** - Test scenarios and success criteria
- **shortname-baseline-results.md** - RED phase results (without shortnames)
- **shortname-green-phase-results.md** - Expected GREEN phase results (with shortnames)
- **run-tests.sh** - Bash test runner (generates test prompts)
- **run-tests.py** - Python test runner (with validation)
- **interactive-test.sh** - Interactive test runner for manual execution

## How to Run Tests

### Option 1: Quick Manual Test (Recommended)

Ask Claude Code to run a test scenario:

```
Can you test the RP shortname recognition? Use the skill content from
understanding-konflux-resources/SKILL.md and ask: "I'm confused about
where to create my RP - should it go in the tenant namespace or managed
namespace?"
```

### Option 2: Automated Test Suite (Python)

```bash
# Generate test prompts
cd understanding-konflux-resources/tests
python3 run-tests.py

# This creates prompt files in results/ directory
# Run each prompt manually and save responses to .result.txt files
# Then re-run to validate:
python3 run-tests.py
```

### Option 3: Interactive Bash Script

```bash
cd understanding-konflux-resources/tests
chmod +x interactive-test.sh
./interactive-test.sh

# Follow the prompts - it will generate test files you can copy/paste
```

### Option 4: Direct Task Tool Usage

Within Claude Code, run each test scenario:

**Test 1: RP Recognition**
```
Task tool with model=haiku:
"You have access to the understanding-konflux-resources skill (content below).

[paste SKILL.md content]

User question: I'm confused about where to create my RP - should it go
in the tenant namespace or managed namespace?

Answer naturally, then explain how you interpreted 'RP'."
```

## Test Scenarios

### Test 1: RP (ReleasePlan)
- **Prompt:** "Where should I create my RP?"
- **Expected:** Recognizes RP=ReleasePlan, answers "tenant namespace"
- **Validates:** Description field triggers, abbreviation table works

### Test 2: ITS (IntegrationTestScenario)
- **Prompt:** "My ITS isn't running after builds"
- **Expected:** Recognizes ITS, provides specific troubleshooting
- **Validates:** Keywords work, troubleshooting section found

### Test 3: RPA (ReleasePlanAdmission)
- **Prompt:** "Do I create RPA or does platform team?"
- **Expected:** Recognizes RPA, answers "platform engineer creates it"
- **Validates:** Role/responsibility information correct

### Test 4: Mixed Shortnames
- **Prompt:** "How does RPA reference RP?"
- **Expected:** Recognizes both, explains namespace separation
- **Validates:** Multiple abbreviations in one query

### Test 5: Lowercase
- **Prompt:** "my its isn't triggering"
- **Expected:** Still recognizes despite lowercase
- **Validates:** Case-insensitive matching

## Success Criteria

For each test, verify:

1. ✅ **Recognition:** Agent identifies the abbreviation correctly
2. ✅ **Accuracy:** Answer matches skill content
3. ✅ **Specificity:** Uses exact troubleshooting steps (not generic advice)
4. ✅ **Confidence:** High confidence due to skill content

## Validation Checklist

- [ ] RP → ReleasePlan, tenant namespace
- [ ] RPA → ReleasePlanAdmission, managed namespace, platform engineer
- [ ] ITS → IntegrationTestScenario, specific troubleshooting
- [ ] Lowercase variations work
- [ ] Mixed abbreviations handled correctly
- [ ] No confusion with non-Konflux abbreviations

## TDD Phases

This testing follows RED-GREEN-REFACTOR:

**RED Phase** ✅ Complete
- Baseline tests run WITHOUT shortnames
- Failures documented in `shortname-baseline-results.md`

**GREEN Phase** ✅ Complete
- Skill updated with abbreviations
- Expected improvements documented in `shortname-green-phase-results.md`

**REFACTOR Phase** ⏭️ Next
- Run actual tests with updated skill
- Identify any new rationalizations/failures
- Close loopholes if needed

## Test Results Directory

After running tests, results/ will contain:

```
results/
├── rp-namespace-placement.prompt.txt
├── rp-namespace-placement.result.txt
├── its-not-running.prompt.txt
├── its-not-running.result.txt
├── rpa-creation-responsibility.prompt.txt
├── rpa-creation-responsibility.result.txt
└── ...
```

## Troubleshooting

**Problem:** Agent doesn't recognize abbreviation
- **Check:** Is the abbreviation in the description field?
- **Check:** Is it in the keywords section?
- **Check:** Is it in the Quick Reference table?

**Problem:** Agent recognizes but gives wrong answer
- **Check:** Is the correct information in the skill content?
- **Check:** Is the agent using the provided skill content?

**Problem:** Tests can't be automated
- **Solution:** Use manual testing with Task tool
- **Solution:** Create skill installation for full automation

## Contributing Test Results

When you run tests, please document:

1. Date and model used (e.g., "2025-11-07, haiku")
2. Full agent response
3. Whether it passed/failed
4. Any unexpected behavior

Save to `results/test-run-YYYY-MM-DD.md`
