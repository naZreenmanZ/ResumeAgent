from __future__ import annotations

from pathlib import Path
import re


def export_tailored_pdf(markdown_path: Path) -> Path:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as exc:
        raise RuntimeError("PDF export requires reportlab. Install with: python3 -m pip install reportlab") from exc

    sections = parse_tailored_markdown(markdown_path.read_text(encoding="utf-8"))
    output_path = markdown_path.with_suffix(".pdf")

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ResumeTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=20,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    body = ParagraphStyle(
        name="ResumeBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=11,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
    )
    bullet = ParagraphStyle(
        name="ResumeBullet",
        parent=body,
        leftIndent=10,
        firstLineIndent=-6,
        bulletIndent=0,
    )
    meta = ParagraphStyle(
        name="Meta",
        parent=body,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#4b5563"),
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    story: list[object] = []
    title = first_resume_title(sections)
    story.append(Paragraph(escape(title), styles["ResumeTitle"]))

    for header_line in sections.get("Header", [])[:2]:
        story.append(Paragraph(escape(header_line), meta))

    ordered_sections = [
        "Professional Summary",
        "Professional Experience",
        "Technical Skills",
        "Certifications & Achievements",
        "Education",
        "Languages",
    ]

    for section_name in ordered_sections:
        lines = sections.get(section_name, [])
        if not lines:
            continue
        story.append(Paragraph(escape(section_name), styles["SectionHeading"]))
        if section_name == "Professional Experience":
            render_experience_lines(story, lines, body, bullet, Paragraph)
        elif section_name in {"Education", "Certifications & Achievements", "Languages"}:
            render_bullet_lines(story, lines, bullet, Paragraph)
        elif section_name == "Technical Skills":
            for line in lines:
                story.append(Paragraph(markdown_bold_to_reportlab(escape(strip_bullet(line))), bullet, bulletText="-"))
        else:
            story.append(Paragraph(escape(" ".join(lines)), body))
        story.append(Spacer(1, 3))

    document.build(story)
    return output_path


def parse_tailored_markdown(content: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = ""
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("<!--") or line.startswith("-->"):
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if line.startswith("# "):
            sections.setdefault("Document Title", []).append(line[2:].strip())
            current = "Header"
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)
    return sections


def first_resume_title(sections: dict[str, list[str]]) -> str:
    titles = sections.get("Document Title", [])
    return titles[0] if titles else "Resume"


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
        elif current and not current.endswith((".", ":", "|")) and len(current) < 180:
            current = f"{current} {cleaned}"
        else:
            if current:
                compacted.append(current)
            current = cleaned
    if current:
        compacted.append(current)
    return compacted


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_bullet(value: str) -> str:
    cleaned = value.strip()
    for prefix in ("- ", "* ", "● ", "• "):
        if cleaned.startswith(prefix):
            return cleaned[len(prefix):].strip()
    return cleaned


def split_skill_lines(lines: list[str]) -> list[str]:
    skills: list[str] = []
    for line in lines:
        skills.extend(part.strip() for part in line.split(",") if part.strip())
    return skills


def render_bullet_lines(story: list[object], lines: list[str], style: object, paragraph: object) -> None:
    for line in lines:
        if strip_bullet(line):
            story.append(paragraph(escape(strip_bullet(line)), style, bulletText="-"))


def render_experience_lines(story: list[object], lines: list[str], body: object, bullet: object, paragraph: object) -> None:
    for line in lines:
        if line.startswith("### "):
            story.append(paragraph(f"<b>{escape(line[4:].strip())}</b>", body))
        elif strip_bullet(line):
            story.append(paragraph(escape(strip_bullet(line)), bullet, bulletText="-"))


def escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def markdown_bold_to_reportlab(value: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
