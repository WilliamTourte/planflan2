// Fonctions pour les établissements
function cancelEdit(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'block';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'none';
}

function editEtablissement(idEtab) {
    document.getElementById('etablissement-' + idEtab + '-display').style.display = 'none';
    document.getElementById('etablissement-' + idEtab + '-edit').style.display = 'block';
}

// Fonctions pour les flans
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

function cancelEdit(idFlan) {
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
function editEvaluation(idEval) {
    document.getElementById('evaluation-' + idEval + '-display').style.display = 'none';
    document.getElementById('evaluation-' + idEval + '-edit').style.display = 'block';
}

function cancelEdit(idEval) {
    document.getElementById('evaluation-' + idEval + '-display').style.display = 'block';
    document.getElementById('evaluation-' + idEval + '-edit').style.display = 'none';
}