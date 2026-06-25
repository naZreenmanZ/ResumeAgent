# Issue 008: PDF Export And Approval Workflow

Type: AFK

Blocked by: Issue 007

User stories covered: 24, 25, 26, 30, 31, 40

## What to build

Add a polished PDF export and approval workflow to the UI. The user should be able to export the tailored resume, open the generated PDF, verify the exact file path, and approve it for upload.

The approval state should be stored so the Application Flow can refuse to upload an unapproved or stale resume.

## Acceptance criteria

- [ ] The user can export a tailored resume to PDF from the UI.
- [ ] The generated PDF path is displayed clearly.
- [ ] The user can open or preview the generated PDF.
- [ ] The UI records whether the current resume PDF is approved for upload.
- [ ] Approval is invalidated when the tailored draft changes.
- [ ] The Application Flow cannot proceed to upload without an approved PDF unless explicitly overridden.
- [ ] Tests cover export success and approval invalidation.
