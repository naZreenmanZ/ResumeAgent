from __future__ import annotations

from pathlib import Path
import re
from sqlite3 import Row

from .config import AppConfig
from .models import normalize_text

MENA_TERMS = {
    "uae",
    "united arab emirates",
    "dubai",
    "abu dhabi",
    "sharjah",
    "saudi arabia",
    "riyadh",
    "jeddah",
    "qatar",
    "doha",
    "oman",
    "muscat",
    "bahrain",
    "kuwait",
    "egypt",
    "cairo",
    "jordan",
    "amman",
    "lebanon",
    "beirut",
}


def is_mena_job(job: Row) -> bool:
    location = normalize_text(str(job["location"]))
    url = str(job["url"]).lower()
    return any(term in location or f"/{term.replace(' ', '-')}/" in url for term in MENA_TERMS)


def select_resume_path(config: AppConfig, job: Row) -> Path:
    return config.mena_resume_path if is_mena_job(job) else config.non_mena_resume_path


def read_resume_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF resumes require pypdf. Install with: python3 -m pip install pypdf") from exc

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(page.strip() for page in pages if page.strip())
    return path.read_text(encoding="utf-8")


def extract_keywords(job: Row, limit: int = 12) -> list[str]:
    text = " ".join(
        [
            str(job["title"]),
            str(job["description"]),
            str(job["requirements"]),
            str(job["matched_keywords"]),
        ]
    )
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", text)
    ignored = {
        "and",
        "the",
        "with",
        "for",
        "you",
        "our",
        "build",
        "role",
        "tools",
        "services",
        "jobs",
        "apply",
        "easy",
        "company",
        "candidate",
        "candidates",
        "careers",
        "michael",
        "page",
        "posted",
    }
    priority_terms = [
        "Python",
        "backend",
        "APIs",
        "database",
        "scalable",
        "secure",
        "performance",
        "DevOps",
        "AI",
        "third-party",
        "communication",
        "full-stack",
        "SRE",
        "automation",
        "SQL",
    ]
    seen: set[str] = set()
    keywords: list[str] = []
    haystack = normalize_text(text)
    for term in priority_terms:
        normalized_term = normalize_text(term)
        if normalized_term in haystack and normalized_term not in seen:
            seen.add(normalized_term)
            keywords.append(term)
            if len(keywords) >= limit:
                return keywords

    for word in words:
        normalized = normalize_text(word)
        if normalized in ignored or normalized in seen:
            continue
        seen.add(normalized)
        keywords.append(word)
        if len(keywords) >= limit:
            break
    return keywords


def matching_resume_lines(base_resume: str, keywords: list[str], limit: int = 5) -> list[str]:
    keyword_set = {normalize_text(keyword) for keyword in keywords}
    candidate_lines = [
        candidate for candidate in extract_resume_highlight_candidates(base_resume)
        if is_complete_candidate(candidate)
    ]
    matches: list[str] = []
    for stripped in candidate_lines:
        normalized = normalize_text(stripped)
        if any(keyword in normalized for keyword in keyword_set):
            matches.append(as_bullet(stripped))
        if len(matches) >= limit:
            break
    if matches:
        return matches
    return [as_bullet(line) for line in candidate_lines[:limit]]


def extract_resume_highlight_candidates(base_resume: str) -> list[str]:
    lines = [line.strip() for line in base_resume.splitlines()]
    candidates: list[str] = []
    current: list[str] = []
    bullet_prefixes = ("-", "*", "●", "•")

    for line in lines:
        if not line:
            continue
        starts_bullet = line.startswith(bullet_prefixes)
        looks_heading = line.isupper() and len(line.split()) <= 5
        if starts_bullet:
            if current:
                candidates.append(clean_candidate(" ".join(current)))
            current = [line.lstrip("-*●• ").strip()]
            continue
        if current and not looks_heading:
            current.append(line)
        elif current:
            candidates.append(clean_candidate(" ".join(current)))
            current = []

    if current:
        candidates.append(clean_candidate(" ".join(current)))

    return [candidate for candidate in candidates if len(candidate.split()) >= 5]


def is_complete_candidate(value: str) -> bool:
    cleaned = value.strip().lower()
    if "| team lead" in cleaned or "full stack enginee r" in cleaned:
        return False
    return not cleaned.endswith((" and", ",", " with", " using", " by"))


def clean_candidate(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_line(value: str) -> str:
    return clean_candidate(value)


def as_bullet(value: str) -> str:
    cleaned = value.strip()
    if cleaned.startswith(("-", "*")):
        return cleaned
    return f"- {cleaned}"


def strip_bullet(value: str) -> str:
    return value.strip().lstrip("-*●• ").strip()


def build_targeted_summary(job: Row, keywords: list[str]) -> str:
    role = str(job["title"]).strip() or "software engineering"
    focus_terms = polished_focus_terms(keywords)
    focus = ", ".join(focus_terms[:5]) if focus_terms else "backend engineering and product delivery"
    return (
        f"Full Stack Engineer with 5+ years of experience building production web applications and "
        f"backend services relevant to {role} roles. Strong experience across {focus}, with hands-on "
        "delivery using React, TypeScript, Node.js, Python, REST APIs, AWS, database optimization, "
        "automation, and production performance improvements. Known for collaborating with product, "
        "design, business, and engineering teams to ship reliable, user-focused systems."
    )


def polished_focus_terms(keywords: list[str]) -> list[str]:
    replacements = {
        "backend": "backend development",
        "APIs": "API design",
        "database": "database-backed systems",
        "scalable": "scalable architecture",
        "secure": "secure application design",
        "performance": "performance optimization",
        "third-party": "third-party integrations",
        "communication": "cross-functional communication",
        "automation": "workflow automation",
    }
    terms: list[str] = []
    for keyword in keywords:
        term = replacements.get(keyword, keyword)
        if normalize_text(term) not in {normalize_text(existing) for existing in terms}:
            terms.append(term)
    return terms


def tailor_resume(base_resume_path: Path, output_dir: Path, job: Row) -> Path:
    base_resume = read_resume_text(base_resume_path)
    keywords = extract_keywords(job)
    profile = parse_resume_profile(base_resume)
    safe_name = re.sub(r"[^A-Za-z0-9]+", "-", f"{job['company']}-{job['title']}").strip("-").lower()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{safe_name}-{job['fingerprint'][:8]}.md"

    jd_snapshot = str(job["description"]).strip()
    if len(jd_snapshot) > 1200:
        jd_snapshot = jd_snapshot[:1200].rsplit(" ", 1)[0] + "..."

    tailored = (
        "<!--\n"
        f"Internal tailoring note: {job['title']} at {job['company']}.\n"
        f"Source resume: {base_resume_path}\n"
        f"JD signals: {jd_snapshot or 'No detailed JD text captured yet.'}\n"
        "-->\n\n"
        f"# {profile['name']}\n\n"
        f"{profile['contact']}\n\n"
        "## Professional Summary\n\n"
        f"{build_targeted_summary(job, keywords)}\n\n"
        "## Professional Experience\n\n"
        f"{format_experience(profile['experience'])}\n\n"
        "## Technical Skills\n\n"
        f"{format_skills_by_category(profile['skills'], keywords)}\n\n"
        "## Certifications & Achievements\n\n"
        f"{format_lines(profile['certifications'])}\n\n"
        "## Education\n\n"
        f"{format_lines(clean_education(profile['education']))}\n\n"
        "## Languages\n\n"
        f"{format_lines(profile['languages'])}\n"
    )

    output_path.write_text(tailored, encoding="utf-8")
    return output_path


def parse_resume_profile(base_resume: str) -> dict[str, object]:
    normalized_resume = normalize_resume_layout(base_resume)
    compact_lines = [clean_line(line) for line in normalized_resume.splitlines()]
    compact_lines = [line for line in compact_lines if line]
    name = first_nonempty(compact_lines, "NASREEN MANZOOR")
    contact = next(
        (line for line in compact_lines[:8] if "@" in line or "+971" in line),
        "Dubai, United Arab Emirates | nazreenmanz@gmail.com | +971 555239823",
    )
    return {
        "name": name,
        "contact": contact,
        "skills": extract_technical_skills(normalized_resume),
        "experience": extract_professional_experience(normalized_resume),
        "certifications": extract_list_section(
            normalized_resume,
            "CERTIFICATIONS & ACHIEVEMENTS",
            ["Backend:", "EDUCATION"],
        ),
        "education": extract_list_section(normalized_resume, "EDUCATION", ["LANGUAGES"]),
        "languages": extract_list_section(normalized_resume, "LANGUAGES", []),
    }


def normalize_resume_layout(base_resume: str) -> str:
    text = re.sub(r"[ \t]+", " ", base_resume)
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = text.replace("Full Stack Enginee r", "Full Stack Engineer")
    text = text.replace("SQLAlchemy ,", "SQLAlchemy,")
    return text.strip()


def extract_between(text: str, start: str, end_markers: list[str]) -> str:
    start_match = re.search(re.escape(start), text, flags=re.IGNORECASE)
    if not start_match:
        return ""
    start_index = start_match.end()
    end_index = len(text)
    for marker in end_markers:
        match = re.search(re.escape(marker), text[start_index:], flags=re.IGNORECASE)
        if match:
            end_index = min(end_index, start_index + match.start())
    return text[start_index:end_index].strip()


def extract_professional_experience(text: str) -> list[dict[str, object]]:
    section = extract_between(text, "PROFESSIONAL EXPERIENCE", ["TECHNICAL SKILLS"])
    if not section:
        return []

    second_role = "Full Stack Engineer | Team Lead"
    first_part, second_part = split_once(section, second_role)
    jobs: list[dict[str, object]] = []

    first_bullets = extract_bullets(first_part)
    if first_bullets:
        jobs.append(
            {
                "heading": "Full Stack Engineer — Suvik | Sharjah Research & Technology Park, UAE | 2023 – Present",
                "bullets": first_bullets,
            }
        )

    if second_part:
        second_bullets = extract_bullets(second_part)
        if second_bullets:
            jobs.append(
                {
                    "heading": "Full Stack Engineer | Team Lead — ESPL, Mumbai | 2021 – 2023",
                    "bullets": second_bullets,
                }
            )

    return jobs


def split_once(value: str, marker: str) -> tuple[str, str]:
    index = value.find(marker)
    if index == -1:
        return value, ""
    return value[:index], value[index:]


def extract_bullets(section: str) -> list[str]:
    raw_parts = [part.strip() for part in re.split(r"\s*●\s*", section) if part.strip()]
    bullets: list[str] = []
    for part in raw_parts:
        cleaned = clean_line(part)
        if not cleaned or cleaned.startswith("Full Stack Engineer"):
            continue
        cleaned = re.sub(r"^.*?\bPresent\b\s*", "", cleaned)
        cleaned = re.sub(r"^.*?\b2023\b\s*", "", cleaned)
        if len(cleaned.split()) >= 7 and is_complete_candidate(cleaned):
            bullets.append(cleaned)
    return bullets[:10]


def extract_technical_skills(text: str) -> list[str]:
    section = extract_between(text, "CERTIFICATIONS & ACHIEVEMENTS", ["EDUCATION"])
    skill_lines = []
    for prefix in ["Backend:", "Frontend:", "Cloud & DevOps:", "Databases:", "Architecture & Security:", "Tools & Practices:"]:
        match = re.search(re.escape(prefix) + r"\s*(.*?)(?=Backend:|Frontend:|Cloud & DevOps:|Databases:|Architecture & Security:|Tools & Practices:|$)", section, flags=re.IGNORECASE | re.DOTALL)
        if match:
            skill_lines.append(f"{prefix} {clean_line(match.group(1))}")
    if skill_lines:
        return skill_lines
    return extract_skill_terms(text)


def extract_list_section(text: str, start: str, end_markers: list[str]) -> list[str]:
    section = extract_between(text, start, end_markers)
    parts = split_compacted_bullets(compact_resume_lines(section.splitlines()))
    cleaned = [
        clean_line(part)
        for part in parts
        if clean_line(part) and normalize_text(clean_line(part)) not in {"education", "languages"}
    ]
    return cleaned[:10]


def first_nonempty(lines: list[str], fallback: str) -> str:
    return lines[0] if lines else fallback


def extract_skill_terms(base_resume: str) -> list[str]:
    known = [
        "React",
        "TypeScript",
        "Node.js",
        "Python",
        "Flask",
        "Angular",
        "REST APIs",
        "AWS",
        "SQL",
        "SQLAlchemy",
        "Celery",
        "Django",
        "Next.js",
        "Git",
        "API Design",
        "Backend Development",
        "Cloud Architecture",
        "CI/CD",
        "Performance Optimization",
        "Database Optimization",
        "AI-assisted Workflows",
    ]
    haystack = normalize_text(base_resume)
    skills: list[str] = []
    for skill in known:
        if normalize_text(skill) in haystack and skill not in skills:
            skills.append(skill)
    return skills


def extract_section_lines(base_resume: str, start_heading: str, end_headings: list[str]) -> list[str]:
    lines = [clean_line(line) for line in base_resume.splitlines()]
    capture = False
    collected: list[str] = []
    for line in lines:
        if not line:
            continue
        normalized = normalize_text(line)
        if normalize_text(start_heading) in normalized:
            capture = True
            continue
        if capture and (
            any(normalize_text(end) in normalized for end in end_headings)
            or line.startswith(("Backend:", "Frontend:", "Cloud & DevOps:", "Databases:", "Architecture & Security:", "Tools & Practices:"))
        ):
            break
        if capture:
            collected.append(line)
    compacted = compact_resume_lines(collected)
    return split_compacted_bullets(compacted)[:8]


def split_compacted_bullets(lines: list[str]) -> list[str]:
    split_lines: list[str] = []
    for line in lines:
        parts = [part.strip() for part in re.split(r"\s*●\s*", line) if part.strip()]
        if len(parts) > 1:
            split_lines.extend(parts)
        else:
            split_lines.append(line.lstrip("● ").strip())
    return split_lines


def compact_resume_lines(lines: list[str]) -> list[str]:
    compacted: list[str] = []
    current = ""
    for line in lines:
        cleaned = clean_line(line)
        if not cleaned:
            continue
        starts_bullet = cleaned.startswith(("●", "•", "-"))
        looks_heading = cleaned.isupper() and len(cleaned.split()) <= 5
        if starts_bullet or looks_heading:
            if current:
                compacted.append(current)
            current = cleaned
        elif current and len(current) < 140:
            current = f"{current} {cleaned}"
        else:
            if current:
                compacted.append(current)
            current = cleaned
    if current:
        compacted.append(current)
    return compacted


def format_skills(base_skills: list[str], keywords: list[str]) -> str:
    ordered: list[str] = []
    for skill in [*keywords, *base_skills]:
        normalized = normalize_text(skill)
        if normalized and normalized not in {normalize_text(value) for value in ordered}:
            ordered.append(skill)
    return ", ".join(ordered[:24])


def format_skills_by_category(base_skills: list[str], keywords: list[str]) -> str:
    categories = parse_skill_categories(base_skills)
    categories = {category: clean_skill_values(values) for category, values in categories.items()}
    keyword_categories = {
        "Backend": ["Python", "backend", "APIs", "database", "third-party", "automation", "SQL"],
        "Frontend": ["full-stack", "React", "TypeScript"],
        "Cloud & DevOps": ["DevOps", "SRE", "performance"],
        "Databases": ["database", "SQL"],
        "Architecture & Security": ["scalable", "secure", "performance"],
        "Tools & Practices": ["AI", "communication"],
    }
    for category, terms in keyword_categories.items():
        existing = categories.setdefault(category, [])
        for keyword in keywords:
            if normalize_text(keyword) in {normalize_text(term) for term in terms}:
                add_unique(existing, skill_label(keyword))

    ordered_categories = [
        "Backend",
        "Frontend",
        "Cloud & DevOps",
        "Databases",
        "Architecture & Security",
        "Tools & Practices",
    ]
    lines: list[str] = []
    for category in ordered_categories:
        values = categories.get(category, [])
        if values:
            lines.append(f"- **{category}:** {', '.join(values)}")
    return "\n".join(lines)


def parse_skill_categories(base_skills: list[str]) -> dict[str, list[str]]:
    categories: dict[str, list[str]] = {}
    for line in base_skills:
        if ":" not in line:
            continue
        category, raw_values = line.split(":", 1)
        values = [value.strip() for value in raw_values.split(",") if value.strip()]
        categories[category.strip()] = values
    return categories


def clean_skill_values(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        label = skill_label(value)
        if normalize_text(label) not in {normalize_text(existing) for existing in cleaned}:
            cleaned.append(label)
    return cleaned


def skill_label(value: str) -> str:
    replacements = {
        "database": "Database Optimization",
        "APIs": "API Design",
        "backend": "Backend Development",
        "secure": "Secure Application Design",
        "scalable": "Scalable System Design",
        "third-party": "Third-party Integrations",
        "performance": "Performance Optimization",
        "communication": "Cross-functional Communication",
        "automation": "Workflow Automation",
        "AI": "AI-assisted Development",
    }
    return replacements.get(value, value)


def add_unique(values: list[str], value: str) -> None:
    normalized = normalize_text(value)
    if normalized and normalized not in {normalize_text(item) for item in values}:
        values.insert(0, value)


def format_experience(experience: list[dict[str, object]]) -> str:
    if not experience:
        return "- Experience available on request"
    blocks: list[str] = []
    for job in experience:
        heading = str(job["heading"])
        bullets = [as_bullet(clean_resume_bullet(str(bullet))) for bullet in job["bullets"]]
        blocks.append("\n".join([f"### {heading}", *bullets]))
    return "\n\n".join(blocks)


def clean_resume_bullet(value: str) -> str:
    cleaned = clean_line(value)
    cleaned = cleaned.replace("8 months ,", "8 months,")
    cleaned = cleaned.replace("■", ";").replace("○", ";")
    cleaned = re.sub(r"\s*;\s*", "; ", cleaned)
    cleaned = cleaned.replace("of:; ", "of: ")
    return cleaned


def format_lines(lines: list[str]) -> str:
    if not lines:
        return "- Available on request"
    filtered = [
        line for line in lines
        if line.strip() and normalize_text(line) not in {"languages", "education", "certifications"}
    ]
    return "\n".join(as_bullet(line) for line in filtered) if filtered else "- Available on request"


def clean_education(lines: list[str]) -> list[str]:
    text = " ".join(clean_line(line) for line in lines if clean_line(line))
    if not text:
        return []

    education: list[str] = []
    master = re.search(
        r"(Master of Computer Applications \(MCA\)).*?(APJ Abdul Kalam University).*?(2018\s*[–-]\s*2021).*?CGPA:\s*([0-9.]+)",
        text,
        flags=re.IGNORECASE,
    )
    bachelor = re.search(
        r"(Bachelor of Computer Applications \(BCA\)).*?(Calicut University).*?(2015\s*[–-]\s*2018).*?CGPA:\s*([0-9.]+)",
        text,
        flags=re.IGNORECASE,
    )
    if master:
        education.append(
            f"{master.group(1)} — {master.group(2)} | {normalize_dash(master.group(3))} | CGPA: {master.group(4)}"
        )
    if bachelor:
        education.append(
            f"{bachelor.group(1)} — {bachelor.group(2)} | {normalize_dash(bachelor.group(3))} | CGPA: {bachelor.group(4)}"
        )
    return education or lines


def normalize_dash(value: str) -> str:
    return re.sub(r"\s*[–-]\s*", " – ", value.strip())
