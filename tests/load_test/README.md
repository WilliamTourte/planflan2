# Tests de charge PlanFlan - Environnement de développement

## Prérequis
- Python 3.7+
- Locust installé (`pip install locust`)
- Application Flask en cours d'exécution
- Package python-dotenv (`pip install python-dotenv`)

## Configuration

1. **Vérifier votre configuration** :
   - L'application doit tourner sur le port spécifié dans `.env` (FLASK_RUN_PORT) ou 5000 par défaut
   - La base de données doit contenir des établissements pour Lyon, Toulouse et Paris

2. **Installer les dépendances** :
```bash
pip install locust python-dotenv
```

## Exécution des tests

### Option 1: Avec interface web (recommandé pour débuter)
```bash
locust -f tests/load_test/simple_locustfile.py
```
Puis ouvrir http://localhost:8089 dans votre navigateur.

### Option 2: Mode headless (pour les tests automatisés)
```bash
locust -f tests/load_test/simple_locustfile.py --headless \
       --users 30 \
       --spawn-rate 5 \
       --run-time 1m \
       --csv=results
```

## Scénarios de test recommandés

### Test 1: Vérification de base (pour s'assurer que tout fonctionne)
- Utilisateurs: 10
- Taux de montée: 2 utilisateurs/s
- Durée: 30 secondes
- Objectif: Vérifier que l'application répond correctement

### Test 2: Charge légère (simulation d'activité normale)
- Utilisateurs: 50
- Taux de montée: 5 utilisateurs/s
- Durée: 2 minutes
- Objectif: Observer le comportement avec une charge modérée

### Test 3: Charge moyenne (pour voir les premières limites)
- Utilisateurs: 150
- Taux de montée: 10 utilisateurs/s
- Durée: 3 minutes
- Objectif: Identifier les premiers goulots d'étranglement

### Test 4: Charge élevée (pour tester les limites)
- Utilisateurs: 300
- Taux de montée: 15 utilisateurs/s
- Durée: 5 minutes
- Objectif: Voir comment l'application se comporte sous forte charge

## Analyse des résultats

### Métriques à surveiller
1. **Temps de réponse** :
   - Moyen : devrait rester sous 1-2 secondes
   - 95e percentile : indicateurs des requêtes les plus lentes

2. **Débit** :
   - Nombre de requêtes par seconde
   - Doit rester stable ou augmenter linéairement

3. **Taux d'erreur** :
   - Doit rester sous 1%
   - Surveiller les erreurs 500 (problèmes serveur)

4. **Utilisation des ressources** :
   - CPU et mémoire de votre machine
   - Connexions base de données

### Actions en cas de problèmes
- Si les temps de réponse dépassent 3-5 secondes : problème de performance
- Si le taux d'erreur dépasse 1% : problème de stabilité
- Si le débit chute soudainement : problème de capacité

## Bonnes pratiques
- Commencez toujours par un test léger pour vérifier la configuration
- Augmentez progressivement la charge
- Surveillez les logs de votre application Flask en parallèle
- Notez les seuils où les problèmes apparaissent