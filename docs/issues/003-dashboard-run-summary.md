# Issue 003: Dashboard Run Summary

Type: AFK

Blocked by: Issue 001, Issue 002

User stories covered: 4, 10, 27, 28, 32, 33, 37

## What to build

Build a Dashboard that summarizes the current ResumeAgent state: last run, next scheduled run, jobs found, jobs queued, resumes awaiting review, applications ready for action, submitted applications, duplicates, skipped jobs, and portal warnings.

This should become the default workspace home screen.

## Acceptance criteria

- [ ] Dashboard loads live summary data from the backend.
- [ ] The user can trigger a manual scan from the Dashboard.
- [ ] The Dashboard shows portal warnings without making the whole app look failed.
- [ ] Counts link to the relevant filtered views where practical.
- [ ] Empty states guide the user to run a scan or configure portals.
- [ ] Loading and error states are specific and recoverable.
