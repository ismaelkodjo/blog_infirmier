from decimal import Decimal
from .models import Produit

CART_SESSION_KEY = "panier"


class Cart:
    """Panier basé sur la session : léger, pas d'écriture DB pour un visiteur qui navigue."""

    def __init__(self, request):
        self.session = request.session
        panier = self.session.get(CART_SESSION_KEY)
        if panier is None:
            panier = self.session[CART_SESSION_KEY] = {}
        self.panier = panier

    def ajouter(self, produit: Produit, quantite: int = 1):
        produit_id = str(produit.id)
        if produit_id not in self.panier:
            self.panier[produit_id] = {"quantite": 0, "prix": str(produit.prix)}
        self.panier[produit_id]["quantite"] += quantite
        self.sauvegarder()

    def retirer(self, produit: Produit):
        produit_id = str(produit.id)
        if produit_id in self.panier:
            del self.panier[produit_id]
            self.sauvegarder()

    def sauvegarder(self):
        self.session.modified = True

    def vider(self):
        self.session[CART_SESSION_KEY] = {}
        self.sauvegarder()

    def __iter__(self):
        produit_ids = self.panier.keys()
        produits = Produit.objects.filter(id__in=produit_ids)
        panier = self.panier.copy()
        for produit in produits:
            panier[str(produit.id)]["produit"] = produit

        for item in panier.values():
            item["prix"] = Decimal(item["prix"])
            item["sous_total"] = item["prix"] * item["quantite"]
            yield item

    def __len__(self):
        return sum(item["quantite"] for item in self.panier.values())

    def total(self) -> Decimal:
        return sum(Decimal(item["prix"]) * item["quantite"] for item in self.panier.values())