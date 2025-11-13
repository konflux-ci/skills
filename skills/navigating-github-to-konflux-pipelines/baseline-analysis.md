# Baseline Test Analysis (RED Phase)

## Identified Failure Patterns

Without the skill, agents exhibit these consistent problems:

### 1. Doesn't Know GitHub CLI Commands for Checks
- **Symptom**: Asks user for more context instead of using available commands
- **Example**: "Could you share the specific error messages?" instead of `gh pr checks`
- **Root Cause**: Doesn't know `gh pr checks` or `gh api check-runs` commands exist

### 2. Incorrect Konflux Check Pattern Matching
- **Symptom**: Suggests wrong prefixes like `konflux/`, `build/`, `ci/`
- **Correct Pattern**: Check NAME contains "konflux" (case-insensitive) or URL contains "konflux"
- **Examples of Correct Names**: "Red Hat Konflux / ...", "Konflux Fedora / ...", "Integration Service / ..."

### 3. Suggests Manual Browser-Based Workflows
- **Symptom**: Recommends `gh pr view --web` to open browser
- **Better Approach**: Use `gh pr view --json` or `gh api` for programmatic access
- **Impact**: Can't automate or script the workflow

### 4. Confuses GitHub Actions with Konflux Checks
- **Symptom**: Suggests looking at "Actions" tab or `gh run list`
- **Correct**: Konflux uses GitHub Checks API (check-runs), not Actions workflows
- **Impact**: Sends user to wrong place entirely

### 5. Doesn't Know How to Extract URLs from Check Output
- **Symptom**: Suggests checking cluster with kubectl instead of getting URL from GitHub first
- **Missing Knowledge**: Integration test checks have PipelineRun URLs in `output.text` field
- **Command Needed**: `gh api repos/.../commits/.../check-runs --jq '.check_runs[].output.text'`

### 6. Good at Manual URL Parsing (Positive Finding!)
- **Works Well**: When given a URL directly, can extract cluster/namespace/pipelinerun
- **Keep**: Agents understand URL structure, just need to know how to GET the URLs

### 7. Doesn't Distinguish Build vs Integration Test Checks
- **Missing**: Knowledge that `-on-pull-request` and `-on-push` are build checks with direct URLs
- **Missing**: Integration test checks need output parsing

## Key Gaps to Address in Skill

1. **Teach `gh pr checks` and `gh api` commands**
2. **Correct Konflux check identification pattern** (case-insensitive "konflux" in name/URL)
3. **Distinguish build checks (direct URL) from integration tests (parse output)**
4. **Show `-on-pull-request` vs `-on-push` naming**
5. **Emphasize programmatic API access over browser workflows**
6. **Clarify Checks API vs Actions workflows**

## Rationalizations Observed

- "I don't have direct access" → Actually does via gh CLI
- "I cannot use WebSearch" → Doesn't need to, can use gh API
- "I recommend you check manually" → Should provide commands
- "Would you like me to help you with..." → Should just DO it

## Success Criteria for GREEN Phase

Agent should:
- ✅ Use `gh pr checks` or `gh api` immediately (no asking for context)
- ✅ Filter for "konflux" (case-insensitive) in check names
- ✅ Extract PipelineRun URLs programmatically
- ✅ Distinguish -on-pull-request vs -on-push
- ✅ Know build checks have direct URLs, integration tests need parsing
- ✅ Provide complete kubectl-ready information (cluster, namespace, pipelinerun)
