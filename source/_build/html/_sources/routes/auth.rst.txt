
.. automodule:: app.routes.auth
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------
=======
Routes d'authentification
=========================

Ce module contient les routes d'authentification de l'application PlanFlan.

Routes détaillées
----------------
=========================

.. automodule:: app.routes.auth
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------

.. http:get:: /login

   Affiche le formulaire de connexion.

   **Description** :
   
   Affiche le formulaire de connexion pour les utilisateurs.

   **Exemple de réponse** :

   .. sourcecode:: html

      <form method="POST" action="/login">
          <input type="text" name="username" placeholder="Nom d'utilisateur">
          <input type="password" name="password" placeholder="Mot de passe">
          <button type="submit">Se connecter</button>
      </form>

   :status 200: succès

.. http:post:: /login

   Traite la soumission du formulaire de connexion.

   **Paramètres** :
   
   * ``username`` (string) : Nom d'utilisateur
   * ``password`` (string) : Mot de passe

   **Réponses** :
   
   * Redirige vers le tableau de bord en cas de succès
   * Réaffiche le formulaire avec erreurs en cas d'échec

   :status 302: redirection en cas de succès
   :status 200: réaffichage du formulaire en cas d'erreur

.. http:get:: /logout

   Déconnecte l'utilisateur.

   **Description** :
   
   Déconnecte l'utilisateur et redirige vers la page d'accueil.

   :status 302: redirection vers la page d'accueil