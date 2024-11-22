# Dockerfile

FROM python:3.9-buster

# install nginx
RUN apt-get update && apt-get install nginx vim libxml2-dev libxmlsec1-dev clamav-daemon clamav-freshclam clamav-unofficial-sigs -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN if [ ! -f /etc/debug.log ]; then touch /etc/debug.log ; fi
RUN chmod a=rwx /etc/debug.log

# copy source and install dependencies
RUN mkdir -p /tmp/app
RUN mkdir -p /tmp/app/pip_cache
RUN mkdir -p /tmp/app/openlxp-xia-coursera
COPY requirements.txt start-server.sh start-app.sh /tmp/app/
RUN chmod +x /tmp/app/start-server.sh
RUN chmod +x /tmp/app/start-app.sh
COPY ./app /tmp/app/openlxp-xia-coursera/
WORKDIR /tmp/app
RUN pip install -r requirements.txt --cache-dir /tmp/app/pip_cache
RUN chown -R www-data:www-data /tmp/app
WORKDIR /tmp/app/openlxp-xia-coursera/
RUN freshclam
RUN service clamav-daemon start

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
