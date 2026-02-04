# =============================================================================
# Stage 1: Builder - Installation des dépendances
# =============================================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Installer les dépendances de build en une seule couche et nettoyer le cache apt
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        pkg-config \
        python3-dev \
        default-libmysqlclient-dev \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les dépendances (layer cachée si requirements ne change pas)
COPY requirements-prod.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime - Image finale légère
# =============================================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Installer uniquement les dépendances runtime (pas de build-essential)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-mysql-client \
        libmariadb3 && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier le code source
COPY . .

# Créer le dossier uploads avec les bonnes permissions
RUN mkdir -p /app/static/uploads && \
    chmod -R 777 /app/static/uploads

# Copier et préparer l'entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Configuration de l'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["sh", "-c", "/app/entrypoint.sh"]
