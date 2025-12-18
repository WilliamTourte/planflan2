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

from math import radians, sin, cos, sqrt, atan2

def calculer_distance(lat1, lon1, lat2, lon2):
    # Rayon de la Terre en kilomètres
    R = 6371.0

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
