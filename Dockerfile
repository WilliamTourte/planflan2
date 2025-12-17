FROM python:3.12-slim

WORKDIR /python-docker

RUN apt-get update
RUN apt-get install -y --no-install-recommends pkg-config python3-dev default-libmysqlclient-dev build-essential default-mysql-client

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
# CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
