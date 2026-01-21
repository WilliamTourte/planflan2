Documentation des routes Flask
==============================

Ce chapitre documente les routes de l'application Flask PlanFlan.

.. toctree::
   :maxdepth: 2
   :caption: Routes principales:

   routes/main
   routes/auth
   routes/maps
   routes/photos

Conventions des routes
----------------------

Les routes suivent les conventions suivantes :

* **Préfixes** : Les routes sont regroupées par fonctionnalité
* **Méthodes HTTP** : Utilisation appropriée de GET, POST, PUT, DELETE
* **Sécurité** : Routes protégées avec @login_required lorsque nécessaire
* **Documentation** : Chaque route devrait avoir un docstring décrivant son rôle

Exemple de documentation d'une route
------------------------------------

.. http:get:: /api/etablissements

   Récupère la liste des établissements.

   **Exemple de requête** :

   .. sourcecode:: http

      GET /api/etablissements HTTP/1.1
      Host: exemple.com
      Accept: application/json

   **Exemple de réponse** :

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "etablissements": [
          {
            "id": 1,
            "nom": "Boulangerie Martin",
            "adresse": "12 rue de Paris"
          }
        ]
      }

   :query param1: description du paramètre 1
   :query param2: description du paramètre 2
   :status 200: succès
   :status 401: non autorisé
   :status 404: non trouvé