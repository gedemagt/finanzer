ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
  apk add --no-cache \
    python3 git py3-pip curl

    
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN git clone -b dash https://github.com/gedemagt/finanzer

WORKDIR /finanzer

RUN /root/.local/bin/poetry config virtualenvs.create false \
  && /root/.local/bin/poetry install --only main --no-interaction --no-ansi

CMD [ "python3", "finance/webapp/webapp.py" ]
