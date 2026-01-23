/**
 * Module API pour l'application PlanFlan
 * 
 * Ce module gère les appels API vers le backend
 */

import { showLoading, hideLoading, showToast } from './utils.js';

/**
 * Fonction générique pour les appels API avec gestion des erreurs
 * @param {string} url - URL de l'API
 * @param {object} options - Options de la requête
 * @returns {Promise} Promesse avec la réponse
 */
export async function fetchWithErrorHandling(url, options = {}) {
    try {
        showLoading("Chargement des données...");
        console.log(`Appel API: ${url}`, options);
        
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.message || `Erreur API: ${response.status}`;
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        console.log(`Réponse API réussie pour ${url}:`, data);
        return data;
    } catch (error) {
        console.error(`Erreur lors de l'appel API à ${url}:`, error);
        showToast(error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

/**
 * Récupère la liste des établissements
 * @returns {Promise<Array>} Liste des établissements
 */
export async function fetchEtablissements() {
    return fetchWithErrorHandling('/api/etablissements');
}

/**
 * Récupère les villes correspondant à une requête
 * @param {string} query - Terme de recherche
 * @returns {Promise<Array>} Liste des villes
 */
export async function fetchVilles(query) {
    return fetchWithErrorHandling(`/api/villes?q=${encodeURIComponent(query)}`);
}

/**
 * Vérifie si un établissement existe déjà
 * @param {string} nom - Nom de l'établissement
 * @returns {Promise<object>} Résultat de la vérification
 */
export async function checkEtablissementExists(nom) {
    return fetchWithErrorHandling('/verifier_etablissement', {
        method: 'POST',
        body: JSON.stringify({ nom })
    });
}

/**
 * Extrait les informations d'une adresse
 * @param {string} adresse - Adresse à analyser
 * @returns {Promise<object>} Informations extraites
 */
export async function extractAddressInfo(adresse) {
    return fetchWithErrorHandling('/extraire_infos_adresse', {
        method: 'POST',
        body: JSON.stringify({ adresse })
    });
}

/**
 * Récupère le contenu d'un infowindow pour un établissement
 * @param {number} idEtab - ID de l'établissement
 * @returns {Promise<string>} Contenu HTML de l'infowindow
 */
export async function fetchInfowindowContent(idEtab) {
    try {
        showLoading("Chargement des détails...");
        const response = await fetch(`/get_infowindow_content?id_etab=${idEtab}`);
        
        if (!response.ok) {
            throw new Error(`Erreur lors du chargement du contenu: ${response.status}`);
        }
        
        const content = await response.text();
        return content;
    } catch (error) {
        console.error("Erreur lors de la récupération du contenu de l'infowindow:", error);
        showToast(error.message, 'error');
        return `<div class="infowindow-content"><p>Impossible de charger les détails</p></div>`;
    } finally {
        hideLoading();
    }
}

/**
 * Soumet un nouvel établissement
 * @param {object} etablissementData - Données de l'établissement
 * @returns {Promise<object>} Résultat de la soumission
 */
export async function submitEtablissement(etablissementData) {
    return fetchWithErrorHandling('/proposer_etablissement', {
        method: 'POST',
        body: JSON.stringify(etablissementData)
    });
}

/**
 * Met à jour un établissement existant
 * @param {number} idEtab - ID de l'établissement
 * @param {object} updateData - Données à mettre à jour
 * @returns {Promise<object>} Résultat de la mise à jour
 */
export async function updateEtablissement(idEtab, updateData) {
    return fetchWithErrorHandling(`/etablissement/${idEtab}/update`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
    });
}

/**
 * Supprime un établissement
 * @param {number} idEtab - ID de l'établissement
 * @returns {Promise<object>} Résultat de la suppression
 */
export async function deleteEtablissement(idEtab) {
    return fetchWithErrorHandling(`/etablissement/${idEtab}/delete`, {
        method: 'DELETE'
    });
}

// Export pour compatibilité avec les anciens scripts
document.api = {
    fetchWithErrorHandling,
    fetchEtablissements,
    fetchVilles,
    checkEtablissementExists,
    extractAddressInfo,
    fetchInfowindowContent,
    submitEtablissement,
    updateEtablissement,
    deleteEtablissement
};