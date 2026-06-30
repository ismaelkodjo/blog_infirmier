from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Formation, CategorieFormation, SessionPresentiel, Inscription, ProgressionLecon, Lecon
from .forms import InscriptionForm


def formations_home(request):
    categories = CategorieFormation.objects.all()
    formations_vedette = Formation.objects.filter(active=True, en_vedette=True)[:6]
    type_filtre = request.GET.get('type')
    categorie_slug = request.GET.get('categorie')
    formations = Formation.objects.filter(active=True)
    categorie_active = None
    if type_filtre:
        formations = formations.filter(type_formation=type_filtre)
    if categorie_slug:
        categorie_active = get_object_or_404(CategorieFormation, slug=categorie_slug)
        formations = formations.filter(categorie=categorie_active)
    return render(request, 'formations/home.html', {
        'categories': categories,
        'formations_vedette': formations_vedette,
        'formations': formations,
        'categorie_active': categorie_active,
        'type_filtre': type_filtre,
    })


def formation_detail(request, slug):
    formation = get_object_or_404(Formation, slug=slug, active=True)
    sessions = formation.sessions.filter(statut='ouvert').order_by('date_debut')
    modules = formation.modules.prefetch_related('lecons').order_by('ordre')
    deja_inscrit = False
    if request.user.is_authenticated:
        deja_inscrit = Inscription.objects.filter(
            formation=formation,
            utilisateur=request.user,
            statut__in=['en_attente', 'confirme', 'termine']
        ).exists()
    return render(request, 'formations/detail.html', {
        'formation': formation,
        'sessions': sessions,
        'modules': modules,
        'deja_inscrit': deja_inscrit,
    })


def inscription(request, slug):
    formation = get_object_or_404(Formation, slug=slug, active=True)
    sessions = formation.sessions.filter(statut='ouvert').order_by('date_debut')

    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            ins = form.save(commit=False)
            ins.formation = formation
            session_id = request.POST.get('session')
            if session_id:
                try:
                    ins.session = SessionPresentiel.objects.get(pk=session_id, formation=formation)
                except SessionPresentiel.DoesNotExist:
                    pass
            if request.user.is_authenticated:
                ins.utilisateur = request.user
            ins.montant_paye = 0
            ins.save()
            return redirect('formations:inscription_confirmation', numero=ins.numero)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'prenom': request.user.first_name,
                'nom': request.user.last_name,
                'email': request.user.email,
            }
        form = InscriptionForm(initial=initial)

    return render(request, 'formations/inscription.html', {
        'formation': formation,
        'sessions': sessions,
        'form': form,
    })


def inscription_confirmation(request, numero):
    ins = get_object_or_404(Inscription, numero=numero)
    return render(request, 'formations/inscription_confirmation.html', {'inscription': ins})


@login_required
def espace_apprenant(request):
    inscriptions = Inscription.objects.filter(
        utilisateur=request.user,
        statut__in=['confirme', 'termine']
    ).select_related('formation')
    return render(request, 'formations/espace_apprenant.html', {'inscriptions': inscriptions})


@login_required
def lecon_detail(request, slug, lecon_id):
    formation = get_object_or_404(Formation, slug=slug, active=True)
    deja_inscrit = Inscription.objects.filter(
        formation=formation,
        utilisateur=request.user,
        statut__in=['confirme', 'termine']
    ).exists()
    if not deja_inscrit:
        messages.warning(request, "Vous devez être inscrit à cette formation pour accéder aux leçons.")
        return redirect('formations:detail', slug=slug)
    lecon = get_object_or_404(Lecon, pk=lecon_id, module__formation=formation)
    progression, _ = ProgressionLecon.objects.get_or_create(utilisateur=request.user, lecon=lecon)
    if request.method == 'POST' and request.POST.get('marquer_terminee'):
        from django.utils import timezone
        progression.terminee = True
        progression.date_completion = timezone.now()
        progression.save()
        messages.success(request, "Leçon marquée comme terminée !")
        return redirect('formations:lecon', slug=slug, lecon_id=lecon_id)
    return render(request, 'formations/lecon.html', {
        'formation': formation,
        'lecon': lecon,
        'progression': progression,
    })
