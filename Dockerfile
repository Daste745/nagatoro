FROM python:3.8.5-slim-buster
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python3", "-u" ,"./nagatoro.py" ]
