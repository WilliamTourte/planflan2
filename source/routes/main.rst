
.. automodule:: app.routes.main
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------
=======
Routes principales
==================

Ce module contient les routes principales de l'application PlanFlan.

Routes détaillées
----------------
==================

.. automodule:: app.routes.main
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------

.. http:get:: /

   Affiche la page d'accueil de l'application.

   **Description** :
   
   Cette route affiche la page d'accueil avec la liste des établissements et le formulaire de recherche.

   **Exemple de réponse** :

   .. sourcecode:: html

      <!DOCTYPE html>
      <html>
      <head>
          <title>PlanFlan - Accueil</title>
      </head>
      <body>
          <!-- Contenu de la page d'accueil -->
      </body>
      </html>

   :status 200: succès

.. http:get:: /dashboard

   Affiche le tableau de bord utilisateur.

   **Description** :
   
   Route protégée qui affiche le tableau de bord de l'utilisateur connecté avec ses flans et établissements.

   **Requiert** :
   
   * Utilisateur authentifié

   **Exemple de réponse** :

   .. sourcecode:: html

      <!DOCTYPE html>
      <html>
      <head>
          <title>PlanFlan - Tableau de bord</title>
      </head>
      <body>
          <!-- Contenu du tableau de bord -->
      </body>
      </html>

   :status 200: succès
   :status 401: non authentifié

.. http:get:: /etablissement/<int:etab_id>

   Affiche la page d'un établissement spécifique.

   **Paramètres** :
   
   * ``etab_id`` (int) : ID de l'établissement

   **Exemple de réponse** :

   .. sourcecode:: html

      <!DOCTYPE html>
      <html>
      <head>
          <title>PlanFlan - [Nom de l'établissement]</title>
      </head>
      <body>
          <!-- Contenu de la page de l'établissement -->
      </body>
      </html>

   :status 200: succès
   :status 404: établissement non trouvé