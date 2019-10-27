FROM nginx:latest

RUN rm /etc/nginx/conf.d/sites-available/*
COPY conf /etc/nginx/conf.d/sites-available
COPY html /usr/share/nginx/html
