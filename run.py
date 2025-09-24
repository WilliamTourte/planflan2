from app import create_app # dans __init__.py

app = create_app() # Pendant le développement

if __name__ == '__main__': # Lance le serveur seulement quand j'exécute le fichier
    app.run(debug=True)
