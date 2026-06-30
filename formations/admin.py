from django.contrib import admin
from .models import (
    CategorieFormation, Formation, ModuleFormation, Lecon,
    SessionPresentiel, Inscription, ProgressionLecon
)


@admin.register(CategorieFormation)
class CategorieFormationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


class LeconInline(admin.TabularInline):
    model = Lecon
    extra = 1
    fields = ['ordre', 'titre', 'type_lecon', 'duree_minutes', 'gratuite']


class ModuleInline(admin.StackedInline):
    model = ModuleFormation
    extra = 0
    show_change_link = True


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'categorie', 'type_formation', 'niveau', 'prix', 'active', 'en_vedette']
    list_filter = ['type_formation', 'niveau', 'active', 'en_vedette', 'categorie']
    list_editable = ['prix', 'active', 'en_vedette']
    search_fields = ['titre', 'description']
    prepopulated_fields = {'slug': ('titre',)}
    inlines = [ModuleInline]


@admin.register(ModuleFormation)
class ModuleFormationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'formation', 'ordre', 'duree_minutes']
    list_filter = ['formation']
    inlines = [LeconInline]


@admin.register(SessionPresentiel)
class SessionPresentielAdmin(admin.ModelAdmin):
    list_display = ['formation', 'date_debut', 'ville', 'places_max', 'places_disponibles', 'statut']
    list_filter = ['statut', 'ville', 'formation']
    ordering = ['date_debut']

    def places_disponibles(self, obj):
        return obj.places_disponibles
    places_disponibles.short_description = "Places dispo"


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'prenom', 'nom', 'formation', 'statut', 'mode_paiement', 'montant_paye', 'date_inscription']
    list_filter = ['statut', 'mode_paiement', 'formation']
    search_fields = ['numero', 'prenom', 'nom', 'email']
    readonly_fields = ['numero', 'date_inscription']
    ordering = ['-date_inscription']
