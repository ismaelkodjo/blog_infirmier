from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from .models import NewsletterSubscriber


class SubscribeForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50, required=False)


@require_POST
@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def subscribe_view(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        first_name = form.cleaned_data.get('first_name', '')
        sub, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={'first_name': first_name, 'is_active': True})
        if not created and not sub.is_active:
            sub.is_active = True
            sub.save()
            messages.success(request, "Votre abonnement a été réactivé !")
        elif created:
            messages.success(request, "Vous êtes maintenant abonné à la newsletter !")
        else:
            messages.info(request, "Vous êtes déjà abonné.")
    else:
        messages.error(request, "Veuillez saisir un email valide.")
    return redirect('core:home')


def unsubscribe_confirm_view(request, token):
    """Affiche une page de confirmation avant de désinscrire (protection contre les crawlers)."""
    sub = get_object_or_404(NewsletterSubscriber, token=token, is_active=True)
    return render(request, 'newsletter/unsubscribe_confirm.html', {
        'token': token,
        'title': 'Confirmer la désinscription',
    })


@require_POST
def unsubscribe_view(request, token):
    """Désinscription effective — nécessite une requête POST."""
    try:
        sub = NewsletterSubscriber.objects.get(token=token)
        sub.is_active = False
        sub.unsubscribed_at = timezone.now()
        sub.save()
        messages.success(request, "Vous avez été désinscrit avec succès.")
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "Lien de désinscription invalide.")
    return render(request, 'newsletter/unsubscribed.html', {'title': 'Désinscription'})
