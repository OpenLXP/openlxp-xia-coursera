#!/usr/bin/env bash
# start-server.sh

python manage.py waitdb 
python manage.py migrate 
python manage.py createcachetable 
python manage.py loaddata admin_theme_data.json 
python manage.py loaddata openlxp_email.json 
python manage.py loaddata openlxp_notification_template.json 
python manage.py loaddata openlxp_notification_subject.json 
python manage.py loaddata openlxp_notification_email.json 
cd /tmp/app/ 
if [ -n "$TMP_SOURCE_DIR" ] ; then 
    (cd openlxp-xia-coursera; install -d -o www-data -p $TMP_SOURCE_DIR) 
else 
    (cd openlxp-xia-coursera; install -d -o www-data -p tmp/source) 
fi 
pwd 
service clamav-daemon restart 
./start-server.sh 
