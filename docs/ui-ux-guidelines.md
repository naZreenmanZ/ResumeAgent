# ResumeAgent UI/UX Guidelines

## Product Experience Vision

ResumeAgent should feel like a calm job-search cockpit, not a noisy automation tool. The interface must help the user understand what the agent found, what it changed, what it is about to upload, and what still needs approval.

The product is personal, local-first, and human-in-the-loop. The UI should make automation feel controlled and inspectable rather than magical. Every screen should answer one of these questions:

- What jobs did the agent find?
- Why is this job relevant?
- Which resume will be used?
- What changed in the tailored resume?
- Has this job already been applied to?
- What action needs my approval?
- What happened after the portal interaction?

## Experience Principles

1. Keep the user in control.
   ResumeAgent may scan, prepare, tailor, and assist, but final application submission should remain clearly approved unless the user explicitly enables full-auto mode.

2. Make every automated decision explainable.
   Show relevance score, matched skills, blocked terms, region-based resume choice, duplicate status, and application state in plain language.

3. Protect personal data by design.
   Base resumes, tailored resumes, trackers, portal imports, and local config are private local artifacts. The UI should reinforce where files live and never imply they are being uploaded anywhere except the selected job portal.

4. Resume quality comes before application speed.
   The review flow must make it easy to catch missing headings, bad formatting, internal bot labels, incorrect company names, or an old CV before upload.

5. Treat portals as fragile external systems.
   Browser automation states must be explicit: logged out, upload needed, upload success, duplicate application, ready to submit, submitted, failed, or manual action required.

6. Design for repeat use.
   This is not a landing page. The main UI is an operational workspace for daily or hourly job search runs.

## Information Architecture

The app should use a compact sidebar or top-level navigation with these primary areas:

- Dashboard
- Job Queue
- Resume Review
- Application Flow
- Tracker
- Portals
- Settings

The Dashboard is the default first screen after setup. It should summarize current work, not sell the product.

## Core Screens

### Dashboard

Purpose: Show the current state of the job-search agent.

Key content:

- Last run time
- Next scheduled run, if enabled
- Jobs found today
- Jobs queued
- Resumes awaiting review
- Applications ready for portal action
- Submitted applications
- Duplicate or skipped jobs
- Portal warnings

Primary actions:

- Run scan now
- Prepare next resume
- Review queue
- Open tracker

Design notes:

- Use dense, readable status panels.
- Avoid large marketing-style hero sections.
- Surface warnings without making the page feel broken.

### Job Queue

Purpose: Let the user review and choose jobs before tailoring or applying.

Each job row/card should show:

- Job title
- Company
- Location
- Portal
- Posted/discovered date
- Relevance score
- Matched skills
- Region
- Selected base resume type: MENA photo or NP
- Duplicate/applied status
- Current state: new, queued, tailored, ready to apply, applied, skipped, failed

Primary actions:

- View details
- Tailor resume
- Skip
- Mark not relevant
- Open portal page

Filters:

- Portal
- Location/region
- Score range
- Status
- Resume type
- Date discovered

Design notes:

- Prefer a table with expandable detail over large decorative cards.
- Make duplicate/applied status impossible to miss.
- Use color sparingly: green for ready/submitted, amber for needs review, red for blocked/error, gray for skipped/duplicate.

### Job Detail

Purpose: Explain why ResumeAgent selected the role and what it will do next.

Sections:

- Job overview
- Job description
- Requirements
- Match analysis
- Resume selection
- Application history
- Portal notes

Match analysis should include:

- Skills matched
- Skills missing or weak
- Target title match
- Blocked keywords found, if any
- Reason for score

Primary actions:

- Generate tailored resume
- Regenerate tailored resume
- Open resume review
- Create application plan
- Skip job

### Resume Review

Purpose: Review the tailored resume before upload.

The review screen is one of the most important parts of the product. It must make employer-facing resume quality easy to inspect.

Required layout:

- Left side: job requirements and match summary
- Right side: tailored resume preview
- Optional lower panel: change summary

Required checks:

- Name and contact details present
- No role label or portal URL after the name
- Professional Summary present
- Professional Experience present
- Company names present
- Technical Skills categorized
- Certifications & Achievements present
- Education present and readable
- Languages present
- No internal labels such as Targeted Summary, Targeted Emphasis, Base Resume Content, bot notes, or Job URL

Primary actions:

- Approve for upload
- Regenerate
- Edit draft
- Export PDF
- Open PDF

Design notes:

- Show the final resume as close to PDF appearance as practical.
- The user should be able to compare “what the job asks for” against “what the resume now emphasizes.”
- Validation failures should block upload approval until resolved or consciously overridden.

### Application Flow

Purpose: Guide portal-specific application steps clearly.

State model:

- Not started
- Portal opened
- Login required
- CV upload required
- Upload in progress
- Upload success modal detected
- Ready for submit
- User approval required
- Submitted
- Already applied
- Failed
- Manual action required

For each state, show:

- Current portal
- Job title and company
- Tailored resume path
- Last detected browser event
- Next required action
- Whether user input is needed

Primary actions:

- Open portal
- Attach tailored CV
- Confirm upload completed
- Submit application
- Mark already applied
- Mark failed

Design notes:

- The submit button must be visually distinct and confirm intent.
- If the portal redirects to login, stop and ask the user to log in.
- If a duplicate page is detected, offer to mark the job as already applied.
- If file picker automation is unavailable, the UI should show the exact file path and manual selection steps.

### Tracker

Purpose: Provide the source of truth for applications.

Columns:

- Applied date
- Portal
- Job title
- Company
- Location
- Status
- Portal reference
- Resume PDF path
- Job URL
- Notes

Primary actions:

- Export CSV
- Export XLSX
- Open resume
- Open job URL
- Edit status

Statuses:

- queued
- tailored
- ready_to_apply
- applied
- already_applied
- skipped
- failed

Design notes:

- This screen should feel like a clean spreadsheet, not a report.
- Keep paths selectable/copyable.
- Show when tracker export last refreshed.

### Portals

Purpose: Manage which job portals are enabled and how they are scanned.

Portal fields:

- Name
- Enabled/disabled
- Adapter type
- Scan method
- Last scan result
- Last warning
- Login/session state, if known
- Notes

Adapter types:

- saved search import
- feed
- browser agent
- demo JSON
- setup required

Primary actions:

- Enable/disable portal
- Add portal
- Edit portal settings
- Import saved search file
- Test scan

Design notes:

- Make unsupported or setup-required portals clear without making them look like failures.
- Prefer “needs setup” over vague error messages.

### Settings

Purpose: Configure local behavior safely.

Sections:

- Base resume paths
- Runtime folders
- Target roles
- Target skills
- Locations/regions
- Blocked keywords
- Schedule
- Approval mode
- Privacy and git safety

Required settings:

- MENA resume path
- Non-MENA NP resume path
- Tailored resume folder
- Tracking folder
- Database path
- Scan interval
- Default application mode

Design notes:

- Use file pickers for paths when possible.
- Warn before enabling full-auto submit.
- Show whether required folders exist.

## Visual Design Direction

The approved direction is a Premium Career Command Center. The interface should feel polished, calm, and career-focused while still being serious enough for application tracking and resume review. It should feel accessible to an individual job seeker today and credible enough to evolve into a product others could use later.

Recommended style:

- Warm off-white or very light neutral background
- White or near-white work surfaces
- Dark readable text with softer secondary text
- Muted borders and subtle shadows used sparingly
- Navy or deep teal as the primary accent
- Green, amber, red, blue, and gray reserved for status meaning
- Clean typography with a slightly premium editorial feel
- Softer cards for summary panels, but dense tables for queues and trackers
- Guided flows for resume review and application approval
- Clear empty states that feel helpful, not decorative

Layout direction:

- Dashboard may use refined summary panels, but should remain operational.
- Job Queue and Tracker should prioritize tables, filtering, and fast scanning.
- Resume Review should use a polished split-pane workspace.
- Application Flow should feel like a guided checklist with strong state clarity.
- Settings should feel like a clean control panel, not a developer config file.

Personality:

- Calm
- Confident
- Polished
- Trustworthy
- Human-in-the-loop
- Career-focused

The UI should not feel like a generic AI tool. It should feel like a private workspace that helps the user make better career moves with less repetitive effort.

Avoid:

- Marketing landing-page layouts
- Oversized hero sections
- Decorative gradients
- Purple-heavy AI-tool styling
- Excessive rounded cards
- Floating cards inside cards
- Mascots or playful illustrations
- Raw terminal-style screens as the primary experience
- Hiding operational details behind vague AI language

Suggested color roles:

- Primary: action buttons, selected navigation, and key progress indicators
- Green: submitted, ready, upload success
- Amber: needs review, manual action required
- Red: failed, blocked, missing required data
- Blue: informational portal state
- Gray: skipped, duplicate, disabled

Suggested palette direction:

- Background: warm off-white
- Surface: white
- Primary accent: navy or deep teal
- Secondary accent: muted emerald
- Warning: amber
- Error: controlled red
- Borders: soft warm gray

Components:

- Use segmented controls for mode selection.
- Use toggles for portal enablement and schedule state.
- Use tabs for resume preview, change summary, and validation checks.
- Use status pills for application state.
- Use icon buttons with tooltips for quick actions such as open, export, copy, refresh, and settings.
- Use confirmation modals for upload, submit, full-auto mode, and duplicate override.

## Interaction Rules

### Approval

Any action that uploads a resume or submits an application must show:

- Job title
- Company
- Portal
- Resume PDF path
- Resume version
- Final action label

Final submit should require an explicit click such as “Submit application” and should not be hidden behind a generic “Continue” button.

### Resume Tailoring

Resume generation should be a visible pipeline:

1. Select base resume
2. Extract content
3. Tailor to JD
4. Validate required sections
5. Export PDF
6. Await approval

Validation warnings should be shown before upload.

### Duplicate Protection

When a job is already applied or looks like a duplicate:

- Disable apply actions by default.
- Show the matched previous application.
- Allow manual override only with a clear confirmation.

### Portal Failures

Portal errors should be recoverable and specific:

- Login required
- Selector changed
- File upload unavailable
- Upload confirmation not detected
- Duplicate application detected
- Portal scan failed

Avoid generic “Something went wrong” messages.

## Empty, Loading, And Error States

Empty queue:

- Show that no jobs are currently queued.
- Offer “Run scan now” and “Check portal settings.”

No tailored resumes:

- Show “No tailored resumes yet.”
- Offer to select a job from the queue.

Portal setup required:

- Explain which adapter information is missing.
- Offer to configure saved search import, feed, or browser settings.

Login required:

- Tell the user to log in in the browser.
- Keep the current job context visible.

Upload blocked:

- Show the tailored PDF path.
- Show manual file picker steps.
- Provide a “I selected the file” confirmation action.

## Content Style

Tone should be direct, calm, and specific.

Use:

- “Tailored resume ready”
- “Upload success detected”
- “Already applied on GulfTalent”
- “Login required before continuing”
- “Professional Experience missing”
- “Technical Skills are not categorized”

Avoid:

- “Magic apply”
- “AI is thinking”
- “Targeted Summary”
- “Bot output”
- “Base Resume Content”
- “Just trust the agent”

## Accessibility Requirements

- All controls must be keyboard accessible.
- Every icon-only button needs a tooltip and accessible label.
- Status must not rely only on color.
- Text must meet readable contrast.
- Tables need clear headers.
- Long paths should wrap or truncate with full value available on hover/copy.
- Modal dialogs must trap focus and support Escape to close unless an action is destructive.

## Responsive Behavior

Desktop is the primary target because resume review and portal interaction need space.

Desktop:

- Sidebar navigation
- Tables for queues and trackers
- Split panes for job description and resume preview

Tablet:

- Collapsible navigation
- Job detail and resume preview can stack

Mobile:

- Read-only monitoring and quick approvals only
- Avoid complex resume editing on small screens

## MVP UI Scope

The first UI should include:

- Dashboard
- Job Queue
- Job Detail
- Resume Review
- Tracker
- Settings

Application Flow can start as a guided state panel before becoming deeper browser automation.

Portal management can start with viewing and enabling configured portals, then expand into full adapter setup.

## Future UI Scope

- Side-by-side diff between base resume and tailored resume
- Resume QA score before upload
- Portal capability matrix
- Browser state timeline
- One-click manual import from saved searches
- Notifications for hourly runs
- Multi-profile support
- Hosted team/SaaS mode only if the product direction changes later

## Non-Negotiables

- Never upload a resume without showing which PDF will be used.
- Never submit an application without an explicit approved state unless full-auto mode is enabled.
- Never show internal tailoring labels in the final resume preview or PDF.
- Never hide duplicate application warnings.
- Never make personal data look cloud-synced unless cloud sync actually exists.
- Never let one portal failure block the whole queue.
