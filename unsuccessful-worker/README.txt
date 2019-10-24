Airfoil, Dockerfile and docker-compose.yml in the same dir /home/a/.
(I have to type the full dir, or it won't be linked, weird.)
In Airfoil, murtazo already unziped and runme.sh already edited

After docker-compose up, using docker ps can see only have minio running. 
So I use docker-compose run worker /bin/bash, but the CMD[] in dockerfile didn't run so I just type them in.

In tasks.py, in this scrip didn't use celery, call with angel 12.

And in tasks.py, the function to upload to minio doesn't work.. connection refused I think??