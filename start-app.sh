#!/usr/bin/env bash
# start-server.sh

cd /tmp/app/openlxp-xia-coursera/
sed -i 's/hashlib.md5()/hashlib.md5(usedforsecurity=False)/g' /tmp/app/.cache/python-packages/django/db/backends/utils.py
python manage.py waitdb 
python manage.py migrate --skip-checks
python manage.py createcachetable 
python manage.py loaddata admin_theme_data.json 
python manage.py loaddata openlxp_email.json 
python manage.py loaddata openlxp_notification_template.json 
python manage.py loaddata openlxp_notification_subject.json 
python manage.py loaddata openlxp_notification_email.json 
python manage.py collectstatic --no-input
cp -ur ./static/ /tmp/shared/
cp -ur ./media/ /tmp/shared/
cd /tmp/app/ 
if [ -n "$TMP_SOURCE_DIR" ] ; then 
    (cd openlxp-xia-coursera; install -d -o python -p $TMP_SOURCE_DIR) 
else 
    (cd openlxp-xia-coursera; install -d -o python -p tmp/source) 
fi 
pwd 
service clamav-daemon restart 
./start-server.sh 
