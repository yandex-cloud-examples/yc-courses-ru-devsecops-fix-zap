FROM python:3.10.8-alpine

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY ./app/requirements.txt .
RUN pip install --no-cache-dir  -r requirements.txt

COPY ./app $APP_HOME

EXPOSE 80
WORKDIR /app

ENV FLASK_APP=finenomore \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

ENTRYPOINT [ "flask", "run", "--host=0.0.0.0", "--port=80" ]
