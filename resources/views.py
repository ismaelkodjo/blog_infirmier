"""
Vues pour les ressources téléchargeables.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Resource
import os


def resource_list(request):
    """Liste des ressources."""
    resources = Resource.objects.filter(is_public=True).select_related('author', 'category')

    # Filtrage par type
    file_type = request.GET.get('type', '')
    if file_type:
        resources = resources.filter(file_type=file_type)

    # Recherche
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
    })


def resource_detail(request, slug):
    """Détail d'une ressource."""
    resource = get_object_or_404(Resource, slug=slug, is_public=True)
    related = Resource.objects.filter(
        is_public=True, category=resource.category
    ).exclude(pk=resource.pk)[:4]

    return render(request, 'resources/resource_detail.html', {
        'resource': resource,
        'related': related,
        'title': resource.title,
    })


def resource_download(request, slug):
    """Télécharger une ressource."""
    resource = get_object_or_404(Resource, slug=slug, is_public=True)

    if not resource.file:
        raise Http404("Fichier non disponible.")

    # Incrémenter le compteur
    Resource.objects.filter(pk=resource.pk).update(download_count=__import__('django.db.models', fromlist=['F']).F('download_count') + 1)

    try:
        response = FileResponse(open(resource.file.path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(resource.file.name)}"'
        return response
    except FileNotFoundError:
        raise Http404("Fichier introuvable.")
