from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Produit, CategorieProduit, Panier, LignePanier, Commande, LigneCommande, Adresse, ZoneLivraison
from .forms import CommandeForm, AdresseForm


def _get_or_create_panier(request):
    if not request.session.session_key:
        request.session.create()
    panier, _ = Panier.objects.get_or_create(session_key=request.session.session_key)
    return panier


def boutique_home(request):
    categories = CategorieProduit.objects.all()
    produits_vedette = Produit.objects.filter(disponible=True, en_vedette=True)[:8]
    categorie_slug = request.GET.get('categorie')
    categorie_active = None
    produits = Produit.objects.filter(disponible=True)
    if categorie_slug:
        categorie_active = get_object_or_404(CategorieProduit, slug=categorie_slug)
        produits = produits.filter(categorie=categorie_active)
    return render(request, 'boutique/home.html', {
        'categories': categories,
        'produits_vedette': produits_vedette,
        'produits': produits,
        'categorie_active': categorie_active,
    })


def produit_detail(request, slug):
    produit = get_object_or_404(Produit, slug=slug, disponible=True)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie, disponible=True
    ).exclude(pk=produit.pk)[:4]
    return render(request, 'boutique/produit_detail.html', {
        'produit': produit,
        'produits_similaires': produits_similaires,
    })


def panier_detail(request):
    panier = _get_or_create_panier(request)
    zones = ZoneLivraison.objects.all()
    return render(request, 'boutique/panier.html', {
        'panier': panier,
        'zones': zones,
    })


def panier_ajouter(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id, disponible=True)
    panier = _get_or_create_panier(request)
    quantite = int(request.POST.get('quantite', 1))
    ligne, created = LignePanier.objects.get_or_create(panier=panier, produit=produit)
    if not created:
        ligne.quantite += quantite
    else:
        ligne.quantite = quantite
    ligne.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'nombre': panier.get_nombre_articles(),
            'message': f"« {produit.nom} » ajouté au panier",
        })
    messages.success(request, f"« {produit.nom} » ajouté au panier.")
    return redirect('boutique:panier')


def panier_modifier(request, ligne_id):
    panier = _get_or_create_panier(request)
    ligne = get_object_or_404(LignePanier, pk=ligne_id, panier=panier)
    quantite = int(request.POST.get('quantite', 1))
    if quantite <= 0:
        ligne.delete()
    else:
        ligne.quantite = quantite
        ligne.save()
    return redirect('boutique:panier')


def panier_supprimer(request, ligne_id):
    panier = _get_or_create_panier(request)
    LignePanier.objects.filter(pk=ligne_id, panier=panier).delete()
    return redirect('boutique:panier')


def commander(request):
    panier = _get_or_create_panier(request)
    if not panier.lignes.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('boutique:home')
    zones = ZoneLivraison.objects.all()
    if request.method == 'POST':
        adresse_form = AdresseForm(request.POST)
        commande_form = CommandeForm(request.POST)
        if adresse_form.is_valid() and commande_form.is_valid():
            adresse = adresse_form.save(commit=False)
            if request.user.is_authenticated:
                adresse.utilisateur = request.user
            zone_id = request.POST.get('zone_livraison')
            if zone_id:
                try:
                    adresse.zone_livraison = ZoneLivraison.objects.get(pk=zone_id)
                except ZoneLivraison.DoesNotExist:
                    pass
            adresse.save()

            commande = commande_form.save(commit=False)
            commande.adresse_livraison = adresse
            if request.user.is_authenticated:
                commande.utilisateur = request.user
            commande.sous_total = panier.get_total()
            frais = adresse.zone_livraison.frais if adresse.zone_livraison else 0
            commande.frais_livraison = frais
            commande.total = commande.sous_total + frais
            commande.save()

            for ligne in panier.lignes.all():
                LigneCommande.objects.create(
                    commande=commande,
                    produit=ligne.produit,
                    nom_produit=ligne.produit.nom,
                    prix_unitaire=ligne.produit.prix_actuel,
                    quantite=ligne.quantite,
                )
                if ligne.produit.stock >= ligne.quantite:
                    ligne.produit.stock -= ligne.quantite
                    ligne.produit.save()

            panier.lignes.all().delete()
            return redirect('boutique:commande_confirmation', numero=commande.numero)
    else:
        adresse_form = AdresseForm()
        commande_form = CommandeForm()

    return render(request, 'boutique/commander.html', {
        'panier': panier,
        'adresse_form': adresse_form,
        'commande_form': commande_form,
        'zones': zones,
    })


def commande_confirmation(request, numero):
    commande = get_object_or_404(Commande, numero=numero)
    return render(request, 'boutique/commande_confirmation.html', {'commande': commande})
