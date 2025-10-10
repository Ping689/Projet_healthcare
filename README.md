# Projet de Migration de Données Healthcare (via Docker)

Ce projet contient un processus automatisé pour migrer des données de santé d'un fichier CSV vers une base de données MongoDB, le tout entièrement conteneurisé à l'aide de Docker et Docker Compose.

## Installation et Connexion (Guide Détaillé)

Pour garantir un fonctionnement stable, ce projet utilise un réseau Docker externe. Voici les étapes complètes, de la création du réseau à la connexion avec un client externe comme MongoDB Compass.

**1. Création du Réseau Docker**

Ce projet nécessite un réseau Docker nommé `projet_healthcare`. Ouvrez un terminal et exécutez la commande suivante une seule fois :

```bash
docker network create projet_healthcare
```
*Le fichier `docker-compose.yml` est configuré pour utiliser ce réseau externe.*

**2. Lancement des Services**

Une fois le réseau créé, lancez tous les services en arrière-plan :
```bash
docker-compose up -d --build
```
Cette commande va :
- Construire l'image du script de migration.
- Démarrer le conteneur MongoDB.
- Démarrer le conteneur de migration qui va automatiquement nettoyer le CSV, insérer les données dans la base, et s'arrêter.

**3. Connexion avec MongoDB Compass**

Pour visualiser les données, vous pouvez vous connecter avec MongoDB Compass en utilisant les paramètres suivants :

- **Chaîne de connexion** :
  ```
  mongodb://root:password@localhost:27017/?authSource=admin
  ```
- **Configuration Avancée** :
  - Allez dans l'onglet `More Options`.
  - Assurez-vous que le paramètre **`TLS/SSL`** est bien sur **`None`**.

**Dépannage :**
Si la connexion échoue, assurez-vous qu'aucun autre service (comme une instance locale de MongoDB) n'utilise le port `27017` sur votre machine.

---

## Déroulement du Processus de Migration

Lorsque vous lancez la commande `docker-compose up`, voici la séquence d'événements qui se produit :

1.  **Orchestration** : `docker-compose` lit le fichier `docker-compose.yml` et connecte les services au réseau externe `projet_healthcare`.

2.  **Démarrage de la Base de Données** : Le service `mongodb` est démarré. Une base de données MongoDB 5.0 est initialisée et un volume nommé `mongo-data` est créé pour assurer la persistance des données.

3.  **Démarrage du Service de Migration** : Le service `migration_process` est démarré. Il exécute la commande suivante, qui enchaîne plusieurs scripts Python :

    *   **`wait_for_mongo.py`** : Ce script met le processus en pause jusqu'à ce que la base de données `mongodb` soit entièrement prête à accepter des connexions.

    *   **`clean_csv.py`** : Ce script lit le fichier source `healthcare_dataset.csv`, effectue des opérations de nettoyage et sauvegarde le résultat dans `healthcare_dataset_cleaned.csv`.

    *   **`migration.py`** : Le cœur du processus. Ce script se connecte à la base de données, vide la collection `patients` pour garantir une migration propre, lit le fichier `healthcare_dataset_cleaned.csv`, et insère les données dans la collection.

    *   **`test_integrity.py`** : Une fois la migration terminée, ce script exécute automatiquement une série de tests pour valider l'intégrité des données dans MongoDB.

4.  **Fin du Processus** : Une fois tous les scripts exécutés avec succès, le conteneur `migration_process` s'arrête.

## Comment Vérifier le Résultat

*   **Consulter les logs** : Pour voir le détail de chaque étape du processus, utilisez la commande :
    ```bash
    docker-compose logs migration_process
    ```

*   **Inspecter la base de données (ligne de commande)** : Pour vous connecter directement à la base de données et voir un exemple de document inséré, utilisez la commande suivante :
    ```bash
    docker exec -it mongodb mongosh -u root -p password --eval "use healthcare; db.patients.findOne();"
    ```

## Comment Nettoyer l'Environnement

Pour arrêter et supprimer tous les conteneurs, réseaux et volumes créés par `docker-compose`, exécutez la commande :

```bash
docker-compose down -v
```

*   L'option `-v` est importante car elle supprime également le volume `mongo-data`, vous assurant de repartir de zéro lors de la prochaine exécution.
*   Note : Cette commande ne supprime pas le réseau externe `projet_healthcare`. Pour le supprimer, utilisez `docker network rm projet_healthcare`.