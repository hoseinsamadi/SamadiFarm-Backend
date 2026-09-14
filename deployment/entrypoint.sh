#!/bin/sh
set -eu

cd /app/backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec supervisord -n -c /etc/supervisor/conf.d/samadi-farm.conf
