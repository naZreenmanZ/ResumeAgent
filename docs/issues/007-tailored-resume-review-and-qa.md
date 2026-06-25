# Issue 007: Tailored Resume Review And QA

Type: AFK

Blocked by: Issue 006

User stories covered: 17, 18, 19, 20, 21, 22, 23, 24, 40

## What to build

Build the Resume Review screen for inspecting tailored resume content before PDF export or upload. The view should compare job requirements against the tailored resume and run resume QA checks that catch employer-facing quality problems.

This slice should prevent the earlier issues where internal labels appeared in the final resume, professional experience was missing, or technical skills were not categorized.

## Acceptance criteria

- [ ] Resume Review shows the job requirements and tailored resume preview side by side.
- [ ] The tailored resume preview preserves employer-facing headings from the base resume.
- [ ] QA checks verify name/contact, Professional Summary, Professional Experience, company names, Technical Skills categories, Certifications & Achievements, Education, and Languages.
- [ ] QA checks flag forbidden internal labels such as Targeted Summary, Targeted Emphasis, Base Resume Content, bot notes, and Job URL.
- [ ] QA checks flag a role label or portal URL appearing immediately after the candidate name.
- [ ] Failed QA checks block approval by default.
- [ ] The user can regenerate or edit the tailored draft before approval.
