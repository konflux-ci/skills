# Baseline Test Scenarios for understanding-konflux-resources

These scenarios test whether an agent can correctly understand and apply Konflux resource concepts WITHOUT having access to a reference skill.

## Scenario 1: Resource Selection (Recognition Test)

**Pressure type:** Ambiguity + Time pressure

**Scenario:**
```
User: "I need to build my frontend app from the main branch of my repo. What Konflux resource should I create?"

Expected correct answer: Component CR
Common errors without skill:
- Suggesting Application (too high-level)
- Suggesting Snapshot (wrong - snapshots are created automatically)
- Suggesting PipelineRun (too low-level, Konflux manages this)
```

## Scenario 2: Namespace Confusion (Application Test)

**Pressure type:** Similar concepts + Typical confusion

**Scenario:**
```
User: "I want to set up a release pipeline with credentials. Should I create the ReleasePlan in my tenant namespace or managed namespace?"

Expected correct answer:
- ReleasePlan goes in tenant namespace
- ReleasePlanAdmission (with credentials) goes in managed namespace
- Release CR references the plan

Common errors without skill:
- Putting everything in one namespace
- Not understanding tenant vs managed separation
- Confusing where credentials belong
```

## Scenario 3: Snapshot Lifecycle (Gap Test)

**Pressure type:** Implied action + Assumed knowledge

**Scenario:**
```
User: "I just committed new code to my component. Do I need to create a new Snapshot now?"

Expected correct answer: No - Integration Service creates snapshots automatically after successful builds

Common errors without skill:
- Saying yes, user needs to create snapshot
- Not knowing snapshots are auto-created
- Confusing manual vs automatic resource creation
```

## Scenario 4: Application vs Component (Common Confusion)

**Pressure type:** Similar terms + Real-world complexity

**Scenario:**
```
User: "I have a microservices app with 5 repos: frontend, backend, auth-service, data-service, and queue-worker. Each builds separately but they deploy together. How many Applications and Components do I need?"

Expected correct answer:
- 1 Application (groups the coherent set)
- 5 Components (one per repo/build artifact)

Common errors without skill:
- Creating 5 Applications
- Creating 1 Component
- Not understanding the grouping relationship
```

## Scenario 5: Resource Relationships (Integration Test)

**Pressure type:** Complex workflow + Multiple resources

**Scenario:**
```
User: "Walk me through what Konflux resources get created when I push code to my component's repo."

Expected correct flow:
1. Component exists (pre-created by user)
2. Push triggers PipelineRun (auto-created by Build Service)
3. PipelineRun builds artifact
4. Integration Service creates new Snapshot (auto)
5. Integration Service runs IntegrationTestScenarios (if configured)
6. User can create Release CR to release the snapshot

Common errors without skill:
- Missing auto-created resources
- Wrong order of operations
- Not understanding which resources user creates vs system creates
```

## Scenario 6: When to Use What (Decision Tree Test)

**Pressure type:** Multiple valid-sounding options

**Scenario:**
```
User: "I want to run security scans on my builds. Do I need an IntegrationTestScenario, a custom build pipeline, or a Release pipeline task?"

Expected correct answer: IntegrationTestScenario - it's a test against the snapshot

Common errors without skill:
- Suggesting custom build pipeline (wrong - tests run after build)
- Suggesting Release pipeline task (wrong phase)
- Not understanding the build→test→release separation
```

## Success Criteria

For each scenario, agent should:
- ✅ Choose correct resource type
- ✅ Explain why (demonstrates understanding)
- ✅ Note what user creates vs system creates
- ✅ Understand namespace placement where relevant

## Testing Protocol

1. Run each scenario with FRESH subagent (no conversation history)
2. Document exact responses verbatim
3. Identify rationalization patterns
4. Note what information agent lacks or gets wrong
5. Use findings to build the skill
