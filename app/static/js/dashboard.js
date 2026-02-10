// Export for testing and module access
// Les fonctions seront exportées à la fin du fichier après leur définition

/**
 * Show the delete account form and focus on the password field.
 */
function showDeleteAccountForm() {
    const deleteAccountSection = document.getElementById("delete-account-section");
    const deletePasswordInput = document.getElementById("delete-password");
    
    if (deleteAccountSection && deletePasswordInput) {
        deleteAccountSection.style.display = "block";
        deletePasswordInput.focus();
    } else {
        console.error('Delete account elements not found:', {
            deleteAccountSection: !!deleteAccountSection,
            deletePasswordInput: !!deletePasswordInput
        });
    }
}

/**
 * Cancel account deletion and hide the delete account form.
 * Also removes error parameters from the URL.
 */
function cancelDeleteAccount() {
    const deleteAccountSection = document.getElementById("delete-account-section");
    if (deleteAccountSection) {
        deleteAccountSection.style.display = "none";
        // Supprimer les paramètres d'erreur de l'URL
        const url = new URL(window.location.href);
        url.searchParams.delete("error");
        window.history.replaceState({}, "", url.toString());
    } else {
        console.error('Delete account section not found');
    }
}

// Afficher le formulaire si erreur dans l'URL
document.addEventListener("DOMContentLoaded", function () {
    if (window.location.search.includes("error=")) {
        showDeleteAccountForm();
    }
});

/**
 * Toggle the visibility of a section by its ID.
 * Only affects the clicked section, other sections remain in their current state.
 * @param {string} sectionId - The ID of the section to toggle
 */
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const currentDisplay = window.getComputedStyle(section).display;
        if (currentDisplay === "none") {
            section.style.display = "block";
        } else {
            section.style.display = "none";
        }
    }
}

/**
 * Initialize all event listeners for the dashboard page.
 * Sets up handlers for profile editing, account deletion, and section toggling.
 */
function initDashboardEventListeners() {
    const editProfileBtn = document.getElementById("edit-profile-btn");
    const cancelEditBtn = document.getElementById("cancel-edit-btn");
    const deleteAccountBtn = document.getElementById("delete-account-btn");
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    
    if (editProfileBtn) {
        editProfileBtn.addEventListener("click", function () {
            const userInfo = document.getElementById("user-info");
            const editProfileForm = document.getElementById("edit-profile-form");
            if (userInfo && editProfileForm) {
                userInfo.style.display = "none";
                editProfileForm.style.display = "block";
            } else {
                console.error('Profile edit elements not found');
            }
        });
    }
    
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener("click", function () {
            const userInfo = document.getElementById("user-info");
            const editProfileForm = document.getElementById("edit-profile-form");
            if (userInfo && editProfileForm) {
                userInfo.style.display = "block";
                editProfileForm.style.display = "none";
            } else {
                console.error('Profile edit elements not found');
            }
        });
    }
    
    // Bouton pour afficher le formulaire de suppression de compte
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener("click", showDeleteAccountForm);
    }
    
    // Bouton pour annuler la suppression de compte
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener("click", cancelDeleteAccount);
    }
    
    // Titres cliquables pour basculer les sections
const sectionTitles = [
    { id: 'mes-evaluations-title', section: 'mes-evaluations' },
    { id: 'mes-flans-title', section: 'mes-flans' },
    { id: 'derniers-flans-title', section: 'derniers-flans' },
    { id: 'derniers-etablissements-title', section: 'derniers-etablissements' },
    { id: 'dernieres-evaluations-title', section: 'dernieres-evaluations' }
];

sectionTitles.forEach(function(title) {
    const element = document.getElementById(title.id);
    
    if (element) {
        // Trouver la section correspondante de manière robuste
        let sectionElement = document.getElementById(title.section);
        
        // Si la section n'est pas trouvée directement, utiliser une approche plus robuste
        if (!sectionElement) {
            // Essayer de trouver la section en regardant les éléments suivants
            let current = element.nextElementSibling;
            while (current) {
                // Vérifier si c'est un élément DIV avec la bonne classe
                if (current.tagName === 'DIV' && current.classList.contains('section-content')) {
                    sectionElement = current;
                    break;
                }
                // Sinon, passer à l'élément suivant
                current = current.nextElementSibling;
            }
        }

        if (sectionElement) {
            element.addEventListener('click', function(event) {
                // Empêcher TOUTE propagation
                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();

                // Toggle UNIQUEMENT cette section
                const currentDisplay = window.getComputedStyle(sectionElement).display;
                sectionElement.style.display = (currentDisplay === "none") ? "block" : "none";

                console.log(`Toggled ${title.section}:`, sectionElement.style.display);

                return false;
            });

            element.style.cursor = 'pointer';
            element.style.userSelect = 'none'; // Empêcher la sélection du texte
        } else {
            console.warn(`Section not found for title: ${title.id}`);
        }
    }
});
}

// Make functions available globally for inline scripts
if (typeof window !== 'undefined') {
    window.dashboard = {
        showDeleteAccountForm,
        cancelDeleteAccount,
        initDashboardEventListeners,
        toggleSection
    };
}

// Export for testing and module access
export { initDashboardEventListeners, showDeleteAccountForm, cancelDeleteAccount, toggleSection };

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", initDashboardEventListeners);