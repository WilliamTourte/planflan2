Documentation JavaScript (Auto-générée)
========================================

Cette page documente les fonctions et modules JavaScript de l'application PlanFlan.
La documentation est générée automatiquement à partir des commentaires JSDoc dans les fichiers source.

.. contents::
    :local:
    :depth: 2

Module API
----------

Fonctions pour l'interaction avec le serveur backend.

.. js:autosummary::
   :maxdepth: 2

   api

Module Carte (Map)
------------------

Gestion de la carte Leaflet et des marqueurs géographiques.

.. js:autosummary::
   :maxdepth: 2

   map

Fonctions principales:

* ``createEmojiIcon()`` - Crée des icônes personnalisées avec des emoji
* ``createEtablissementMarker()`` - Crée un marqueur pour un établissement
* ``initMap()`` - Initialise la carte
* ``updateMapMarkers()`` - Met à jour les marqueurs de la carte

Module Macros
-------------

Fonctions utilitaires réutilisables pour les opérations courantes.

.. js:autosummary::
   :maxdepth: 2

   macros

Fonctions principales:

* ``editEtablissement()`` - Passe un établissement en mode édition
* ``cancelEdit()`` - Annule l'édition d'un établissement
* ``editFlan()`` - Passe un flan en mode édition
* ``cancelEditFlan()`` - Annule l'édition d'un flan
* ``editEvaluation()`` - Passe une évaluation en mode édition
* ``cancelEditEval()`` - Annule l'édition d'une évaluation
* ``initMacroEventListeners()`` - Initialise les écouteurs d'événements

Module Utilitaires (Utils)
--------------------------

Fonctions utilitaires et helpers pour le code JavaScript.

.. js:autosummary::
   :maxdepth: 2

   utils

Module Géolocalisation
-----------------------

Gestion de la géolocalisation utilisateur.

.. js:autosummary::
   :maxdepth: 2

   geolocation

Module Base
-----------

Scripts de base communs à toutes les pages.

.. js:autosummary::
   :maxdepth: 2

   base

Module Filtres
--------------

Gestion des filtres et des critères de recherche.

.. js:autosummary::
   :maxdepth: 2

   filters

Module AutoComplete
-------------------

Fonctionnalité d'auto-complétion pour les champs de formulaire.

.. js:autosummary::
   :maxdepth: 2

   autocomplete

Module Dashboard
----------------

Fonctionnalités du tableau de bord.

.. js:autosummary::
   :maxdepth: 2

   dashboard

Module Principale (Main)
------------------------

Script principal de l'application.

.. js:autosummary::
   :maxdepth: 2

   main

Notes pour les développeurs
---------------------------

Conventions JSDoc
^^^^^^^^^^^^^^^^^

Tous les fichiers JavaScript utilisent les commentaires JSDoc standards:

.. code-block:: javascript

    /**
     * Description courte de la fonction.
     * 
     * Description longue si nécessaire avec plus de détails
     * sur le fonctionnement et les cas d'usage.
     * 
     * @param {type} paramName - Description du paramètre
     * @param {type} [optionalParam] - Paramètre optionnel
     * @returns {type} Description de la valeur retournée
     * 
     * @example
     * // Exemple d'utilisation
     * myFunction(param1, param2);
     */
    export function myFunction(paramName, optionalParam) {
        // Implementation
    }

Types supportés
^^^^^^^^^^^^^^^

* ``{string}`` - Chaîne de caractères
* ``{number}`` - Nombre
* ``{boolean}`` - Booléen
* ``{Object}`` - Objet générique
* ``{Array}`` - Tableau
* ``{Function}`` - Fonction
* ``{Promise}`` - Promesse asynchrone
* ``{HTMLElement}`` - Élément DOM
* ``{void}`` - Pas de valeur retournée

Organisation du code
^^^^^^^^^^^^^^^^^^^^

Les fichiers JavaScript sont organisés dans ``app/static/js/`` et suivent une structure modulaire:

* **Modules d'API**: Interaction avec le serveur
* **Modules de UI**: Gestion de l'interface utilisateur
* **Modules utilitaires**: Fonctions réutilisables
* **Modules métier**: Logique applicative

Pour plus d'informations, consultez la `documentation de JSDoc <https://jsdoc.app/>`_.
