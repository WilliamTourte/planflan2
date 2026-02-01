
.. automodule:: app.routes.maps
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------
=======
Routes de cartes
===============

Ce module contient les routes liées à la cartographie et aux API géographiques.

Routes détaillées
----------------
===============

.. automodule:: app.routes.maps
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------

.. http:get:: /map

   Affiche la carte interactive des établissements.

   **Description** :
   
   Affiche une carte interactive avec tous les établissements proposant des flans.

   **Paramètres optionnels** :
   
   * ``lat`` (float) : Latitude pour centrer la carte
   * ``lng`` (float) : Longitude pour centrer la carte
   * ``zoom`` (int) : Niveau de zoom (1-20)

   **Exemple de réponse** :

   .. sourcecode:: html

      <div id="map"></div>
      <script>
      // Initialisation de la carte Google Maps
      function initMap() {
          const map = new google.maps.Map(document.getElementById("map"), {
              center: {lat: 48.8566, lng: 2.3522},
              zoom: 12
          });
      }
      </script>

   :status 200: succès

.. http:get:: /api/etablissements

   API - Récupère la liste des établissements.

   **Description** :
   
   Retourne la liste des établissements au format JSON pour l'API.

   **Paramètres optionnels** :
   
   * ``lat`` (float) : Latitude pour filtrer les établissements proches
   * ``lng`` (float) : Longitude pour filtrer les établissements proches
   * ``radius`` (int) : Rayon de recherche en mètres

   **Exemple de réponse** :

   .. sourcecode:: json

      {
        "etablissements": [
          {
            "id": 1,
            "nom": "Boulangerie Martin",
            "adresse": "12 rue de Paris, 75001 Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "distance": 150.5
          }
        ]
      }

   :status 200: succès
   :status 400: paramètres invalides