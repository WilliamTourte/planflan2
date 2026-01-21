@echo off
REM Script pour générer la documentation Sphinx de PlanFlan
REM Usage: build_docs.bat

echo Génération de la documentation Sphinx pour PlanFlan...
cd source
sphinx-build -b html . _build/html

if %ERRORLEVEL% equ 0 (
    echo Documentation générée avec succès !
    echo La documentation est disponible dans: source/_build/html
    echo Ouvrir index.html dans un navigateur pour la consulter.
) else (
    echo Erreur lors de la génération de la documentation.
)

cd ..