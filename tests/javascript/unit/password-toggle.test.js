/**
 * Tests unitaires pour le module password-toggle.js
 */

import { initializePasswordToggles } from '../../../app/static/js/password-toggle.js';

describe('Password Toggle Module', () => {
    beforeEach(() => {
        // Réinitialiser le DOM avant chaque test
        document.body.innerHTML = '';
        jest.clearAllMocks();
    });

    describe('initializePasswordToggles', () => {
        it('should initialize toggle buttons correctly', () => {
            // Setup DOM with password field and toggle button
            document.body.innerHTML = `
                <input type="password" id="password-field" name="password">
                <button data-toggle-password data-target="password-field">
                    <i class="bi bi-eye"></i>
                </button>
            `;

            // Call the function
            initializePasswordToggles();

            // Verify button exists
            const button = document.querySelector('[data-toggle-password]');
            expect(button).toBeTruthy();

            // Verify event listener was added (by simulating click)
            const passwordInput = document.getElementById('password-field');
            expect(passwordInput.type).toBe('password');

            // Simulate click
            button.click();

            // Verify password field type changed
            expect(passwordInput.type).toBe('text');

            // Verify icon changed
            const icon = button.querySelector('i');
            expect(icon.classList.contains('bi-eye-slash')).toBe(true);
            expect(icon.classList.contains('bi-eye')).toBe(false);
        });

        it('should handle multiple toggle buttons', () => {
            document.body.innerHTML = `
                <input type="password" id="password1" name="password1">
                <button data-toggle-password data-target="password1">
                    <i class="bi bi-eye"></i>
                </button>

                <input type="password" id="password2" name="password2">
                <button data-toggle-password data-target="password2">
                    <i class="bi bi-eye"></i>
                </button>
            `;

            initializePasswordToggles();

            const button1 = document.querySelectorAll('[data-toggle-password]')[0];
            const button2 = document.querySelectorAll('[data-toggle-password]')[1];
            const password1 = document.getElementById('password1');
            const password2 = document.getElementById('password2');

            // Click first button
            button1.click();
            expect(password1.type).toBe('text');
            expect(password2.type).toBe('password'); // Should not affect second field

            // Click second button
            button2.click();
            expect(password2.type).toBe('text');
            expect(password1.type).toBe('text'); // First should remain text
        });

        it('should toggle back to password when clicked again', () => {
            document.body.innerHTML = `
                <input type="password" id="password-field" name="password">
                <button data-toggle-password data-target="password-field">
                    <i class="bi bi-eye"></i>
                </button>
            `;

            initializePasswordToggles();

            const button = document.querySelector('[data-toggle-password]');
            const passwordInput = document.getElementById('password-field');
            const icon = button.querySelector('i');

            // First click - show password
            button.click();
            expect(passwordInput.type).toBe('text');
            expect(icon.classList.contains('bi-eye-slash')).toBe(true);

            // Second click - hide password
            button.click();
            expect(passwordInput.type).toBe('password');
            expect(icon.classList.contains('bi-eye')).toBe(true);
            expect(icon.classList.contains('bi-eye-slash')).toBe(false);
        });

        it('should handle missing target element gracefully', () => {
            document.body.innerHTML = `
                <button data-toggle-password data-target="non-existent-field">
                    <i class="bi bi-eye"></i>
                </button>
            `;

            // Should not throw error
            expect(() => initializePasswordToggles()).not.toThrow();
        });

        it('should handle missing icon element gracefully', () => {
            document.body.innerHTML = `
                <input type="password" id="password-field" name="password">
                <button data-toggle-password data-target="password-field">
                    Show/Hide
                </button>
            `;

            // Should not throw error
            expect(() => {
                initializePasswordToggles();
                const button = document.querySelector('[data-toggle-password]');
                button.click();
            }).not.toThrow();
        });
    });
});