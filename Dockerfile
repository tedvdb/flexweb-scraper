FROM python:3.10-slim

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

VOLUME /app/output

ENTRYPOINT [ "python", "/app/fetch.py" ]