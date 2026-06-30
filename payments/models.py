from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Transaction(models.Model):
    """
    Transaction générique : peut être liée à n'importe quel objet payable
    (Order de vente, Inscription à une formation, Resource premium...)
    via content_type/object_id, ce qui évite de dupliquer la logique de
    paiement dans chaque app.
    """

    class Methode(models.TextChoices):
        PAYPAL = "paypal", "PayPal"
        MTN = "mtn", "MTN Mobile Money"
        MOOV = "moov", "Moov Money"

    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        VALIDEE = "validee", "Validée"
        ECHOUEE = "echouee", "Échouée"
        REMBOURSEE = "remboursee", "Remboursée"

    # Lien générique vers l'objet payé (Order, Inscription, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, default="XOF")
    methode = models.CharField(max_length=10, choices=Methode.choices)
    statut = models.CharField(
        max_length=15, choices=Statut.choices, default=Statut.EN_ATTENTE
    )
    reference_externe = models.CharField(
        max_length=120, blank=True,
        help_text="ID PayPal ou ID transaction Mobile Money"
    )
    telephone = models.CharField(
        max_length=20, blank=True,
        help_text="Requis pour Mobile Money"
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-cree_le"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self):
        return f"{self.get_methode_display()} - {self.montant} {self.devise} ({self.statut})"

    def marquer_validee(self, reference_externe: str = ""):
        self.statut = self.Statut.VALIDEE
        if reference_externe:
            self.reference_externe = reference_externe
        self.save(update_fields=["statut", "reference_externe", "maj_le"])