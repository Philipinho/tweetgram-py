from database import DB
from instagram_basic_display import InstagramBasicDisplay


class InstagramTokenRefresh:

    def refresh_access_token(self):
        db = DB()
        ig = InstagramBasicDisplay.InstagramBasicDisplay(app_id="", app_secret="", redirect_url="")

        social_accounts = db.fetch_active_social_accounts()

        for account in social_accounts:
            refreshed_token = ig.refresh_token(token=account.insta_access_token)

            # update insta_user_id too by making a request to the "me" API endpoint
            db.update_insta_access_token(new_access_token=refreshed_token['access_token'],
                                         token_expires=refreshed_token['expires_in'], social_id=account.social_id)
