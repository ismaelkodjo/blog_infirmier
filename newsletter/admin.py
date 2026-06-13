from django.contrib import admin
from .models import NewsletterSubscriber
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'is_active', 'subscribed_at']
    list_filter = ['is_active']
    list_editable = ['is_active']
