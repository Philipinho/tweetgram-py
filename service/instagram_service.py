import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

from database import DB
from logs.twitter_service1 import TwitterService
from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay
from decrypter import decrypter

from datetime import datetime

from celery_init import make_celery

celery = make_celery()

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[CeleryIntegration()], traces_sample_rate=1.0
)


class InstagramService:

    def process_media(self):
        print("Running IG Service")
        # twitter = TwitterService()

        db = DB()

        ig = InstagramBasicDisplay(app_id="", app_secret="", redirect_url="")

        social_accounts = db.fetch_active_social_accounts()

        for account in social_accounts:
            insta_media = None
            try:
                ig.set_access_token(decrypter.decrypt(account.insta_access_token))
            except Exception as e:
                print(e)
                continue

            try:
                insta_media = ig.get_user_media(account.insta_user_id)
            except Exception as e:
                error_message = str(e) + " - timestamp: " + str(datetime.utcnow())
                if 'error validating access token' in str(e).lower():
                    db.update_social_account_status(status=0, social_id=account.social_id)
                    db.update_last_insta_error(error_msg=error_message, social_id=account.social_id)
                else:
                    print(error_message)
                    continue

            if db.is_premium(account.owner_id):
                user_plan = "premium"
            else:
                user_plan = "free"

            social_account_info = {
                "owner_id": account.owner_id,
                "social_id": account.social_id,
                "insta_user_id": account.insta_user_id,
                "auto_post": account.auto_post,
                "remove_caption": account.remove_caption,
                "remove_hashtags": account.remove_hashtags,
                "enable_photo": account.enable_photo,
                "enable_video": account.enable_video,
                "user_plan": user_plan,
                "twitter_access_token": account.tw_access_token,
                "twitter_access_token_secret": account.tw_access_token_secret,
            }

            insta_media_info = {}

            instagram_media_list = []

            for media in insta_media['data']:
                if media['id'] == account.insta_last_post_id:
                    print("end of discussion. No new post")
                    break

                previous_time = datetime.strptime(str(account.insta_last_timestamp), "%Y-%m-%d %H:%M:%S")
                current_time = datetime.strptime(str(media['timestamp']), "%Y-%m-%dT%H:%M:%S+%f")

                if previous_time > current_time or current_time == previous_time:
                    print("break, time difference.")
                    break

                instagram_media_list.append(media)

            instagram_media_list.reverse()  # get the media in a descending order

            for media in instagram_media_list:
                if 'caption' in media:
                    insta_media_info['caption'] = media['caption']

                insta_media_info['username'] = media['username']
                insta_media_info['insta_post_id'] = media['id']
                insta_media_info['insta_thumbnail_url'] = media['permalink']
                insta_media_info['insta_permalink'] = media['permalink']
                insta_media_info['media_type'] = str(media['media_type']).lower()
                insta_media_info['timestamp'] = media['timestamp']

                if str(media['media_type']).lower() == 'video':
                    insta_media_info['insta_thumbnail_url'] = media['thumbnail_url']
                else:
                    insta_media_info['insta_thumbnail_url'] = media['media_url']

                media_list = []

                if str(media['media_type']).lower() == 'image' or str(media['media_type']).lower() == 'video':
                    media_dict = {"media_id": media['id'], "media_url": media['media_url'],
                                  "media_type": str(media['media_type']).lower()}
                    media_list.append(media_dict)

                elif str(media['media_type']).lower() == 'carousel_album':

                    for child_media in media['children']['data']:
                        child_media_info = {"media_id": child_media['id'], "media_url": child_media['media_url'],
                                            "media_type": str(child_media['media_type']).lower()}
                        media_list.append(child_media_info)

                    media_list = media_list[0:4]  # fetch top 4 media files

                insta_media_info['media_list'] = media_list

                try:
                    # twitter.send_tweet_with_media(social_account_info, insta_media_info)
                    send_tweet_task.delay(social_account_info, insta_media_info)
                except Exception as e:
                    db.update_insta_last_id_and_time(post_id=media['id'], timestamp=media['timestamp'],
                                                     social_id=account.social_id)
                    sentry_sdk.capture_exception(e)
                    print("send tweet task exception: " + str(e))


@celery.task()
def send_tweet_task(social_account: dict, media_info: dict):
    twitter = TwitterService()
    twitter.send_tweet_with_media(social_account, media_info)
