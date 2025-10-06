<<<<<<< HEAD
# Projet_healthcare
=======
# Projet de Migration de Données Healthcare (via Docker)

Ce projet contient un processus automatisé pour migrer des données de santé d'un fichier CSV vers une base de données MongoDB, le tout entièrement conteneurisé à l'aide de Docker et Docker Compose.

## Prérequis

*   [Docker]
*   [Docker Compose]

Assurez-vous que le service Docker est en cours d'exécution sur votre machine.

## Comment Lancer la Migration

L'ensemble du processus de migration est automatisé et peut être lancé avec une seule commande depuis la racine de ce projet.

```bash
docker-compose up --build
```

*   `--build` : Cette option force la reconstruction de l'image du service de migration, ce qui est utile si vous avez modifié les scripts Python.
*   Pour lancer en arrière-plan, ajoutez l'option `-d` : `docker-compose up --build -d`.

## Déroulement du Processus de Migration

Lorsque vous lancez la commande `docker-compose up`, voici la séquence d'événements qui se produit :

1.  **Orchestration** : `docker-compose` lit le fichier `docker-compose.yml` et crée un réseau interne pour les services.

2.  **Démarrage de la Base de Données** : Le service `mongodb` est démarré. Une base de données MongoDB 5.0 est initialisée et un volume nommé `mongo-data` est créé pour assurer la persistance des données.

3.  **Démarrage du Service de Migration** : Le service `migration_process` est démarré. Il exécute la commande suivante, qui enchaîne plusieurs scripts Python :

    *   **`wait_for_mongo.py`** : Ce script met le processus en pause jusqu'à ce que la base de données `mongodb` soit entièrement prête à accepter des connexions. Cela évite les erreurs de connexion prématurées.

    *   **`clean_csv.py`** : Ce script lit le fichier source `healthcare_dataset.csv`, effectue des opérations de nettoyage (suppression de doublons, standardisation) et sauvegarde le résultat dans `healthcare_dataset_cleaned.csv`.

    *   **`migration.py`** : Le cœur du processus. Ce script se connecte à la base de données, vide la collection `patients` pour garantir une migration propre, lit le fichier `healthcare_dataset_cleaned.csv`, et insère les données dans la collection.

    *   **`test_integrity.py`** : Une fois la migration terminée, ce script exécute automatiquement une série de tests pour valider l'intégrité des données dans MongoDB (nombre de documents, présence des champs, absence de doublons, etc.).

4.  **Fin du Processus** : Une fois tous les scripts exécutés avec succès, le conteneur `migration_process` s'arrête avec un code de sortie `0`.

## Comment Vérifier le Résultat

*   **Consulter les logs** : Pour voir le détail de chaque étape du processus, utilisez la commande :
    ```bash
    docker-compose logs migration_process
    ```

*   **Inspecter la base de données** : Pour vous connecter directement à la base de données et voir un exemple de document inséré, utilisez la commande suivante :
    ```bash
    docker exec -it mongodb mongosh -u root -p password --eval "use healthcare; db.patients.findOne();"
    ```

## Comment Nettoyer l'Environnement

Pour arrêter et supprimer tous les conteneurs, réseaux et volumes créés par `docker-compose`, exécutez la commande :

```bash
docker-compose down -v
```

*   L'option `-v` est importante car elle supprime également le volume `mongo-data`, vous assurant de repartir de zéro lors de la prochaine exécution.
>>>>>>> f7e48c0 (Ajout du fichier README.md)
