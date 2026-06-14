# Blog Infirmier de Santé Publique

Plateforme Django complète pour un infirmier de santé publique. Blog professionnel avec gestion d'articles, ressources téléchargeables, newsletter, tableau de bord et optimisation SEO.

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Django 5.1, Python 3.13 |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| BDD dev | SQLite3 |
| BDD prod | PostgreSQL |
| Éditeur | CKEditor 5 |
| Tags | django-taggit |
| Forms | django-crispy-forms |
| Serveur | Gunicorn + Nginx |
| Statiques | WhiteNoise |

---

## Architecture du projet

```
blog_infirmier/
├── blog_infirmier/       # Configuration principale
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/             # Authentification & profils
├── blog/                 # Articles, catégories, commentaires
├── resources/            # Ressources téléchargeables
├── contact/              # Formulaire de contact
├── newsletter/           # Abonnements email
├── dashboard/            # Tableau de bord admin
├── core/                 # Pages statiques (accueil, à propos…)
├── templates/            # Templates HTML
├── static/               # CSS, JS, images
├── media/                # Uploads utilisateurs
├── fixtures/             # Données de démonstration
├── requirements.txt
├── manage.py
└── .env.example
```

---

## Installation sous Windows 11

### Prérequis
- Python 3.13+ : https://www.python.org/downloads/
- Git : https://git-scm.com/download/win

### Étapes

```cmd
:: 1. Cloner le projet
git clone https://github.com/votre-repo/blog_infirmier.git
cd blog_infirmier

:: 2. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate

:: 3. Installer les dépendances
pip install -r requirements.txt

:: 4. Configurer l'environnement
copy .env.example .env
:: Éditer .env avec Notepad ou VS Code

:: 5. Appliquer les migrations
python manage.py migrate

:: 6. Charger les données de démonstration
python manage.py loaddata fixtures/categories.json

:: 7. Créer un superutilisateur

:: 8. Collecter les fichiers statiques
python manage.py collectstatic --noinput

:: 9. Lancer le serveur de développement
python manage.py runserver
```

Accéder à : http://127.0.0.1:8000
Administration : http://127.0.0.1:8000/amou/

---

## Installation sous Ubuntu 22.04 / 24.04

### Prérequis

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.13 python3.13-venv python3-pip git build-essential libpq-dev
```

### Étapes

```bash
# 1. Cloner le projet
git clone https://github.com/votre-repo/blog_infirmier.git
cd blog_infirmier

# 2. Environnement virtuel
python3.13 -m venv venv
source venv/bin/activate

# 3. Dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
nano .env   # Éditer les variables

# 5. Migrations
python manage.py migrate

# 6. Données de démo
python manage.py loaddata fixtures/categories.json

# 7. Superutilisateur
python manage.py createsuperuser

# 8. Statiques
python manage.py collectstatic --noinput

# 9. Lancer en développement
python manage.py runserver 0.0.0.0:8000
```

---

## Déploiement production : Nginx + Gunicorn

### 1. Installer PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE blog_infirmier_db;
CREATE USER blog_user WITH PASSWORD 'motdepasse_fort';
GRANT ALL PRIVILEGES ON DATABASE blog_infirmier_db TO blog_user;
\q
```

Mettre à jour `.env` :
```env
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=blog_infirmier_db
DB_USER=blog_user
DB_PASSWORD=motdepasse_fort
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
```

### 2. Configurer Gunicorn

```bash
pip install gunicorn psycopg2-binary

# Test
gunicorn --bind 0.0.0.0:8000 blog_infirmier.wsgi:application
```

Créer le service systemd `/etc/systemd/system/blog_infirmier.service` :

```ini
[Unit]
Description=Blog Infirmier Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/blog_infirmier
Environment="PATH=/var/www/blog_infirmier/venv/bin"
ExecStart=/var/www/blog_infirmier/venv/bin/gunicorn \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --workers 3 \
    --bind unix:/run/gunicorn/blog_infirmier.sock \
    blog_infirmier.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/log/gunicorn /run/gunicorn
sudo chown www-data:www-data /var/log/gunicorn /run/gunicorn
sudo systemctl daemon-reload
sudo systemctl enable blog_infirmier
sudo systemctl start blog_infirmier
sudo systemctl status blog_infirmier
```

### 3. Configurer Nginx

Installer Nginx :
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Créer `/etc/nginx/sites-available/blog_infirmier` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    # Logs
    access_log /var/log/nginx/blog_infirmier_access.log;
    error_log  /var/log/nginx/blog_infirmier_error.log;

    # Sécurité
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Fichiers statiques (WhiteNoise les sert déjà, mais Nginx est plus rapide)
    location /static/ {
        alias /var/www/blog_infirmier/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Fichiers médias
    location /media/ {
        alias /var/www/blog_infirmier/media/;
        expires 7d;
    }

    # Proxy vers Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/blog_infirmier.sock;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    # Limite taille upload (ressources)
    client_max_body_size 20M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/blog_infirmier /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. SSL avec Let's Encrypt (HTTPS)

```bash
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
sudo systemctl reload nginx
```

### 5. Permissions et sécurité

```bash
# Copier le projet
sudo cp -r /home/ubuntu/blog_infirmier /var/www/blog_infirmier
sudo chown -R www-data:www-data /var/www/blog_infirmier
sudo chmod -R 755 /var/www/blog_infirmier
sudo chmod -R 775 /var/www/blog_infirmier/media

# Collecter les statiques
cd /var/www/blog_infirmier
source venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate
```

---

## Commandes utiles

```bash
# Créer des migrations après modification des modèles
python manage.py makemigrations
python manage.py migrate

# Shell Django
python manage.py shell

# Créer un superutilisateur
python manage.py createsuperuser

# Recharger les fixtures
python manage.py loaddata fixtures/categories.json

# Vider la base de données (dev)
python manage.py flush

# Logs en production
sudo journalctl -u blog_infirmier -f
sudo tail -f /var/log/nginx/blog_infirmier_access.log
```

---

## Variables d'environnement (.env)

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Django | Chaîne aléatoire 50+ caractères |
| `DEBUG` | Mode debug | `True` (dev) / `False` (prod) |
| `ALLOWED_HOSTS` | Hôtes autorisés | `votre-domaine.com,www.votre-domaine.com` |
| `DB_ENGINE` | Backend BDD | `django.db.backends.sqlite3` ou `postgresql` |
| `DB_NAME` | Nom base de données | `blog_infirmier_db` |
| `DB_USER` | Utilisateur BDD | `blog_user` |
| `DB_PASSWORD` | Mot de passe BDD | Mot de passe fort |
| `EMAIL_BACKEND` | Backend email | `smtp.EmailBackend` en prod |
| `EMAIL_HOST` | Serveur SMTP | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | Email expéditeur | `votre@email.com` |
| `EMAIL_HOST_PASSWORD` | Mot de passe app | Mot de passe d'application Gmail |
| `SITE_URL` | URL publique | `https://votre-domaine.com` |

---

## Fonctionnalités implémentées

### ✅ Gestion des utilisateurs
- Inscription / Connexion / Déconnexion
- Réinitialisation de mot de passe (email)
- Modification du profil avec avatar
- Changement de mot de passe
- Rôles : Administrateur, Auteur, Visiteur

### ✅ Blog
- Création / Modification / Suppression d'articles
- Éditeur riche CKEditor avec upload d'images
- Catégories (15 prédéfinies)
- Tags avec django-taggit
- Articles similaires
- Compteur de vues (par session)
- Temps de lecture automatique
- Pagination
- Recherche full-text
- Articles mis en avant

### ✅ Commentaires
- Commentaires imbriqués (réponses)
- Modération (approbation/rejet)
- Signalement de commentaires
- Commentaires pour visiteurs non connectés

### ✅ Ressources
- Upload PDF, Word, Excel, PowerPoint
- Compteur de téléchargements
- Filtrage par type
- Téléchargement sécurisé

### ✅ Newsletter
- Inscription / Désinscription (token unique)
- Gestion des abonnés en admin

### ✅ Tableau de bord
- Statistiques globales
- Graphiques Chart.js (articles/mois, répartition/catégorie)
- Modération commentaires inline
- Liste des articles récents

### ✅ SEO
- URLs slug optimisées
- Sitemap XML automatique
- Robots.txt configurable
- Open Graph (Facebook)
- Twitter Cards
- Schema.org JSON-LD (Article, WebSite)
- Breadcrumbs
- Meta description / keywords par article

### ✅ Sécurité
- Protection CSRF sur tous les formulaires
- Validation des formulaires côté serveur
- Gestion sécurisée des médias
- Permissions et autorisations
- Hachage bcrypt des mots de passe
- En-têtes de sécurité HTTP (production)
- Protection XSS via Django templates

---

## Licence

Projet développé pour usage professionnel. Adaptation et redistribution soumises à accord.

---

*Développé avec ❤️ pour la santé publique — Django 5.1 + Bootstrap 5.3*
