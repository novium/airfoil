FROM python:buster
RUN pip3 install flask mysql-connector-python celery


WORKDIR /usr/src/app
COPY api.py .
COPY ../worker/tasks.py tasks.py

CMD [ "python3", "api.py" ]
