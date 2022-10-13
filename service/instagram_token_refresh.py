import os

from instagram_basic_display import InstagramBasicDisplayException

from database import DB
from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay

from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

load_dotenv()

sentry_sdk.init(
    dsn=os.environ['SENTRY_URL'],
    integrations=[FlaskIntegration(), ], traces_sample_rate=1.0
)


class InstagramTokenRefresh:

    def refresh_access_token(self):

        db = DB()
        ig = InstagramBasicDisplay(app_id="", app_secret="", redirect_url="")

        social_accounts = db.fetch_active_social_accounts()

        for account in social_accounts:
            try:
                refreshed_token = ig.refresh_token(token=account.insta_access_token)
                db.update_insta_access_token(new_access_token=refreshed_token['access_token'],
                                             token_expires=refreshed_token['expires_in'], social_id=account.social_id)

            except InstagramBasicDisplayException as e:
                user_details = account.insta_username + ":" + account.insta_user_id
                sentry_sdk.capture_message(user_details)
                sentry_sdk.capture_exception(e)
                print(user_details + " - " + str(e))
