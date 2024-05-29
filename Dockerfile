FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY askme_mamou/static /usr/share/nginx/html/static
COPY askme_mamou/uploads /usr/share/nginx/html/uploads
