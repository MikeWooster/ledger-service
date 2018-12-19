FROM python:3.6-alpine

RUN apk update && apk add postgresql-dev gcc musl-dev

RUN adduser -D ledger

WORKDIR /home/ledger

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY ledger ledger
COPY migrations migrations
COPY boot.sh boot.sh
COPY ledger_runner.py ledger_runner.py
RUN chmod +x boot.sh ledger_runner.py

ENV FLASK_APP ledger

RUN chown -R ledger:ledger ./

USER ledger

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]

