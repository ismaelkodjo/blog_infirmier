"""
Vue de contact — sans crispy_forms.
"""

from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message...', 'rows': 6}),
        }


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            msg.ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            msg.save()
            try:
                send_mail(
                    subject=f'[Contact Blog] {msg.get_subject_display()} de {msg.name}',
                    message=f'Nom: {msg.name}\nEmail: {msg.email}\n\nMessage:\n{msg.message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER or 'snanliebe@gmail.com'],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Votre message a été envoyé avec succès ! Je vous répondrai dans les plus brefs délais.")
            return redirect('contact:contact_view')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form, 'title': 'Contact'})
