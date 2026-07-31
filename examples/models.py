from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from .utils import validate_uploaded_file, generate_unique_filename, get_file_category
import os 



# ============================================================================
# CATÉGORIES DE DOCUMENTS
# ============================================================================

class Category(models.Model):
    """
    Catégories de documents (ex: Actes de naissance, Délibérations, etc.)
    """
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    couleur = models.CharField(
        max_length=7, 
        default='#1890ff',
        help_text="Code couleur hexadécimal (ex: #1890ff)",
        verbose_name="Couleur"
    )
    icone = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Nom de l'icône Ant Design (ex: FileTextOutlined)",
        verbose_name="Icône"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories_created',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le slug"""
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


# ============================================================================
# TAGS (ÉTIQUETTES)
# ============================================================================

class Tag(models.Model):
    """
    Tags pour classifier les documents (ex: urgent, confidentiel, 2026)
    """
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom du tag")
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    couleur = models.CharField(
        max_length=7,
        default='#52c41a',
        help_text="Code couleur hexadécimal",
        verbose_name="Couleur"
    )
    description = models.CharField(max_length=200, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


# ============================================================================
# DOSSIERS (ARBORESCENCE)
# ============================================================================

# ...

class AuditLog(models.Model):
    """ """


from .middleware import get_client_ip, get_current_request

def create_log(user, action, instance, details=None):
    """
    Helper pour créer des logs MANUELS
    (utilisé uniquement pour DOWNLOAD, VIEW qui n'ont pas de signals)
    """
    try:
        request = get_current_request()
        ip = get_client_ip() if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255] if request else ''
        
        from .models import Document
        
        AuditLog.objects.create(
            user=user,
            action=action,
            document=instance if isinstance(instance, Document) else None,
            details=details or {},
            ip_address=ip,
            user_agent=user_agent
        )
    except Exception as e:
        print(f"⚠️ Erreur log manuel : {e}")



        