# Konflux Skills

Claude Code skills to help developers work with the [Konflux CI/CD platform](https://konflux-ci.dev).

## What Are These Skills?

Skills are reusable knowledge modules that Claude Code can automatically invoke to help you with Konflux-specific tasks. They provide quick reference materials, best practices, and patterns for common Konflux workflows.

## Available Skills

### understanding-konflux-resources

Provides quick reference for Konflux Custom Resources (Applications, Components, Snapshots, IntegrationTestScenarios, ReleasePlans, etc.):
- Which resource to use for different tasks
- Who creates each resource (user vs system)
- Where resources belong (tenant vs managed namespace)
- Common confusions and how to avoid them

## Installation

First, add the konflux-skills marketplace (one-time setup):

```bash
claude marketplace add https://github.com/konflux-ci/skills.git
```

Then install the skill you want:

```bash
claude skill install konflux-skills:understanding-konflux-resources
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
