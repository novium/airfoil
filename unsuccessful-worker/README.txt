murtazo.tgz & tasks.py & Dockerfile in this folder, dockercompose.yml at root dir.

!! runme.sh can only run with python 2.7, so I change python3 to python

Still cannot access our minio, but test with play.io, everything works.

minio failed to link:

urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='data', port=80): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f61615c8150>: Failed to establish a new connection: [Errno 111] Connection refused',))
