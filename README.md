# Airfoil

For the course 1TD265 (Applied Cloud Computing) @ Uppsala University. Sets up a distributed airfoil calculation cluster using FEniCS with dynamic scaling based on the size of the workload. Requires OpenStack.

## Local development:
1. docker-compose up

## Deploy:
0. Update `docker-compose.prod.yml` with your domain(s). 3 are required for the web interface, object storage, and API.
1. Create an instance with Docker and OpenStack credentials as environment variables.
2. Install docker
3. Authenticate with GitHub package registry (to download private packages)
4. Run `docker stack deploy -c docker-compose.prod.yml --with-registry-auth`
5. Run `cd worker-monitor && python3 workerMonitor.py`
6. Go to yourdomain.tld and get computing!

*Notes*

Traefik (reverse proxy) service discovery can be a slow when deploying it, it speeds up later. Configure hostnames in docker-compose.prod.yml to the correct hostnames before deploying. Services available:

* api.hostname.tld (REST API)
* data.hostname.tld (MinIO / Object Storage)
* hostname.tld (Web Interface)
* hostname.tld:8080 (Traefik/reverse proxy monitoring)

Preferably, don't mooch off our hosting of the murtazo.tgz tarball! Update it to your location in worker/Dockerfile :)

# Dependencies

- docker

Also, make sure that the docker daemon is running. If not, run `systemctl start docker.service`.
