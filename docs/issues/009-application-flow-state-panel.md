# Issue 009: Application Flow State Panel

Type: HITL

Blocked by: Issue 008

User stories covered: 26, 27, 28, 29, 30, 31, 41

## What to build

Build the Application Flow screen that guides portal application steps with explicit state. The first version should model the workflow even if some portal actions remain manual.

The screen should show current portal, job title, company, tailored resume path, detected browser event, next required action, and whether user input is needed.

## Acceptance criteria

- [ ] Application Flow supports states for not started, portal opened, login required, CV upload required, upload in progress, upload success, ready for submit, user approval required, submitted, already applied, failed, and manual action required.
- [ ] The exact approved PDF path is shown before upload.
- [ ] The submit action is visually distinct and requires explicit approval.
- [ ] Login-required state stops automation and asks the user to log in.
- [ ] Duplicate application state offers to mark the job as already applied.
- [ ] File upload blocked state shows manual file picker steps.
- [ ] Manual confirmation actions are available for "I selected the file" and "upload success shown."
