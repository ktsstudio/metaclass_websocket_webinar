
FROM python:3.9-slim as builder
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc git build-essential
RUN pip install -U pip setuptools wheel

WORKDIR /wheels
COPY requirements.txt /
RUN pip wheel -r /requirements.txt


FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1

COPY --from=builder /wheels /wheels
RUN apt update && apt install gettext -y
RUN pip install -U pip
RUN pip install /wheels/* \
        && rm -rf /wheels \
        && rm -rf /root/.cache/pip/*

WORKDIR /code
COPY . .

ARG API_TOKEN
ARG CONNECT_PATH
RUN cat client/index.html | envsubst > client/index.html.new && mv client/index.html.new client/index.html

ENTRYPOINT ["python"]
CMD ["main.py"]
