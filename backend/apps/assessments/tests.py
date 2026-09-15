"""API tests for the assessment engine (Phase 5).

Covers the complete student flow (list -> start -> answer -> submit -> result),
score write-back to the student's skill record, correct-answer secrecy before
submission, retake/resubmit guards, ownership isolation, and admin CRUD.
"""

from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.users.models import User

from .models import Assessment, AssessmentResult, Option, Question, StudentAttempt

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ASSESSMENTS_URL = "/api/v1/assessments"
RESULTS_URL = "/api/v1/students/me/assessment-results"
ADMIN_ASSESSMENTS_URL = "/api/v1/admin/assessments"

PASSWORD = "Tr0ub4dor&3"


def register_and_login(client, email="riya@example.com"):
    client.post(
        REGISTER_URL,
        {
            "full_name": "Riya Sharma",
            "email": email,
            "password": PASSWORD,
            "role": "STUDENT",
            "college": "NIT Trichy",
            "course": "B.Tech CSE",
            "year": 3,
        },
        format="json",
    )
    res = client.post(LOGIN_URL, {"email": email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def build_assessment(skill, *, published=True, question_count=3, title="Python Test"):
    """Assessment where options[0] is correct, options[1] is wrong."""
    assessment = Assessment.objects.create(
        title=title,
        skill=skill,
        is_published=published,
        duration_minutes=10,
    )
    for i in range(question_count):
        question = Question.objects.create(
            assessment=assessment, text=f"Question {i + 1}?", order=i
        )
        Option.objects.create(
            question=question, text=f"Correct answer {i + 1}", is_correct=True, order=0
        )
        Option.objects.create(
            question=question, text=f"Wrong answer {i + 1}", is_correct=False, order=1
        )
    return assessment


def answers_for(start_data, correct_flags):
    """Turn a start response + per-question booleans into a submit payload."""
    return [
        {
            "question_id": q["id"],
            "option_id": q["options"][0 if correct else 1]["id"],
        }
        for q, correct in zip(start_data["questions"], correct_flags)
    ]


class AssessmentFlowTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.skill = Skill.objects.get(name="Python")
        register_and_login(self.client)
        self.user = User.objects.get(email="riya@example.com")
        self.assessment = build_assessment(self.skill)
        self.url = f"{ASSESSMENTS_URL}/{self.assessment.id}"

    def test_list_shows_only_published_assessments_with_metadata(self):
        hidden = build_assessment(self.skill, published=False, title="Draft test")
        res = self.client.get(ASSESSMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [a["title"] for a in res.data]
        self.assertIn(self.assessment.title, titles)
        self.assertNotIn(hidden.title, titles)
        item = next(a for a in res.data if a["id"] == self.assessment.id)
        self.assertEqual(item["question_count"], 3)
        self.assertEqual(item["skill"]["name"], "Python")
        self.assertEqual(item["my_attempts"], 0)
        self.assertIsNone(item["my_last_score"])

    def test_start_returns_questions_but_never_correct_answers(self):
        res = self.client.post(f"{self.url}/start")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("attempt", res.data)
        self.assertEqual(res.data["attempt"]["status"], "IN_PROGRESS")
        self.assertEqual(len(res.data["questions"]), 3)
        for question in res.data["questions"]:
            for option in question["options"]:
                self.assertNotIn("is_correct", option)
                self.assertEqual(
                    set(option.keys()), {"id", "text", "order"}
                )
        # Correct answers must not leak anywhere in the response.
        self.assertNotIn("is_correct", str(res.data))

    def test_start_resumes_the_same_in_progress_attempt(self):
        first = self.client.post(f"{self.url}/start")
        second = self.client.post(f"{self.url}/start")
        self.assertEqual(first.data["attempt"]["id"], second.data["attempt"]["id"])
        self.assertEqual(
            StudentAttempt.objects.filter(
                user=self.user, status=StudentAttempt.Status.IN_PROGRESS
            ).count(),
            1,
        )

    def test_submit_perfect_score_writes_result_and_skill_score(self):
        start = self.client.post(f"{self.url}/start").data
        res = self.client.post(
            f"{self.url}/submit",
            {
                "attempt_id": start["attempt"]["id"],
                "answers": answers_for(start, [True, True, True]),
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["score"], 100.0)
        self.assertEqual(res.data["correct_count"], 3)
        self.assertEqual(res.data["total_questions"], 3)
        self.assertTrue(res.data["review"])
        self.assertTrue(all(item["is_correct"] for item in res.data["review"]))
        # Suggestions reflect a perfect run.
        joined = " ".join(res.data["improvement_suggestions"])
        self.assertIn("strong command", joined)

        attempt = StudentAttempt.objects.get(pk=start["attempt"]["id"])
        self.assertEqual(attempt.status, StudentAttempt.Status.SUBMITTED)
        self.assertIsNotNone(attempt.submitted_at)

        row = UserSkill.objects.get(user=self.user, skill=self.skill)
        self.assertEqual(row.assessment_score, Decimal("100.0"))
        self.assertEqual(row.experience_level, "EXPERT")
        self.assertEqual(row.proficiency_level, 1)  # engine-created, neutral default

    def test_submit_partial_score_with_review_and_suggestions(self):
        start = self.client.post(f"{self.url}/start").data
        res = self.client.post(
            f"{self.url}/submit",
            {
                "attempt_id": start["attempt"]["id"],
                "answers": answers_for(start, [True, False, True]),
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["score"], 66.7)
        self.assertEqual(res.data["correct_count"], 2)
        wrong = next(item for item in res.data["review"] if not item["is_correct"])
        self.assertNotEqual(
            wrong["selected_option_text"], wrong["correct_option_text"]
        )
        self.assertTrue(wrong["correct_option_text"].startswith("Correct answer"))
        # The wrong question is referenced in the suggestions.
        joined = " ".join(res.data["improvement_suggestions"])
        self.assertIn("Question 2?", joined)

        row = UserSkill.objects.get(user=self.user, skill=self.skill)
        self.assertEqual(row.assessment_score, Decimal("66.7"))

    def test_submit_with_missing_questions_rejected(self):
        start = self.client.post(f"{self.url}/start").data
        res = self.client.post(
            f"{self.url}/submit",
            {
                "attempt_id": start["attempt"]["id"],
                "answers": answers_for(start, [True, False])[:2],  # only two of three
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        attempt = StudentAttempt.objects.get(pk=start["attempt"]["id"])
        self.assertEqual(attempt.status, StudentAttempt.Status.IN_PROGRESS)
        self.assertEqual(AssessmentResult.objects.count(), 0)

    def test_submit_with_option_from_another_question_rejected(self):
        start = self.client.post(f"{self.url}/start").data
        questions = start["questions"]
        # Pick the correct-looking shape but swap an option between questions.
        answers = [
            {
                "question_id": questions[i]["id"],
                "option_id": questions[(i + 1) % len(questions)]["options"][0]["id"],
            }
            for i in range(len(questions))
        ]
        res = self.client.post(
            f"{self.url}/submit",
            {"attempt_id": start["attempt"]["id"], "answers": answers},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resubmitting_the_same_attempt_is_rejected(self):
        start = self.client.post(f"{self.url}/start").data
        payload = {
            "attempt_id": start["attempt"]["id"],
            "answers": answers_for(start, [True, True, True]),
        }
        self.assertEqual(
            self.client.post(f"{self.url}/submit", payload, format="json").status_code,
            status.HTTP_200_OK,
        )
        res = self.client.post(f"{self.url}/submit", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AssessmentResult.objects.count(), 1)

    def test_retake_after_submit_creates_a_fresh_attempt(self):
        first = self.client.post(f"{self.url}/start").data
        self.client.post(
            f"{self.url}/submit",
            {"attempt_id": first["attempt"]["id"], "answers": answers_for(first, [True] * 3)},
            format="json",
        )
        second = self.client.post(f"{self.url}/start").data
        self.assertNotEqual(second["attempt"]["id"], first["attempt"]["id"])
        self.assertEqual(second["attempt"]["status"], "IN_PROGRESS")

    def test_attempt_is_owner_scoped(self):
        start = self.client.post(f"{self.url}/start").data
        # Another student cannot submit someone else's attempt.
        register_and_login(self.client, email="other@example.com")
        res = self.client.post(
            f"{self.url}/submit",
            {
                "attempt_id": start["attempt"]["id"],
                # Shape-valid payload: the attempt simply is not theirs.
                "answers": [{"question_id": 99999, "option_id": 1}],
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        # ...and sees an empty results history.
        self.assertEqual(self.client.get(RESULTS_URL).data, [])

    def test_results_history_lists_newest_first_with_reviews(self):
        first = self.client.post(f"{self.url}/start").data
        self.client.post(
            f"{self.url}/submit",
            {"attempt_id": first["attempt"]["id"], "answers": answers_for(first, [True] * 3)},
            format="json",
        )
        second = self.client.post(f"{self.url}/start").data
        self.client.post(
            f"{self.url}/submit",
            {"attempt_id": second["attempt"]["id"], "answers": answers_for(second, [True, False, True])},
            format="json",
        )
        res = self.client.get(RESULTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]["score"], 66.7)  # newest first
        self.assertEqual(res.data[1]["score"], 100.0)
        self.assertIn("review", res.data[0])
        self.assertEqual(res.data[0]["assessment"]["title"], "Python Test")

    def test_role_and_auth_guards(self):
        # Anonymous user.
        self.client.credentials()
        self.assertEqual(self.client.get(ASSESSMENTS_URL).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            self.client.post(f"{self.url}/start").status_code, status.HTTP_401_UNAUTHORIZED
        )
        # Professor is authenticated but not a student.
        register_and_login(self.client, email="anita-prof@example.com")
        user = User.objects.get(email="anita-prof@example.com")
        user.role = User.Role.PROFESSOR
        user.save()
        res = self.client.post(LOGIN_URL, {"email": "anita-prof@example.com", "password": PASSWORD}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        self.assertEqual(self.client.get(ASSESSMENTS_URL).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.client.post(f"{self.url}/start").status_code, status.HTTP_403_FORBIDDEN
        )


class AssessmentSecrecyAndAdminTests(APITestCase):
    def setUp(self):
        ensure_skill_catalog()
        self.skill = Skill.objects.get(name="Python")

    def _admin_login(self):
        boss, _ = User.objects.get_or_create(
            username="boss",
            email="boss@example.com",
            defaults={"role": User.Role.ADMIN},
        )
        boss.set_password(PASSWORD)
        boss.role = User.Role.ADMIN
        boss.save()
        res = self.client.post(
            LOGIN_URL, {"email": "boss@example.com", "password": PASSWORD}, format="json"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_admin_creates_assessment_with_questions_and_options(self):
        self._admin_login()
        res = self.client.post(
            ADMIN_ASSESSMENTS_URL,
            {
                "title": "React Hooks",
                "skill": self.skill.id,
                "difficulty": "ADVANCED",
                "duration_minutes": 15,
                "is_published": True,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        assessment_id = res.data["id"]

        # A question with four options and exactly one correct.
        res = self.client.post(
            f"{ADMIN_ASSESSMENTS_URL}/{assessment_id}/questions",
            {
                "text": "Which hook manages local state?",
                "marks": 2,
                "order": 1,
                "options": [
                    {"text": "useState", "is_correct": True, "order": 0},
                    {"text": "useEffect", "is_correct": False, "order": 1},
                    {"text": "useMemo", "is_correct": False, "order": 2},
                    {"text": "useRef", "is_correct": False, "order": 3},
                ],
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        question_id = res.data["id"]

        # Admin reads the bank WITH correct answers.
        res = self.client.get(f"{ADMIN_ASSESSMENTS_URL}/{assessment_id}/questions")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("is_correct", res.data[0]["options"][0])

        # Student list shows the new published assessment.
        register_and_login(self.client)
        res = self.client.get(ASSESSMENTS_URL)
        self.assertIn("React Hooks", [a["title"] for a in res.data])

        # Back to admin to manage the question bank.
        self._admin_login()
        res = self.client.patch(
            f"/api/v1/admin/questions/{question_id}",
            {
                "text": "Which hook manages local state? (updated)",
                "options": [
                    {"text": "useState", "is_correct": True, "order": 0},
                    {"text": "useEffect", "is_correct": False, "order": 1},
                ],
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data["options"][0]["is_correct"], True
        )

    def test_admin_question_validation_rules(self):
        self._admin_login()
        assessment = build_assessment(self.skill)
        url = f"{ADMIN_ASSESSMENTS_URL}/{assessment.id}/questions"
        base = {
            "text": "Pick one?",
            "options": [
                {"text": "A", "is_correct": True, "order": 0},
                {"text": "B", "is_correct": False, "order": 1},
            ],
        }
        # No correct answer.
        res = self.client.post(
            url,
            {
                **base,
                "options": [
                    {"text": "A", "is_correct": False, "order": 0},
                    {"text": "B", "is_correct": False, "order": 1},
                ],
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Two correct answers.
        res = self.client.post(
            url,
            {
                **base,
                "options": [
                    {"text": "A", "is_correct": True, "order": 0},
                    {"text": "B", "is_correct": True, "order": 1},
                ],
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Fewer than two options.
        res = self.client.post(
            url,
            {
                "text": "Pick one?",
                "options": [{"text": "Only", "is_correct": True, "order": 0}],
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_cannot_reach_admin_bank(self):
        register_and_login(self.client)
        res = self.client.get(ADMIN_ASSESSMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.post(
            ADMIN_ASSESSMENTS_URL,
            {"title": "Nope", "skill": self.skill.id},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_delete_assessment_with_attempts(self):
        register_and_login(self.client)
        user = User.objects.get(email="riya@example.com")
        assessment = build_assessment(self.skill)
        self.assessment_url = f"{ASSESSMENTS_URL}/{assessment.id}"
        start = self.client.post(f"{self.assessment_url}/start").data
        self.client.post(
            f"{self.assessment_url}/submit",
            {
                "attempt_id": start["attempt"]["id"],
                "answers": answers_for(start, [True, True, True]),
            },
            format="json",
        )
        self._admin_login()
        res = self.client.delete(f"{ADMIN_ASSESSMENTS_URL}/{assessment.id}")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Assessment.objects.filter(pk=assessment.id).exists())
