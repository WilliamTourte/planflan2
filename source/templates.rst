Documentation des templates et macros
=====================================

Ce chapitre documente les templates Jinja2 et les macros utilisées dans l'application.

Structure des templates
-----------------------

Les templates sont organisés dans le dossier ``app/templates/`` :

* ``base.html`` - Template de base avec structure HTML commune
* ``macros.html`` - Macros réutilisables
* ``*.html`` - Templates spécifiques pour chaque page

Macros principales
------------------

Macro ``render_field(field)``

Rend un champ de formulaire avec son label et ses erreurs.

**Paramètres** :

* ``field`` : Champ WTForms à rendre

**Exemple d'utilisation** :

.. code-block:: jinja

   {{ render_field(form.username) }}

Macro ``render_flan_card(flan)``

Rend une carte d'affichage d'un flan.

**Paramètres** :

* ``flan`` : Objet Flan à afficher

**Exemple d'utilisation** :

.. code-block:: jinja

   {{ render_flan_card(flan) }}

Blocs principaux
----------------

Le template ``base.html`` définit les blocs suivants :

* ``title`` - Titre de la page
* ``content`` - Contenu principal
* ``scripts`` - Scripts JavaScript spécifiques
* ``styles`` - Styles CSS spécifiques

Héritage des templates
----------------------

Exemple d'héritage :

.. code-block:: jinja

   {% extends "base.html" %}
   
   {% block title %}
   Page d'accueil - PlanFlan
   {% endblock %}
   
   {% block content %}
   <h1>Bienvenue sur PlanFlan !</h1>
   {% endblock %}

Variables globales
------------------

Variables disponibles dans tous les templates :

* ``current_user`` - Utilisateur connecté
* ``config`` - Configuration de l'application
* ``request`` - Objet requête Flask