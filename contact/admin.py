from django.contrib import admin
from .models import ContactMessage
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['subject', 'is_read']
    list_editable = ['is_read']
    readonly_fields = ['name','email','subject','message','ip_address','created_at']
