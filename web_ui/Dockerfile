FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY conf /etc/nginx/conf.d
COPY html /usr/share/nginx/html
