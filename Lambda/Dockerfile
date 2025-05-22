FROM python:3.12

RUN apt update -y && apt install -y zip

WORKDIR /home

COPY requirements.txt .

RUN mkdir -p python \
 && pip install --no-cache-dir -r requirements.txt -t python

RUN zip -r python_dependencies.zip python/