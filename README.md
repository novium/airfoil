# Airfoil

## Local development:
1. docker-compose up

## Deploy:
1. Create an instance with Docker and OpenStack credentials as environment variables.
2. Install docker
3. Authenticate with GitHub package registry
4. `docker stack deploy -c docker-compose.prod.yml --with-registry-auth`

*Notes*

Traefik (reverse proxy) service discovery can be a slow when deploying it, it speeds up later. Configure hostnames in docker-compose.prod.yml to the correct hostnames before deploying. Services available:

* api.hostname.tld (REST API)
* data.hostname.tld (MinIO / Object Storage)
* hostname.tld (Web Interface)
* hostname.tld:8080 (Traefik/reverse proxy monitoring)

# Dependencies

- docker
- docker-compose

Also, make sure that the docker daemon is running. If not, run `systemctl start docker.service`.
