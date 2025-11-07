# Shortname Discovery Test

## Test Objective
Verify that the skill is discoverable when users reference Konflux resources by their common shortnames (RP, RPA, ITS, etc.)

## Test Scenarios

### Scenario 1: Basic Shortname Usage
**User prompt:** "I'm confused about where to create my RP - should it go in the tenant namespace or managed namespace?"

**Expected behavior:** Agent should recognize this is about ReleasePlan and load the understanding-konflux-resources skill

**Success criteria:**
- Agent identifies RP = ReleasePlan
- Agent loads understanding-konflux-resources skill
- Agent correctly answers: ReleasePlan goes in tenant namespace, ReleasePlanAdmission goes in managed namespace

### Scenario 2: Multiple Shortnames
**User prompt:** "After my Component builds, do I need to manually create a Snapshot before my ITS runs?"

**Expected behavior:** Agent should recognize ITS = IntegrationTestScenario and load the skill

**Success criteria:**
- Agent identifies ITS = IntegrationTestScenario
- Agent loads understanding-konflux-resources skill
- Agent correctly answers: Snapshots are auto-created, no manual creation needed

### Scenario 3: Mixed Shortnames
**User prompt:** "How does the RPA reference the RP? Do they need to be in the same namespace?"

**Expected behavior:** Agent should recognize RPA = ReleasePlanAdmission and RP = ReleasePlan

**Success criteria:**
- Agent loads understanding-konflux-resources skill
- Agent correctly explains namespace separation
- Agent answers based on skill content

### Scenario 4: Common Abbreviations in Context
**User prompt:** "My ITS is not running after builds complete. I have the Component and Application set up. What am I missing?"

**Expected behavior:** Agent should load skill and provide troubleshooting guidance

**Success criteria:**
- Agent recognizes this is a Konflux question
- Agent loads understanding-konflux-resources skill
- Agent provides troubleshooting steps from the skill

## Common Shortnames to Support

- **RP** = ReleasePlan
- **RPA** = ReleasePlanAdmission
- **ITS** = IntegrationTestScenario
- **App** = Application
- **Comp** = Component

## Baseline Test (Without Shortnames in Skill)

Testing against current skill version (1.0.0) which does NOT include shortnames in description or keywords.

### Test Execution Plan

1. Launch subagent with standard Claude Code environment
2. Do NOT pre-load understanding-konflux-resources skill
3. Present each scenario prompt
4. Observe whether agent:
   - Loads the skill organically
   - Recognizes shortname meanings
   - Provides correct answers

### Hypothesis

Without shortnames in the skill description or keywords:
- Agent may not load the skill when user uses shortnames
- Agent may need to explicitly search or guess shortname meanings
- Discovery will be slower/less reliable
