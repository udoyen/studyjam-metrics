# Image source: https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/
FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

COPY ./app/main.py /app/

# RUN pip install -r requirements.txt

EXPOSE 80