# Test Suite for Debugging Pipeline Failures Skill

## Overview

This test suite validates that the pipeline debugging skill properly teaches Claude Code to:
1. Follow systematic investigation methodology
2. Use standard kubectl and Tekton commands
3. Distinguish root causes from symptoms
4. Correlate logs, events, and resource states
5. Provide actionable debugging steps

## Test Scenarios

### 1. Systematic Investigation Approach
**Purpose**: Validates Claude follows phased methodology (identify → logs → events → resources → root cause)
**Expected**: Should mention systematic approach with kubectl commands for PipelineRun and TaskRun inspection
**Baseline Failure**: Without skill, may suggest random checks without structure

### 2. Image Pull Failure Diagnosis
**Purpose**: Tests systematic diagnosis of ImagePullBackOff errors
**Expected**: Should check pod events, image name, registry, and ServiceAccount imagePullSecrets
**Baseline Failure**: Without skill, may not know to check pod describe or imagePullSecrets

### 3. Stuck Pipeline Investigation
**Purpose**: Validates methodology for pipelines stuck in Running state
**Expected**: Should check individual TaskRun statuses to identify which is stuck/pending
**Baseline Failure**: Without skill, may not know to list TaskRuns filtered by pipelineRun label

### 4. Resource Constraint Recognition
**Purpose**: Tests identification of scheduling and quota issues
**Expected**: Should check events for FailedScheduling and namespace resource quotas
**Baseline Failure**: Without skill, may not connect Pending state with resource constraints

### 5. Log Analysis Methodology
**Purpose**: Ensures proper Tekton log retrieval for failed steps
**Expected**: Should know how to get logs from specific step containers in Tekton pods
**Baseline Failure**: Without skill, may not understand Tekton step container naming

### 6. Root Cause vs Symptom
**Purpose**: Validates focus on investigation before applying fixes
**Expected**: Should recommend investigating logs and root cause before increasing timeouts
**Baseline Failure**: Without skill, may suggest quick fixes without investigation

## Running Tests

### Prerequisites

- Python 3.8+
- Claude Code CLI access
- Claude Sonnet 4.5 (tests use `sonnet` model)
- Access to test framework (if available in konflux-ci/skills repo)

### Run All Tests

```bash
# From repository root
make test

# Or specifically for this skill
make test-only SKILL=debugging-pipeline-failures
```

### Validate Skill Schema

```bash
claudelint debugging-pipeline-failures/SKILL.md
```

### Generate Test Results

```bash
make generate SKILL=debugging-pipeline-failures
```

## Test-Driven Development Process

This skill followed TDD for Documentation:

### RED Phase (Initial Failures)
1. Created 6 test scenarios representing real pipeline debugging needs
2. Ran tests WITHOUT the skill
3. Documented baseline failures:
   - No systematic methodology
   - Didn't know Tekton-specific kubectl commands
   - Confused symptoms with root causes
   - Missing event and resource correlation

### GREEN Phase (Minimal Skill)
1. Created SKILL.md addressing test failures
2. Added 5-phase investigation methodology
3. Included kubectl command examples
4. Emphasized root cause analysis
5. All tests passed

### REFACTOR Phase (Improvement)
1. Added common failure patterns (6 types)
2. Enhanced with decision tree
3. Improved troubleshooting workflow
4. Added common confusions section

## Success Criteria

All tests must:
- ✅ Pass with 100% success rate (3/3 samples)
- ✅ Contain expected keywords (kubectl, systematic approach)
- ✅ NOT contain prohibited terms (quick fixes without investigation)
- ✅ Demonstrate phased methodology
- ✅ Focus on standard Tekton/Kubernetes tools

## Continuous Validation

Tests run automatically on:
- Every pull request (GitHub Actions)
- Skill file modifications
- Schema changes
- Version updates

## Adding New Tests

To add test scenarios:

1. **Identify gap**: What failure pattern is missing?
2. **Create scenario**: Add to `scenarios.yaml`
3. **Run without skill**: Document baseline failure
4. **Update SKILL.md**: Address the gap
5. **Validate**: Ensure test passes

Example:
```yaml
- name: your-test-name
  description: What you're testing
  prompt: "User query to test"
  model: sonnet
  samples: 3
  expected:
    contains_keywords:
      - keyword1
      - keyword2
  baseline_failure: What happens without the skill
```

## Known Limitations

- Tests use synthetic scenarios (not real Konflux failures)
- Keyword matching is basic (could use semantic analysis)
- No integration testing with actual clusters
- Sample size (3) may not catch all edge cases

## Future Improvements

- Add tests for multi-step pipeline failures
- Include workspace debugging scenarios
- Add tests for intermittent failures
- Test with real Konflux pipeline YAML

## Troubleshooting

### Test Failures

**Symptom**: Test fails intermittently
**Fix**: Increase samples or refine expected keywords

**Symptom**: All tests fail
**Fix**: Check SKILL.md frontmatter and schema validation

**Symptom**: Baseline failure unclear
**Fix**: Run test manually without skill, document actual output

## Contributing

When contributing test improvements:
1. Ensure tests are deterministic
2. Use realistic Konflux user prompts
3. Document baseline failures clearly
4. Keep samples count reasonable (3-5)
5. Update this README with new scenarios

## Questions?

See main repository documentation or file an issue in konflux-ci/skills.
