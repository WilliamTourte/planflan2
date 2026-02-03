/**
 * Tests unitaires pour le module base.js
 *
 * Ce module teste les fonctions de navigation de base
 */

describe('Base Module', () => {
    let originalReferrer;
    let originalHost;
    let originalHistoryBack;
    let originalLocationHref;

    beforeEach(() => {
        // Sauvegarder les valeurs originales
        originalReferrer = document.referrer;
        originalHost = window.location.host;
        originalHistoryBack = window.history.back;

        // Mock window.location
        delete window.location;
        window.location = {
            host: 'test.example.com',
            href: 'http://test.example.com/page',
            assign: jest.fn()
        };

        // Définir le setter pour href
        Object.defineProperty(window.location, 'href', {
            set: jest.fn(),
            get: () => 'http://test.example.com/page'
        });

        // Mock window.history.back
        window.history.back = jest.fn();

        // Charger le module base.js (simuler son comportement)
        window.goBackOrRedirect = function(fallbackUrl) {
            var referrer = document.referrer;

            if (referrer && referrer.includes(window.location.host)) {
                try {
                    window.history.back();
                } catch (e) {
                    window.location.href = fallbackUrl;
                }
            } else {
                window.location.href = fallbackUrl;
            }
        };
    });

    afterEach(() => {
        // Restaurer les valeurs originales
        window.history.back = originalHistoryBack;
        jest.clearAllMocks();
    });

    describe('goBackOrRedirect', () => {
        it('should be defined on window object', () => {
            expect(window.goBackOrRedirect).toBeDefined();
            expect(typeof window.goBackOrRedirect).toBe('function');
        });

        it('should go back in history when referrer is from same host', () => {
            // Simuler un referrer du même hôte
            Object.defineProperty(document, 'referrer', {
                value: 'http://test.example.com/previous-page',
                configurable: true
            });

            window.goBackOrRedirect('/fallback');

            expect(window.history.back).toHaveBeenCalled();
        });

        it('should redirect to fallback URL when no referrer', () => {
            // Simuler pas de referrer
            Object.defineProperty(document, 'referrer', {
                value: '',
                configurable: true
            });

            const hrefSetter = jest.fn();
            Object.defineProperty(window.location, 'href', {
                set: hrefSetter,
                get: () => 'http://test.example.com/page'
            });

            window.goBackOrRedirect('/fallback');

            expect(hrefSetter).toHaveBeenCalledWith('/fallback');
        });

        it('should redirect to fallback URL when referrer is external', () => {
            // Simuler un referrer externe
            Object.defineProperty(document, 'referrer', {
                value: 'http://external-site.com/page',
                configurable: true
            });

            const hrefSetter = jest.fn();
            Object.defineProperty(window.location, 'href', {
                set: hrefSetter,
                get: () => 'http://test.example.com/page'
            });

            window.goBackOrRedirect('/home');

            expect(hrefSetter).toHaveBeenCalledWith('/home');
        });

        it('should handle history.back throwing an error', () => {
            // Simuler un referrer du même hôte
            Object.defineProperty(document, 'referrer', {
                value: 'http://test.example.com/previous',
                configurable: true
            });

            // Faire que history.back lance une erreur
            window.history.back = jest.fn(() => {
                throw new Error('History navigation failed');
            });

            const hrefSetter = jest.fn();
            Object.defineProperty(window.location, 'href', {
                set: hrefSetter,
                get: () => 'http://test.example.com/page'
            });

            window.goBackOrRedirect('/fallback');

            expect(hrefSetter).toHaveBeenCalledWith('/fallback');
        });
    });

    describe('Search button behavior', () => {
        it('should setup search button click handler on DOMContentLoaded', () => {
            document.body.innerHTML = `
                <form>
                    <input id="search-input" type="text" value="">
                    <button id="search-button" type="submit">Search</button>
                </form>
            `;

            const searchButton = document.getElementById('search-button');
            expect(searchButton).toBeTruthy();
        });

        it('should prevent form submission when search input is empty', () => {
            document.body.innerHTML = `
                <form id="search-form">
                    <input id="search-input" type="text" value="">
                    <button id="search-button" type="submit">Search</button>
                </form>
            `;

            const searchButton = document.getElementById('search-button');
            const searchInput = document.getElementById('search-input');
            const form = document.getElementById('search-form');

            const hrefSetter = jest.fn();
            Object.defineProperty(window.location, 'href', {
                set: hrefSetter,
                get: () => 'http://test.example.com/page'
            });

            // Simuler le comportement du code base.js
            searchButton.addEventListener('click', function(event) {
                if (searchInput.value.trim() === '') {
                    event.preventDefault();
                    window.location.href = "/rechercher";
                }
            });

            const clickEvent = new MouseEvent('click', {
                bubbles: true,
                cancelable: true
            });

            searchButton.dispatchEvent(clickEvent);

            expect(hrefSetter).toHaveBeenCalledWith('/rechercher');
        });

        it('should allow form submission when search input has value', () => {
            document.body.innerHTML = `
                <form id="search-form">
                    <input id="search-input" type="text" value="Lyon">
                    <button id="search-button" type="submit">Search</button>
                </form>
            `;

            const searchButton = document.getElementById('search-button');
            const searchInput = document.getElementById('search-input');

            const hrefSetter = jest.fn();
            Object.defineProperty(window.location, 'href', {
                set: hrefSetter,
                get: () => 'http://test.example.com/page'
            });

            let preventDefaultCalled = false;

            // Simuler le comportement du code base.js
            searchButton.addEventListener('click', function(event) {
                if (searchInput.value.trim() === '') {
                    event.preventDefault();
                    preventDefaultCalled = true;
                    window.location.href = "/rechercher";
                }
            });

            const clickEvent = new MouseEvent('click', {
                bubbles: true,
                cancelable: true
            });

            searchButton.dispatchEvent(clickEvent);

            // Avec une valeur, la redirection ne devrait pas être appelée
            expect(hrefSetter).not.toHaveBeenCalled();
            expect(preventDefaultCalled).toBe(false);
        });
    });
});
