# Image source: https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/
FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

COPY ./app/ /app/

# RUN apk add --update alpine-sdk
RUN apk update && apk add --no-cache \ 
    autoconf build-base binutils cmake curl \
    musl-dev python3-dev libffi-dev openssl-dev \
    cargo file gcc g++ git libgcc libtool linux-headers \
    libxslt-dev make musl-dev ninja tar unzip wget
    
RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python","-u","main.py"]