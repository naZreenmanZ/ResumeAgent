# ResumeAgent Implementation Issues

This folder contains the implementation backlog for ResumeAgent, derived from:

- [ResumeAgent PRD](../resume-agent-prd.md)
- [ResumeAgent UI/UX Guidelines](../ui-ux-guidelines.md)

The issues are written as vertical slices. Each one should produce something demoable or verifiable on its own.

## Backlog Order

1. [Local Web App Shell](001-local-web-app-shell.md)
2. [Backend API Around Existing CLI Engine](002-backend-api-around-existing-cli-engine.md)
3. [Dashboard Run Summary](003-dashboard-run-summary.md)
4. [Portal Settings And Scan Trigger](004-portal-settings-and-scan-trigger.md)
5. [Job Queue Review](005-job-queue-review.md)
6. [Job Detail And Match Explanation](006-job-detail-and-match-explanation.md)
7. [Tailored Resume Review And QA](007-tailored-resume-review-and-qa.md)
8. [PDF Export And Approval Workflow](008-pdf-export-and-approval-workflow.md)
9. [Application Flow State Panel](009-application-flow-state-panel.md)
10. [Tracker UI And Exports](010-tracker-ui-and-exports.md)
11. [Hourly Watcher And Notifications](011-hourly-watcher-and-notifications.md)
12. [GulfTalent Browser Workflow Hardening](012-gulftalent-browser-workflow-hardening.md)

## Slice Types

- `AFK`: Can be implemented without further product decisions.
- `HITL`: Needs human review, portal login, design approval, or live-portal validation.

## Implementation Notes

- Keep the app local-first.
- Keep personal files ignored by git.
- Preserve the human-in-the-loop approval model.
- Build against the Premium Career Command Center visual direction.
- Do not create unattended application submission unless full-auto mode is explicitly enabled.
