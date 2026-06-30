# payments/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Transaction
from .services import PayPalService


@login_required
def paypal_capture(request, transaction_id):
    """Capture une commande PayPal et redirige vers la confirmation de l'objet lié."""
    transaction = get_object_or_404(Transaction, id=transaction_id, utilisateur=request.user)
    order_id = request.GET.get("token")  # PayPal renvoie le token dans l'URL de retour

    resultat = PayPalService.capturer_commande(order_id)
    if resultat.get("status") == "COMPLETED":
        transaction.marquer_validee(reference_externe=order_id)
        # content_object peut être un Order (vente) ou une Inscription (formations)
        if hasattr(transaction.content_object, "valider_paiement"):
            transaction.content_object.valider_paiement()
        return redirect(transaction.content_object.get_absolute_url())

    transaction.statut = Transaction.Statut.ECHOUEE
    transaction.save(update_fields=["statut"])
    return redirect("boutique:checkout_echec")


@csrf_exempt
def momo_webhook(request):
    """Webhook appelé par l'agrégateur Mobile Money à la confirmation du paiement."""
    reference = request.POST.get("reference")
    statut = request.POST.get("status")

    transaction = get_object_or_404(Transaction, reference_externe=reference)
    if statut == "SUCCESS":
        transaction.marquer_validee()
        if hasattr(transaction.content_object, "valider_paiement"):
            transaction.content_object.valider_paiement()
    else:
        transaction.statut = Transaction.Statut.ECHOUEE
        transaction.save(update_fields=["statut"])

    return JsonResponse({"ok": True})