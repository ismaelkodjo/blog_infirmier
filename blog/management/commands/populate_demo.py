"""
Commande Django pour créer les données de démonstration.
Usage : python manage.py populate_demo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Crée des données de démonstration complètes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Création des données de démonstration...'))
        self._users()
        self._categories()
        self._articles()
        self._resources()
        self._subscribers()
        self._contacts()
        self.stdout.write(self.style.SUCCESS('\nDonnées créées avec succès !'))
        self.stdout.write(self.style.SUCCESS('admin / admin123  |  auteur1 / auteur123'))

    def _users(self):
        from accounts.models import Profile
        users = [
            ('admin', 'admin@blog.com', 'admin123', 'Admin', 'Système', True, 'admin', 'Administration'),
            ('auteur1', 'infirmier@blog.com', 'auteur123', 'Dr. Kouamé', 'Yao', False, 'author', 'Santé Publique & Épidémiologie'),
            ('auteur2', 'infirmiere@blog.com', 'auteur123', 'Aminata', 'Coulibaly', False, 'author', 'Santé Maternelle & Infantile'),
            ('visiteur1', 'visiteur@example.com', 'visiteur123', 'Paul', 'Dupont', False, 'visitor', ''),
        ]
        for username, email, pwd, first, last, is_super, role, spec in users:
            if User.objects.filter(username=username).exists():
                continue
            if is_super:
                u = User.objects.create_superuser(username=username, email=email, password=pwd, first_name=first, last_name=last)
            else:
                u = User.objects.create_user(username=username, email=email, password=pwd, first_name=first, last_name=last)
            p, _ = Profile.objects.get_or_create(user=u)
            p.role = role
            p.speciality = spec
            p.bio = f"Professionnel de santé, spécialiste en {spec}." if spec else "Visiteur du blog."
            p.institution = "Direction Régionale de la Santé Publique"
            p.save()
            self.stdout.write(f'  Utilisateur : {username}')

    def _categories(self):
        from blog.models import Category
        cats = [
            ("Santé publique", "bi-heart-pulse", "#1a6fc4", 1),
            ("Système d information sanitaire", "bi-database", "#6610f2", 2),
            ("Épidémiologie", "bi-graph-up", "#dc3545", 3),
            ("Vaccination", "bi-capsule", "#fd7e14", 4),
            ("Hygiène hospitalière", "bi-shield-plus", "#20c997", 5),
            ("Santé maternelle", "bi-person-hearts", "#e83e8c", 6),
            ("Santé infantile", "bi-emoji-smile", "#ffc107", 7),
            ("Nutrition", "bi-apple", "#28a745", 8),
            ("Santé communautaire", "bi-people", "#17a2b8", 9),
            ("Promotion de la santé", "bi-megaphone", "#6f42c1", 10),
            ("Maladies transmissibles", "bi-virus", "#dc3545", 11),
            ("Maladies non transmissibles", "bi-heart", "#fd7e14", 12),
            ("Santé environnementale", "bi-tree", "#28a745", 13),
            ("Santé numérique", "bi-phone", "#1a6fc4", 14),
            ("Informatique médicale", "bi-laptop", "#6610f2", 15),
        ]
        for name, icon, color, order in cats:
            Category.objects.get_or_create(name=name, defaults={
                'slug': slugify(name), 'icon': icon, 'color': color, 'order': order,
                'description': f"Articles sur {name.lower()}."
            })
        self.stdout.write(f'  {len(cats)} catégories créées')

    def _articles(self):
        from blog.models import Article, Category, Comment
        author = User.objects.filter(username='auteur1').first()
        author2 = User.objects.filter(username='auteur2').first()
        if not author:
            return

        articles = [
            ("Introduction aux Systèmes d'Information Sanitaire",
             "Santé publique",
             "Cet article présente les fondamentaux des SIS, DHIS2 et leur rôle en santé publique.",
             "<h2>Qu'est-ce qu'un SIS ?</h2><p>Un système d'information sanitaire est l'ensemble des mécanismes permettant la collecte, le traitement et l'analyse des données de santé. Il est indispensable pour orienter les politiques de santé publique.</p><h2>DHIS2</h2><p>Le District Health Information Software 2 est utilisé dans plus de 70 pays comme plateforme nationale de gestion des données de santé. Il permet la collecte, la visualisation et l'analyse des indicateurs de santé.</p><h2>Indicateurs clés</h2><ul><li>Taux de mortalité infantile</li><li>Couverture vaccinale</li><li>Taux d'accouchements assistés</li><li>Prévalence du paludisme</li></ul>",
             ["DHIS2", "SIS", "données-santé"], author, True),
            ("La vaccination en Afrique : enjeux du PEV",
             "Vaccination",
             "Le Programme Élargi de Vaccination reste l'intervention la plus coût-efficace en santé publique.",
             "<h2>Le PEV</h2><p>Lancé en 1974 par l'OMS, le Programme Élargi de Vaccination vise à protéger tous les enfants contre les maladies évitables. En Afrique, ce programme a permis de sauver des millions de vies.</p><h2>Vaccins du calendrier</h2><ul><li>BCG contre la tuberculose</li><li>VPO/VPI contre la poliomyélite</li><li>Penta (DTP-HepB-Hib)</li><li>Pneumocoque PCV13</li><li>Rougeole-Rubéole</li></ul><h2>Défis</h2><p>La chaîne du froid, l'accessibilité géographique et les réticences restent les principaux défis à surmonter pour améliorer la couverture vaccinale.</p>",
             ["PEV", "vaccination", "enfants"], author, True),
            ("Paludisme en Afrique : épidémiologie et prévention",
             "Maladies transmissibles",
             "Le paludisme reste la première cause de mortalité infantile en Afrique subsaharienne.",
             "<h2>Épidémiologie</h2><p>Selon l'OMS, 249 millions de cas de paludisme ont été enregistrés en 2022, dont 95% en Afrique subsaharienne. La maladie est causée par des parasites Plasmodium transmis par les moustiques Anophèles.</p><h2>Prévention</h2><ul><li>Moustiquaires imprégnées d'insecticide (MILDA)</li><li>Pulvérisation intradomiciliaire (PID)</li><li>Traitement préventif intermittent (TPI)</li><li>Vaccin RTS,S/AS01 (Mosquirix)</li></ul><h2>Traitement</h2><p>Les combinaisons thérapeutiques à base d'artémisinine (CTA) sont le traitement standard recommandé par l'OMS.</p>",
             ["paludisme", "prévention", "Afrique"], author, False),
            ("Santé numérique en Afrique : état des lieux",
             "Santé numérique",
             "La révolution digitale transforme les systèmes de santé africains.",
             "<h2>La santé numérique</h2><p>La e-santé désigne l'ensemble des TIC appliquées à la santé. En Afrique, plus de 2000 solutions mHealth ont été déployées pour améliorer l'accès aux soins.</p><h2>Applications concrètes</h2><ul><li>DHIS2 : utilisé dans 44 pays africains</li><li>OpenMRS : dossier médical électronique open-source</li><li>M-TIBA Kenya : paiement mobile des soins</li><li>Télémédecine : développement post-COVID</li></ul><h2>Défis</h2><p>Infrastructures numériques, protection des données et durabilité des financements sont les principaux défis à relever.</p>",
             ["e-santé", "mHealth", "télémédecine"], author, True),
            ("Hygiène des mains : les 5 indications OMS",
             "Hygiène hospitalière",
             "L'hygiène des mains est l'intervention la plus efficace contre les infections nosocomiales.",
             "<h2>Les IAS</h2><p>Les infections associées aux soins touchent 1 patient sur 10 dans les pays à revenus faibles. L'hygiène des mains est la mesure préventive la plus efficace et la moins coûteuse.</p><h2>Les 5 moments OMS</h2><ol><li>Avant le contact avec le patient</li><li>Avant un geste aseptique</li><li>Après un risque d'exposition à un liquide biologique</li><li>Après le contact avec le patient</li><li>Après contact avec l'environnement du patient</li></ol><h2>SHA vs eau et savon</h2><p>La solution hydro-alcoolique (SHA) est recommandée en 1ère intention pour son efficacité (>99,9%) et sa rapidité d'action (30 secondes).</p>",
             ["hygiène-mains", "IAS", "prévention"], author2, False),
            ("Malnutrition de l'enfant : dépistage et prise en charge",
             "Nutrition",
             "La malnutrition aiguë sévère reste une urgence médicale en Afrique subsaharienne.",
             "<h2>Classifications</h2><p>La malnutrition aiguë sévère (MAS) est définie par un périmètre brachial (PB) inférieur à 115 mm, un rapport Poids/Taille inférieur à -3 ET/SD ou la présence d'œdèmes bilatéraux.</p><h2>Dépistage</h2><ul><li>Périmètre brachial (PB) : mesure simple et rapide</li><li>Rapport Poids/Taille selon courbes OMS 2006</li><li>Œdèmes bilatéraux (godet positif)</li></ul><h2>Protocole PCIMA</h2><p>La Prise en Charge Intégrée de la Malnutrition Aiguë comprend l'UNTA (ambulatoire) et l'UNTI (hospitalier) selon la présence de complications.</p>",
             ["malnutrition", "enfants", "PCIMA"], author2, False),
        ]

        for title, cat_name, summary, content, tags, auth, featured in articles:
            if Article.objects.filter(title=title).exists():
                continue
            try:
                cat = Category.objects.get(name=cat_name)
            except Category.DoesNotExist:
                cat = None
            art = Article.objects.create(
                title=title, summary=summary, content=content,
                author=auth, category=cat, status='published',
                published_at=timezone.now() - timedelta(days=random.randint(1, 90)),
                featured=featured,
                meta_description=summary[:155],
                views_count=random.randint(80, 2000),
            )
            art.tags.add(*tags)
            Comment.objects.create(
                article=art, author_name="Lecteur santé", author_email="lecteur@example.com",
                content="Excellent article, très utile pour notre pratique ! Merci beaucoup.",
                is_approved=True,
            )
            self.stdout.write(f'  Article : {title[:55]}')

    def _resources(self):
        from resources.models import Resource
        from blog.models import Category
        author = User.objects.filter(username='auteur1').first()
        if not author:
            return
        resources = [
            ("Guide pratique du paludisme OMS 2023", "pdf", "Santé publique", 245),
            ("Calendrier vaccinal PEV 2024", "pdf", "Vaccination", 389),
            ("Manuel DHIS2 agents de santé", "pdf", "Système d information sanitaire", 156),
            ("Collecte données SNIS", "excel", "Système d information sanitaire", 512),
            ("Protocole PCIMA malnutrition", "pdf", "Nutrition", 298),
            ("Formation hygiène des mains OMS", "powerpoint", "Hygiène hospitalière", 134),
        ]
        for title, ftype, cat_name, count in resources:
            try:
                cat = Category.objects.get(name=cat_name)
            except Category.DoesNotExist:
                cat = None
            Resource.objects.get_or_create(title=title, defaults={
                'file_type': ftype, 'category': cat, 'author': author,
                'description': f"Ressource de référence : {title}.",
                'download_count': count, 'is_public': True,
                'file': f'resources/demo/{slugify(title)}.{ftype}',
            })
        self.stdout.write(f'  {len(resources)} ressources créées')

    def _subscribers(self):
        from newsletter.models import NewsletterSubscriber
        subs = [
            ("marie.kone@example.com", "Marie"), ("ibrahim.diallo@example.com", "Ibrahim"),
            ("fatou.traore@example.com", "Fatou"), ("jean.dupont@example.com", "Jean"),
            ("aicha.bamba@example.com", "Aïcha"), ("paul.martin@example.com", "Paul"),
        ]
        for email, name in subs:
            NewsletterSubscriber.objects.get_or_create(email=email, defaults={'first_name': name, 'is_active': True})
        self.stdout.write(f'  {len(subs)} abonnés créés')

    def _contacts(self):
        from contact.models import ContactMessage
        msgs = [
            ("Dr. Kofi Mensah", "kofi@example.com", "collaboration",
             "Bonjour, je suis épidémiologiste au Ghana et j'aimerais collaborer sur un article concernant la surveillance épidémiologique."),
            ("Amina Touré", "amina@example.com", "article",
             "Pourriez-vous écrire un article sur le rôle des agents de santé communautaire dans la lutte contre le VIH/SIDA ?"),
        ]
        for name, email, subject, message in msgs:
            ContactMessage.objects.get_or_create(email=email, defaults={
                'name': name, 'subject': subject, 'message': message, 'is_read': False,
            })
        self.stdout.write(f'  {len(msgs)} messages de contact créés')
