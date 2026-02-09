// Fonctions pour les établissements
/**
 * Annule l'édition d'un établissement et revient en mode affichage.
 * 
 * @function cancelEdit
 * @param {number} idEtab - L'identifiant de l'établissement à annuler l'édition
 * @returns {void}
 * 
 * @example
 * // Annuler l'édition de l'établissement avec l'ID 123
 * cancelEdit(123);
 */
export function cancelEdit(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'block';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'none';
}

/**
 * Active le mode édition pour un établissement.
 * 
 * @function editEtablissement
 * @param {number} idEtab - L'identifiant de l'établissement à éditer
 * @returns {void}
 * 
 * @example
 * // Activer l'édition de l'établissement avec l'ID 123
 * editEtablissement(123);
 */
export function editEtablissement(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'none';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'block';
}

// Fonctions pour les flans
/**
 * Active le mode édition pour un flan.
 * 
 * @function editFlan
 * @param {number} idFlan - L'identifiant du flan à éditer
 * @returns {void}
 * 
 * @description
 * Cette fonction bascule entre le mode affichage et le mode édition pour un flan.
 * Elle copie les valeurs actuelles dans les champs de formulaire et affiche le formulaire d'édition.
 * 
 * @example
 * // Activer l'édition du flan avec l'ID 456
 * editFlan(456);
 */
/**
 * Active le mode édition pour un flan.
 * 
 * @function editFlan
 * @param {number} idFlan - L'identifiant du flan à éditer
 * @returns {void}
 * 
 * @example
 * // Activer l'édition du flan avec l'ID 456
 * editFlan(456);
 */
export function editFlan(idFlan) {
    // Masquer le mode affichage et afficher le mode édition
    document.getElementById('flan-' + idFlan + '-display').style.display = 'none';
    document.getElementById('flan-' + idFlan + '-edit').style.display = 'block';
    
    // Copier les valeurs des éléments d'affichage vers les champs de formulaire
    const nomElement = document.getElementById('flan-' + idFlan + '-nom');
    const descriptionElement = document.getElementById('flan-' + idFlan + '-description');
    const nomInput = document.getElementById('edit-flan-' + idFlan + '-nom');
    const descriptionInput = document.getElementById('edit-flan-' + idFlan + '-description');
    
    if (nomElement && nomInput) {
        nomInput.value = nomElement.textContent.trim();
    }
    if (descriptionElement && descriptionInput) {
        descriptionInput.value = descriptionElement.textContent.trim();
    }
}

/**
 * Annule l'édition d'un flan et revient en mode affichage.
 * 
 * @function cancelEditFlan
 * @param {number} idFlan - L'identifiant du flan à annuler l'édition
 * @returns {void}
 * 
 * @example
 * // Annuler l'édition du flan avec l'ID 456
 * cancelEditFlan(456);
 */
export function cancelEditFlan(idFlan) {
    const displayElement = document.getElementById('flan-' + idFlan + '-display');
    const editElement = document.getElementById('flan-' + idFlan + '-edit');

    if (displayElement && editElement) {
        displayElement.style.display = 'block';
        editElement.style.display = 'none';
    } else {
        console.error('Elements not found for flan cancel editing:', {
            displayElement: !!displayElement,
            editElement: !!editElement
        });
    }
}

// Fonctions pour les évaluations
/**
 * Active le mode édition pour une évaluation.
 * 
 * @function editEvaluation
 * @param {number} idEval - L'identifiant de l'évaluation à éditer
 * @returns {void}
 * 
 * @description
 * Cette fonction bascule entre le mode affichage et le mode édition pour une évaluation.
 * Le formulaire est pré-rempli par la route avec les valeurs existantes.
 * 
 * @example
 * // Activer l'édition de l'évaluation avec l'ID 789
 * editEvaluation(789);
 */
export function editEvaluation(idEval) {
    // Masquer le mode affichage et afficher le mode édition
    const displayElement = document.getElementById('evaluation-' + idEval + '-display');
    const editElement = document.getElementById('evaluation-' + idEval + '-edit');
    
    if (displayElement && editElement) {
        displayElement.style.display = 'none';
        editElement.style.display = 'block';
    } else {
        console.error('Elements not found for evaluation editing:', {
            displayElement: !!displayElement,
            editElement: !!editElement
        });
    }
}

/**
 * Annule l'édition d'une évaluation et revient en mode affichage.
 * 
 * @function cancelEditEval
 * @param {number} idEval - L'identifiant de l'évaluation à annuler l'édition
 * @returns {void}
 * 
 * @example
 * // Annuler l'édition de l'évaluation avec l'ID 789
 * cancelEditEval(789);
 */
export function cancelEditEval(idEval) {
    const displayElement = document.getElementById('evaluation-' + idEval + '-display');
    const editElement = document.getElementById('evaluation-' + idEval + '-edit');
    
    if (displayElement && editElement) {
        displayElement.style.display = 'block';
        editElement.style.display = 'none';
    } else {
        console.error('Elements not found for evaluation cancel editing:', {
            displayElement: !!displayElement,
            editElement: !!editElement
        });
    }
}

/**
 * Initialise les écouteurs d'événements pour les boutons d'action macro.
 * 
 * @function initMacroEventListeners
 * @returns {void}
 * 
 * @description
 * Cette fonction configure les écouteurs d'événements pour tous les boutons
 * d'édition et d'annulation générés par les macros Jinja2.
 * Elle est appelée automatiquement lors du chargement du script.
 * 
 * @example
 * // Appelé automatiquement au chargement
 * // Peut aussi être appelé manuellement si nécessaire
 * initMacroEventListeners();
 */
export function initMacroEventListeners() {
    // Check if we're in a browser environment
    if (typeof document === 'undefined') {
        return;
    }
    
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupMacroListeners);
    } else {
        setupMacroListeners();
    }
    
    /**
     * Configure les écouteurs d'événements pour tous les boutons d'édition macro
     * @returns {void}
     */
    function setupMacroListeners() {
        // Get all edit buttons generated by macros
        const editButtons = document.querySelectorAll('.macro-edit-btn');
        
        editButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                const objectType = this.getAttribute('data-object-type');
                const objectId = this.getAttribute('data-object-id');
                
                // Call the appropriate edit function based on object type
                switch(objectType) {
                    case 'etablissement':
                        editEtablissement(parseInt(objectId));
                        break;
                    case 'flan':
                        editFlan(parseInt(objectId));
                        break;
                    case 'evaluation':
                        editEvaluation(parseInt(objectId));
                        break;
                    default:
                        console.error('Unknown object type:', objectType);
                }
            });
        });
        
        // Setup cancel buttons event listeners
        const cancelButtons = document.querySelectorAll('.btn-canceledit');
        cancelButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                const objectType = this.getAttribute('data-object-type');
                const objectId = this.getAttribute('data-object-id');
                
                // Call the appropriate cancel function based on object type
                switch(objectType) {
                    case 'etablissement':
                        cancelEdit(parseInt(objectId));
                        break;
                    case 'flan':
                        cancelEditFlan(parseInt(objectId));
                        break;
                    case 'evaluation':
                        cancelEditEval(parseInt(objectId));
                        break;
                    case 'profile':
                        // Handle profile edit cancellation
                        const userInfo = document.getElementById('user-info');
                        const editProfileForm = document.getElementById('edit-profile-form');
                        if (userInfo && editProfileForm) {
                            userInfo.style.display = 'block';
                            editProfileForm.style.display = 'none';
                        }
                        break;
                    default:
                        console.error('Unknown object type:', objectType);
                }
            });
        });
        
        // Setup form event listeners
        const deleteForms = document.querySelectorAll('.macro-delete-form');
        deleteForms.forEach(form => {
            // The confirm is already handled by onsubmit, no need for additional JS
        });
        
        const validateForms = document.querySelectorAll('.macro-validate-form');
        validateForms.forEach(form => {
            // The confirm is already handled by onsubmit, no need for additional JS
        });
    }
}

// Auto-initialize when this script is loaded
initMacroEventListeners();
