FROM python:buster
RUN pip3 install flask mysql-connector-python


WORKDIR /usr/src/app
COPY api.py .

CMD [ "python3", "api.py" ]
