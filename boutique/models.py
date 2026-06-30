from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid


class CategorieProduit(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, default='fas fa-box', help_text="Classe Font Awesome")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Catégorie produit"
        verbose_name_plural = "Catégories produits"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('boutique:categorie', kwargs={'slug': self.slug})


class Produit(models.Model):
    categorie = models.ForeignKey(CategorieProduit, on_delete=models.SET_NULL, null=True, related_name='produits')
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description_courte = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='boutique/produits/', blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    poids_kg = models.DecimalField(max_digits=6, decimal_places=3, default=0, help_text="Poids en kg (pour frais de port)")
    disponible = models.BooleanField(default=True)
    en_vedette = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('boutique:produit', kwargs={'slug': self.slug})

    @property
    def prix_actuel(self):
        return self.prix_promo if self.prix_promo else self.prix

    @property
    def en_promotion(self):
        return bool(self.prix_promo and self.prix_promo < self.prix)

    @property
    def en_stock(self):
        return self.stock > 0


class ZoneLivraison(models.Model):
    nom = models.CharField(max_length=100)
    frais = models.DecimalField(max_digits=8, decimal_places=2)
    delai_jours = models.PositiveIntegerField(default=3, help_text="Délai en jours ouvrables")

    class Meta:
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"
        ordering = ['frais']

    def __str__(self):
        return f"{self.nom} — {self.frais} FCFA"


class Adresse(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adresses', null=True, blank=True)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    adresse_ligne1 = models.CharField(max_length=255)
    adresse_ligne2 = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, default='Togo')
    zone_livraison = models.ForeignKey(ZoneLivraison, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Adresse"

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.ville}"


class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente',     'En attente de paiement'),
        ('confirme',       'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('expedie',        'Expédiée'),
        ('livre',          'Livrée'),
        ('annule',         'Annulée'),
    ]
    MODE_PAIEMENT_CHOICES = [
        ('virement',       'Virement bancaire'),
        ('a_la_livraison', 'Paiement à la livraison'),
        ('mobile_money',   'Mobile Money (Flooz/T-Money)'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes')
    adresse_livraison = models.ForeignKey(Adresse, on_delete=models.SET_NULL, null=True, related_name='commandes')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='virement')
    numero = models.CharField(max_length=20, unique=True, blank=True)
    notes = models.TextField(blank=True)
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    suivi = models.CharField(max_length=200, blank=True, help_text="Numéro de suivi transporteur")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Commande #{self.numero}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"CMD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('boutique:commande_detail', kwargs={'numero': self.numero})


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    nom_produit = models.CharField(max_length=200)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Ligne de commande"

    def __str__(self):
        return f"{self.quantite}× {self.nom_produit}"

    @property
    def sous_total(self):
        if self.prix_unitaire is None or self.quantite is None:
            return 0
        return self.prix_unitaire * self.quantite

class Panier(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"

    def __str__(self):
        return f"Panier {self.session_key}"

    def get_total(self):
        return sum(ligne.sous_total for ligne in self.lignes.all())

    def get_nombre_articles(self):
        return sum(ligne.quantite for ligne in self.lignes.all())


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Ligne de panier"
        unique_together = ('panier', 'produit')

    def __str__(self):
        return f"{self.quantite}× {self.produit.nom}"

    @property
    def sous_total(self):
        return self.produit.prix_actuel * self.quantite
