"""
Modèles pour la gestion des utilisateurs et profils.
"""

import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def validate_avatar(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Type d'image non autorisé. Extensions acceptées : {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
        )
    if value.size > 2 * 1024 * 1024:
        raise ValidationError("L'image ne doit pas dépasser 2 Mo.")


class Profile(models.Model):
    """Profil étendu pour chaque utilisateur."""

    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('author', 'Auteur'),
        ('visitor', 'Visiteur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Utilisateur")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='visitor', verbose_name="Rôle")
    bio = models.TextField(blank=True, null=True, verbose_name="Biographie")
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Photo de profil", validators=[validate_avatar])
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    website = models.URLField(blank=True, null=True, verbose_name="Site web")
    linkedin = models.URLField(blank=True, null=True, verbose_name="LinkedIn")
    twitter = models.URLField(blank=True, null=True, verbose_name="Twitter")
    facebook = models.URLField(blank=True, null=True, verbose_name="Facebook")
    speciality = models.CharField(max_length=200, blank=True, null=True, verbose_name="Spécialité")
    institution = models.CharField(max_length=200, blank=True, null=True, verbose_name="Institution")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff

    def is_author(self):
        return self.role in ['admin', 'author'] or self.user.is_staff


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil lors de la création d'un utilisateur."""
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
