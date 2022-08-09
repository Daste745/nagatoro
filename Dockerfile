FROM python:3.10-buster AS build

# We could use poetry directly to avoid problems with unhashable packages (such as discord.py)
COPY requirements.txt /requirements.txt
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
STOPSIGNAL SIGINT

COPY docker-entrypoint.sh /usr/local/bin

COPY --from=build /venv /venv
COPY . /app
WORKDIR /app

ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD [ "python",  "main.py" ]
