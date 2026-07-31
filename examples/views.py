from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view, permission_classes

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as django_filters
from django.http import HttpResponse, FileResponse
from django.conf import settings

from datetime import timedelta
import csv
import os
import magic
import time

from .models import (
    Category, Tag
)
from .serializers import (
    CategorySerializer,
    TagSerializer,
)
from .filters import DocumentFilter, FolderFilter
from .utils import validate_uploaded_file
from accounts.permissions import CanManageUsers, roles_required




# ============================================================================
# VIEWSETS POUR CATÉGORIES
# ============================================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les catégories de documents
    
    Liste des endpoints :
    - GET /api/documents/categories/ : Liste des catégories
    - GET /api/documents/categories/<id>/ : Détail d'une catégorie
    - POST /api/documents/categories/ : Créer une catégorie (ADMIN)
    - PUT/PATCH /api/documents/categories/<id>/ : Modifier une catégorie (ADMIN)
    - DELETE /api/documents/categories/<id>/ : Supprimer une catégorie (ADMIN)
    """
    queryset = Category.objects.filter(is_active=True).order_by('nom')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'created_at']
    ordering = ['nom']
    
    def get_permissions(self):
        """Seuls les admins peuvent créer/modifier/supprimer"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanManageUsers()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Enregistrer l'utilisateur créateur"""
        serializer.save(created_by=self.request.user)


# ============================================================================
# VIEWSETS POUR TAGS
# ============================================================================

class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les tags
    
    Liste des endpoints :
    - GET /api/documents/tags/ : Liste des tags
    - GET /api/documents/tags/<id>/ : Détail d'un tag
    - POST /api/documents/tags/ : Créer un tag (ADMIN)
    - PUT/PATCH /api/documents/tags/<id>/ : Modifier un tag (ADMIN)
    - DELETE /api/documents/tags/<id>/ : Supprimer un tag (ADMIN)
    """
    queryset = Tag.objects.filter(is_active=True).order_by('nom')
    filterset_class = DocumentFilter
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'created_at']
    ordering = ['nom']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanManageUsers()]
        return super().get_permissions()


# ...