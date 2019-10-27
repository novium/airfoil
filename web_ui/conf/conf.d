server {
    listen 80;
    server_name: data.cloud.dev.novium.pw;

    location / {
        proxy_pass http://data:9000;
        proxy_http_version	1.1;
        proxy_cache_bypass	$http_upgrade;

        proxy_set_header Upgrade			$http_upgrade;
        proxy_set_header Connection 		"upgrade";
        proxy_set_header Host				$host;
        proxy_set_header X-Real-IP			$remote_addr;
        proxy_set_header X-Forwarded-For	$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto	$scheme;
        proxy_set_header X-Forwarded-Host	$host;
        proxy_set_header X-Forwarded-Port	$server_port;
    }
}

server {
    listen 80;
    server_name: api.cloud.dev.novium.pw;

    location / {
        proxy_pass http://api:8080;
        proxy_http_version	1.1;
        proxy_cache_bypass	$http_upgrade;

        proxy_set_header Upgrade			$http_upgrade;
        proxy_set_header Connection 		"upgrade";
        proxy_set_header Host				$host;
        proxy_set_header X-Real-IP			$remote_addr;
        proxy_set_header X-Forwarded-For	$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto	$scheme;
        proxy_set_header X-Forwarded-Host	$host;
        proxy_set_header X-Forwarded-Port	$server_port;
    }
}

server {
    listen 80;
    server_name cloud.dev.novium.pw;

    location / {
        root /usr/share/nginx/html;
    }
}
