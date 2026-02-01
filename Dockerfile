FROM python:3.12-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y --no-install-recommends pkg-config python3-dev default-libmysqlclient-dev build-essential default-mysql-client

# Copie de la liste de dépendances
COPY requirements.txt .
# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer le dossier uploads avec les bonnes permissions
RUN mkdir -p /app/static/uploads && \
    chmod -R 777 /app/static/uploads

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "/app/entrypoint.sh"]
# CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
