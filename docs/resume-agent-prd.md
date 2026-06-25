# ResumeAgent PRD

## Problem Statement

Job searching across multiple portals is repetitive, easy to lose track of, and risky when applications are duplicated or sent with the wrong resume. The user wants a personal, non-commercial ResumeAgent that can find relevant roles, tailor a base resume to each job description, generate a polished PDF, upload it to the selected job portal, submit applications when approved, and maintain an application tracker.

The first working runs proved the core value: the agent can scan/queue jobs, generate tailored resumes, upload a CV on GulfTalent when the file is selected, submit an application, and mark the application locally. They also exposed product gaps: file-picker automation is brittle in the in-app browser, browser scanner failures should not stop the whole run, and generated resumes must look like employer-ready resumes rather than internal bot artifacts.

## Solution

ResumeAgent will be a local, executable, human-in-the-loop application assistant. It will:

- Scan configured job portals or imported saved-search results.
- Score jobs against the user's skills, titles, locations, and blocked terms.
- Deduplicate jobs and avoid reapplying.
- Select the correct base resume by region, using the MENA resume with photo for MENA jobs and the NP resume for non-MENA jobs.
- Tailor resume content to the job description while preserving professional resume structure and headings.
- Export a polished PDF per job into a consistent tailored resume folder.
- Prepare a per-job application plan.
- Assist browser-based application workflows, including CV upload, modal detection, application review, and final submit.
- Track application outcomes in local SQLite plus CSV/XLSX tracker files.
- Keep all personal data, resumes, tailored PDFs, imports, trackers, and local config out of git.

## User Stories

1. As a job seeker, I want to choose which portals ResumeAgent scans, so that I stay in control of where my profile is used.
2. As a job seeker, I want ResumeAgent to support LinkedIn, Indeed, GulfTalent, NaukriGulf, Bayt, Wellfound, and JobTogether, so that I can centralize my search.
3. As a job seeker, I want to add new portals later, so that the system grows with my job search.
4. As a job seeker, I want jobs scanned every hour or on manual trigger, so that relevant opportunities are found without constant manual checking.
5. As a job seeker, I want jobs scored against my skills and target positions, so that I apply to roles that are actually relevant.
6. As a job seeker, I want blocked keywords to reject bad jobs, so that unpaid, commission-only, or irrelevant jobs do not waste time.
7. As a job seeker, I want duplicate jobs detected, so that the same role is not queued repeatedly.
8. As a job seeker, I want previously applied jobs excluded, so that I do not accidentally apply twice.
9. As a job seeker, I want duplicate application states detected from the portal, so that already-applied jobs are recorded locally.
10. As a job seeker, I want a visible queue of candidate jobs, so that I can understand what the agent plans to work on.
11. As a job seeker, I want a base resume folder, so that the system always knows where source resumes belong.
12. As a job seeker, I want a tailored resume folder, so that all generated PDFs and drafts are saved consistently.
13. As a job seeker, I want a tracking folder, so that application trackers are saved consistently.
14. As a job seeker, I want all personal files ignored by git, so that resumes, trackers, imports, and config are not pushed publicly.
15. As a job seeker, I want MENA jobs to use my photo resume, so that regional expectations are handled correctly.
16. As a job seeker, I want non-MENA jobs to use my NP resume, so that the right version is used elsewhere.
17. As a job seeker, I want each resume tailored to the exact JD, so that the employer sees the most relevant version of my experience.
18. As a job seeker, I want tailoring to preserve the base resume's professional headings, so that no important section disappears.
19. As a job seeker, I want Professional Experience to include company names, titles, locations, and dates, so that the resume remains credible.
20. As a job seeker, I want Technical Skills categorized, so that recruiters can scan my stack quickly.
21. As a job seeker, I do not want internal labels like Targeted Summary, Base Resume Content, Job URL, or bot notes in the final resume, so that the resume looks employer-ready.
22. As a job seeker, I do not want the job portal URL or role label after my name, so that the header looks like a normal resume.
23. As a job seeker, I want Education and Certifications to be cleanly formatted, so that the final PDF looks polished.
24. As a job seeker, I want resume content reviewed before upload when needed, so that quality problems are caught before submission.
25. As a job seeker, I want a PDF export, so that the portal receives an uploadable resume file.
26. As a job seeker, I want application plans created per job, so that the agent has a concrete checklist before interacting with a portal.
27. As a job seeker, I want the browser flow to detect upload success modals, so that I know the CV was actually attached.
28. As a job seeker, I want the browser flow to detect duplicate-application pages, so that the tracker is updated without retrying.
29. As a job seeker, I want the browser flow to stop at login if my portal session expires, so that credentials remain under my control.
30. As a job seeker, I want final application submission to require explicit approval unless full-auto mode is intentionally enabled, so that sensitive actions are controlled.
31. As a job seeker, I want ResumeAgent to submit applications only after the tailored CV is attached, so that the old CV is not sent accidentally.
32. As a job seeker, I want tracker files in CSV and XLSX, so that I can review applications in Excel.
33. As a job seeker, I want the tracker to include application date, portal, job title, company, location, URL, portal reference, resume path, and status, so that I have a complete history.
34. As a job seeker, I want a local executable command, so that I can run the system without remembering Python module syntax.
35. As a job seeker, I want a `run-once` command, so that I can trigger one cycle manually.
36. As a job seeker, I want a `watch` command, so that I can run the process hourly.
37. As a job seeker, I want failed portal scanners to produce warnings instead of crashing the whole run, so that one flaky site does not block all preparation.
38. As a developer, I want portal adapters behind a small interface, so that each site can evolve independently.
39. As a developer, I want job storage and application storage separated, so that queueing and application tracking remain clear.
40. As a developer, I want resume tailoring isolated from PDF rendering, so that resume quality can improve without changing portal logic.
41. As a developer, I want browser application logic separated from scanning and resume generation, so that upload/submit workflows can be tested and improved independently.
42. As a developer, I want tests around dedupe, scoring, resume structure, PDF export, tracker export, portal failures, and CLI behavior, so that core behavior remains reliable.

## Implementation Decisions

- The product is local-first and personal-use only. It stores state locally and does not require a hosted backend.
- The executable entry point is a project wrapper around the Python CLI.
- Configuration is kept in a local TOML file that is ignored by git.
- Runtime folders are explicit and stable:
  - base resumes
  - tailored resumes and application plans
  - tracking spreadsheets
  - portal imports
- Git ignores personal config, base resume files, generated tailored resumes, tracker spreadsheets, imports, databases, and environment files. Placeholder files keep required folders present in the repository.
- Jobs are represented with portal, portal job id, title, company, location, URL, description, requirements, and discovered timestamp.
- Job fingerprints are stable and deduplicate by portal plus portal id when available, falling back to normalized title/company/location.
- Applications are tracked separately from jobs and keyed by job fingerprint to prevent duplicates.
- The scan pipeline loops through enabled portal adapters. Setup-required adapters and runtime-failing adapters are recorded as skipped warnings instead of aborting the entire run.
- Portal adapters are selected by type. Current adapter families are saved-search import, feed, browser agent, demo JSON, and setup-required placeholder.
- Saved-search imports are the safer default for broad portal support. Browser automation is reserved for portals where account usage and site terms allow it.
- GulfTalent browser scanning can work but is fragile under local macOS/Playwright permissions. The pipeline must tolerate browser scanner failure.
- Region selection chooses the MENA resume for MENA jobs and the NP resume for non-MENA jobs.
- Resume tailoring reads the chosen base resume, extracts profile sections, preserves employer-facing headings, and writes a tailored markdown draft.
- Tailored resume content must not expose internal tailoring notes in the rendered PDF.
- The final resume must retain Professional Summary, Professional Experience, Technical Skills, Certifications & Achievements, Education, and Languages.
- Professional Experience must preserve employer names and dates for Suvik and ESPL.
- Technical Skills are rendered by category rather than as an unstructured list.
- PDF export is generated from tailored markdown and uses simple, stable resume formatting.
- Application plans are generated per job and include the tailored markdown path, uploadable PDF path, portal URL, and submit mode.
- Tracker export writes both CSV and XLSX using local application records.
- `run-once` scans, prepares up to N queued jobs, exports PDFs, and refreshes trackers.
- `watch` runs the same preparation cycle repeatedly at a configured minute interval.
- The GulfTalent application flow currently requires human help for native file selection because the in-app browser does not expose a reliable `setInputFiles` method and native file-picker automation is inconsistent.
- Browser submission must verify page state: upload success, duplicate-application page, review page, submit button, and post-submit confirmation or already-applied state.
- If GulfTalent redirects to login, ResumeAgent stops and asks the user to log in.

## Testing Decisions

- Tests should assert external behavior rather than internal implementation details.
- Dedupe tests should verify that the same portal job does not enter the queue twice.
- Scoring tests should verify required keyword matching and blocked keyword behavior.
- Pipeline tests should verify setup-required portal warnings and runtime scanner failure isolation.
- Resume tests should verify employer-facing structure:
  - no internal labels
  - no role/headline line after the name
  - professional sections remain present
  - company names remain present
  - technical skills are categorized
  - education is cleaned
- PDF export tests should verify a tailored markdown draft produces a PDF artifact.
- Tracker tests should verify CSV and XLSX files contain application records.
- CLI tests should verify portal placeholder addition and config path behavior.
- Browser upload and native file picker behavior should be treated as integration/manual-HITL until a reliable browser automation surface or portal API is available.
- A future browser workflow test should use a controlled mock page with modals, upload states, duplicate states, and submit states before being applied to live portals.

## Out of Scope

- Commercial SaaS operation.
- Circumventing job portal restrictions, CAPTCHAs, login protections, or terms of service.
- Fully unattended submission on portals where final submit requires user review.
- Storing passwords or login credentials.
- Uploading personal files without user approval.
- Guaranteeing live portal compatibility when a portal changes markup or blocks automation.
- Replacing the user's professional judgment about whether a role is desirable.
- Building a hosted dashboard in the current phase.
- LLM-provider integration for resume rewriting in the current local MVP.

## Further Notes

- Completed so far:
  - local project scaffold
  - CLI commands
  - config and git safety
  - portal adapter framework
  - saved-search/feed/demo/browser adapter types
  - SQLite job/application store
  - scoring and dedupe
  - MENA vs NP resume selection
  - tailored markdown generation
  - PDF export
  - application plans
  - CSV/XLSX tracker export
  - executable wrapper
  - manual and hourly run commands
  - GulfTalent first application submitted successfully
  - duplicate application detection recorded locally
  - GitHub repository created and initial project pushed
  - scanner failure isolation added after repeated Playwright Crashpad failures

- Known limitations:
  - GulfTalent file upload cannot currently be completed end-to-end by the in-app browser API because file input setting is unavailable.
  - The native macOS file picker sometimes ignores scripted path entry, requiring manual selection.
  - Live browser scanning can fail on macOS due to Playwright Chromium permissions.
  - Resume tailoring is heuristic and should eventually be upgraded to a stronger optimizer with stricter layout validation.

- Recommended next milestones:
  - Build a dedicated GulfTalent application workflow module that models login, edit-CV, upload, review, duplicate, submit, and confirmation states.
  - Add a mock portal test harness for upload/modal/submit flows.
  - Add a resume QA command that renders/extracts the PDF and fails on forbidden phrases or missing sections.
  - Add a portal capability matrix documenting each portal's supported scan and apply method.
  - Add an approval queue UI or terminal review mode before upload.
  - Add stronger resume tailoring using a controlled LLM prompt with employer-facing output validation.
