# Dockerfile

FROM registry.il2.dso.mil/adl-ousd/ecc/ecc-base-python-image:6ed46ad7 as build

WORKDIR /home/python
COPY --chown=python:python  . .

RUN if [ ! -f /tmp/debug.log ]; then touch /tmp/debug.log ; fi && \
    chmod a=rwx /tmp/debug.log && \
# copy source and install dependencies
    mkdir -p /tmp/app && \
    mkdir -p /tmp/app/pip_cache && \
    mkdir -p /tmp/app/openlxp-xia-coursera 

COPY --chown=python:python --chmod=755 requirements.txt start-server.sh start-app.sh /tmp/app/
COPY --chown=python:python .cache/python-packages /tmp/app/.cache/python-packages/
ENV PYTHONPATH /tmp/app/.cache/python-packages
ENV PATH $PATH:/tmp/app/.cache/python-packages/bin

COPY ./app /tmp/app/openlxp-xia-coursera/
WORKDIR /tmp/app/openlxp-xia-coursera/

# Remove unecessary python test files for twistlock scan
RUN rm -rf /home/python/.cache/python-packages/future/backports/test/badcert.pem \
/home/python/.cache/python-packages/future/backports/test/badkey.pem \
/home/python/.cache/python-packages/future/backports/test/keycert.passwd.pem \ 
/home/python/.cache/python-packages/future/backports/test/keycert.pem \
/home/python/.cache/python-packages/future/backports/test/keycert2.pem \
/home/python/.cache/python-packages/future/backports/test/ssl_key.passwd.pem \ 
/home/python/.cache/python-packages/future/backports/test/ssl_key.pem \
/home/python/.cache/python-packages/tornado/test/test.key \
/tmp/app/.cache/python-packages/future/backports/test/badcert.pem \
/tmp/app/.cache/python-packages/future/backports/test/badkey.pem \
/tmp/app/.cache/python-packages/future/backports/test/keycert.passwd.pem \
/tmp/app/.cache/python-packages/future/backports/test/keycert.pem \
/tmp/app/.cache/python-packages/future/backports/test/keycert2.pem \
/tmp/app/.cache/python-packages/future/backports/test/ssl_key.passwd.pem \
/tmp/app/.cache/python-packages/future/backports/test/ssl_key.pem \
/tmp/app/.cache/python-packages/tornado/test/test.key

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
