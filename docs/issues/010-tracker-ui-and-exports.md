# Issue 010: Tracker UI And Exports

Type: AFK

Blocked by: Issue 002

User stories covered: 8, 9, 13, 32, 33, 39

## What to build

Create the Tracker UI as the source of truth for applications. It should show application records from local storage and support CSV/XLSX export through the existing tracker module.

The interface should feel like a clean spreadsheet with strong filtering and clear status.

## Acceptance criteria

- [ ] Tracker loads application records from the backend.
- [ ] Columns include applied date, portal, job title, company, location, status, portal reference, resume PDF path, job URL, and notes.
- [ ] The user can filter by portal, status, company, and date.
- [ ] The user can export CSV and XLSX.
- [ ] The UI shows the last tracker export time.
- [ ] Resume paths and job URLs are selectable or openable.
- [ ] Mark-applied and already-applied states are reflected in the tracker.
