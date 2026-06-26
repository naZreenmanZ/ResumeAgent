from __future__ import annotations

import argparse
from pathlib import Path
from time import sleep

from .application_agent import build_application_plan
from .config import init_project, load_config
from .db import JobStore
from .pdf_export import export_tailored_pdf
from .pipeline import scan_enabled_portals
from .resume import select_resume_path, tailor_resume
from .services import prepare_application_assets
from .tracker import export_application_tracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobapply")
    parser.add_argument("--config", default="config.toml", help="Path to config TOML.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create local config files.")
    subparsers.add_parser("scan", help="Scan enabled portals and queue matching jobs.")
    subparsers.add_parser("queue", help="List queued jobs.")
    subparsers.add_parser("export-tracker", help="Export application tracking CSV and XLSX.")
    subparsers.add_parser("portal-list", help="List configured portals.")
    subparsers.add_parser("portal-template", help="Print the saved-search import CSV header.")

    run_once = subparsers.add_parser(
        "run-once",
        help="Scan, tailor the next queued jobs, export PDFs, and refresh the tracker.",
    )
    run_once.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Maximum queued jobs to prepare in this run.",
    )
    run_once.add_argument(
        "--mode",
        choices=["review_before_submit", "full_auto"],
        default="review_before_submit",
        help="Whether generated application plans may allow final submit.",
    )

    watch = subparsers.add_parser("watch", help="Run the preparation loop repeatedly.")
    watch.add_argument(
        "--interval-minutes",
        type=int,
        default=60,
        help="Minutes between runs.",
    )
    watch.add_argument("--limit", type=int, default=1, help="Jobs to prepare per run.")
    watch.add_argument(
        "--mode",
        choices=["review_before_submit", "full_auto"],
        default="review_before_submit",
        help="Whether generated application plans may allow final submit.",
    )

    portal_add = subparsers.add_parser("portal-add", help="Add a future portal placeholder.")
    portal_add.add_argument("--name", required=True, help="Portal name, for example dice or monster.")
    portal_add.add_argument(
        "--method",
        default="saved search or approved source",
        help="Expected access method for this portal.",
    )
    portal_add.add_argument("--enabled", action="store_true", help="Enable the portal immediately.")

    tailor = subparsers.add_parser("tailor", help="Generate a tailored resume draft.")
    tailor.add_argument("--job-id", required=True, help="Job fingerprint or fingerprint prefix.")

    export_pdf = subparsers.add_parser("export-pdf", help="Export a tailored resume draft to PDF.")
    export_pdf.add_argument("draft_path", help="Path to a tailored markdown draft.")

    plan_apply = subparsers.add_parser(
        "plan-apply",
        help="Create an application plan for a queued job after tailoring its resume.",
    )
    plan_apply.add_argument("--job-id", required=True, help="Job fingerprint or fingerprint prefix.")
    plan_apply.add_argument(
        "--mode",
        choices=["review_before_submit", "full_auto"],
        default="review_before_submit",
        help="Whether the agent may press the final submit button.",
    )

    applied = subparsers.add_parser("mark-applied", help="Mark a job as applied.")
    applied.add_argument("--job-id", required=True, help="Job fingerprint or fingerprint prefix.")
    applied.add_argument("--portal-ref", required=True, help="Portal confirmation, URL, or note.")
    applied.add_argument("--resume-path", help="Resume draft path used for the application.")

    return parser


def resolve_job_id(store: JobStore, value: str) -> str:
    rows = store.connection.execute(
        "SELECT fingerprint FROM jobs WHERE fingerprint LIKE ?",
        (f"{value}%",),
    ).fetchall()
    if not rows:
        raise SystemExit(f"No job found for id prefix: {value}")
    if len(rows) > 1:
        raise SystemExit(f"Job id prefix is ambiguous: {value}")
    return str(rows[0]["fingerprint"])


def command_init() -> None:
    created = init_project(Path.cwd())
    if created:
        print("Created:")
        for path in created:
            print(f"  {path}")
    else:
        print("Project config already exists.")


def command_scan(config_path: str) -> None:
    config = load_config(config_path)
    store = JobStore(config.database_path)
    try:
        stats = scan_enabled_portals(config, store)
    finally:
        store.close()
    print(
        "Scan complete: "
        f"{stats['seen']} seen, {stats['inserted']} new, "
        f"{stats['queued']} matched, {stats['blocked']} blocked, "
        f"{stats['skipped_portals']} portals skipped."
    )
    warnings = stats["warnings"]
    if isinstance(warnings, list) and warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")


def command_run_once(config_path: str, limit: int, mode: str) -> None:
    config = load_config(config_path)
    ensure_runtime_dirs(config)
    store = JobStore(config.database_path)
    try:
        stats = scan_enabled_portals(config, store)
        print(
            "Scan complete: "
            f"{stats['seen']} seen, {stats['inserted']} new, "
            f"{stats['queued']} matched, {stats['blocked']} blocked."
        )
        rows = store.queued_jobs()[: max(limit, 0)]
        if not rows:
            print("No queued jobs to prepare.")
        for row in rows:
            resume_path, upload_resume_path, _ = prepare_application_assets(
                config,
                store,
                str(row["fingerprint"]),
                mode,
            )
            print(
                f"Prepared {row['fingerprint'][:8]} | {row['title']} | "
                f"{row['company']} | {upload_resume_path}"
            )
        csv_path, xlsx_path = export_application_tracker(store, config.tracking_dir)
        print(f"Tracker refreshed: {csv_path}")
        print(f"Tracker refreshed: {xlsx_path}")
    finally:
        store.close()


def command_watch(config_path: str, interval_minutes: int, limit: int, mode: str) -> None:
    interval_seconds = max(interval_minutes, 1) * 60
    print(f"Watching for jobs every {max(interval_minutes, 1)} minute(s). Press Ctrl+C to stop.")
    while True:
        command_run_once(config_path, limit, mode)
        sleep(interval_seconds)


def command_queue(config_path: str) -> None:
    config = load_config(config_path)
    store = JobStore(config.database_path)
    try:
        rows = store.queued_jobs()
        if not rows:
            print("No queued jobs.")
            return
        for row in rows:
            print(
                f"{row['fingerprint'][:8]} | score {row['score']:>3} | "
                f"{row['title']} | {row['company']} | {row['location']}"
            )
            print(f"  {row['url']}")
    finally:
        store.close()


def command_portal_list(config_path: str) -> None:
    config = load_config(config_path)
    if not config.portals:
        print("No portals configured.")
        return
    for portal in config.portals:
        state = "enabled" if portal.enabled else "disabled"
        method = portal.options.get("method", portal.type)
        print(f"{portal.name} | {state} | {portal.type} | {method}")


def command_portal_template() -> None:
    print("title,company,location,url,description,requirements,job_id")


def command_portal_add(config_path: str, name: str, method: str, enabled: bool) -> None:
    normalized_name = name.strip().lower().replace(" ", "-")
    if not normalized_name:
        raise SystemExit("Portal name cannot be empty.")

    config_file = Path(config_path)
    if not config_file.exists():
        raise SystemExit(f"Config file does not exist: {config_path}")

    config = load_config(config_file)
    existing_names = {portal.name.lower() for portal in config.portals}
    if normalized_name in existing_names:
        raise SystemExit(f"Portal already exists: {normalized_name}")

    block = (
        "\n[[portals]]\n"
        f'name = "{normalized_name}"\n'
        f"enabled = {'true' if enabled else 'false'}\n"
        'type = "setup_required"\n'
        f'method = "{method}"\n'
        'notes = "Placeholder until adapter is implemented."\n'
    )
    with config_file.open("a", encoding="utf-8") as handle:
        handle.write(block)
    print(f"Added portal: {normalized_name}")


def command_tailor(config_path: str, job_id: str) -> None:
    config = load_config(config_path)
    store = JobStore(config.database_path)
    try:
        fingerprint = resolve_job_id(store, job_id)
        job = store.get_job(fingerprint)
        if job is None:
            raise SystemExit(f"No job found: {job_id}")
        resume_path = select_resume_path(config, job)
        output_path = tailor_resume(resume_path, config.tailored_resume_dir, job)
        store.set_job_status(fingerprint, "tailored")
        print(output_path)
    finally:
        store.close()


def command_export_pdf(draft_path: str) -> None:
    output_path = export_tailored_pdf(Path(draft_path))
    print(output_path)


def command_plan_apply(config_path: str, job_id: str, mode: str) -> None:
    config = load_config(config_path)
    store = JobStore(config.database_path)
    try:
        fingerprint = resolve_job_id(store, job_id)
        job = store.get_job(fingerprint)
        if job is None:
            raise SystemExit(f"No job found: {job_id}")
        resume_path, upload_resume_path, plan_path = prepare_application_assets(
            config,
            store,
            fingerprint,
            mode,
        )
        job = store.get_job(fingerprint)
        if job is None:
            raise SystemExit(f"No job found after tailoring: {job_id}")
        plan = build_application_plan(job, resume_path, upload_resume_path, mode)
        print(plan.summary())
        print(plan_path)
    finally:
        store.close()


def command_mark_applied(
    config_path: str,
    job_id: str,
    portal_ref: str,
    resume_path: str | None,
) -> None:
    config = load_config(config_path)
    store = JobStore(config.database_path)
    try:
        fingerprint = resolve_job_id(store, job_id)
        store.mark_applied(fingerprint, portal_ref, resume_path)
        csv_path, xlsx_path = export_application_tracker(store, config.tracking_dir)
        print(f"Marked applied: {fingerprint[:8]}")
        print(f"Tracker refreshed: {csv_path}")
        print(f"Tracker refreshed: {xlsx_path}")
    finally:
        store.close()


def command_export_tracker(config_path: str) -> None:
    config = load_config(config_path)
    store = JobStore(config.database_path)
    try:
        csv_path, xlsx_path = export_application_tracker(store, config.tracking_dir)
        print(csv_path)
        print(xlsx_path)
    finally:
        store.close()


def ensure_runtime_dirs(config) -> None:
    config.base_resume_dir.mkdir(parents=True, exist_ok=True)
    config.tailored_resume_dir.mkdir(parents=True, exist_ok=True)
    config.tracking_dir.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        command_init()
    elif args.command == "scan":
        command_scan(args.config)
    elif args.command == "run-once":
        command_run_once(args.config, args.limit, args.mode)
    elif args.command == "watch":
        command_watch(args.config, args.interval_minutes, args.limit, args.mode)
    elif args.command == "queue":
        command_queue(args.config)
    elif args.command == "export-tracker":
        command_export_tracker(args.config)
    elif args.command == "portal-list":
        command_portal_list(args.config)
    elif args.command == "portal-template":
        command_portal_template()
    elif args.command == "portal-add":
        command_portal_add(args.config, args.name, args.method, args.enabled)
    elif args.command == "tailor":
        command_tailor(args.config, args.job_id)
    elif args.command == "export-pdf":
        command_export_pdf(args.draft_path)
    elif args.command == "plan-apply":
        command_plan_apply(args.config, args.job_id, args.mode)
    elif args.command == "mark-applied":
        command_mark_applied(args.config, args.job_id, args.portal_ref, args.resume_path)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
