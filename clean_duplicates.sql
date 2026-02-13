-- Script pour nettoyer les doublons dans la table etablissements
-- Étape 1: Voir les doublons
SELECT nom, adresse, COUNT(*) as count
FROM etablissements
GROUP BY nom, adresse
HAVING COUNT(*) > 1;

-- Étape 2: Supprimer les doublons (un par un)
-- Remplacez les valeurs ci-dessous par les doublons réels que vous voyez
-- Exemple pour supprimer un doublon de "Test Etab" à "123 Rue Test"
-- Garde un seul enregistrement et supprime les autres

-- Pour chaque doublon trouvé, exécutez quelque chose comme:
-- DELETE FROM etablissements WHERE id_etab IN (
--     SELECT id_etab FROM (
--         SELECT id_etab
--         FROM etablissements
--         WHERE nom = 'Test Etab' AND adresse = '123 Rue Test'
--         ORDER BY id_etab DESC
--         LIMIT 1  -- Garde le plus récent
--     ) AS to_keep
-- );

-- Alternative plus simple: supprimer tous sauf un
-- DELETE FROM etablissements
-- WHERE (nom, adresse) = ('Test Etab', '123 Rue Test')
-- AND id_etab NOT IN (
--     SELECT MIN(id_etab)
--     FROM etablissements
--     WHERE nom = 'Test Etab' AND adresse = '123 Rue Test'
-- );