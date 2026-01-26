// Fonctions pour les établissements
/**
 * Cancel editing an establishment and return to display mode.
 * @param {number} idEtab - The ID of the establishment to cancel editing
 */
export function cancelEdit(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'block';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'none';
}

/**
 * Enable editing mode for an establishment.
 * @param {number} idEtab - The ID of the establishment to edit
 */
export function editEtablissement(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'none';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'block';
}

// Fonctions pour les flans
/**
 * Enable editing mode for a flan.
 * @param {number} idFlan - The ID of the flan to edit
 */
export function editFlan(idFlan) {
    console.log('DEBUG: editFlan called with idFlan:', idFlan);
    
    const displayElement = document.getElementById('flan-' + idFlan + '-display');
    const editElement = document.getElementById('flan-' + idFlan + '-edit');
    const nomElement = document.getElementById('flan-' + idFlan + '-nom');
    const descriptionElement = document.getElementById('flan-' + idFlan + '-description');
    const editNomInput = document.getElementById('edit-flan-' + idFlan + '-nom');
    const editDescriptionInput = document.getElementById('edit-flan-' + idFlan + '-description');

    console.log('DEBUG: Element IDs searched:', {
        displayId: 'flan-' + idFlan + '-display',
        editId: 'flan-' + idFlan + '-edit',
        nomId: 'flan-' + idFlan + '-nom',
        descId: 'flan-' + idFlan + '-description',
        editNomId: 'edit-flan-' + idFlan + '-nom',
        editDescId: 'edit-flan-' + idFlan + '-description'
    });

    console.log('DEBUG: Elements found:', {
        displayElement: displayElement,
        editElement: editElement,
        nomElement: nomElement,
        descriptionElement: descriptionElement,
        editNomInput: editNomInput,
        editDescriptionInput: editDescriptionInput
    });

    if (displayElement && editElement && nomElement && descriptionElement && editNomInput && editDescriptionInput) {
        console.log('DEBUG: All elements found, proceeding with edit');
        editNomInput.value = nomElement.textContent;
        // Remove the .replace() call since the description doesn't have "Description : " prefix
        editDescriptionInput.value = descriptionElement.textContent.trim();
        
        console.log('DEBUG: Before display changes:', {
            displayStyle: displayElement.style.display,
            editStyle: editElement.style.display
        });
        
        displayElement.style.display = 'none';
        editElement.style.display = 'block';
        
        console.log('DEBUG: After display changes:', {
            displayStyle: displayElement.style.display,
            editStyle: editElement.style.display
        });
        
        // Ajout d'un log pour vérifier si le formulaire est visible
        setTimeout(() => {
            console.log('DEBUG: Form visibility after 1 second:', {
                editElementStyle: editElement.style.display,
                editElementOffsetHeight: editElement.offsetHeight,
                editElementClientHeight: editElement.clientHeight
            });
        }, 1000);
    } else {
        console.error('Elements not found for flan editing:', {
            displayElement: !!displayElement,
            editElement: !!editElement,
            nomElement: !!nomElement,
            descriptionElement: !!descriptionElement,
            editNomInput: !!editNomInput,
            editDescriptionInput: !!editDescriptionInput
        });
        
        // Log all elements with similar IDs to help debugging
        const allElements = document.querySelectorAll('[id^="flan-"], [id^="edit-flan-"]');
        console.log('DEBUG: All elements with flan IDs:', Array.from(allElements).map(el => el.id));
    }
}

/**
 * Cancel editing a flan and return to display mode.
 * @param {number} idFlan - The ID of the flan to cancel editing
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
 * Enable editing mode for an evaluation.
 * @param {number} idEval - The ID of the evaluation to edit
 */
export function editEvaluation(idEval) {
    document.getElementById('evaluation-' + idEval + '-display').style.display = 'none';
    document.getElementById('evaluation-' + idEval + '-edit').style.display = 'block';
}

/**
 * Cancel editing an evaluation and return to display mode.
 * @param {number} idEval - The ID of the evaluation to cancel editing
 */
export function cancelEditEval(idEval) {
    document.getElementById('evaluation-' + idEval + '-display').style.display = 'block';
    document.getElementById('evaluation-' + idEval + '-edit').style.display = 'none';
}

/**
 * Initialize event listeners for macro action buttons.
 * This function sets up event listeners for edit buttons generated by macros.
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
    
    function setupMacroListeners() {
        // Get all edit buttons generated by macros
        const editButtons = document.querySelectorAll('.macro-edit-btn');
        
        editButtons.forEach(button => {
            button.addEventListener('click', function() {
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
            button.addEventListener('click', function() {
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
