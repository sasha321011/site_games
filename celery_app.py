#celery -A .celery_app worker --loglevel=info -P gevent
#celery -A celery_app beat --loglevel=info
#celery -A .celery_app flower
#http://127.0.0.1:5555/

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitegames.settings')

app = Celery('sitegames')
app.conf.broker_connection_retry_on_startup = True
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL


app.conf.beat_schedule_filename = os.path.join(settings.BASE_DIR, 'tmp', 'celerybeat-schedule')


app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

