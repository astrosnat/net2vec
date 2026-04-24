<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Principle 1 placeholder -> I. Complexity Under Four
- Principle 2 placeholder -> II. SOLID Design
- Principle 3 placeholder -> III. Separation of Concerns
- Principle 4 placeholder -> IV. Testable Agent-Facing Behavior
- Principle 5 placeholder -> V. Explicit Data and Integration Boundaries
Added sections:
- Engineering Constraints
- Delivery Workflow
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md
- ✅ .specify/templates/tasks-template.md
- ✅ .specify/templates/agent-file-template.md
- ✅ .specify/templates/checklist-template.md
- ✅ .specify/templates/commands/*.md (directory not present)
Follow-up TODOs:
- None
-->
# net2vec Constitution

## Core Principles

### I. Complexity Under Four
Every function or method MUST keep cyclomatic complexity below 4, meaning the
measured value MUST be 3 or less. Code that needs additional branching MUST be
split into smaller named units before it is merged. Exceptions require an
explicit justification in the implementation plan and a follow-up refactoring
task. Rationale: net2vec exists to make agent workflows easier to reason about;
small decision surfaces reduce hidden behavior and review cost.

### II. SOLID Design
Production code MUST follow SOLID design principles. Each module, class, and
service MUST have one clear reason to change, depend on abstractions where a
boundary is meaningful, and remain open to extension without modifying stable
callers. Feature work MUST document any intentional SOLID tradeoff in the plan
before implementation. Rationale: the project will connect ingestion,
embedding, storage, and agents; stable contracts prevent these areas from
becoming tightly coupled.

### III. Separation of Concerns
Web ingestion, parsing, embedding, vector persistence, retrieval, agent-facing
interfaces, and orchestration MUST remain separated by explicit module
boundaries. Business rules MUST NOT be hidden in CLI handlers, framework glue,
or infrastructure adapters. Shared utilities MUST be introduced only when they
remove real duplication across at least two callers. Rationale: clear
boundaries let features evolve independently and keep agent integration code
auditable.

### IV. Testable Agent-Facing Behavior
Every behavior that changes what an agent can retrieve, call, or rely on MUST
have an independently executable test or validation step. Tests MUST cover
normal behavior, relevant edge cases, and contract expectations at module
boundaries. New features MUST be delivered in independently testable increments
that preserve existing agent-facing behavior unless a breaking change is
explicitly approved. Rationale: agents amplify small regressions, so observable
behavior needs direct verification.

### V. Explicit Data and Integration Boundaries
Data schemas, embedding inputs, embedding outputs, vector identifiers, and
external integration contracts MUST be explicit and version-aware. Code MUST
validate data crossing a boundary before using it. Changes that alter stored
data, retrieval semantics, or external contracts MUST include a migration or
compatibility plan. Rationale: net2vec depends on reliable movement from web
text to embeddings to agent consumption.

## Engineering Constraints

- New code MUST keep cyclomatic complexity below 4 per function or method.
- SOLID and separation-of-concerns compliance MUST be reviewed during planning
  and code review.
- Public boundaries MUST use typed, documented contracts appropriate to the
  language and framework in use.
- Infrastructure concerns such as logging, persistence, HTTP access, and
  embedding providers MUST be isolated behind adapters or service boundaries.
- Error handling MUST preserve useful diagnostic context without leaking secrets
  or coupling callers to provider-specific failure shapes.

## Delivery Workflow

- Plans MUST include a Constitution Check that covers complexity, SOLID design,
  separation of concerns, testability, and data or integration boundaries.
- Specifications MUST define measurable behavior and identify any data or
  integration contracts affected by the feature.
- Tasks MUST be grouped into independently testable increments and include
  explicit quality tasks for complexity review, boundary review, and contract
  validation.
- Reviews MUST block changes that exceed the complexity limit, blur established
  boundaries, or introduce untested agent-facing behavior.
- Any approved exception MUST include the reason, the rejected simpler
  alternative, and a dated follow-up task.

## Governance

This constitution supersedes conflicting project practices. Amendments require
a written rationale, an impact review of templates and runtime guidance, and an
updated Sync Impact Report in this file. Versioning follows semantic versioning:
MAJOR for incompatible governance or principle changes, MINOR for added or
materially expanded principles or sections, and PATCH for clarifications that do
not change obligations.

All implementation plans, specifications, task lists, and code reviews MUST
verify compliance with the current constitution. Reviewers MUST treat the
complexity limit, SOLID adherence, separation of concerns, testable
agent-facing behavior, and explicit boundary contracts as required gates.

**Version**: 1.0.0 | **Ratified**: 2026-04-24 | **Last Amended**: 2026-04-24
