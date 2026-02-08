/**
 * Module pour gérer l'affichage/masquage des mots de passe
 */

/**
 * Module pour gérer l'affichage/masquage des mots de passe
 */

export function initializePasswordToggles() {
    // Sélectionner tous les boutons de toggle
    const toggleButtons = document.querySelectorAll('[data-toggle-password]');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            const icon = this.querySelector('i');

            if (passwordInput) {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                } else {
                    passwordInput.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                }
            }
        });
    });
}