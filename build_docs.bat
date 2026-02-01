@echo off
REM Script pour générer la documentation Sphinx de PlanFlan
REM Usage: build_docs.bat [clean|serve]

if "%1"=="clean" (
    echo Nettoyage de la documentation générée...
    rmdir /s /q source\_build
    echo Documentation nettoyée !
    goto end
)

if "%1"=="serve" (
    echo Génération et serveur de la documentation Sphinx pour PlanFlan...
    cd source
    sphinx-build -b html . _build\html
    cd ..
    if %ERRORLEVEL% equ 0 (
        echo Documentation générée avec succès !
        echo Démarrage du serveur sur http://localhost:8000
        echo Appuyez sur Ctrl+C pour arrêter le serveur...
        cd source\_build\html
        python -m http.server 8000
    ) else (
        echo Erreur lors de la génération de la documentation.
    )
    goto end
)

if "%1"=="strict" (
    echo Génération de la documentation avec avertissements stricts...
    cd source
    sphinx-build -W -b html . _build\html
    if %ERRORLEVEL% equ 0 (
        echo Documentation générée avec succès !
    ) else (
        echo Erreurs trouvées lors de la génération.
    )
    cd ..
    goto end
)

REM Défaut : générer simplement la documentation
echo Génération de la documentation Sphinx pour PlanFlan...
cd source
sphinx-build -b html . _build\html

if %ERRORLEVEL% equ 0 (
    echo Documentation générée avec succès !
    echo La documentation est disponible dans: source\_build\html
    echo Ouvrir index.html dans un navigateur pour la consulter.
) else (
    echo Erreur lors de la génération de la documentation.
)

cd ..

:end