from flask import url_for


def enlever_accents(text): # Enlève les accents parce que la police ne les gère pas bien
    import unicodedata
    if text is None:
        return ''
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')


def afficher_etablissements(resultats):
    etablissements = []
    etablissements_json = []
    for etab in resultats:
        etablissements.append(etab)
        etablissements_json.append(etab.to_dict(include_flans=True))
    return etablissements, etablissements_json
