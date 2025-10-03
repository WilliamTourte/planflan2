from flask import url_for




def enlever_accents(text): # Enlève les accents parce que la police ne les gère pas bien
    import unicodedata
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')

def afficher_etablissements(resultats):
    etablissements = resultats
    etablissements_json = [{
        'id_etab': etab.id_etab,
        'nom': etab.nom,
        'adresse': etab.adresse,
        'ville': etab.ville,
        'code_postal': etab.code_postal,
        'latitude': float(etab.latitude),
        'longitude': float(etab.longitude),
        'url': url_for('main.afficher_etablissement_unique', id_etab=etab.id_etab)
    } for etab in etablissements]


    return(etablissements, etablissements_json)