/**
 * Show the delete account form and focus on the password field.
 */
function showDeleteAccountForm() {
    document.getElementById("delete-account-section").style.display = "block";
    document.getElementById("delete-password").focus();
}

/**
 * Cancel account deletion and hide the delete account form.
 * Also removes error parameters from the URL.
 */
function cancelDeleteAccount() {
    document.getElementById("delete-account-section").style.display = "none";
    // Supprimer les paramètres d'erreur de l'URL
    const url = new URL(window.location.href);
    url.searchParams.delete("error");
    window.history.replaceState({}, "", url);
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
document
    .getElementById("edit-profile-btn")
    .addEventListener("click", function () {
        document.getElementById("user-info").style.display = "none";
        document.getElementById("edit-profile-form").style.display = "block";
    });
document
    .getElementById("cancel-edit-btn")
    .addEventListener("click", function () {
        document.getElementById("user-info").style.display = "block";
        document.getElementById("edit-profile-form").style.display = "none";
    });