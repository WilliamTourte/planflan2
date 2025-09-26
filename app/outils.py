def enlever_accents(text): # Enlève les accents parce que la police ne les gère pas bien
    import unicodedata
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
