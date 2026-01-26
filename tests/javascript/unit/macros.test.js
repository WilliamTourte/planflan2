/**
 * Tests unitaires pour les fonctions de macros.js
 * 
 * Ces tests vérifient que les fonctions d'édition et d'annulation
 * pour les flans fonctionnent correctement.
 */

import { editFlan, cancelEditFlan, initMacroEventListeners } from '../../../app/static/js/macros.js';

describe('Macros Functions - Flan Edition', () => {
  // Mock des fonctions globales et du DOM
  let consoleErrorSpy;
  
  beforeEach(() => {
    // Configurer un DOM de base pour un flan
    document.body.innerHTML = `
      <div id="flan-1-display" style="display: block;">
        <h2 id="flan-1-nom">Flan Vanille</h2>
        <span id="flan-1-description">Un délicieux flan à la vanille</span>
      </div>
      <div id="flan-1-edit" style="display: none;">
        <form>
          <input type="text" id="edit-flan-1-nom" value="">
          <input type="text" id="edit-flan-1-description" value="">
        </form>
      </div>
      <button class="macro-edit-btn" data-object-type="flan" data-object-id="1">
        Edit
      </button>
    `;

    // Espionner console.error pour détecter les erreurs
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
    jest.clearAllMocks();
  });

  describe('editFlan Function', () => {
    it('should correctly edit a flan without description prefix', () => {
      // Appeler la fonction d'édition
      editFlan(1);

      // Vérifier que les éléments sont correctement basculés
      expect(document.getElementById('flan-1-display').style.display).toBe('none');
      expect(document.getElementById('flan-1-edit').style.display).toBe('block');

      // Vérifier que les valeurs sont correctement copiées
      expect(document.getElementById('edit-flan-1-nom').value).toBe('Flan Vanille');
      expect(document.getElementById('edit-flan-1-description').value).toBe('Un délicieux flan à la vanille');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle flan with empty description', () => {
      // Modifier le DOM pour avoir une description vide
      document.getElementById('flan-1-description').textContent = '';

      // Appeler la fonction d'édition
      editFlan(1);

      // Vérifier que les valeurs sont correctement copiées
      expect(document.getElementById('edit-flan-1-description').value).toBe('');
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle flan with description containing only spaces', () => {
      // Modifier le DOM pour avoir une description avec seulement des espaces
      document.getElementById('flan-1-description').textContent = '   ';

      // Appeler la fonction d'édition
      editFlan(1);

      // Vérifier que les valeurs sont correctement copiées et trimées
      expect(document.getElementById('edit-flan-1-description').value).toBe('');
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle missing elements gracefully', () => {
      // Supprimer un élément requis
      document.getElementById('flan-1-nom').remove();

      // Appeler la fonction d'édition
      editFlan(1);

      // Vérifier qu'un message d'erreur a été logged
      expect(consoleErrorSpy).toHaveBeenCalled();
    });
  });

  describe('cancelEditFlan Function', () => {
    it('should correctly cancel flan editing', () => {
      // Mettre en mode édition d'abord
      document.getElementById('flan-1-display').style.display = 'none';
      document.getElementById('flan-1-edit').style.display = 'block';

      // Appeler la fonction d'annulation
      cancelEditFlan(1);

      // Vérifier que les éléments sont correctement basculés
      expect(document.getElementById('flan-1-display').style.display).toBe('block');
      expect(document.getElementById('flan-1-edit').style.display).toBe('none');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle missing elements gracefully', () => {
      // Supprimer un élément requis
      document.getElementById('flan-1-display').remove();

      // Appeler la fonction d'annulation
      cancelEditFlan(1);

      // Vérifier qu'un message d'erreur a été logged
      expect(consoleErrorSpy).toHaveBeenCalled();
    });
  });

  describe('Macro Event Listeners Integration', () => {
    it('should correctly attach event listeners to flan edit buttons', () => {
      // Appeler initMacroEventListeners pour attacher les écouteurs
      initMacroEventListeners();

      // Simuler un clic sur le bouton d'édition
      const editButton = document.querySelector('.macro-edit-btn');
      editButton.click();

      // Vérifier que la fonction appropriée a été appelée (vérification du comportement réel)
      expect(document.getElementById('flan-1-display').style.display).toBe('none');
      expect(document.getElementById('flan-1-edit').style.display).toBe('block');
      expect(document.getElementById('edit-flan-1-nom').value).toBe('Flan Vanille');
      expect(document.getElementById('edit-flan-1-description').value).toBe('Un délicieux flan à la vanille');

      // Vérifier qu'aucun message d'erreur n'a été logged
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });

    it('should handle multiple flan edit buttons', () => {
      // Ajouter un deuxième flan
      document.body.innerHTML += `
        <div id="flan-2-display" style="display: block;">
          <h2 id="flan-2-nom">Flan Chocolat</h2>
          <span id="flan-2-description">Un délicieux flan au chocolat</span>
        </div>
        <div id="flan-2-edit" style="display: none;">
          <form>
            <input type="text" id="edit-flan-2-nom" value="">
            <input type="text" id="edit-flan-2-description" value="">
          </form>
        </div>
        <button class="macro-edit-btn" data-object-type="flan" data-object-id="2">
          Edit Flan 2
        </button>
      `;

      // Réinitialiser les event listeners
      initMacroEventListeners();

      // Tester le deuxième bouton
      const editButtons = document.querySelectorAll('.macro-edit-btn');
      editButtons[1].click();

      // Vérifier que le bon flan est édité
      expect(document.getElementById('flan-2-display').style.display).toBe('none');
      expect(document.getElementById('flan-2-edit').style.display).toBe('block');
      expect(document.getElementById('edit-flan-2-nom').value).toBe('Flan Chocolat');
      expect(document.getElementById('edit-flan-2-description').value).toBe('Un délicieux flan au chocolat');

      // Vérifier que le premier flan n'a pas été modifié
      expect(document.getElementById('flan-1-display').style.display).toBe('block');
      expect(document.getElementById('flan-1-edit').style.display).toBe('none');
    });
  });
});