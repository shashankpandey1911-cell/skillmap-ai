"""Create the demo users used for the hackathon walkthrough.

Passwords are read from the environment (DEMO_ADMIN_PASSWORD, etc.) with
obvious demo defaults — these are local/demo-only credentials, never used
in production. Run with: python manage.py seed_demo
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.applications.seed_data import ensure_demo_applications
from apps.assessments.seed_data import ensure_demo_assessments
from apps.careers.seed_data import ensure_demo_careers
from apps.feedback.seed_data import ensure_demo_feedback
from apps.learning.seed_data import ensure_demo_resources
from apps.opportunities.seed_data import ensure_demo_opportunities
from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.students.models import Certification, Project, StudentProfile

User = get_user_model()

DEMO_USERS = [
    {
        "username": "demo_admin",
        "email": "admin@skillmap.ai",
        "password": os.environ.get("DEMO_ADMIN_PASSWORD", "Admin@2026"),
        "role": User.Role.ADMIN,
        "first_name": "Platform",
        "last_name": "Admin",
    },
    {
        "username": "demo_professor",
        "email": "professor@skillmap.ai",
        "password": os.environ.get("DEMO_PROFESSOR_PASSWORD", "Prof@2026"),
        "role": User.Role.PROFESSOR,
        "first_name": "Anita",
        "last_name": "Desai",
    },
    {
        "username": "demo_student",
        "email": "student@skillmap.ai",
        "password": os.environ.get("DEMO_STUDENT_PASSWORD", "Student@2026"),
        "role": User.Role.STUDENT,
        "first_name": "Rohan",
        "last_name": "Mehta",
        "profile": {
            "college": "National Institute of Technology, Trichy",
            "course": "B.Tech Computer Science",
            "branch": "Computer Science and Engineering",
            "year": 3,
            "cgpa": 8.6,
            "semester": 5,
            "achievements": "Winner, Smart India Hackathon 2025; Dean's List (3 semesters)",
            "career_goal": "Software Development Engineer at a top product company",
            "preferred_domain": "Full-stack / AI-ML",
            "interests": "Machine learning, open source, competitive programming",
            "about": "CSE undergraduate passionate about building products that solve real problems.",
            "linkedin_url": "https://linkedin.com/in/rohanmehta",
            "github_url": "https://github.com/rohanmehta",
        },
        "skills": [  # (skill name, proficiency 1-5, experience level)
            ("Python", 5, "ADVANCED"),
            ("Django", 4, "ADVANCED"),
            ("React", 4, "INTERMEDIATE"),
            ("SQL", 4, "INTERMEDIATE"),
            ("PostgreSQL", 3, "INTERMEDIATE"),
            ("Git", 5, "ADVANCED"),
            ("Docker", 3, "INTERMEDIATE"),
            ("Machine Learning", 4, "INTERMEDIATE"),
            ("Data Visualization", 3, "INTERMEDIATE"),
            ("Communication", 4, "ADVANCED"),
        ],
        "projects": [
            {
                "name": "SkillMap AI",
                "description": "Career-guidance platform that scores student skills, finds gaps and matches careers.",
                "technologies": "React, Django REST Framework, PostgreSQL",
                "github_url": "https://github.com/rohanmehta/skillmap",
                "demo_url": "https://skillmap.demo",
            },
            {
                "name": "Campus Placement Tracker",
                "description": "Web app for students to track drives, deadlines and preparation progress.",
                "technologies": "React, Node.js, MongoDB",
                "github_url": "https://github.com/rohanmehta/placement-tracker",
            },
        ],
        "certifications": [
            {
                "name": "AWS Certified Cloud Practitioner",
                "provider": "Amazon Web Services",
                "issued_date": "2025-06-15",
                "credential_url": "https://www.credly.com/badges/aws-cp",
            },
            {
                "name": "Python for Everybody Specialization",
                "provider": "Coursera / University of Michigan",
                "issued_date": "2024-11-20",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Create the demo admin, professor and student accounts."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all demo users and reseed from scratch',
        )

    def handle(self, *args, **options):
        if options['reset']:
            emails = [u['email'] for u in DEMO_USERS]
            deleted = User.objects.filter(email__in=emails).delete()
            self.stdout.write(self.style.WARNING(f'Deleted existing demo data: {deleted}'))
        created_catalog = ensure_skill_catalog()
        if created_catalog:
            self.stdout.write(self.style.SUCCESS(f"Seeded {created_catalog} catalog skills."))
        created_assessments = ensure_demo_assessments()
        if created_assessments:
            self.stdout.write(
                self.style.SUCCESS(f"Seeded {created_assessments} demo assessments.")
            )
        created_careers = ensure_demo_careers()
        if created_careers:
            self.stdout.write(
                self.style.SUCCESS(f"Seeded {created_careers} demo careers.")
            )
        created_resources = ensure_demo_resources()
        if created_resources:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {created_resources} demo learning resources."
                )
            )
        created_opportunities = ensure_demo_opportunities()
        if created_opportunities:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {created_opportunities} demo opportunities."
                )
            )
        created = []
        for data in DEMO_USERS:
            email = data["email"]
            user = User.objects.filter(email=email).first()
            if user is None:
                user = User(
                    username=data["username"],
                    email=email,
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    role=data["role"],
                )
                user.set_password(data["password"])
                user.save()
                profile = data.get("profile")
                if profile:
                    StudentProfile.objects.create(user=user, **profile)
                for project in data.get("projects", []):
                    Project.objects.create(user=user, **project)
                for cert in data.get("certifications", []):
                    Certification.objects.create(user=user, **cert)
                for skill_name, proficiency, experience in data.get("skills", []):
                    skill = Skill.objects.filter(name=skill_name).first()
                    if skill:
                        UserSkill.objects.create(
                            user=user,
                            skill=skill,
                            proficiency_level=proficiency,
                            experience_level=experience,
                        )
                created.append(data["username"])
            else:
                self.stdout.write(f"  - {data['username']} already exists, skipped.")

        created_applications = ensure_demo_applications()
        if created_applications:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {created_applications} demo applications."
                )
            )
        created_feedback = ensure_demo_feedback()
        if created_feedback:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {created_feedback} demo career feedback entries."
                )
            )

        self.stdout.write(self.style.SUCCESS("Demo users ready:"))
        for data in DEMO_USERS:
            self.stdout.write(
                f"  {data['email']:<28} / {data['password']}  "
                f"({data['role'].lower()})"
            )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created: {', '.join(created)}"))