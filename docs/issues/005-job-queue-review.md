# Issue 005: Job Queue Review

Type: AFK

Blocked by: Issue 001, Issue 002

User stories covered: 5, 6, 7, 8, 10, 15, 16, 24

## What to build

Build the Job Queue screen so the user can review discovered roles before resume tailoring or application planning. The queue should prioritize fast scanning, filtering, duplicate awareness, and clear status.

Each job should show title, company, location, portal, discovered date, relevance score, matched skills, region, selected base resume type, duplicate/applied status, and current workflow state.

## Acceptance criteria

- [ ] Queue loads jobs from the backend.
- [ ] Jobs can be filtered by portal, location/region, score, status, resume type, and date discovered.
- [ ] Duplicate or already-applied jobs are clearly marked.
- [ ] The selected base resume type is visible for each job.
- [ ] The user can open job detail, skip a job, or start tailoring from the queue.
- [ ] The layout uses a dense table or table-like list rather than decorative cards.
