"""ATS-based job search helper focused on Malaysia roles."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class JobPosting:
    title: str
    company: str
    location: str
    description: str
    required_skills: list[str]
    preferred_skills: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateProfile:
    skills: list[str]
    desired_keywords: list[str] = field(default_factory=list)


class ATSMalaysiaJobSearchAgent:
    """Ranks Malaysia jobs using simple ATS-style keyword matching."""

    _MALAYSIA_LOCATION_TERMS = (
        "malaysia",
        "kuala lumpur",
        "selangor",
        "penang",
        "johor",
        "putrajaya",
        "sarawak",
        "sabah",
    )

    @staticmethod
    def _normalize(value: str) -> str:
        return value.strip().lower()

    def _is_malaysia_job(self, location: str) -> bool:
        normalized_location = self._normalize(location)
        return any(term in normalized_location for term in self._MALAYSIA_LOCATION_TERMS)

    def _match_count(self, needles: list[str], haystack: set[str]) -> int:
        return sum(1 for needle in needles if self._normalize(needle) in haystack)

    def score_job(self, job: JobPosting, candidate: CandidateProfile) -> float:
        candidate_skills = {self._normalize(skill) for skill in candidate.skills}

        required_count = len(job.required_skills)
        required_match = self._match_count(job.required_skills, candidate_skills)
        required_score = (required_match / required_count) * 60 if required_count else 60

        preferred_count = len(job.preferred_skills)
        preferred_match = self._match_count(job.preferred_skills, candidate_skills)
        preferred_score = (preferred_match / preferred_count) * 20 if preferred_count else 0

        combined_text = self._normalize(f"{job.title} {job.description}")
        keyword_count = len(candidate.desired_keywords)
        keyword_match = sum(
            1
            for keyword in candidate.desired_keywords
            if self._normalize(keyword) in combined_text
        )
        keyword_score = (keyword_match / keyword_count) * 20 if keyword_count else 0

        return round(required_score + preferred_score + keyword_score, 2)

    def search_jobs(
        self,
        jobs: list[JobPosting],
        candidate: CandidateProfile,
        *,
        top_k: int = 10,
        min_score: float = 0,
    ) -> list[dict[str, object]]:
        ranked_jobs = []
        for job in jobs:
            if not self._is_malaysia_job(job.location):
                continue
            score = self.score_job(job, candidate)
            if score < min_score:
                continue
            ranked_jobs.append(
                {
                    "job": job,
                    "score": score,
                }
            )

        ranked_jobs.sort(key=lambda result: result["score"], reverse=True)
        return ranked_jobs[:top_k]
