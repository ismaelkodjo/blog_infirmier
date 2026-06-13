from django.db import models
import uuid

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Prénom")
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="Token")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Abonné Newsletter"
        verbose_name_plural = "Abonnés Newsletter"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
