from __future__ import annotations

from .config import ProfileConfig
from .models import Job, ScoredJob, normalize_text


def score_job(job: Job, profile: ProfileConfig) -> ScoredJob:
    haystack = normalize_text(
        " ".join([job.title, job.company, job.location, job.description, *job.requirements])
    )

    matched: list[str] = []
    blocked: list[str] = []
    score = 0

    for title in profile.target_titles:
        if normalize_text(title) in haystack:
            score += 25
            matched.append(title)

    for location in profile.target_locations:
        if normalize_text(location) in haystack:
            score += 15
            matched.append(location)

    for keyword in profile.required_keywords:
        if normalize_text(keyword) in haystack:
            score += 10
            matched.append(keyword)

    for keyword in profile.blocked_keywords:
        if normalize_text(keyword) in haystack:
            blocked.append(keyword)
            score -= 100

    return ScoredJob(job=job, score=max(score, 0), matched_keywords=matched, blocked_keywords=blocked)
