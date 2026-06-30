from django.contrib import admin
from .models import CategorieProduit, Produit, ZoneLivraison, Adresse, Commande, LigneCommande, Panier, LignePanier


@admin.register(CategorieProduit)
class CategorieProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ordre', 'slug']
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ['ordre', 'nom']


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ['nom_produit', 'prix_unitaire', 'quantite', 'sous_total']

    def sous_total(self, obj):
        if obj.pk is None:
            return "-"
        return f"{obj.sous_total:,.0f} FCFA"
    sous_total.short_description = "Sous-total"


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'prix', 'prix_promo', 'stock', 'disponible', 'en_vedette']
    list_filter = ['categorie', 'disponible', 'en_vedette']
    list_editable = ['prix', 'stock', 'disponible', 'en_vedette']
    search_fields = ['nom', 'description']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(ZoneLivraison)
class ZoneLivraisonAdmin(admin.ModelAdmin):
    list_display = ['nom', 'frais', 'delai_jours']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['numero', 'get_client', 'statut', 'mode_paiement', 'total', 'date_creation']
    list_filter = ['statut', 'mode_paiement']
    search_fields = ['numero', 'adresse_livraison__prenom', 'adresse_livraison__nom']
    readonly_fields = ['numero', 'date_creation', 'date_modification']
    inlines = [LigneCommandeInline]
    ordering = ['-date_creation']

    def get_client(self, obj):
        if obj.adresse_livraison:
            return f"{obj.adresse_livraison.prenom} {obj.adresse_livraison.nom}"
        return obj.utilisateur or "—"
    get_client.short_description = "Client"
