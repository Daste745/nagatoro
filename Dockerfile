FROM python:3.8.5-slim-buster
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mv ./data ./data-example
# CMD [ "python3","-u","./nagatoro.py" ]
RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT [ "./docker-entrypoint.sh" ]
