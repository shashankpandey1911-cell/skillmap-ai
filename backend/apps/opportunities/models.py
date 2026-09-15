"""Job / internship / hackathon / competition listings (Phase 9).

Opportunity             — a posting students can browse: role, company, type,
                           description, eligibility, location/remote option,
                           deadline, external application link and compensation
                           (salary / stipend / prize). Only ACTIVE postings with
                           a future (or no) deadline are shown to students.

OpportunityRequirement  — a skill an opportunity expects and the minimum
                           proficiency (0-100) that counts as meeting it. The
                           browse/detail endpoints compare these against a
                           student's UserSkill records to show a real match %.

Applications that students submit against an opportunity live in the
`applications` app (Phase 10).
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.skills.models import Skill


class Opportunity(models.Model):
    """A single job, internship, hackathon or competition posting."""

    class Type(models.TextChoices):
        JOB = "JOB", "Job"
        INTERNSHIP = "INTERNSHIP", "Internship"
        HACKATHON = "HACKATHON", "Hackathon"
        COMPETITION = "COMPETITION", "Competition"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DRAFT = "DRAFT", "Draft"
        CLOSED = "CLOSED", "Closed"

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    opportunity_type = models.CharField(max_length=20, choices=Type.choices)
    description = models.TextField(blank=True)
    eligibility = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)
    # Optional; an empty deadline means the posting runs until further notice.
    deadline = models.DateField(null=True, blank=True)
    # External application page (careers site / form). Students who apply do so
    # there; the platform records applications in the `applications` app.
    application_link = models.URLField(blank=True)
    # Salary / stipend / prize details when available (free text: "₹8–16 LPA",
    # "₹25k/month stipend", "Prizes worth ₹2L").
    compensation = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} @ {self.company}"


class OpportunityRequirement(models.Model):
    """A skill an opportunity expects, with the minimum level that counts.

    min_level mirrors CareerSkillRequirement.target_level so the match math is
    directly comparable with the student's 0-100 skill levels.
    """

    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="requirements"
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="opportunity_requirements"
    )
    min_level = models.PositiveSmallIntegerField(
        default=60, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        ordering = ["-min_level", "skill__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["opportunity", "skill"],
                name="unique_opportunity_skill_requirement",
            )
        ]

    def __str__(self) -> str:
        return f"{self.opportunity.title} — {self.skill.name} (≥{self.min_level})"
