"""Demo assessments for the hackathon walkthrough.

Each entry seeds a published Assessment with questions and options (exactly
one correct per question). Idempotent: assessments already present by title
are skipped.
"""

from apps.skills.models import Skill
from apps.users.models import User

from .models import Assessment, Option, Question

_DEMO_ASSESSMENTS = [
    {
        "title": "Python Fundamentals",
        "description": "Core Python: data types, functions, collections, exceptions and operators.",
        "skill": "Python",
        "difficulty": Assessment.Difficulty.INTERMEDIATE,
        "duration_minutes": 10,
        "questions": [
            {
                "text": "Which keyword is used to define a function in Python?",
                "options": ["function", "def", "func", "define"],
                "correct": 1,
            },
            {
                "text": "Which of these data types is immutable?",
                "options": ["List", "Set", "Tuple", "Dictionary"],
                "correct": 2,
            },
            {
                "text": "What does `print(type([]))` output?",
                "options": ["<class 'list'>", "<class 'tuple'>", "<class 'array'>", "<class 'dict'>"],
                "correct": 0,
            },
            {
                "text": "Which statement is used to handle exceptions in Python?",
                "options": ["if / else", "for / while", "try / except", "switch / case"],
                "correct": 2,
            },
            {
                "text": "Which list method appends an element at the end?",
                "options": ["push()", "append()", "add()", "insert()"],
                "correct": 1,
            },
            {
                "text": "What is the result of `2 ** 3`?",
                "options": ["6", "8", "9", "5"],
                "correct": 1,
            },
        ],
    },
    {
        "title": "SQL Basics",
        "description": "Structured Query Language: queries, joins, aggregation and filtering.",
        "skill": "SQL",
        "difficulty": Assessment.Difficulty.BEGINNER,
        "duration_minutes": 8,
        "questions": [
            {
                "text": "Which SQL statement retrieves data from a table?",
                "options": ["GET", "SELECT", "FETCH", "USE"],
                "correct": 1,
            },
            {
                "text": "Which keyword is used to combine rows from two tables on a condition?",
                "options": ["MERGE", "LINK", "JOIN", "COMBINE"],
                "correct": 2,
            },
            {
                "text": "Which aggregate function counts the number of rows?",
                "options": ["SUM()", "AVG()", "TOTAL()", "COUNT()"],
                "correct": 3,
            },
            {
                "text": "Which clause filters groups created by GROUP BY?",
                "options": ["WHERE", "HAVING", "FILTER", "LIMIT"],
                "correct": 1,
            },
        ],
    },
]


def ensure_demo_assessments() -> int:
    """Create the demo assessments (published) if they don't exist yet."""
    created = 0
    admin_user = User.objects.filter(role=User.Role.ADMIN).first()
    for spec in _DEMO_ASSESSMENTS:
        if Assessment.objects.filter(title=spec["title"]).exists():
            continue
        skill = Skill.objects.filter(name=spec["skill"]).first()
        if skill is None:
            continue  # catalog not seeded yet
        assessment = Assessment.objects.create(
            title=spec["title"],
            description=spec["description"],
            skill=skill,
            difficulty=spec["difficulty"],
            duration_minutes=spec["duration_minutes"],
            is_published=True,
            created_by=admin_user,
        )
        for position, qspec in enumerate(spec["questions"], start=1):
            question = Question.objects.create(
                assessment=assessment,
                text=qspec["text"],
                order=position,
            )
            Option.objects.bulk_create(
                [
                    Option(
                        question=question,
                        text=text,
                        is_correct=index == qspec["correct"],
                        order=index,
                    )
                    for index, text in enumerate(qspec["options"])
                ]
            )
        created += 1
    return created
