FROM python:buster
RUN pip3 install flask mysql-connector-python celery minio


WORKDIR /usr/src/app
COPY api.py .
COPY tasks.py .

CMD [ "python3", "api.py" ]
