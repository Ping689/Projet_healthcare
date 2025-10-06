# Utiliser une image Python officielle et légère
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances et les installer
# Copier ce fichier en premier permet de profiter du cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers du projet dans le conteneur
COPY . .

# Définir la commande à exécuter lorsque le conteneur démarre
# Le script attendra que la base de données soit prête (géré par docker-compose)
CMD ["python", "migration.py"]
