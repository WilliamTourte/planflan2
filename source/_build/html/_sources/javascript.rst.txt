Documentation JavaScript
========================

Ce chapitre documente les scripts JavaScript utilisés dans l'application.

Structure des scripts
---------------------

Les scripts JavaScript sont organisés dans le dossier ``app/static/js/`` :

* ``base.js`` - Scripts de base communs à toutes les pages
* ``dashboard.js`` - Fonctionnalités du tableau de bord
* ``geoloc.js`` - Gestion de la géolocalisation
* ``index.js`` - Scripts pour la page d'accueil
* ``liste_etablissements.js`` - Gestion de la liste des établissements
* ``macros.js`` - Fonctions JavaScript réutilisables
* ``map_filter.js`` - Filtres pour la carte
* ``proposer_etablissement.js`` - Formulaire de proposition d'établissement

Fonctions principales
---------------------

Fonction ``initMap()``

Initialise la carte Google Maps.

**Exemple d'utilisation** :

.. code-block:: javascript

   // Appelé automatiquement au chargement de la page
   initMap();

Fonction ``updateMapMarkers(etablissements)``

Met à jour les marqueurs de la carte avec les établissements donnés.

**Paramètres** :

* ``etablissements`` (Array) : Liste des établissements à afficher

**Exemple d'utilisation** :

.. code-block:: javascript

   const etablissements = [
     {id: 1, nom: "Boulangerie", lat: 48.8566, lng: 2.3522},
     {id: 2, nom: "Pâtisserie", lat: 48.8588, lng: 2.3471}
   ];
   updateMapMarkers(etablissements);

Fonction ``getCurrentPosition()``

Récupère la position géographique actuelle de l'utilisateur.

**Retourne** :

* Promise qui résout avec les coordonnées {lat, lng}

**Exemple d'utilisation** :

.. code-block:: javascript

   getCurrentPosition()
     .then(position => {
       console.log("Position actuelle:", position);
     })
     .catch(error => {
       console.error("Erreur de géolocalisation:", error);
     });

Événements personnalisés
------------------------

Événement ``map:updated``

Événement déclenché lorsque la carte est mise à jour.

**Exemple d'utilisation** :

.. code-block:: javascript

   document.addEventListener('map:updated', function(e) {
     console.log('Carte mise à jour avec', e.detail.etablissementsCount, 'établissements');
   });

Conventions de codage
---------------------

* **ES6+** : Utilisation des fonctionnalités modernes de JavaScript
* **Modules** : Organisation en modules avec import/export
* **Async/Await** : Gestion asynchrone avec async/await
* **Événements** : Utilisation d'événements personnalisés pour la communication
* **Documentation** : Commentaires JSDoc pour les fonctions principales