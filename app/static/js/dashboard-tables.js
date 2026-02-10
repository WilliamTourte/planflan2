/**
 * Dashboard Tables Module
 * Gestion simple des tableaux du dashboard
 */

/**
 * Génère l'URL pour un objet donné
 * @param {string} type - Type d'objet ('etablissement', 'flan', 'evaluation')
 * @param {number} id - ID de l'objet
 * @returns {string} URL complète
 */
function generateObjectUrl(type, id) {
    const baseUrl = window.location.origin;
    switch(type) {
        case 'etablissement': return `${baseUrl}/etablissement/${id}`;
        case 'flan': return `${baseUrl}/flan/${id}`;
        case 'evaluation': return `${baseUrl}/evaluation/${id}`;
        default: return '#';
    }
}

/**
 * Charge les données pour les tableaux du dashboard
 */
async function loadDashboardTables() {
    const dashboardContent = document.querySelector('.dashboard-content');
    const isAdmin = dashboardContent && dashboardContent.dataset.isAdmin === 'True';

    // Charger les flans de l'utilisateur
    await loadUserFlans();

    // Charger les évaluations de l'utilisateur
    await loadUserEvaluations();

    // Si admin, charger les tableaux admin
    if (isAdmin) {
        const adminTables = document.querySelector('.admin-tables');
        if (adminTables) {
            adminTables.style.display = 'block';
        }
        await loadRecentEtablissements();
        await loadRecentFlans();
        await loadRecentEvaluations();
    }
}

/**
 * Charge les flans proposés par l'utilisateur
 */
async function loadUserFlans() {
    try {
        const response = await fetch('/api/dashboard/user/flans');
        if (!response.ok) throw new Error('Erreur lors du chargement des flans');

        const data = await response.json();
        const tbody = document.getElementById('mes-flans-body');

        if (tbody) {
            if (data.data && data.data.length > 0) {
                tbody.innerHTML = data.data.map(flan => `
                    <tr class="clickable-row"
                        data-id="${flan.id_flan}"
                        data-type="flan"
                        style="cursor: pointer;">
                        <td>${escapeHtml(flan.nom)}</td>
                        <td>${escapeHtml(flan.etablissement ? flan.etablissement.nom : 'N/A')}</td>
                        <td>${flan.type_saveur || 'N/A'}</td>
                        <td>${flan.prix ? flan.prix + '€' : 'N/A'}</td>
                        <td>${new Date().toLocaleDateString()}</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="6">Aucun flan proposé</td></tr>';
            }
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Charge les évaluations de l'utilisateur
 */
async function loadUserEvaluations() {
    try {
        const response = await fetch('/api/dashboard/user/evaluations');
        if (!response.ok) throw new Error('Erreur lors du chargement des évaluations');

        const data = await response.json();
        const tbody = document.getElementById('mes-evaluations-body');

        if (tbody) {
            if (data.data && data.data.length > 0) {
                tbody.innerHTML = data.data.map(evaluation => `
                    <tr class="clickable-row"
                        data-id="${evaluation.id_eval}"
                        data-type="evaluation"
                        style="cursor: pointer;">
                        <td>${escapeHtml(evaluation.flan ? evaluation.flan.nom : 'N/A')}</td>
                        <td>${escapeHtml(evaluation.flan && evaluation.flan.etablissement ? evaluation.flan.etablissement.nom : 'N/A')}</td>
                        <td>${evaluation.moyenne || 'N/A'}</td>
                        <td>${new Date(evaluation.date_creation).toLocaleDateString()}</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5">Aucune évaluation</td></tr>';
            }
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Charge les derniers établissements (admin)
 */
async function loadRecentEtablissements() {
    try {
        const response = await fetch('/api/dashboard/admin/recent_etablissements');
        if (!response.ok) throw new Error('Erreur lors du chargement des établissements');

        const data = await response.json();
        const tbody = document.getElementById('derniers-etablissements-body');

        if (tbody) {
            if (data.data && data.data.length > 0) {
                tbody.innerHTML = data.data.map(etab => `
                    <tr class="clickable-row"
                        data-id="${etab.id_etab}"
                        data-type="etablissement"
                        style="cursor: pointer;">
                        <td>${escapeHtml(etab.nom)}</td>
                        <td>${escapeHtml(etab.ville)}</td>
                        <td>${etab.type_etab}</td>

                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="3">Aucun établissement récent</td></tr>';
            }
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Charge les derniers flans (admin)
 */
async function loadRecentFlans() {
    try {
        const response = await fetch('/api/dashboard/admin/recent_flans');
        if (!response.ok) throw new Error('Erreur lors du chargement des flans');

        const data = await response.json();
        const tbody = document.getElementById('derniers-flans-body');

        if (tbody) {
            if (data.data && data.data.length > 0) {
                tbody.innerHTML = data.data.map(flan => `
                    <tr class="clickable-row"
                        data-id="${flan.id_flan}"
                        data-type="flan"
                        style="cursor: pointer;">
                        <td>${escapeHtml(flan.nom)}</td>
                        <td>${escapeHtml(flan.etablissement ? flan.etablissement.nom : 'N/A')}</td>
                        <td>${flan.type_saveur || 'N/A'}</td>

                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="3">Aucun flan récent</td></tr>';
            }
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Charge les dernières évaluations (admin)
 */
async function loadRecentEvaluations() {
    try {
        const response = await fetch('/api/dashboard/admin/recent_evaluations');
        if (!response.ok) throw new Error('Erreur lors du chargement des évaluations');

        const data = await response.json();
        const tbody = document.getElementById('dernieres-evaluations-body');

        if (tbody) {
            if (data.data && data.data.length > 0) {
                tbody.innerHTML = data.data.map(evaluation => `
                    <tr class="clickable-row"
                        data-id="${evaluation.id_eval}"
                        data-type="evaluation"
                        style="cursor: pointer;">
                        <td>${escapeHtml(evaluation.flan ? evaluation.flan.nom : 'N/A')}</td>
                        <td>${escapeHtml(evaluation.flan && evaluation.flan.etablissement ? evaluation.flan.etablissement.nom : 'N/A')}</td>
                        <td>${escapeHtml(evaluation.utilisateur ? evaluation.utilisateur.pseudo : evaluation.id_user)}</td>
                        <td>${evaluation.moyenne || 'N/A'}</td>
                        <td>${new Date(evaluation.date_creation).toLocaleDateString()}</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5">Aucune évaluation récente</td></tr>';
            }
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Échappe les caractères HTML pour éviter les injections XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Gestionnaire de clic pour les lignes cliquables
 */
function setupClickableRows() {
    document.addEventListener('click', function(e) {
        // Vérifier si le clic provient d'une ligne cliquable
        let row = e.target.closest('.clickable-row');

        // Si on a cliqué sur un bouton ou un élément interactif, ne pas naviguer
        if (e.target.closest('button, a, input, select, textarea, .no-propagate')) {
            return;
        }

        // Si c'est bien une ligne cliquable
        if (row) {
            const type = row.dataset.type;
            const id = row.dataset.id;
            const url = generateObjectUrl(type, id);

            // Navigation vers l'URL
            window.location.href = url;
        }
    });
}

// Initialisation au chargement de la page
document.addEventListener("DOMContentLoaded", function() {
    loadDashboardTables();
    setupClickableRows();
});