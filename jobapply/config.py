from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import ast
import shutil


@dataclass(frozen=True)
class ProfileConfig:
    target_titles: list[str] = field(default_factory=list)
    target_locations: list[str] = field(default_factory=list)
    required_keywords: list[str] = field(default_factory=list)
    blocked_keywords: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PortalConfig:
    name: str
    enabled: bool
    type: str
    options: dict[str, object]


@dataclass(frozen=True)
class AppConfig:
    database_path: Path
    base_resume_path: Path
    mena_resume_path: Path
    non_mena_resume_path: Path
    output_dir: Path
    profile: ProfileConfig
    portals: list[PortalConfig]
    base_resume_dir: Path = Path("resumes")
    tailored_resume_dir: Path = Path("tailored_resumes")
    tracking_dir: Path = Path("tracking")


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    data = parse_simple_toml(config_path.read_text(encoding="utf-8"))
    root = config_path.parent

    profile_data = data.get("profile", {})
    profile = ProfileConfig(
        target_titles=list(profile_data.get("target_titles", [])),
        target_locations=list(profile_data.get("target_locations", [])),
        required_keywords=list(profile_data.get("required_keywords", [])),
        blocked_keywords=list(profile_data.get("blocked_keywords", [])),
    )

    portals: list[PortalConfig] = []
    for item in data.get("portals", []):
        options = dict(item)
        name = str(options.pop("name"))
        enabled = bool(options.pop("enabled", True))
        portal_type = str(options.pop("type"))
        if "path" in options:
            option_path = Path(str(options["path"]))
            options["path"] = str(option_path if option_path.is_absolute() else root / option_path)
        portals.append(PortalConfig(name=name, enabled=enabled, type=portal_type, options=options))

    base_resume_path = resolve_path(data.get("base_resume_path", "resumes/base_resume.md"), root)
    mena_resume_path = resolve_path(data.get("mena_resume_path", base_resume_path), root)
    non_mena_resume_path = resolve_path(data.get("non_mena_resume_path", base_resume_path), root)
    base_resume_dir = resolve_path(data.get("base_resume_dir", "resumes"), root)
    tailored_resume_dir = resolve_path(
        data.get("tailored_resume_dir", data.get("output_dir", "tailored_resumes")),
        root,
    )
    tracking_dir = resolve_path(data.get("tracking_dir", "tracking"), root)

    return AppConfig(
        database_path=(root / data.get("database_path", "jobapply.sqlite3")).resolve(),
        base_resume_path=base_resume_path,
        mena_resume_path=mena_resume_path,
        non_mena_resume_path=non_mena_resume_path,
        output_dir=tailored_resume_dir,
        base_resume_dir=base_resume_dir,
        tailored_resume_dir=tailored_resume_dir,
        tracking_dir=tracking_dir,
        profile=profile,
        portals=portals,
    )


def resolve_path(value: object, root: Path) -> Path:
    path = Path(str(value))
    return (path if path.is_absolute() else root / path).resolve()


def parse_simple_toml(content: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current: dict[str, object] = data

    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line == "[profile]":
            profile: dict[str, object] = {}
            data["profile"] = profile
            current = profile
            continue
        if line == "[[portals]]":
            portals = data.setdefault("portals", [])
            if not isinstance(portals, list):
                raise ValueError("portals must be a list")
            portal: dict[str, object] = {}
            portals.append(portal)
            current = portal
            continue
        if "=" not in line:
            raise ValueError(f"Unsupported config line: {raw_line}")

        key, value = [part.strip() for part in line.split("=", 1)]
        current[key] = parse_simple_toml_value(value)

    return data


def parse_simple_toml_value(value: str) -> object:
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith("[") or value.startswith('"'):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError:
        return value


def init_project(target_dir: str | Path = ".") -> list[Path]:
    root = Path(target_dir)
    created: list[Path] = []
    copies = {
        root / "config.toml": root / "config.example.toml",
        root / "resumes" / "base_resume.md": root / "resumes" / "base_resume.md",
    }

    if not (root / "config.toml").exists():
        shutil.copyfile(root / "config.example.toml", root / "config.toml")
        created.append(root / "config.toml")

    resume_path = root / "resumes" / "base_resume.md"
    resume_path.parent.mkdir(parents=True, exist_ok=True)
    if not resume_path.exists():
        template = root / "resumes" / "base_resume.md"
        if template.exists():
            shutil.copyfile(template, resume_path)
        created.append(resume_path)

    for directory in (root / "tailored_resumes", root / "tracking", root / "imports"):
        directory.mkdir(parents=True, exist_ok=True)
        keep_file = directory / ".gitkeep"
        if not keep_file.exists():
            keep_file.write_text("", encoding="utf-8")
            created.append(keep_file)

    return created
