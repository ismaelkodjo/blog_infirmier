"""
Modèles pour les ressources téléchargeables.
"""

import os
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from blog.models import Category


ALLOWED_RESOURCE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def validate_resource_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_RESOURCE_EXTENSIONS:
        raise ValidationError(
            f"Type de fichier non autorisé. Extensions acceptées : {', '.join(sorted(ALLOWED_RESOURCE_EXTENSIONS))}"
        )


def validate_image_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Type d'image non autorisé. Extensions acceptées : {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
        )


class Resource(models.Model):
    """Ressource téléchargeable (PDF, Word, Excel, PPT)."""

    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('excel', 'Excel'),
        ('powerpoint', 'PowerPoint'),
        ('other', 'Autre'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    file = models.FileField(upload_to='resources/', verbose_name="Fichier", validators=[validate_resource_file])
    file_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='pdf', verbose_name="Type de fichier")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources', verbose_name="Catégorie")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources', verbose_name="Auteur")
    thumbnail = models.ImageField(upload_to='resources/thumbnails/', blank=True, null=True, verbose_name="Miniature", validators=[validate_image_file])
    download_count = models.PositiveIntegerField(default=0, verbose_name="Téléchargements")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    is_public = models.BooleanField(default=True, verbose_name="Public")

    class Meta:
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Resource.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('resources:resource_detail', kwargs={'slug': self.slug})

    def get_icon(self):
        icons = {
            'pdf': 'bi-file-earmark-pdf',
            'word': 'bi-file-earmark-word',
            'excel': 'bi-file-earmark-excel',
            'powerpoint': 'bi-file-earmark-slides',
            'other': 'bi-file-earmark',
        }
        return icons.get(self.file_type, 'bi-file-earmark')

    def get_color(self):
        colors = {
            'pdf': 'danger',
            'word': 'primary',
            'excel': 'success',
            'powerpoint': 'warning',
            'other': 'secondary',
        }
        return colors.get(self.file_type, 'secondary')
