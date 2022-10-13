import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

CELERYBEAT_SCHEDULE = {
    'instagram-job': {
        'task': 'instagram.process_media',
        # Run every 2 minutes
        'schedule': crontab(minute='*/2'),
    },
    'refresh-task': {
        'task': 'instagram.refresh_token',
        # At 16h UTC everyday
        'schedule': crontab(minute=0, hour=16),
    }
}
CELERY_TIMEZONE = 'UTC'


def make_celery(app=None):
    if not app:
        name = app
    else:
        name = app.import_name

    celery = Celery(name, broker=os.environ['CELERY_BROKER_URL'],
                    backend=os.environ['CELERY_BROKER_URL'])

    celery.conf.update(timezone='Africa/Lagos')

    #celery.conf.update(beat_schedule=CELERYBEAT_SCHEDULE)

    # celery.conf.update()
    # celery.config_from_object()

    # celery.conf.update(CELERYBEAT_SCHEDULE)
    # celery.conf.update(CELERY_TIMEZONE)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
