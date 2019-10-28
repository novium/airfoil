murtazo.tgz & tasks.py & Dockerfile in this folder, dockercompose.yml at root dir.

Install numpy in python 2.7 (foe runme.sh), others in python3

Changed parameter and now a call lasts 20 secound in my virtubox, can make it longer if you want.

Locally checked by:
docker-compose rm -f -s worker
docker-compose build --no-cache worker
docker-compose up -d broker
docker-compose up

enter container and python:

send celery request and enter settings of database and minio:

minioClient.list_buckets()
myresult = mycursor.fetchall()
for x in myresult:
  print(x)
  
  
Both works.
