# Issue 004: Portal Settings And Scan Trigger

Type: AFK

Blocked by: Issue 001, Issue 002

User stories covered: 1, 2, 3, 4, 37, 38

## What to build

Create the Portals screen for viewing, enabling, disabling, and testing configured portal adapters. The screen should show each portal's name, enabled state, adapter type, scan method, last scan result, last warning, and setup status.

The first version should support the existing configured portal model and make unsupported portals clear as "needs setup."

## Acceptance criteria

- [ ] Portal list is loaded from local config.
- [ ] Enabled/disabled state is visible for each portal.
- [ ] Adapter type and scan method are shown.
- [ ] The user can trigger a test scan for a portal or all portals.
- [ ] Setup-required portals display a clear non-failure state.
- [ ] Runtime portal failures display structured warnings.
- [ ] Changes that affect config require confirmation before being saved.
