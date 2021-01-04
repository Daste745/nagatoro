# Using python:slim so we don't have to install build deps manually
FROM python:slim AS build

COPY requirements.txt /requirements.txt
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:alpine

COPY --from=build /venv /venv
COPY . /app
WORKDIR /app

CMD [ "/venv/bin/python", "-u" ,"./nagatoro.py" ]
