FROM python:3.12
ENV PYTHONUNBUFFERED 1

# Needed for SAML support
RUN  apt-get update
# RUN  apt-get -y install libxml2-dev libxmlsec1-dev libxmlsec1-openssl

WORKDIR /code/
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY manage.py ./
COPY Makefile ./      
COPY ./example ./example/
COPY ./django_static ./django_static/  
RUN python manage.py collectstatic --noinput
