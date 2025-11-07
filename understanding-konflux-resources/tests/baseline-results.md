# Baseline Test Results - understanding-konflux-resources

## Summary of Failures

All 6 scenarios revealed significant gaps in agent knowledge about Konflux resources.

## Scenario 1: Resource Selection
**Question:** "What Konflux resource should I create to build my frontend app?"

**Agent Response:** Suggested "ApplicationSource" resource (incorrect - this doesn't exist)
**Correct Answer:** Component CR

**Failure Analysis:**
- Invented non-existent resource name "ApplicationSource"
- Mixed up AppStudio terminology
- Didn't know the actual resource name is "Component"

## Scenario 2: Namespace Confusion
**Question:** "Should I create the ReleasePlan in my tenant namespace or managed namespace?"

**Agent Response:** Put ReleasePlan in managed namespace (WRONG)
**Correct Answer:** ReleasePlan in tenant namespace, ReleasePlanAdmission in managed namespace

**Failure Analysis:**
- Completely reversed the correct placement
- Reasoning sounded plausible but was factually wrong
- Didn't understand tenant vs managed namespace separation

## Scenario 3: Snapshot Lifecycle
**Question:** "Do I need to create a new Snapshot after committing code?"

**Agent Response:** "Yes, you need to create a new Snapshot" (WRONG)
**Correct Answer:** No - Integration Service creates snapshots automatically

**Failure Analysis:**
- Fundamentally misunderstood Snapshot lifecycle
- Didn't know which resources are user-created vs system-created
- Made user do manual work that's automated

## Scenario 4: Application vs Component
**Question:** "5 repos that deploy together - how many Applications and Components?"

**Agent Response:** 1 Application, 5 Components (CORRECT!)

**Success:** This one was answered correctly! Agent understood the grouping relationship.

## Scenario 5: Resource Flow
**Question:** "What resources get created when I push code?"

**Agent Response:** Mentioned "BuildConfig" (OpenShift-specific, not Konflux), mixed terminology
**Issues:**
- Used OpenShift BuildConfig instead of Tekton PipelineRun
- Component is pre-created, not created on push
- Correct that Snapshot gets created
- Didn't mention Integration Service role

**Failure Analysis:**
- Mixed OpenShift and Konflux concepts
- Unclear on which resources are pre-existing vs created on-push

## Scenario 6: Security Scanning
**Question:** "IntegrationTestScenario, custom build pipeline, or Release pipeline task for security scans?"

**Agent Response:** IntegrationTestScenario (CORRECT!)

**Success:** Agent correctly identified IntegrationTestScenario and reasoning was sound.

## Key Patterns Identified

### Critical Gaps (Need to Address)
1. **User-created vs System-created resources** - Agents don't know which resources they create vs which Konflux creates automatically
2. **Namespace placement rules** - Wrong placement of ReleasePlan/ReleasePlanAdmission
3. **Snapshot lifecycle** - Fundamental misunderstanding of automatic creation
4. **Resource naming** - Inventing non-existent resource names
5. **Konflux vs OpenShift/Kubernetes terminology** - Mixing concepts from different platforms

### What Agents Got Right
1. Application/Component relationship (1 app, many components)
2. IntegrationTestScenario for testing
3. General understanding of CI/CD flow concepts

## Skill Must Address

1. **Clear table of all Konflux CRDs** with:
   - Resource name
   - Purpose
   - Who creates it (user or system)
   - Which namespace it belongs in

2. **Decision tree for "which resource do I need?"**

3. **Common confusions explicitly called out:**
   - Snapshots are auto-created, NOT user-created
   - ReleasePlan (tenant) vs ReleasePlanAdmission (managed)
   - Component vs Application distinction

4. **Resource lifecycle flows** showing what happens when code is pushed

5. **Namespace placement rules**
