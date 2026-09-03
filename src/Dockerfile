# Utiliser Alpine comme image de base
FROM python:3.10-alpine

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    && apk add --no-cache libffi \
    && apk add --no-cache libstdc++ \
    && apk add --no-cache jpeg-dev zlib-dev

# Copier tous les fichiers du répertoire courant dans le conteneur
COPY . .

# Installer les dépendances Python à partir de requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Supprimer les dépendances de construction pour réduire la taille de l'image
RUN apk del .build-deps

