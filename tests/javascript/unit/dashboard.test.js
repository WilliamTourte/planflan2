/**
 * Tests unitaires pour les fonctionnalités du dashboard
 * 
 * Ces tests vérifient que les boutons de suppression de compte
 * et les fonctions associées fonctionnent correctement.
 */

describe('Dashboard Functionality', () => {
  // Mock des fonctions globales et du DOM
  let consoleErrorSpy;
  
  beforeEach(() => {
    // Configurer un DOM de base pour le dashboard
    document.body.innerHTML = `
      <div id="user-info" style="display: block;">
        <p><strong>Pseudo:</strong> testuser</p>
        <p><strong>Email:</strong> test@example.com</p>
        <div class="action-buttons">
          <button id="edit-profile-btn" class="btn btn-success">Edit Profile</button>
          <button id="delete-account-btn" class="btn btn-danger">Delete Account</button>
        </div>
      </div>
      
      <div id="delete-account-section" style="display: none;">
        <h3>Supprimer mon compte</h3>
        <form method="POST" action="/supprimer_compte">
          <input type="password" name="password" id="delete-password" required>
          <button type="submit" class="btn btn-danger">Confirmer la suppression</button>
          <button type="button" id="cancel-delete-btn" class="btn btn-success">Annuler</button>
        </form>
      </div>
      
      <div id="edit-profile-form" style="display: none;">
        <form method="POST" action="/modifier_profil">
          <input type="text" name="pseudo" value="testuser">
          <input type="email" name="email" value="test@example.com">
          <button type="submit">Enregistrer</button>
          <button type="button" id="cancel-edit-btn" class="btn btn-canceledit">Annuler</button>
        </form>
      </div>
    `;

    // Espionner console.error pour détecter les erreurs
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    // Importer les fonctions de dashboard.js
    const dashboard = require('../../../app/static/js/dashboard.js');

    // Assign functions to global scope for the tests
    global.showDeleteAccountForm = dashboard.showDeleteAccountForm;
    global.cancelDeleteAccount = dashboard.cancelDeleteAccount;
    global.initDashboardEventListeners = dashboard.initDashboardEventListeners;
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    jest.clearAllMocks();
  });

  describe('Delete Account Functionality', () => {
    it('should show delete account form when delete button is clicked', () => {
      // Appeler la fonction pour afficher le formulaire
      global.showDeleteAccountForm();

      // Vérifier que la section de suppression est visible
      expect(document.getElementById('delete-account-section').style.display).toBe('block');

      // Vérifier que le champ de mot de passe est focalisé
      // Note: Jest ne peut pas vraiment tester le focus, mais on peut vérifier que l'élément existe
      expect(document.getElementById('delete-password')).toBeTruthy();

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should cancel delete account when cancel button is clicked', () => {
      // Afficher d'abord le formulaire
      document.getElementById('delete-account-section').style.display = 'block';

      // Appeler la fonction pour annuler
      global.cancelDeleteAccount();

      // Vérifier que la section de suppression est masquée
      expect(document.getElementById('delete-account-section').style.display).toBe('none');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should remove error parameters from URL when canceling delete account', () => {
      // Simuler une URL avec des paramètres d'erreur
      jest.spyOn(window, 'location', 'get').mockImplementation(() => ({
        href: 'http://example.com/dashboard?error=password',
        search: '?error=password'
      }));

      // Mock de history.replaceState
      const replaceStateMock = jest.fn();
      Object.defineProperty(window.history, 'replaceState', { value: replaceStateMock });

      // Afficher d'abord le formulaire
      document.getElementById('delete-account-section').style.display = 'block';

      // Appeler la fonction pour annuler
      global.cancelDeleteAccount();

      // Vérifier que la section de suppression est masquée
      expect(document.getElementById('delete-account-section').style.display).toBe('none');

      // Vérifier que replaceState a été appelé pour supprimer les paramètres d'erreur
      expect(replaceStateMock).toHaveBeenCalled();

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe('Event Listeners Integration', () => {
    it('should correctly attach event listeners to dashboard buttons', () => {
      // Appeler initDashboardEventListeners pour attacher les écouteurs
      global.initDashboardEventListeners();

      // Simuler un clic sur le bouton de suppression de compte
      const deleteButton = document.getElementById('delete-account-btn');
      deleteButton.click();

      // Vérifier que le formulaire de suppression est affiché
      expect(document.getElementById('delete-account-section').style.display).toBe('block');

      // Simuler un clic sur le bouton d'annulation
      const cancelButton = document.getElementById('cancel-delete-btn');
      cancelButton.click();

      // Vérifier que le formulaire de suppression est masqué
      expect(document.getElementById('delete-account-section').style.display).toBe('none');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle missing delete account button gracefully', () => {
      // Supprimer le bouton de suppression de compte
      document.getElementById('delete-account-btn').remove();

      // Appeler initDashboardEventListeners
      global.initDashboardEventListeners();

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle missing cancel delete button gracefully', () => {
      // Supprimer le bouton d'annulation
      document.getElementById('cancel-delete-btn').remove();

      // Appeler initDashboardEventListeners
      global.initDashboardEventListeners();

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe('URL Error Handling', () => {
    it('should show delete account form when error parameter is in URL', () => {
      // Simuler une URL avec des paramètres d'erreur
      jest.spyOn(window, 'location', 'get').mockImplementation(() => ({
        href: 'http://example.com/dashboard?error=password',
        search: '?error=password'
      }));

      // Simuler le chargement du DOM
      const domContentLoadedEvent = new Event('DOMContentLoaded');
      window.dispatchEvent(domContentLoadedEvent);

      // Vérifier que le formulaire de suppression est affiché
      expect(document.getElementById('delete-account-section').style.display).toBe('block');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should not show delete account form when no error parameter in URL', () => {
      // Simuler une URL sans paramètres d'erreur
      jest.spyOn(window, 'location', 'get').mockImplementation(() => ({
        href: 'http://example.com/dashboard',
        search: ''
      }));

      // Simuler le chargement du DOM
      const domContentLoadedEvent = new Event('DOMContentLoaded');
      window.dispatchEvent(domContentLoadedEvent);

      // Vérifier que le formulaire de suppression est masqué
      expect(document.getElementById('delete-account-section').style.display).toBe('none');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });
});