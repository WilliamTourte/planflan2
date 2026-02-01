Documentation JavaScript
========================

Ce chapitre documente les scripts JavaScript utilisés dans l'application.

Fonctions principales documentées
---------------------------------

Les fonctions JavaScript principales sont documentées avec des commentaires JSDoc.
Voici quelques exemples de fonctions clés :

Fonctions pour les établissements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**cancelEdit(idEtab)**

Annule l'édition d'un établissement et revient en mode affichage.

* **Paramètre** : ``idEtab`` (number) - L'identifiant de l'établissement à annuler l'édition
* **Retourne** : void

**editEtablissement(idEtab)**

Active le mode édition pour un établissement.

* **Paramètre** : ``idEtab`` (number) - L'identifiant de l'établissement à éditer
* **Retourne** : void

Fonctions pour les flans
^^^^^^^^^^^^^^^^^^^^^^^

**editFlan(idFlan)**

Active le mode édition pour un flan.

* **Paramètre** : ``idFlan`` (number) - L'identifiant du flan à éditer
* **Retourne** : void

**cancelEditFlan(idFlan)**

Annule l'édition d'un flan et revient en mode affichage.

* **Paramètre** : ``idFlan`` (number) - L'identifiant du flan à annuler l'édition
* **Retourne** : void

Fonctions pour les évaluations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**editEvaluation(idEval)**

Active le mode édition pour une évaluation.

* **Paramètre** : ``idEval`` (number) - L'identifiant de l'évaluation à éditer
* **Retourne** : void

**cancelEditEval(idEval)**

Annule l'édition d'une évaluation et revient en mode affichage.

* **Paramètre** : ``idEval`` (number) - L'identifiant de l'évaluation à annuler l'édition
* **Retourne** : void

Fonctions utilitaires
^^^^^^^^^^^^^^^^^^^^

**initMacroEventListeners()**

Initialise les écouteurs d'événements pour les boutons d'action macro.
Cette fonction est appelée automatiquement lors du chargement du script.

* **Retourne** : void

Structure des scripts
---------------------

Les scripts JavaScript sont organisés dans le dossier ``app/static/js/`` :

* ``base.js`` - Scripts de base communs à toutes les pages
* ``dashboard.js`` - Fonctionnalités du tableau de bord
* ``geolocation.js`` - Gestion de la géolocalisation
* ``index.js`` - Scripts pour la page d'accueil
* ``liste_etablissements.js`` - Gestion de la liste des établissements
* ``macros.js`` - Fonctions JavaScript réutilisables
* ``map.js`` - Gestion de la carte
* ``main.js`` - Script principal

Conventions de codage
---------------------

* **ES6+** : Utilisation des fonctionnalités modernes de JavaScript
* **Modules** : Organisation en modules avec import/export
* **Async/Await** : Gestion asynchrone avec async/await
* **Événements** : Utilisation d'événements personnalisés pour la communication
* **Documentation** : Commentaires JSDoc pour les fonctions principales

Pour plus d'informations sur la documentation JavaScript avec Sphinx, voir le fichier ``documentation/SPHINX_JS_DOCUMENTATION.md``.