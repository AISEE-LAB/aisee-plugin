# Knowledge Curation Batch: <title>

_Date: YYYY-MM-DD_
_Status: draft_

## Scope

- Project:
- Candidate sources:
- Team knowledge config:
- Reviewer:

## Summary

| Metric | Count |
|---|---:|
| Candidates reviewed | 0 |
| Draft cards | 0 |
| Deduplicated | 0 |
| Rejected | 0 |
| Needs more evidence | 0 |

## Draft Cards

### <card-id>

```yaml
id: <card-id>
title: <title>
status: candidate
applies_to:
  stacks: []
  frameworks: []
  phases: []
  schemas: []
  surfaces: []
trigger:
  - <observable condition>
recommended_action:
  - <actionable rule>
boundaries:
  - <when not to apply>
```

Review info:

```yaml
risk_types: []
tags: []
evidence:
  - type:
    repo:
    path:
sensitive_information_check:
  - no_secrets: yes
  - no_customer_data: yes
  - generalized_project_details: yes
dedupe:
  status: unique | merged | duplicate | stale-candidate
  notes:
```

## Deduplicated Candidates

| Candidate | Reason | Kept As |
|---|---|---|

## Rejected Candidates

| Candidate | Reason | Follow-up |
|---|---|---|

## Sensitive Information Review

- [ ] No secrets, tokens, cookies, production credentials, customer data, or private URLs.
- [ ] Project-specific names are generalized or explicitly marked project-only.
- [ ] No solution doc body was copied into card text.

## Recommended Next Step

- [ ] Keep as project-local candidates.
- [ ] Ask user for authorization to write drafts into team knowledge worktree.
- [ ] Prepare a batch PR after 3-10 reusable cards are ready.
