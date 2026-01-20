/**
 * Module de géolocalisation pour l'application PlanFlan
 * 
 * Ce module gère la géolocalisation de l'utilisateur et l'interaction avec la carte.
 * Il remplace la logique backend précédente par une approche purement frontend.
 */

/**
 * Classe principale pour gérer la géolocalisation
 */
class GeolocationHandler {
    /**
     * @param {L.Map} map - Instance de la carte Leaflet
     * @param {Object} options - Options de configuration
     */
    constructor(map, options = {}) {
        this.map = map;
        this.userMarker = null;
        this.userCircle = null;
        this.options = {
            defaultZoom: options.defaultZoom || 14,
            maxAccuracyRadius: options.maxAccuracyRadius || 1000,
            ...options
        };
        
        // Créer l'icône de l'utilisateur avec un emoji 📍
        this.userIcon = L.divIcon({
            html: '📍',
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            className: 'user-position-icon'
        });
    }

    /**
     * Active la géolocalisation
     * @returns {Promise} - Promesse résolue avec la position ou rejetée avec l'erreur
     */
    activate() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                const error = new Error("La géolocalisation n'est pas supportée par votre navigateur");
                this._showError(error.message);
                reject(error);
                return;
            }

            // Afficher un indicateur de chargement
            this._showLoading();

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this._hideLoading();
                    this._handlePosition(position);
                    resolve(position);
                },
                (error) => {
                    this._hideLoading();
                    this._handleError(error);
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }

    /**
     * Traite la position reçue
     * @param {GeolocationPosition} position - Position géolocalisée
     */
    _handlePosition(position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        const accuracy = position.coords.accuracy;

        // Centrer la carte sur la position de l'utilisateur
        this.map.setView([lat, lng], this.options.defaultZoom);

        // Ajouter/maj le marqueur de l'utilisateur
        this._updateUserMarker(lat, lng);

        // Ajouter/maj le cercle de précision
        if (accuracy && accuracy <= this.options.maxAccuracyRadius) {
            this._updateAccuracyCircle(lat, lng, accuracy);
        } else {
            this._removeAccuracyCircle();
        }

        // Déclencher un événement pour que d'autres parties du code puissent réagir
        const event = new CustomEvent('userPositionUpdated', {
            detail: {
                latitude: lat,
                longitude: lng,
                accuracy: accuracy,
                timestamp: position.timestamp
            }
        });
        document.dispatchEvent(event);

        this._showSuccess("Position mise à jour avec succès");
    }

    /**
     * Met à jour le marqueur de l'utilisateur
     */
    _updateUserMarker(lat, lng) {
        if (this.userMarker) {
            this.userMarker.setLatLng([lat, lng]);
        } else {
            this.userMarker = L.marker([lat, lng], {
                icon: this.userIcon,
                title: "Votre position",
                riseOnHover: true
            }).addTo(this.map);
            
            // Ajouter un popup informatif
            this.userMarker.bindPopup("<b>Votre position</b><br>Cliquez pour centrer la carte");
            
            // Re-centrer la carte au clic
            this.userMarker.on('click', () => {
                this.map.setView([lat, lng], this.options.defaultZoom);
            });
        }
    }

    /**
     * Met à jour le cercle de précision
     */
    _updateAccuracyCircle(lat, lng, accuracy) {
        if (this.userCircle) {
            this.userCircle.setLatLng([lat, lng]);
            this.userCircle.setRadius(accuracy);
        } else {
            this.userCircle = L.circle([lat, lng], {
                radius: accuracy,
                color: '#3388ff',
                fillColor: '#3388ff',
                fillOpacity: 0.1,
                weight: 1
            }).addTo(this.map);
        }
    }

    /**
     * Supprime le cercle de précision
     */
    _removeAccuracyCircle() {
        if (this.userCircle) {
            this.map.removeLayer(this.userCircle);
            this.userCircle = null;
        }
    }

    /**
     * Gère les erreurs de géolocalisation
     */
    _handleError(error) {
        let message;
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message = "Vous avez refusé l'accès à votre position";
                break;
            case error.POSITION_UNAVAILABLE:
                message = "La position n'est pas disponible";
                break;
            case error.TIMEOUT:
                message = "La requête de géolocalisation a expiré";
                break;
            default:
                message = "Erreur inconnue de géolocalisation";
        }
        
        this._showError(message);
        
        // Déclencher un événement d'erreur
        const event = new CustomEvent('userPositionError', {
            detail: { error: message }
        });
        document.dispatchEvent(event);
    }

    /**
     * Calcule la distance entre deux points (en km)
     * Formule de Haversine
     * @param {number} lat1 - Latitude du premier point
     * @param {number} lon1 - Longitude du premier point
     * @param {number} lat2 - Latitude du deuxième point
     * @param {number} lon2 - Longitude du deuxième point
     * @returns {number} Distance en kilomètres
     */
    static calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Rayon de la Terre en km
        const dLat = this._toRad(lat2 - lat1);
        const dLon = this._toRad(lon2 - lon1);
        const a =
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(this._toRad(lat1)) * Math.cos(this._toRad(lat2)) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    /**
     * Convertit les degrés en radians
     */
    static _toRad(degrees) {
        return degrees * Math.PI / 180;
    }

    /**
     * Affiche un indicateur de chargement
     */
    _showLoading() {
        if (window.showLoading) {
            window.showLoading("Géolocalisation en cours...");
        }
    }

    /**
     * Masque l'indicateur de chargement
     */
    _hideLoading() {
        if (window.hideLoading) {
            window.hideLoading();
        }
    }

    /**
     * Affiche un message de succès
     */
    _showSuccess(message) {
        if (window.showToast) {
            window.showToast(message, 'success');
        }
    }

    /**
     * Affiche un message d'erreur
     */
    _showError(message) {
        console.error("Géolocalisation:", message);
        if (window.showToast) {
            window.showToast(message, 'error');
        }
    }

    /**
     * Nettoie les marqueurs de géolocalisation
     */
    clear() {
        if (this.userMarker) {
            this.map.removeLayer(this.userMarker);
            this.userMarker = null;
        }
        this._removeAccuracyCircle();
    }
}

// Exporter pour les modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GeolocationHandler;
}

// Exporter pour le navigateur
if (typeof window !== 'undefined') {
    window.GeolocationHandler = GeolocationHandler;
}