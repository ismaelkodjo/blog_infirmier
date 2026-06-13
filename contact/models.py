"""
Modèles pour le contact et la newsletter.
"""

from django.db import models


class ContactMessage(models.Model):
    """Message de contact."""

    SUBJECT_CHOICES = [
        ('question', 'Question générale'),
        ('collaboration', 'Proposition de collaboration'),
        ('article', 'Suggestion d\'article'),
        ('resource', 'Demande de ressource'),
        ('other', 'Autre'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='question', verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"Message de {self.name} — {self.get_subject_display()}"
