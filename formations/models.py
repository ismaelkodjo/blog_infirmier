from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid


class CategorieFormation(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, default='fas fa-graduation-cap')

    class Meta:
        verbose_name = "Catégorie formation"
        verbose_name_plural = "Catégories formations"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Formation(models.Model):
    TYPE_CHOICES = [
        ('presentiel', 'Présentiel'),
        ('en_ligne',   'En ligne'),
        ('hybride',    'Hybride'),
    ]
    NIVEAU_CHOICES = [
        ('debutant',     'Débutant'),
        ('intermediaire','Intermédiaire'),
        ('avance',       'Avancé'),
        ('expert',       'Expert'),
    ]

    categorie = models.ForeignKey(CategorieFormation, on_delete=models.SET_NULL, null=True, related_name='formations')
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    sous_titre = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    objectifs = models.TextField(help_text="Objectifs pédagogiques (un par ligne)")
    type_formation = models.CharField(max_length=15, choices=TYPE_CHOICES, default='hybride')
    niveau = models.CharField(max_length=15, choices=NIVEAU_CHOICES, default='debutant')
    duree_heures = models.PositiveIntegerField(default=0, help_text="Durée totale en heures")
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='formations/covers/', blank=True, null=True)
    certificat = models.BooleanField(default=True, help_text="Certificat de fin de formation")
    en_vedette = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    prerequis = models.TextField(blank=True, help_text="Prérequis (un par ligne)")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Formation"
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('formations:detail', kwargs={'slug': self.slug})

    @property
    def prix_actuel(self):
        return self.prix_promo if self.prix_promo else self.prix

    @property
    def en_promotion(self):
        return bool(self.prix_promo and self.prix_promo < self.prix)


class ModuleFormation(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='modules')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    duree_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Module"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.formation.titre} — {self.titre}"


class Lecon(models.Model):
    TYPE_CHOICES = [
        ('video',    'Vidéo'),
        ('pdf',      'PDF / Document'),
        ('quiz',     'Quiz'),
        ('texte',    'Texte'),
    ]

    module = models.ForeignKey(ModuleFormation, on_delete=models.CASCADE, related_name='lecons')
    titre = models.CharField(max_length=200)
    type_lecon = models.CharField(max_length=10, choices=TYPE_CHOICES, default='texte')
    contenu = models.TextField(blank=True, help_text="Contenu texte ou URL vidéo/PDF")
    fichier = models.FileField(upload_to='formations/lecons/', blank=True, null=True)
    duree_minutes = models.PositiveIntegerField(default=0)
    ordre = models.PositiveIntegerField(default=0)
    gratuite = models.BooleanField(default=False, help_text="Leçon accessible sans inscription")

    class Meta:
        verbose_name = "Leçon"
        ordering = ['ordre']

    def __str__(self):
        return self.titre


class SessionPresentiel(models.Model):
    STATUT_CHOICES = [
        ('ouvert',   'Inscriptions ouvertes'),
        ('complet',  'Complet'),
        ('termine',  'Terminé'),
        ('annule',   'Annulé'),
    ]

    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='sessions')
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(max_length=300)
    ville = models.CharField(max_length=100)
    places_max = models.PositiveIntegerField(default=20)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='ouvert')
    informations = models.TextField(blank=True)

    class Meta:
        verbose_name = "Session présentiel"
        verbose_name_plural = "Sessions présentiel"
        ordering = ['date_debut']

    def __str__(self):
        return f"{self.formation.titre} — {self.date_debut.strftime('%d/%m/%Y')}"

    @property
    def places_disponibles(self):
        inscrits = self.inscriptions.filter(statut__in=['confirme', 'en_attente']).count()
        return max(0, self.places_max - inscrits)

    @property
    def est_complet(self):
        return self.places_disponibles == 0


class Inscription(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('confirme',   'Confirmée'),
        ('termine',    'Terminée'),
        ('annule',     'Annulée'),
    ]
    MODE_PAIEMENT_CHOICES = [
        ('virement',       'Virement bancaire'),
        ('sur_place',      'Paiement sur place'),
        ('mobile_money',   'Mobile Money (Flooz/T-Money)'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='inscriptions')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='inscriptions')
    session = models.ForeignKey(SessionPresentiel, on_delete=models.SET_NULL, null=True, blank=True, related_name='inscriptions')
    # Infos si non connecté
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    profession = models.CharField(max_length=200, blank=True)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='virement')
    numero = models.CharField(max_length=20, unique=True, blank=True)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes_admin = models.TextField(blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inscription"
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.formation.titre}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"INS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('formations:inscription_confirmation', kwargs={'numero': self.numero})


class ProgressionLecon(models.Model):
    """Suivi de la progression d'un apprenant sur les leçons en ligne."""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    lecon = models.ForeignKey(Lecon, on_delete=models.CASCADE)
    terminee = models.BooleanField(default=False)
    date_completion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Progression leçon"
        unique_together = ('utilisateur', 'lecon')

    def __str__(self):
        return f"{self.utilisateur} — {self.lecon.titre}"
