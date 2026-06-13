from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsletterSubscriber

def subscribe_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        if email:
            sub, created = NewsletterSubscriber.objects.get_or_create(
                email=email, defaults={'first_name': first_name, 'is_active': True})
            if not created and not sub.is_active:
                sub.is_active = True; sub.save()
                messages.success(request, "Votre abonnement a été réactivé !")
            elif created:
                messages.success(request, "Vous êtes maintenant abonné à la newsletter !")
            else:
                messages.info(request, "Vous êtes déjà abonné.")
        else:
            messages.error(request, "Veuillez saisir un email valide.")
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))

def unsubscribe_view(request, token):
    try:
        sub = NewsletterSubscriber.objects.get(token=token)
        sub.is_active = False; sub.save()
        messages.success(request, "Vous avez été désinscrit.")
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, "Lien de désinscription invalide.")
    return render(request, 'newsletter/unsubscribed.html', {'title': 'Désinscription'})
