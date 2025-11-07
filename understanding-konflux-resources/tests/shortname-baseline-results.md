# Baseline Test Results: Shortname Discovery

**Test Date:** 2025-11-07
**Skill Version:** 1.0.0 (before shortname additions)
**Hypothesis:** Without shortnames in description/keywords, agents won't load skill when users use abbreviations

## Test 1: "RP" Abbreviation

**User Prompt:** "I'm confused about where to create my RP - should it go in the tenant namespace or managed namespace?"

### Agent Behavior

**Skills Loaded:** None

**Interpretation of "RP":**
> "I initially interpreted 'RP' as potentially ambiguous. In the context of Konflux, I did not have an immediate clear mapping for this acronym. Possible interpretations could include:
> - Release Pipeline
> - Resource Placement
> - Resource Profile
> - Resource Provision"

**Response Given:**
> "I apologize, but could you clarify what 'RP' stands for in your context? In Konflux, resources like Application, Component, and Snapshot are typically created, but I want to ensure I understand exactly which resource type you're asking about."

**Confidence Level:** Low

### Analysis

❌ **FAILURE:** Agent did not load `understanding-konflux-resources` skill
❌ **FAILURE:** Agent did not recognize "RP" as ReleasePlan
❌ **FAILURE:** Agent asked for clarification instead of using skill content

**Expected Behavior:**
- Load understanding-konflux-resources skill (not loaded)
- Recognize RP = ReleasePlan (not recognized)
- Answer from line 34 of SKILL.md: "ReleasePlan goes in Tenant namespace, ReleasePlanAdmission goes in Managed namespace"

**Root Cause:** Skill description mentions "ReleasePlans" but not "RP" - no search trigger for abbreviation

---

## Test 2: "ITS" Abbreviation

**User Prompt:** "My ITS is not running after builds complete. I have the Component and Application set up. What am I missing?"

### Agent Behavior

**Skills Loaded:** None

**Interpretation of "ITS":**
> "I interpret 'ITS' as an abbreviation for 'Integration Test Scenario' based on the context of Konflux resources."

**Response Given:**
> Generic troubleshooting advice including:
> - Check resource relationships
> - Verify ITS spec configuration
> - RBAC/permission checks
> - kubectl diagnostic commands

**Confidence Level:** Moderate

### Analysis

❌ **FAILURE:** Agent did not load `understanding-konflux-resources` skill
⚠️ **PARTIAL:** Agent correctly guessed "ITS" = IntegrationTestScenario (from general knowledge)
❌ **FAILURE:** Agent did not use skill-specific troubleshooting content from lines 227-230

**Expected Behavior:**
- Load understanding-konflux-resources skill (not loaded)
- Use troubleshooting content from SKILL.md line 227-230:
  - "IntegrationTestScenario must exist before build completes"
  - "Check scenario references correct Application"
  - "Verify Tekton pipeline referenced by scenario exists"

**Root Cause:** Even when agent guessed shortname correctly, skill wasn't triggered because:
1. Description says "IntegrationTestScenarios" not "ITS"
2. Keywords section (line 233) doesn't include "ITS"

---

## Pattern Analysis

### Discovery Failures

**Both tests show:**
1. Skill never loaded organically when shortnames used
2. Description field only has full resource names
3. Keywords section lacks abbreviations
4. Agents either:
   - Don't recognize shortname (RP)
   - Recognize it but don't load skill (ITS)

### CSO (Claude Search Optimization) Gaps

Current description (line 3):
```
description: Use when working with Konflux CI and need to understand Applications,
Components, Snapshots, IntegrationTestScenarios, ReleasePlans, or namespace placement
```

**Missing triggers:**
- RP, RPA, ITS abbreviations
- Common shorthand users actually type
- Abbreviation context ("RP abbreviation", "ITS shortname")

Current keywords (line 233):
```
Konflux resources, Custom Resource Definition, CRD, Application CR, Component CR,
Snapshot lifecycle, IntegrationTestScenario, ReleasePlan, ReleasePlanAdmission...
```

**Missing keywords:**
- RP, RPA, ITS, App, Comp
- "shortname", "abbreviation", "acronym"

---

## Conclusion: GREEN Phase Requirements

To fix discovery failures, need to add shortnames to:

1. **Description field** - Add "common abbreviations (RP, RPA, ITS)" to trigger list
2. **Keywords section** - Add all abbreviations: RP, RPA, ITS, App, Comp
3. **Document body** - Use parenthetical annotations like "ReleasePlan (RP)" on first mention
4. **Quick Reference table** - Add abbreviation column

This will improve CSO so agents:
- Find skill when users type shortnames
- Recognize which resource is referenced
- Provide accurate answers from skill content
