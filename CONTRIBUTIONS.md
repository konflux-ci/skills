# Contributing to Konflux CI Skills Repository

This guide explains how to contribute skills to the Konflux CI skills repository at https://github.com/konflux-ci/skills.

---

## 📋 Pre-Submission Checklist

Before submitting your skill, ensure:

- ✅ **SKILL.md** exists with proper YAML frontmatter
- ✅ **README.md** exists with skill documentation
- ✅ **tests/scenarios.yaml** exists with 3-6 test scenarios
- ✅ **tests/README.md** exists documenting the test suite
- ✅ All tests pass locally
- ✅ Skill follows naming conventions (kebab-case, gerund for technique skills)
- ✅ Frontmatter is under 1,024 characters
- ✅ Skill content is under word limit (technique: <1,000 words)
- ✅ Schema validation passes (`claudelint`)

---

## 🚀 Step-by-Step Contribution Process

### 1. Fork the Konflux Skills Repository

```bash
# Navigate to https://github.com/konflux-ci/skills
# Click "Fork" button in the top right
# Clone your fork
git clone https://github.com/YOUR-USERNAME/skills.git
cd skills
```

### 2. Create a Feature Branch

```bash
git checkout -b add-your-skill-name
```

### 3. Copy Your Skill

```bash
# Copy your skill directory to the skills repository
cp -r /path/to/your-skill /path/to/skills/

# Verify structure
cd /path/to/skills/your-skill
ls -la
# Should show: SKILL.md, README.md, tests/
```

### 4. Update marketplace.json

Add your skill to `.claude-plugin/marketplace.json`:

```bash
cd /path/to/skills
vi .claude-plugin/marketplace.json
```

Add this entry to the `plugins` array:

```json
{
  "name": "your-skill-name",
  "source": "./your-skill-name",
  "description": "Brief description of what your skill does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

**Important**:
- Ensure JSON syntax is valid (no trailing commas)
- Source path must start with `./`
- Keep description concise but comprehensive

### 5. Validate Your Skill

```bash
# Run linter (requires Docker)
make validate

# Expected output: ✓ Validation passed!
```

**Docker Required**: The validation uses Docker to run claudelint. Install Docker Desktop:
```bash
brew install --cask docker
# Start Docker Desktop app before running make validate
```

### 6. Run Tests Locally

```bash
# Run all tests
make test

# Or test just your skill
make test-only SKILL=your-skill-name

# Generate test results (optional)
make generate SKILL=your-skill-name
```

**All tests must pass before submission.**

### 7. Review Compliance

Check your skill against Konflux requirements:

**YAML Frontmatter:**
```yaml
---
name: your-skill-name  # kebab-case, matches directory
description: Use when [trigger]... [explanation]  # Starts with "Use when"
---
```

**Naming Convention:**
- ✅ **Technique skills**: Use gerunds (debugging, optimizing, monitoring)
- ✅ **Reference skills**: Use nouns (understanding, concepts, architecture)

**Word Count:**
```bash
# Check word count
wc -w your-skill-name/SKILL.md
# Technique skills: <1,000 words
# Reference skills: <1,500 words
```

**Frontmatter Character Count:**
```bash
# Extract and count frontmatter
sed -n '/^---$/,/^---$/p' your-skill-name/SKILL.md | wc -c
# Must be <1,024 characters
```

### 8. Commit Your Changes

```bash
git add your-skill-name/
git add .claude-plugin/marketplace.json

git commit -m "Add your-skill-name skill

- Key feature 1
- Key feature 2
- Key feature 3
- Comprehensive test suite with X scenarios
"
```

**Commit Message Guidelines:**
- First line: Brief summary (imperative mood)
- Blank line
- Bullet points: Key features/changes
- Keep it concise but informative

### 9. Push to Your Fork

```bash
git push origin add-your-skill-name
```

### 10. Create Pull Request

1. Navigate to https://github.com/YOUR-USERNAME/skills
2. Click "Compare & pull request" button
3. Fill in PR template:

```markdown
## Skill: your-skill-name

### Description
Brief description of what your skill does.

### Type
- [x] New skill
- [ ] Skill enhancement
- [ ] Bug fix

### Checklist
- [x] SKILL.md with proper frontmatter
- [x] README.md with documentation
- [x] Test scenarios (X scenarios)
- [x] Tests pass locally
- [x] Schema validation passes
- [x] Word count within limits
- [x] Frontmatter under 1,024 characters

### Key Features
- Feature 1
- Feature 2
- Feature 3

### Testing
All X test scenarios pass:
- Test scenario 1
- Test scenario 2
- Test scenario 3
```

### 11. Respond to Review Feedback

Maintainers may request changes:

**Common feedback:**
- Reduce word count
- Improve test scenarios
- Clarify description
- Fix schema validation errors
- Improve examples

**How to address:**
```bash
# Make changes locally
vi your-skill-name/SKILL.md

# Re-validate
make validate
make test-only SKILL=your-skill-name

# Commit and push
git add your-skill-name/
git commit -m "Address review feedback: [specific changes]"
git push origin add-your-skill-name
```

---

## 📝 Skill Quality Guidelines

### Description (Frontmatter)

**Must:**
- Start with "Use when..."
- Include specific trigger conditions
- Be written in third person
- Be under 1,024 characters total (entire frontmatter)

**Example:**
```yaml
description: Use when investigating Kubernetes pod failures, crashes, resource issues, or service degradation. Provides systematic investigation methodology for incident triage, root cause analysis, and remediation planning in any Kubernetes environment.
```

### Content Structure

**Essential Sections:**
1. **Overview** - Core principles, abbreviations
2. **When to Use** - Clear trigger conditions
3. **Quick Reference** - Tables for fast lookup
4. **Common Confusions** - ✗/✓ examples
5. **Decision Tree** - Q&A navigation
6. **Rules/Guidelines** - Categorized lists
7. **Real-World Examples** - Practical scenarios
8. **Keywords for Search** - Comma-separated terms

**Formatting:**
- Use `**bold**` for critical terms
- Use ✓ and ✗ for correct/incorrect
- Use backticks for `technical-terms`
- Use tables with `|` separators
- Use `**CRITICAL:**` for important warnings

### Test Scenarios

**Requirements:**
- 3-6 scenarios minimum
- Each tests specific skill aspect
- Includes baseline failure documentation
- Uses realistic user prompts
- Has clear expected outputs

**Example:**
```yaml
- name: descriptive-test-name
  description: What this validates
  prompt: "Realistic user query"
  model: haiku  # or sonnet
  samples: 3
  expected:
    contains_keywords:
      - keyword1
      - keyword2
  baseline_failure: What happens without skill
```

---

## 🔍 Common Issues and Solutions

### Issue: Schema Validation Fails

**Error:**
```
SKILL.md: Invalid frontmatter format
```

**Solution:**
1. Ensure frontmatter starts and ends with `---`
2. Check YAML syntax (no tabs, proper indentation)
3. Validate required fields: `name`, `description`
4. Run `make validate` for specific errors

### Issue: Tests Fail

**Error:**
```
Test 'test-name' failed: missing keyword 'expected-keyword'
```

**Solution:**
1. Update SKILL.md to include missing concepts
2. Or refine test expectations if too strict
3. Re-run tests to validate
4. Check baseline failure is documented

### Issue: Word Count Exceeded

**Error:**
```
SKILL.md: 1,234 words (limit: 1,000 for technique skills)
```

**Solution:**
1. Remove redundant examples
2. Consolidate similar sections
3. Move detailed info to README.md
4. Use tables instead of paragraphs
5. Keep only essential content in SKILL.md

### Issue: Marketplace.json Invalid

**Error:**
```
Error parsing marketplace.json: trailing comma
```

**Solution:**
1. Remove trailing commas from JSON
2. Validate JSON syntax online
3. Ensure source paths start with `./`
4. Check all required fields present

### Issue: Docker Not Installed

**Error:**
```
/bin/sh: docker: command not found
```

**Solution:**
```bash
# Install Docker Desktop for Mac
brew install --cask docker
# Start Docker Desktop app
# Then run: make validate
```

---

## ✅ Final Checklist Before PR

- [ ] Skill name follows conventions (kebab-case, gerund)
- [ ] SKILL.md has valid frontmatter (<1,024 chars)
- [ ] Content within word limits
- [ ] README.md is comprehensive
- [ ] 3-6 test scenarios with baseline failures
- [ ] Tests pass locally (`make test`)
- [ ] Schema validation passes (`make validate`)
- [ ] marketplace.json updated correctly
- [ ] Commit message is descriptive
- [ ] PR template filled completely
- [ ] No merge conflicts with main branch

---

## 🚀 Quick Command Reference

```bash
# Validate skill
make validate

# Run all tests
make test

# Test specific skill
make test-only SKILL=your-skill-name

# Generate test results
make generate SKILL=your-skill-name

# Check word count
wc -w your-skill-name/SKILL.md

# Validate JSON
python -m json.tool .claude-plugin/marketplace.json

# Check frontmatter size
sed -n '/^---$/,/^---$/p' your-skill-name/SKILL.md | wc -c
```

---

## 📚 Additional Resources

### Konflux Skills Repository
- **Main Repo**: https://github.com/konflux-ci/skills
- **Guidelines**: Read `CLAUDE.md` in the repository
- **Examples**: Study existing skills for patterns
- **Tests**: Review `test.py` for test framework

### Documentation
- **Skill Format**: Check existing skills for format examples
- **Testing**: Read `Makefile` for test commands
- **Validation**: See `.github/workflows/` for CI/CD

### Tools
- **claudelint**: Schema validation tool (runs via Docker)
- **make**: Build automation
- **Python 3.8+**: For test runner

---

## 🤝 Community Guidelines

### Be Respectful
- Respond professionally to feedback
- Be patient with review process
- Help others by reviewing PRs

### Quality Over Quantity
- One high-quality skill > multiple rushed skills
- Take time to test thoroughly
- Iterate based on feedback

### Continuous Improvement
- Update skills based on user feedback
- Add test scenarios for edge cases
- Improve documentation clarity

---

## 📞 Getting Help

**Questions?**
- Check existing issues: https://github.com/konflux-ci/skills/issues
- Read CLAUDE.md in the repository
- Ask in PR comments
- Reach out to maintainers

**Found a Bug?**
- File an issue with details
- Include steps to reproduce
- Provide test output

---

## 🎉 After Your PR is Merged

1. **Update your fork**: Sync with upstream main
2. **Share the skill**: Tell your team about it
3. **Monitor feedback**: Watch for issues/suggestions
4. **Contribute more**: Consider adding related skills

---

**Good luck with your contribution! The Konflux CI Skills community appreciates your effort to improve Claude Code for everyone.** 🚀
