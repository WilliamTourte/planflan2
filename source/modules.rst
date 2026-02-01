Modules de l'application
========================

Ce chapitre contient la documentation des modules Python de l'application PlanFlan.

Structure du projet
-------------------

L'application PlanFlan est organisée en plusieurs modules principaux :

* ``app/__init__.py`` - Point d'entrée de l'application Flask
* ``app/models.py`` - Modèles de base de données
* ``app/routes/`` - Routes de l'application (main, auth, maps, photos)
* ``app/forms.py`` - Formulaires WTForms
* ``app/outils.py`` - Fonctions utilitaires
* ``app/config.py`` - Configuration de l'application
* ``app/security_headers.py`` - Configuration des headers de sécurité

Architecture
------------

L'application suit une architecture MVC (Modèle-Vue-Contrôleur) :

* **Modèles** : Définis dans ``models.py``, utilisant SQLAlchemy pour l'ORM
* **Vues** : Templates Jinja2 dans le dossier ``templates/``
* **Contrôleurs** : Routes définies dans le dossier ``routes/``

Pour générer la documentation complète du code, vous pouvez utiliser :

.. code-block:: bash

   # Installer les dépendances de développement
   pip install -r requirements.txt
   
   # Générer la documentation avec Sphinx
   cd source
   sphinx-build -b html . _build/html

La documentation générée sera disponible dans ``source/_build/html/``.