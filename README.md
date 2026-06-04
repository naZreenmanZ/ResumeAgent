# Resume Automation

A personal, human-in-the-loop job application assistant.

This project scans enabled job portal adapters, deduplicates opportunities, scores them against your target profile, generates tailored resume drafts, and tracks application state so you do not apply twice.

It intentionally keeps final submission behind your approval. Many job portals restrict automated submission, and a review step also prevents low-quality or incorrect applications.

## Quick Start

```bash
python3 -m jobapply init
./bin/jobapply run-once
./bin/jobapply queue
./bin/jobapply plan-apply --job-id <job_id>
./bin/jobapply mark-applied --job-id <job_id> --portal-ref <confirmation_or_url>
```

`./bin/jobapply` is the executable wrapper for this project. You can still use `python3 -m jobapply --config config.toml ...` if you prefer.

## Personal Setup

Keep personal files out of git. This repo ignores local config, generated resumes, SQLite state, PDF/DOCX resumes, and portal import files.

Create `config.toml` from `config.example.toml`, then set your base resume paths:

```toml
base_resume_dir = "resumes"
mena_resume_path = "/absolute/path/to/resume-with-photo.pdf"
non_mena_resume_path = "/absolute/path/to/resume-without-photo-np.pdf"
tailored_resume_dir = "tailored_resumes"
tracking_dir = "tracking"
```

MENA jobs use `mena_resume_path`. Non-MENA jobs use `non_mena_resume_path`.

If you want to keep resumes inside this project folder, place them under `resumes/`. PDF, DOC, and DOCX files in that folder are ignored by git.

Committed folder map:

- `resumes/`: put base resumes here if you want local copies. Contents are ignored.
- `tailored_resumes/`: tailored markdown drafts, polished PDFs, and application plans. Contents are ignored.
- `tracking/`: application CSV/XLSX trackers. Contents are ignored.
- `imports/`: CSV/JSON portal imports. Contents are ignored except the README/placeholder.

## Configure Portals

Edit `config.toml` after running `init`.

The starter project ships with a `demo` portal adapter that reads from `data/sample_jobs.json`.

The initial selectable portal list is:

- LinkedIn
- Indeed
- GulfTalent
- NaukriGulf
- Bayt
- Wellfound
- JobTogether

These real portal entries currently use `type = "setup_required"` so you can choose them in config before their adapters are implemented. Real support should be added as separate adapters under `jobapply/portals/`. Prefer official APIs, exports, saved-search emails, or RSS feeds where available. Use browser automation only where your account and the portal terms allow it.

To add another portal later, add a new block:

```toml
[[portals]]
name = "newportal"
enabled = false
type = "setup_required"
method = "saved search or approved source"
notes = "Placeholder until adapter is implemented."
```

Or use the CLI:

```bash
python3 -m jobapply --config config.toml portal-add --name monster
python3 -m jobapply --config config.toml portal-list
python3 -m jobapply portal-template
```

## Current Portal Adapter Types

- `saved_search_import`: reads CSV or JSON files from `imports/`
- `feed`: reads RSS, Atom, or JSON feed URLs
- `browser_agent`: uses Playwright with portal-specific selectors
- `demo_json`: reads the included demo data
- `setup_required`: marks a selected portal that still needs an adapter

The default local config uses `saved_search_import` for LinkedIn, Indeed, GulfTalent, NaukriGulf, Bayt, Wellfound, and JobTogether. Add portal results to the matching CSV file under `imports/`, then run `python3 -m jobapply scan`.

## Agent-Style Applying

The intended full pipeline is:

```bash
./bin/jobapply run-once
./bin/jobapply queue
./bin/jobapply plan-apply --job-id <job_id>
./bin/jobapply mark-applied --job-id <job_id> --portal-ref <confirmation_or_url>
```

`plan-apply` generates the tailored markdown draft, exports a polished uploadable PDF, and writes an application plan. By default it uses `review_before_submit`, meaning the agent prepares the application and stops before the final submit action. Use `--mode full_auto` only for portals where you are comfortable with unattended submission.

For a manual trigger:

```bash
./bin/jobapply run-once --limit 1
```

For an hourly local loop:

```bash
./bin/jobapply watch --interval-minutes 60 --limit 1
```

The current browser-assisted workflow still needs portal-specific handling for modals, upload confirmations, and final submit screens. The program prepares and tracks the application; browser submission should only proceed when the portal page clearly confirms each step.

For real website scanning, switch a portal to `type = "browser_agent"` and configure its `search_url` plus selectors. Browser scanning requires Playwright:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

## Workflow

1. Choose portals in `config.toml`.
2. Run `scan` to fetch new jobs.
3. Review `queue`.
4. Run `tailor` for jobs you like.
5. Apply manually or through a compliant adapter.
6. Mark the application as applied with the confirmation URL or portal reference.

## Duplicate Protection

Jobs are deduplicated by:

- portal name
- portal job id when available
- normalized title/company/location fingerprint

Applications are stored in SQLite at the path configured by `database_path`.

`mark-applied` also refreshes:

- `tracking/applications.csv`
- `tracking/applications.xlsx`

These files are ignored by git because they contain personal application history.

## Git Safety

Before pushing, check that no personal artifacts are staged:

```bash
git status --short
git check-ignore -v config.toml generated/ tailored_resumes/app.pdf tracking/applications.xlsx imports/*.csv resumes/*.pdf
```

These should stay local:

- `config.toml`
- `jobapply.sqlite3`
- `generated/`
- `tailored_resumes/*`
- `tracking/*`
- `imports/*.csv`
- `imports/*.json`
- `resumes/*.pdf`
- `resumes/*.docx`

## Project Status

This is an MVP scaffold with one demo adapter and a local heuristic resume tailor. The next natural steps are:

- add portal adapters for the sites you choose
- add a stronger LLM-based resume optimizer
- add browser-based review screens for final application submission
