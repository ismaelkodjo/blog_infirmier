from django.contrib import admin
from .models import Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'speciality', 'institution', 'created_at']
    list_filter = ['role']
    list_editable = ['role']
    search_fields = ['user__username', 'user__email']
