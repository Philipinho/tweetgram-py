import os

from celery.schedules import crontab
from flask import Flask
from dotenv import load_dotenv

from service.instagram_service import InstagramService

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration

from celery_init import make_celery

load_dotenv()

app = Flask(__name__)

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[FlaskIntegration(), CeleryIntegration()], traces_sample_rate=1.0
)

celery = make_celery(app)


@celery.on_after_configure.connect()
def setup_periodic_task(sender, **kwargs):
    #sender.add_periodic_task(10.0, beat.s("Jesus"), name="run every ten seconds")

    # run every 2 minutes
    sender.add_periodic_task(crontab(minute="*/1"), instagram_job.s(), name="Instagram Job")


@celery.task()
def instagram_job():
    ig = InstagramService()
    ig.process_media()


if __name__ == '__main__':
    from waitress import serve

    serve(app, host="0.0.0.0", port=int(os.environ['APP_PORT']))
