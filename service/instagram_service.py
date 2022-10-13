import os

from database import DB
from service.twitter_service import TwitterService
from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay
from decrypter import decrypter

from datetime import datetime

from celery_init import make_celery

celery = make_celery()

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[CeleryIntegration()], traces_sample_rate=1.0
)


class InstagramService:

    def process_media(self):
        print("Running IG Service")
        #twitter = TwitterService()

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

            insta_media_info = {
                "username": "",
                "caption": "",
                "media_urls": [],
                "media_type": "",
                "insta_post_id": "",
                "insta_permalink": "",
                "insta_thumbnail_url": "",
                "timestamp": "",
            }

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
                insta_media_info['sub_media_type'] = str(media['media_type']).lower()
                insta_media_info['timestamp'] = media['timestamp']

                if str(media['media_type']).lower() == 'video':
                    insta_media_info['insta_thumbnail_url'] = media['thumbnail_url']
                else:
                    insta_media_info['insta_thumbnail_url'] = media['media_url']

                media_urls = []

                if str(media['media_type']).lower() == 'carousel_album':
                    child_media_types = []
                    for child_media in media['children']['data']:
                        child_media_types.append(str(child_media['media_type']).lower())

                    # You can not mix Twitter images with videos - Update: Twitter has changed this.
                    # the below code will make the best decision

                    if 'video' in child_media_types:
                        # if videos and images, are present in the carousel album,
                        # if the video is the first media, upload the video alone
                        # if not, select the other images upto 4

                        if str(media['children']['data'][0]['media_type']).lower() == 'video':
                            media_urls.append(media['children']['data'][0]['media_url'])
                            insta_media_info['sub_media_type'] = "carousel_album/video"
                        else:
                            for child_media in media['children']['data']:
                                if str(child_media['media_type']).lower() == 'image':
                                    media_urls.append(child_media['media_url'])

                            insta_media_info['sub_media_type'] = "carousel_album/images"
                            media_urls = media_urls[0:4]  # fetch top 4 images
                    else:
                        # if no video in the carousel, upload first 4 images
                        # Upload top 4 images to Twitter
                        for child_media in media['children']['data']:
                            media_urls.append(child_media['media_url'])

                        insta_media_info['sub_media_type'] = "carousel_album/images"
                        media_urls = media_urls[0:4]
                        # get first four images inside the media_urls
                        # send to twitter

                else:
                    # if we land here, it means that it is a single media, video or image
                    media_urls.append(media['media_url'])

                insta_media_info['media_urls'] = media_urls

                try:
                    send_tweet_task.delay(social_account_info, insta_media_info)
                except Exception as e:
                    # sentry_sdk.capture_exception(e)
                    print("send tweet task exception: " + str(e))


@celery.task()
def send_tweet_task(social_account: dict, media_info: dict):
    twitter = TwitterService()
    twitter.send_tweet_with_media(social_account, media_info)