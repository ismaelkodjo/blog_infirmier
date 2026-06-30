"""
Services de paiement. Adapte les appels API PayPal/MoMo à ton implémentation
existante dans resources/services.py si tu en as déjà une — l'idée ici est
de centraliser pour ne plus la dupliquer dans boutique/ et formations/.
"""
import requests
from django.conf import settings


class PayPalService:
    """Wrapper autour de l'API PayPal Orders v2."""

    BASE_URL = (
        "https://api-m.sandbox.paypal.com"
        if settings.DEBUG
        else "https://api-m.paypal.com"
    )

    @classmethod
    def _get_access_token(cls) -> str:
        response = requests.post(
            f"{cls.BASE_URL}/v1/oauth2/token",
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    @classmethod
    def creer_commande(cls, montant: str, devise: str = "USD") -> dict:
        """Crée une commande PayPal et retourne l'order_id + lien d'approbation."""
        token = cls._get_access_token()
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {"amount": {"currency_code": devise, "value": montant}}
            ],
        }
        response = requests.post(
            f"{cls.BASE_URL}/v2/checkout/orders",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def capturer_commande(cls, order_id: str) -> dict:
        """Capture le paiement après approbation de l'utilisateur sur PayPal."""
        token = cls._get_access_token()
        response = requests.post(
            f"{cls.BASE_URL}/v2/checkout/orders/{order_id}/capture",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


class MobileMoneyService:
    """
    Wrapper Mobile Money (MTN/Moov). Adapte l'URL et les champs au fournisseur
    que tu utilises déjà (ex. agrégateur comme PayGate, Fedapay, CinetPay...).
    """

    @classmethod
    def initier_paiement(cls, telephone: str, montant: str, reseau: str) -> dict:
        endpoint = settings.MOBILE_MONEY_API_URL
        payload = {
            "phone": telephone,
            "amount": montant,
            "network": reseau,  # "mtn" ou "moov"
            "currency": "XOF",
        }
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Authorization": f"Bearer {settings.MOBILE_MONEY_API_KEY}"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def verifier_statut(cls, reference: str) -> dict:
        endpoint = f"{settings.MOBILE_MONEY_API_URL}/{reference}/status"
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {settings.MOBILE_MONEY_API_KEY}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()