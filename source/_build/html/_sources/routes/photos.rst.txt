
.. automodule:: app.routes.photos
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------
=======
Routes de photos
===============

Ce module contient les routes pour la gestion des photos et uploads.

Routes détaillées
----------------
===============

.. automodule:: app.routes.photos
   :members:
   :undoc-members:
   :show-inheritance:

Routes détaillées
----------------

.. http:get:: /photos/<int:photo_id>

   Affiche une photo spécifique.

   **Paramètres** :
   
   * ``photo_id`` (int) : ID de la photo

   **Exemple de réponse** :

   .. sourcecode:: html

      <img src="/static/uploads/photo_123.jpg" alt="Photo de l'établissement">

   :status 200: succès
   :status 404: photo non trouvée

.. http:post:: /upload_photo

   Upload une nouvelle photo.

   **Description** :
   
   Route pour uploader une nouvelle photo pour un établissement ou un flan.

   **Requiert** :
   
   * Utilisateur authentifié
   * Fichier image dans le formulaire

   **Paramètres** :
   
   * ``file`` (file) : Fichier image à uploader
   * ``etablissement_id`` (int) : ID de l'établissement associé
   * ``flan_id`` (int, optionnel) : ID du flan associé

   **Exemple de requête** :

   .. sourcecode:: http

      POST /upload_photo HTTP/1.1
      Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
      
      ------WebKitFormBoundary
      Content-Disposition: form-data; name="file"; filename="flan.jpg"
      Content-Type: image/jpeg
      
      [contenu binaire de l'image]
      ------WebKitFormBoundary
      Content-Disposition: form-data; name="etablissement_id"
      
      123
      ------WebKitFormBoundary--

   **Réponses** :
   
   * Redirige vers la page de l'établissement en cas de succès
   * Réaffiche le formulaire avec erreurs en cas d'échec

   :status 302: redirection en cas de succès
   :status 400: requête invalide
   :status 401: non authentifié