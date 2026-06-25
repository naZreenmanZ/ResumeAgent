# Issue 002: Backend API Around Existing CLI Engine

Type: AFK

Blocked by: None - can start immediately

User stories covered: 4, 5, 7, 8, 10, 34, 35, 36, 38, 39, 40, 41

## What to build

Expose the existing ResumeAgent Python engine through a local backend API so the UI can call scan, queue, tailor, export, plan, tracker, and settings operations without shelling out manually.

The API should reuse the current config, database, portal adapters, scoring, resume, PDF, and tracker modules rather than duplicating logic.

## Acceptance criteria

- [ ] The backend can load the same local `config.toml` used by the CLI.
- [ ] The backend exposes endpoints for health, config summary, scan, queue, job detail, tailor, export PDF, application plan, mark applied, and tracker summary.
- [ ] API responses do not expose private resume contents unless the UI explicitly requests a review view.
- [ ] Portal setup and runtime warnings are returned as structured warnings instead of crashing the API.
- [ ] Existing CLI behavior continues to work.
- [ ] Automated tests cover at least health, queue, scan warning handling, and one tailor/export path.
