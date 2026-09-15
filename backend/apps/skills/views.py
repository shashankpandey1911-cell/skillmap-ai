"""Skill catalog and student skill endpoints."""

from rest_framework import generics, status
from rest_framework.response import Response

from apps.core.permissions import IsStudent

from .models import Skill, UserSkill
from .serializers import SkillSerializer, UserSkillSerializer, UserSkillWriteSerializer


class SkillCatalogView(generics.ListAPIView):
    """GET /skills/catalog?search=&category= — active catalog entries.

    Authenticated users only (global default permission applies).
    """

    serializer_class = SkillSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Skill.objects.filter(is_active=True)
        search = self.request.query_params.get("search", "").strip()
        category = self.request.query_params.get("category", "").strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        if category:
            queryset = queryset.filter(category__iexact=category)
        return queryset


class UserSkillListCreateView(generics.ListCreateAPIView):
    """GET/POST the authenticated student's skills.

    ?search= filters by skill name; ?category= filters by catalog category.
    """

    permission_classes = [IsStudent]
    serializer_class = UserSkillSerializer  # GET representation
    pagination_class = None

    def get_queryset(self):
        queryset = UserSkill.objects.filter(user=self.request.user).select_related("skill")
        search = self.request.query_params.get("search", "").strip()
        category = self.request.query_params.get("category", "").strip()
        if search:
            queryset = queryset.filter(skill__name__icontains=search)
        if category:
            queryset = queryset.filter(skill__category__iexact=category)
        return queryset

    def create(self, request, *args, **kwargs):
        """Validate with the write serializer, respond with the read shape."""
        serializer = UserSkillWriteSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        read = UserSkillSerializer(serializer.instance)
        headers = self.get_success_headers(read.data)
        return Response(read.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Owner-scoped PATCH/DELETE of one of the student's skills."""

    permission_classes = [IsStudent]

    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = UserSkillWriteSerializer(
            instance,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(UserSkillSerializer(serializer.instance).data)