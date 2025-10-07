from flask import url_for




def enlever_accents(text): # Enlève les accents parce que la police ne les gère pas bien
    import unicodedata
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')

def afficher_etablissements(resultats):
    etablissements = resultats
    etablissements_json = [{
        'id_etab': etab.id_etab,
        'nom': enlever_accents(etab.nom), # On enlève les accents car la police Bubblegum ne les gère pas
        'adresse': etab.adresse,
        'ville': etab.ville,
        'code_postal': etab.code_postal,
        'latitude': float(etab.latitude),
        'longitude': float(etab.longitude),
        'url': url_for('main.afficher_etablissement_unique', id_etab=etab.id_etab),
        'visite' : bool(etab.visite),
        'label' : bool(etab.label)
    } for etab in etablissements]


    return(etablissements, etablissements_json)