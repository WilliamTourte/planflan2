// Fonctions pour les établissements
/**
 * Cancel editing an establishment and return to display mode.
 * @param {number} idEtab - The ID of the establishment to cancel editing
 */
function cancelEdit(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'block';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'none';
}

/**
 * Enable editing mode for an establishment.
 * @param {number} idEtab - The ID of the establishment to edit
 */
function editEtablissement(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'none';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'block';
}

// Fonctions pour les flans
/**
 * Enable editing mode for a flan.
 * @param {number} idFlan - The ID of the flan to edit
 */
function editFlan(idFlan) {
    const displayElement = document.getElementById('flan-' + idFlan + '-display');
    const editElement = document.getElementById('flan-' + idFlan + '-edit');
    const nomElement = document.getElementById('flan-' + idFlan + '-nom');
    const descriptionElement = document.getElementById('flan-' + idFlan + '-description');

    if (displayElement && editElement && nomElement && descriptionElement) {
        document.getElementById('edit-flan-nom').value = nomElement.textContent;
        document.getElementById('edit-flan-description').value = descriptionElement.textContent.replace('Description : ', '').trim();
        displayElement.style.display = 'none';
        editElement.style.display = 'block';
    } else {
        console.error('Elements not found');
    }
}

/**
 * Cancel editing a flan and return to display mode.
 * @param {number} idFlan - The ID of the flan to cancel editing
 */
function cancelEditFlan(idFlan) {
    const displayElement = document.getElementById('flan-' + idFlan + '-display');
    const editElement = document.getElementById('flan-' + idFlan + '-edit');

    if (displayElement && editElement) {
        displayElement.style.display = 'block';
        editElement.style.display = 'none';
    } else {
        console.error('Elements not found');
    }
}

// Fonctions pour les évaluations
/**
 * Enable editing mode for an evaluation.
 * @param {number} idEval - The ID of the evaluation to edit
 */
function editEvaluation(idEval) {
    document.getElementById('evaluation-' + idEval + '-display').style.display = 'none';
    document.getElementById('evaluation-' + idEval + '-edit').style.display = 'block';
}

/**
 * Cancel editing an evaluation and return to display mode.
 * @param {number} idEval - The ID of the evaluation to cancel editing
 */
function cancelEditEval(idEval) {
    document.getElementById('evaluation-' + idEval + '-display').style.display = 'block';
    document.getElementById('evaluation-' + idEval + '-edit').style.display = 'none';
}