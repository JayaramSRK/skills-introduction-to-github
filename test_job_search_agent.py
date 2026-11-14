import unittest

from job_search_agent import ATSMalaysiaJobSearchAgent, CandidateProfile, JobPosting


class ATSMalaysiaJobSearchAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = ATSMalaysiaJobSearchAgent()
        self.candidate = CandidateProfile(
            skills=["Python", "SQL", "AWS"],
            desired_keywords=["backend", "api"],
        )

    def test_search_jobs_filters_non_malaysia_locations(self) -> None:
        jobs = [
            JobPosting(
                title="Backend Engineer",
                company="A",
                location="Kuala Lumpur, Malaysia",
                description="Backend API role",
                required_skills=["Python", "SQL"],
            ),
            JobPosting(
                title="Backend Engineer",
                company="B",
                location="Singapore",
                description="Backend API role",
                required_skills=["Python", "SQL"],
            ),
        ]

        results = self.agent.search_jobs(jobs, self.candidate)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["job"].company, "A")

    def test_search_jobs_ranks_best_skill_match_higher(self) -> None:
        jobs = [
            JobPosting(
                title="Python Developer",
                company="TopMatch",
                location="Selangor, Malaysia",
                description="Backend API services",
                required_skills=["Python", "SQL"],
                preferred_skills=["AWS"],
            ),
            JobPosting(
                title="Developer",
                company="LowerMatch",
                location="Selangor, Malaysia",
                description="General software work",
                required_skills=["Java", "Spring"],
                preferred_skills=["Kotlin"],
            ),
        ]

        results = self.agent.search_jobs(jobs, self.candidate)

        self.assertEqual(results[0]["job"].company, "TopMatch")
        self.assertGreater(results[0]["score"], results[1]["score"])

    def test_score_job_uses_desired_keywords(self) -> None:
        with_keywords = JobPosting(
            title="Backend Engineer",
            company="Keywords",
            location="Penang, Malaysia",
            description="Build API integrations",
            required_skills=["Python"],
        )
        without_keywords = JobPosting(
            title="Data Engineer",
            company="NoKeywords",
            location="Penang, Malaysia",
            description="ETL platform and warehousing",
            required_skills=["Python"],
        )

        score_with_keywords = self.agent.score_job(with_keywords, self.candidate)
        score_without_keywords = self.agent.score_job(without_keywords, self.candidate)

        self.assertGreater(score_with_keywords, score_without_keywords)


if __name__ == "__main__":
    unittest.main()
