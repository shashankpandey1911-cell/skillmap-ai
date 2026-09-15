"""AI assistant serializers."""

from rest_framework import serializers


class ResumeExtractRequestSerializer(serializers.Serializer):
    resume_text = serializers.CharField(max_length=10000)


class ExtractedSkillSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=50)
    confidence = serializers.FloatField(min_value=0, max_value=1)


class ExtractedProjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    technologies = serializers.CharField(max_length=500, required=False, allow_blank=True)


class ExtractedEducationSerializer(serializers.Serializer):
    institution = serializers.CharField(max_length=200, required=False, allow_blank=True)
    degree = serializers.CharField(max_length=100, required=False, allow_blank=True)
    field = serializers.CharField(max_length=100, required=False, allow_blank=True)
    year = serializers.CharField(max_length=20, required=False, allow_blank=True)


class ExtractedExperienceSerializer(serializers.Serializer):
    company = serializers.CharField(max_length=200, required=False, allow_blank=True)
    role = serializers.CharField(max_length=100, required=False, allow_blank=True)
    duration = serializers.CharField(max_length=50, required=False, allow_blank=True)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)


class ResumeExtractResponseSerializer(serializers.Serializer):
    skills = ExtractedSkillSerializer(many=True)
    projects = ExtractedProjectSerializer(many=True)
    education = ExtractedEducationSerializer(many=True)
    experience = ExtractedExperienceSerializer(many=True)


class ApprovedExtractRequestSerializer(serializers.Serializer):
    """Student reviews and approves extracted data before saving."""
    skills = ExtractedSkillSerializer(many=True, required=False)
    projects = ExtractedProjectSerializer(many=True, required=False)
    education = ExtractedEducationSerializer(many=True, required=False)
    experience = ExtractedExperienceSerializer(many=True, required=False)


class AIRecommendationSerializer(serializers.Serializer):
    career_title = serializers.CharField(max_length=200)
    match_percentage = serializers.FloatField()
    reasoning = serializers.CharField(max_length=2000)
    matching_skills = serializers.ListField(child=serializers.CharField(max_length=100))
    missing_skills = serializers.ListField(child=serializers.CharField(max_length=100))
    preparation_steps = serializers.ListField(child=serializers.CharField(max_length=200))


class AICareerResponseSerializer(serializers.Serializer):
    ai_powered = serializers.BooleanField()
    recommendations = AIRecommendationSerializer(many=True)


class LearningResourceSuggestionSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    url = serializers.URLField(required=False, allow_blank=True)


class LearningRoadmapItemSerializer(serializers.Serializer):
    skill = serializers.CharField(max_length=100)
    gap_percentage = serializers.FloatField()
    priority = serializers.CharField(max_length=20)
    suggested_resources = LearningResourceSuggestionSerializer(many=True)
    estimated_hours = serializers.IntegerField(required=False, allow_null=True)
    learning_path = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class AILearningResponseSerializer(serializers.Serializer):
    ai_powered = serializers.BooleanField()
    career = serializers.CharField(max_length=200)
    roadmap = LearningRoadmapItemSerializer(many=True)


class AIOpportunityExplanationSerializer(serializers.Serializer):
    ai_powered = serializers.BooleanField()
    explanation = serializers.CharField(max_length=2000)
    matching_skills = serializers.ListField(child=serializers.CharField(max_length=100))
    missing_skills = serializers.ListField(child=serializers.CharField(max_length=100))
    preparation_steps = serializers.ListField(child=serializers.CharField(max_length=200))
    confidence_note = serializers.CharField(max_length=500, required=False, allow_blank=True)
