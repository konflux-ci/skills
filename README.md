# Konflux Skills

Claude Code skills to help developers work with the [Konflux CI/CD platform](https://konflux-ci.dev).

## What Are These Skills?

Skills are reusable knowledge modules that Claude Code can automatically invoke to help you with Konflux-specific tasks. They provide quick reference materials, best practices, and patterns for common Konflux workflows.

## Available Skills

### debugging-pipeline-failures

Systematic approach to investigate Konflux Tekton pipeline failures:
- Debug PipelineRun and TaskRun issues
- Analyze build failures and CI/CD workflow problems
- Use kubectl commands for comprehensive root cause analysis
- Resolve common pipeline states (Pending, Failed, stuck Running)

### navigating-github-to-konflux-pipelines

Find Konflux pipeline information from GitHub PR or branch checks:
- Identify Konflux checks and filter out Prow/SonarCloud
- Extract PipelineRun URLs from build and integration test checks
- Parse URLs to get cluster, namespace, and PipelineRun names for kubectl debugging
- Navigate from GitHub UI to Konflux pipeline details

### understanding-konflux-resources

Quick reference for Konflux Custom Resources:
- Which resource to use for different tasks (Application, Component, Snapshot, etc.)
- Who creates each resource (user vs system)
- Where resources belong (tenant vs managed namespace)
- Common confusions about ReleasePlans, ReleasePlanAdmissions, and IntegrationTestScenarios

### working-with-provenance

Trace Konflux builds from container images back to source:
- Extract provenance attestations from container images
- Find build logs and PipelineRun details from image references
- Verify source commits for deployed containers
- Navigate from artifacts back to builds and source code

### component-build-status

Trigger build of Konflux Component:
- Trigger build of a component
- Wait for release to finish
- Instruct Claude to perform nudging
- Get status of a Component or Application

## Installation

First, add the konflux-skills marketplace (one-time setup):

```bash
claude marketplace add https://github.com/konflux-ci/skills.git
```

Then install individual skills:

```bash
claude skill install konflux-skills:<skill-name>
```

Or install all Konflux skills at once:

```bash
claude skill install konflux-skills
```

## Usage

Once installed, Claude Code will automatically discover and use these skills when you ask Konflux-related questions. No special commands required - just ask naturally:

- "Which Konflux resource should I use to build a container from my Git repository?"
- "Where do I create a ReleasePlan in Konflux?"
- "How are Snapshots created in Konflux?"

## Contributing

Want to contribute a new skill or improve an existing one? See [CLAUDE.md](CLAUDE.md) for development guidelines, testing standards, and the test-driven development process we follow.

## Documentation

- **Project guidelines:** [CLAUDE.md](CLAUDE.md)
- **Testing details:** [TESTING.md](TESTING.md)
- **Konflux documentation:** [konflux-ci.dev/docs](https://konflux-ci.dev/docs/)

## License

Apache 2.0
