server {
    listen 80;
    server_name cloud.dev.novium.pw;

    location / {
        root /usr/share/nginx/html;
    }
}

server {
    listen 80;
    server_name: data.cloud.dev.novium.pw

    location / {
        proxy_pass data:9000;
    }
}

server {
    listen 80;
    server_name: api.cloud.dev.novium.pw

    location / {
        proxy_pass api:8080;
    }
}