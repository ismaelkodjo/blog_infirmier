"""
Vues pour les ressources téléchargeables.
"""

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import Q, F
from .models import Resource
import os


def resource_list(request):
    """Liste des ressources publiques avec filtrage et recherche."""
    resources = Resource.objects.filter(is_public=True).select_related('author', 'category')

    # Filtrage par type de fichier
    file_type = request.GET.get('type', '')
    if file_type:
        resources = resources.filter(file_type=file_type)

    # Recherche full-text basique
    query = request.GET.get('q', '')
    if query:
        resources = resources.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'resources/resource_list.html', {
        'resources': resources,
        'file_type': file_type,
        'query': query,
        'title': 'Ressources',
        # Compteurs par type pour les filtres UI
        'type_choices': Resource.TYPE_CHOICES,
    })


def resource_detail(request, slug):
    """Détail d'une ressource avec ressources liées."""
    resource = get_object_or_404(Resource, slug=slug, is_public=True)
    related = Resource.objects.filter(
        is_public=True,
        category=resource.category
    ).exclude(pk=resource.pk)[:4]

    return render(request, 'resources/resource_detail.html', {
        'resource': resource,
        'related': related,
        'title': resource.title,
    })


def resource_download(request, slug):
    """
    Sert le fichier en téléchargement et incrémente le compteur.

    Corrections apportées :
    - Import F propre (plus de __import__ hacké)
    - Utilise resource.file.open() au lieu de open(path) : compatible
      avec les storages distants (S3, etc.)
    - Content-Type explicite selon le type de fichier
    - Gestion FileNotFoundError propre
    """
    resource = get_object_or_404(Resource, slug=slug, is_public=True)

    if not resource.file:
        raise Http404("Fichier non disponible.")

    # Incrémente sans recharger l'objet entier
    Resource.objects.filter(pk=resource.pk).update(
        download_count=F('download_count') + 1
    )

    # Map type → Content-Type MIME
    mime_types = {
        'pdf':         'application/pdf',
        'word':        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'excel':       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'powerpoint':  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'other':       'application/octet-stream',
    }
    content_type = mime_types.get(resource.file_type, 'application/octet-stream')
    filename = os.path.basename(resource.file.name)

    try:
        # resource.file.open() est compatible S3/local contrairement à open(path)
        response = FileResponse(resource.file.open('rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except (FileNotFoundError, OSError):
        raise Http404("Fichier introuvable sur le serveur.")
