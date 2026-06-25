# Issue 011: Hourly Watcher And Notifications

Type: AFK

Blocked by: Issue 003, Issue 004

User stories covered: 4, 35, 36, 37

## What to build

Add UI support for scheduled hourly runs and local notifications or in-app alerts. The user should be able to enable or disable the watcher, set the scan interval, see the next run time, and review the result of the latest run.

The watcher should reuse the existing `watch` behavior conceptually but expose it through the local app.

## Acceptance criteria

- [ ] The user can enable or disable scheduled runs from Settings or Dashboard.
- [ ] The user can set the interval, defaulting to 60 minutes.
- [ ] Dashboard shows next scheduled run and latest run result.
- [ ] Portal warnings from scheduled runs are visible.
- [ ] Scheduled runs do not submit applications automatically.
- [ ] The watcher can be stopped cleanly.
- [ ] Tests cover schedule config and a simulated watcher tick.
