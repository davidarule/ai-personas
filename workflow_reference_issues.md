# Workflow Reference Issues

## Actual Workflow IDs
- wf0-feature-development
- wf1-bug-fix
- wf2-hotfix
- wf3-branch-creation
- wf4-code-commit
- wf5-pull-request-creation
- wf6-pull-request-review
- wf7-pull-request-response
- wf8-merge
- wf9-post-merge-monitoring
- wf10-conflict-resolution
- wf11-rollback
- wf12-work-item-update
- wf13-pr-readiness-check

## Issues Found

### In wf0-feature-development.yaml:
- References "branch-creation" → Should be "wf3-branch-creation"
- References "code-commit" → Should be "wf4-code-commit"
- References "pr-readiness-check" → Should be "wf13-pr-readiness-check"
- References "pull-request-creation" → Should be "wf5-pull-request-creation"
- References "pull-request-response" → Should be "wf7-pull-request-response"
- References "merge-workflow" → Should be "wf8-merge"
- References "post-merge-monitoring" → Should be "wf9-post-merge-monitoring"
- References "rollback-workflow" → Should be "wf11-rollback"

### In wf1-bug-fix.yaml:
- References "wf6-merge" → Should be "wf8-merge" (wf6 is pull-request-review)
- References "wf7-post-merge-monitoring" → Should be "wf9-post-merge-monitoring"
- References "wf9-rollback" → Should be "wf11-rollback"

### In wf2-hotfix.yaml:
- References "wf6-merge" → Should be "wf8-merge"
- References "wf7-post-merge-monitoring" → Should be "wf9-post-merge-monitoring"
- References "wf9-rollback" → Should be "wf11-rollback"

### In wf8-merge.yaml:
- References "wf8-conflict-resolution" → Should be "wf10-conflict-resolution"
- References "wf10-work-item-update" → Should be "wf12-work-item-update"