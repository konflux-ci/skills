# understanding-konflux-resources

## Purpose

Quick reference for Konflux CI/CD Custom Resources (CRs) - helps users understand which resource to use, who creates it, and where it belongs.

## Addresses Common Confusions

- Application vs Component (Component builds code, Application just groups)
- Snapshots are auto-created (never create manually)
- Namespace placement (ReleasePlan in tenant, ReleasePlanAdmission in managed)
- Resource lifecycle (what you create vs what Konflux creates)

## Testing

Tested with 6 pressure scenarios covering:
1. Resource selection (which CR to use for building)
2. Namespace placement (tenant vs managed)
3. Snapshot lifecycle (auto-creation)
4. Application/Component relationship (microservices)
5. Resource flow (code push workflow)
6. Integration testing (security scans)

All scenarios passing after iterative refinement.

## Key Features

- Quick reference table with "Who Creates" column
- Decision tree in Q&A format
- Common confusions with ❌/✅ format
- Real-world examples
- Troubleshooting section
- Keyword-rich for Claude Search Optimization

## Metrics

- Word count: 1297 words
- Frontmatter: 326 characters (< 1024 limit)
- Test coverage: 6/6 scenarios passing
