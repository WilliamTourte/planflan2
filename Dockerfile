FROM python:3.12-slim

WORKDIR /python-docker

RUN apt-get update
RUN apt-get install -y --no-install-recommends pkg-config python3-dev default-libmysqlclient-dev build-essential default-mysql-client

# Copie de la liste de dépendances
COPY requirements.txt .
# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /python-docker/entrypoint.sh
RUN chmod +x /python-docker/entrypoint.sh

# ENTRYPOINT ["/python-docker/entrypoint.sh"]
CMD ["sh", "-c", "/python-docker/entrypoint.sh"]
# CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
