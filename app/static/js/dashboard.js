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
        window.history.replaceState({}, "", url);
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
 * @param {string} sectionId - The ID of the section to toggle
 */
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section.style.display === "none") {
        section.style.display = "block";
    } else {
        section.style.display = "none";
    }
}

// Script pour basculer entre affichage infos et formulaire
function initDashboardEventListeners() {
    const editProfileBtn = document.getElementById("edit-profile-btn");
    const cancelEditBtn = document.getElementById("cancel-edit-btn");
    
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
}

// Export for testing and global access
export { initDashboardEventListeners, showDeleteAccountForm, cancelDeleteAccount, toggleSection };

// Make functions available globally for inline scripts
if (typeof window !== 'undefined') {
    window.dashboard = {
        showDeleteAccountForm,
        cancelDeleteAccount,
        initDashboardEventListeners,
        toggleSection
    };
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", initDashboardEventListeners);