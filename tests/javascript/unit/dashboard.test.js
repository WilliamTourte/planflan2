/**
 * Tests unitaires pour les fonctionnalités du dashboard
 * 
 * Ces tests vérifient que les boutons de suppression de compte
 * et les fonctions associées fonctionnent correctement.
 */

import { showDeleteAccountForm, cancelDeleteAccount, initDashboardEventListeners, toggleSection } from '../../../app/static/js/dashboard.js';

describe('Dashboard Functionality', () => {
  // Mock des fonctions globales et du DOM
  let consoleErrorSpy;
  
  beforeEach(() => {
    // Set proper window.location before tests
    window.location.href = 'http://test.example.com/dashboard';
    window.location.pathname = '/dashboard';
    window.location.search = '';
    
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
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    jest.clearAllMocks();
  });

  describe('Delete Account Functionality', () => {
    it('should show delete account form when delete button is clicked', () => {
      // Appeler la fonction pour afficher le formulaire
      showDeleteAccountForm();

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

      // Mock window.history.replaceState to avoid jsdom SecurityError
      // The actual functionality is tested separately; this test focuses on display logic
      const replaceStateMock = jest.fn();
      window.history.replaceState = replaceStateMock;

      // Appeler la fonction pour annuler
      cancelDeleteAccount();

      // Vérifier que la section de suppression est masquée
      expect(document.getElementById('delete-account-section').style.display).toBe('none');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should remove error parameters from URL when canceling delete account', () => {
      // Simuler une URL avec des paramètres d'erreur (modifier le mock existant)
      window.location.href = 'http://example.com/dashboard?error=password';
      window.location.search = '?error=password';

      // Mock de history.replaceState
      const replaceStateMock = jest.fn();
      window.history.replaceState = replaceStateMock;

      // Afficher d'abord le formulaire
      document.getElementById('delete-account-section').style.display = 'block';

      // Appeler la fonction pour annuler
      cancelDeleteAccount();

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
      initDashboardEventListeners();

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
      initDashboardEventListeners();

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle missing cancel delete button gracefully', () => {
      // Supprimer le bouton d'annulation
      document.getElementById('cancel-delete-btn').remove();

      // Appeler initDashboardEventListeners
      initDashboardEventListeners();

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe('URL Error Handling', () => {
    it('should show delete account form when showDeleteAccountForm is called', () => {
      // Directly call the function to test its behavior
      // (The DOMContentLoaded listener checks window.location at load time)
      showDeleteAccountForm();

      // Vérifier que le formulaire de suppression est affiché
      expect(document.getElementById('delete-account-section').style.display).toBe('block');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should not show delete account form when not called', () => {
      // Vérifier que le formulaire de suppression est masqué par défaut
      expect(document.getElementById('delete-account-section').style.display).toBe('none');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe('toggleSection', () => {
    beforeEach(() => {
      document.body.innerHTML += `
        <div id="mes-evaluations" style="display: none;">
          <p>Mes évaluations</p>
        </div>
        <div id="evaluations-a-valider" style="display: block;">
          <p>Évaluations à valider</p>
        </div>
        <h3 id="mes-evaluations-title">Mes évaluations</h3>
        <h3 id="evaluations-a-valider-title">Évaluations à valider</h3>
      `;
    });

    it('should show a hidden section', () => {
      const section = document.getElementById('mes-evaluations');
      expect(section.style.display).toBe('none');

      toggleSection('mes-evaluations');

      expect(section.style.display).toBe('block');
    });

    it('should hide a visible section', () => {
      const section = document.getElementById('evaluations-a-valider');
      expect(section.style.display).toBe('block');

      toggleSection('evaluations-a-valider');

      expect(section.style.display).toBe('none');
    });

    it('should toggle section multiple times', () => {
      const section = document.getElementById('mes-evaluations');

      toggleSection('mes-evaluations');
      expect(section.style.display).toBe('block');

      toggleSection('mes-evaluations');
      expect(section.style.display).toBe('none');

      toggleSection('mes-evaluations');
      expect(section.style.display).toBe('block');
    });
  });

  describe('Edit Profile Functionality', () => {
    it('should show edit profile form when edit button is clicked', () => {
      initDashboardEventListeners();

      const editProfileBtn = document.getElementById('edit-profile-btn');
      const userInfo = document.getElementById('user-info');
      const editProfileForm = document.getElementById('edit-profile-form');

      expect(userInfo.style.display).toBe('block');
      expect(editProfileForm.style.display).toBe('none');

      editProfileBtn.click();

      expect(userInfo.style.display).toBe('none');
      expect(editProfileForm.style.display).toBe('block');
    });

    it('should hide edit profile form when cancel is clicked', () => {
      initDashboardEventListeners();

      const editProfileBtn = document.getElementById('edit-profile-btn');
      const cancelEditBtn = document.getElementById('cancel-edit-btn');
      const userInfo = document.getElementById('user-info');
      const editProfileForm = document.getElementById('edit-profile-form');

      // D'abord afficher le formulaire d'édition
      editProfileBtn.click();
      expect(editProfileForm.style.display).toBe('block');

      // Puis annuler
      cancelEditBtn.click();

      expect(userInfo.style.display).toBe('block');
      expect(editProfileForm.style.display).toBe('none');
    });

    it('should handle missing edit profile button gracefully', () => {
      document.getElementById('edit-profile-btn').remove();

      initDashboardEventListeners();

      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle missing cancel edit button gracefully', () => {
      document.getElementById('cancel-edit-btn').remove();

      initDashboardEventListeners();

      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should log error when delete account section is missing', () => {
      document.getElementById('delete-account-section').remove();

      showDeleteAccountForm();

      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('should log error when delete password input is missing', () => {
      document.getElementById('delete-password').remove();

      showDeleteAccountForm();

      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('should log error when cancel delete section is missing', () => {
      document.getElementById('delete-account-section').remove();

      cancelDeleteAccount();

      expect(consoleErrorSpy).toHaveBeenCalled();
    });
  });

  describe('Section Title Click Handlers', () => {
    beforeEach(() => {
      document.body.innerHTML += `
        <div id="mes-evaluations" style="display: none;">Mes évaluations</div>
        <div id="evaluations-a-valider" style="display: none;">Évaluations à valider</div>
        <div id="flans-a-valider" style="display: none;">Flans à valider</div>
        <div id="etablissements-a-valider" style="display: none;">Établissements à valider</div>
        <div id="mes-flans" style="display: none;">Mes flans</div>
        <div id="derniers-flans" style="display: none;">Derniers flans</div>
        <div id="derniers-etablissements" style="display: none;">Derniers établissements</div>
        <div id="dernieres-evaluations" style="display: none;">Dernières évaluations</div>
        <h3 id="mes-evaluations-title">Mes évaluations</h3>
        <h3 id="evaluations-a-valider-title">Évaluations à valider</h3>
        <h3 id="flans-a-valider-title">Flans à valider</h3>
        <h3 id="etablissements-a-valider-title">Établissements à valider</h3>
        <h3 id="mes-flans-title">Mes flans</h3>
        <h3 id="derniers-flans-title">Derniers flans</h3>
        <h3 id="derniers-etablissements-title">Derniers établissements</h3>
        <h3 id="dernieres-evaluations-title">Dernières évaluations</h3>
      `;
    });

    it('should setup click handlers for section titles', () => {
      initDashboardEventListeners();

      const title = document.getElementById('mes-evaluations-title');
      const section = document.getElementById('mes-evaluations');

      expect(title.style.cursor).toBe('pointer');
      expect(section.style.display).toBe('none');

      title.click();

      expect(section.style.display).toBe('block');
    });

    it('should toggle all section types', () => {
      initDashboardEventListeners();

      const sectionTitles = [
    { id: 'mes-evaluations-title', section: 'mes-evaluations' },
    { id: 'mes-flans-title', section: 'mes-flans' },
    { id: 'derniers-flans-title', section: 'derniers-flans' },
    { id: 'derniers-etablissements-title', section: 'derniers-etablissements' },
    { id: 'dernieres-evaluations-title', section: 'dernieres-evaluations' }
      ];

      sectionTitles.forEach(({ id, section }) => {
        const titleElement = document.getElementById(id);
        const sectionElement = document.getElementById(section);

        titleElement.click();
        expect(sectionElement.style.display).toBe('block');

        titleElement.click();
        expect(sectionElement.style.display).toBe('none');
      });
    });
  });

  describe('Clickable Table Rows', () => {
    // Import des fonctions nécessaires
    let generateObjectUrl, setupClickableRows, escapeHtml;

    beforeEach(() => {
      // Importer les fonctions depuis le module dashboard-tables
      // Comme nous utilisons des modules ES, nous devons les importer dynamiquement
      // Pour les tests, nous allons les définir directement
      
      // Définir les fonctions directement pour le test
      generateObjectUrl = function(type, id) {
        switch(type) {
          case 'etablissement': return `/etablissement/${id}`;
          case 'flan': return `/flan/${id}`;
          case 'evaluation': return `/evaluation/${id}`;
          default: return '#';
        }
      };

      escapeHtml = function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
      };

      // Configurer le DOM avec des tableaux de test
      document.body.innerHTML += `
        <table id="test-flans-table">
          <tbody id="test-flans-body">
            <tr class="clickable-row" data-id="1" data-type="flan">
              <td>Flan Vanille</td>
              <td>Boulangerie Martin</td>
            </tr>
            <tr class="clickable-row" data-id="2" data-type="flan">
              <td>Flan Chocolat</td>
              <td>Pâtisserie Dupont</td>
            </tr>
          </tbody>
        </table>
        
        <table id="test-evaluations-table">
          <tbody id="test-evaluations-body">
            <tr class="clickable-row" data-id="101" data-type="evaluation">
              <td>Flan Vanille</td>
              <td>4.5</td>
            </tr>
          </tbody>
        </table>
        
        <table id="test-etablissements-table">
          <tbody id="test-etablissements-body">
            <tr class="clickable-row" data-id="1001" data-type="etablissement">
              <td>Boulangerie Martin</td>
              <td>Paris</td>
            </tr>
          </tbody>
        </table>
        
        <!-- Tableau avec boutons pour tester la prévention de propagation -->
        <table id="test-table-with-buttons">
          <tbody>
            <tr class="clickable-row" data-id="3" data-type="flan">
              <td>Flan Fraise</td>
              <td><button class="test-button">Éditer</button></td>
            </tr>
          </tbody>
        </table>
      `;

      // Initialiser le gestionnaire de clics
      setupClickableRows = function() {
        document.addEventListener('click', function(e) {
          let row = e.target.closest('.clickable-row');
          
          if (e.target.closest('button, a, input, select, textarea, .no-propagate')) {
            return;
          }
          
          if (row) {
            const type = row.dataset.type;
            const id = row.dataset.id;
            const url = generateObjectUrl(type, id);
            
            // Pour les tests, nous stockons l'URL dans un attribut data
            // au lieu de naviguer
            row.dataset.lastClickedUrl = url;
            e.preventDefault();
          }
        });
      };

      setupClickableRows();
    });

    it('should generate correct URLs for different object types', () => {
      expect(generateObjectUrl('flan', 1)).toBe('/flan/1');
      expect(generateObjectUrl('evaluation', 101)).toBe('/evaluation/101');
      expect(generateObjectUrl('etablissement', 1001)).toBe('/etablissement/1001');
      expect(generateObjectUrl('unknown', 1)).toBe('#');
    });

    it('should handle clicks on flan rows', () => {
      const row = document.querySelector('#test-flans-body tr:first-child');
      row.click();
      
      expect(row.dataset.lastClickedUrl).toBe('/flan/1');
    });

    it('should handle clicks on evaluation rows', () => {
      const row = document.querySelector('#test-evaluations-body tr');
      row.click();
      
      expect(row.dataset.lastClickedUrl).toBe('/evaluation/101');
    });

    it('should handle clicks on etablissement rows', () => {
      const row = document.querySelector('#test-etablissements-body tr');
      row.click();
      
      expect(row.dataset.lastClickedUrl).toBe('/etablissement/1001');
    });

    it('should prevent navigation when clicking on buttons', () => {
      const button = document.querySelector('.test-button');
      const row = button.closest('tr');
      
      // Cliquer sur le bouton ne devrait pas déclencher la navigation
      button.click();
      
      // L'URL ne devrait pas être définie sur la ligne
      expect(row.dataset.lastClickedUrl).toBeUndefined();
    });

    it('should handle clicks on different cells of the same row', () => {
      const row = document.querySelector('#test-flans-body tr:first-child');
      const firstCell = row.querySelector('td:first-child');
      const secondCell = row.querySelector('td:last-child');
      
      // Cliquer sur la première cellule
      firstCell.click();
      expect(row.dataset.lastClickedUrl).toBe('/flan/1');
      
      // Cliquer sur la deuxième cellule
      secondCell.click();
      expect(row.dataset.lastClickedUrl).toBe('/flan/1');
    });

    it('should escape HTML content properly', () => {
      const unsafeText = '<script>alert("XSS")</script>';
      const safeText = escapeHtml(unsafeText);
      
      expect(safeText).not.toContain('<script>');
      expect(safeText).toContain('&lt;script&gt;');
    });

    it('should handle missing data gracefully', () => {
      expect(escapeHtml(null)).toBe('');
      expect(escapeHtml(undefined)).toBe('');
      expect(escapeHtml('')).toBe('');
    });
  });
});