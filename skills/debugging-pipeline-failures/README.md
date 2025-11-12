# Debugging Pipeline Failures Skill

A systematic approach to investigating and resolving Konflux Tekton pipeline failures using standard Kubernetes and Tekton tools.

## What This Skill Does

This skill teaches Claude Code to:
- **Follow systematic methodology** - 5-phase investigation process from identification to root cause
- **Use standard tools** - kubectl and Tekton CLI commands for debugging
- **Correlate multiple sources** - Logs, events, and resource states for complete picture
- **Distinguish cause from symptom** - Identify root causes, not just surface-level issues
- **Provide actionable guidance** - Specific kubectl commands and troubleshooting steps

## When to Use

Invoke this skill when dealing with:
- Failed PipelineRuns or TaskRuns in Konflux
- Build failures or test errors
- Stuck or hanging pipelines
- Image pull issues (ImagePullBackOff)
- Resource exhaustion (OOMKilled, quota errors)
- Timeout failures
- Workspace or volume mount problems
- ServiceAccount permission errors

## Key Features

### Systematic 5-Phase Methodology

1. **Identify Failed Component** - Find which PipelineRun/TaskRun failed
2. **Log Analysis** - Extract error messages from failed steps
3. **Event Correlation** - Match Kubernetes events to failure timeline
4. **Resource Inspection** - Examine YAML configurations for issues
5. **Root Cause Analysis** - Correlate findings to identify actual cause

### Common Failure Patterns

Pre-built investigation workflows for:
- Image pull failures (wrong image, registry auth)
- Resource exhaustion (memory, CPU, quota)
- Build script failures (exit codes, missing tools)
- Timeout issues (slow operations, hangs)
- Workspace/volume problems (PVC, mounts)
- Permission errors (RBAC, ServiceAccount)

### Standard Tool Usage

Uses kubectl and Tekton commands anyone can run:
```bash
kubectl get pipelinerun <name> -n <namespace>
kubectl logs <pod> -c step-<name> -n <namespace>
kubectl get events -n <namespace>
kubectl describe taskrun <name> -n <namespace>
```

No special tools or MCP servers required.

## Example Usage

### Basic Pipeline Failure

```
User: "My PipelineRun 'app-build-123' in namespace 'dev' failed. How do I debug it?"

Claude (with skill):
1. Check PipelineRun status: kubectl describe pipelinerun app-build-123 -n dev
2. Identify failed TaskRun from status
3. Get logs: kubectl logs <pod> -c step-<failed-step> -n dev
4. Check events: kubectl get events -n dev
5. Correlate to find root cause
6. Provide specific fix based on error found
```

### ImagePullBackOff Error

```
User: "Getting ImagePullBackOff in my build pipeline."

Claude (with skill):
1. Describe pod to see events: kubectl describe pod <pod> -n <namespace>
2. Check exact error message in events
3. Verify image name and tag
4. Check ServiceAccount imagePullSecrets
5. Provide fix (correct image name, add secret, etc.)
```

### Stuck Pipeline

```
User: "Pipeline running for 2 hours, should be done by now."

Claude (with skill):
1. List TaskRuns: kubectl get taskruns -l tekton.dev/pipelineRun=<name> -n <ns>
2. Identify which TaskRun is running/pending
3. Get logs from running TaskRun to see progress
4. Check if stuck (no new output) or slow (making progress)
5. Recommend timeout increase if legitimate, or investigate hang
```

## What Makes This Skill Different

### Systematic vs Ad-Hoc
- ✅ Follows repeatable 5-phase process
- ✅ Correlates multiple data sources
- ❌ Not random "try this" suggestions

### Root Cause Focus
- ✅ Investigates before recommending fixes
- ✅ Distinguishes symptoms from causes
- ❌ Not quick fixes without understanding

### General Purpose
- ✅ Uses standard kubectl/Tekton tools
- ✅ Works in any Konflux environment
- ❌ No special tools required

## Skill Quality

- **Format**: Follows konflux-ci/skills conventions
- **Testing**: 6 comprehensive test scenarios
- **TDD Approach**: Built using Test-Driven Development for Documentation
- **Word Count**: ~950 words (under 1,000 technique skill target)
- **Tool Agnostic**: Uses standard Kubernetes/Tekton tools

## Integration with Konflux Workflows

This skill complements:
- Konflux CI/CD pipeline development
- Build troubleshooting
- Integration testing
- On-call incident response
- Developer self-service debugging

## Prerequisites

### Required Knowledge
- Basic Tekton concepts (PipelineRun, TaskRun)
- kubectl command familiarity
- Understanding of container/pod concepts

### Required Access
- kubectl access to Konflux namespace
- Permission to view PipelineRuns, TaskRuns, pods, events
- Access to pod logs

### Optional
- Tekton CLI (tkn) for enhanced troubleshooting
- OpenShift CLI (oc) if using OpenShift-based Konflux

## Common User Prompts

This skill works best with prompts like:

**Good**:
- "My PipelineRun 'component-build-xyz' in 'user-ns' failed"
- "Build stuck for 30 minutes, TaskRun 'build-step-abc'"
- "Getting ImagePullBackOff in pipeline 'deploy-prod'"
- "TaskRun shows OOMKilled, how do I fix it?"

**Less Optimal**:
- "Pipeline broken" (too vague)
- "Nothing works" (no specifics)
- "Help with Tekton" (not actionable)

## Related Skills

Complements existing Konflux skills:
- `understanding-konflux-resources` - For resource basics
- Other pipeline or CI/CD skills in the repository

## Contributing

Improvements welcome:
- Additional failure patterns
- Enhanced decision trees
- More kubectl examples
- Platform-specific tips (EKS, GKE, OpenShift)

## License

Same as parent repository (Apache 2.0).

## Authors

**Gjorgji Georgievski** (ggeorgie@redhat.com)

Systematic debugging methodology based on SRE best practices and real-world Konflux troubleshooting experience.

## Version History

- **1.0.0** - Initial skill creation
  - 5-phase investigation methodology
  - 6 common failure patterns with kubectl commands
  - Root cause vs symptom distinction
  - Decision tree and troubleshooting workflow
  - Test-driven development with 6 scenarios
