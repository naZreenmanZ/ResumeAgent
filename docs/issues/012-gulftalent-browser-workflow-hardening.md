# Issue 012: GulfTalent Browser Workflow Hardening

Type: HITL

Blocked by: Issue 009

User stories covered: 27, 28, 29, 30, 31, 37, 41

## What to build

Harden the GulfTalent application workflow using the Application Flow state model. The goal is to reliably detect login, edit-CV, upload success modal, duplicate application page, review page, submit button, and post-submit confirmation where the portal and browser automation surface allow it.

This issue requires live portal validation and should never attempt to bypass login protections, CAPTCHA, portal restrictions, or user approval.

## Acceptance criteria

- [ ] GulfTalent login redirects are detected and shown as login required.
- [ ] GulfTalent duplicate application pages can be marked as already applied locally.
- [ ] Upload success modal detection is implemented where observable.
- [ ] The flow stops before final submit until the user approves.
- [ ] The exact tailored PDF path is displayed when manual file selection is required.
- [ ] Successful submission or already-applied state updates the local tracker.
- [ ] A mock portal test page covers upload modal, duplicate, review, submit, and confirmation states before live testing.
