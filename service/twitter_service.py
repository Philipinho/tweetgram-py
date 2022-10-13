import os
import re

import requests
import tweepy
import io

from decrypter import decrypter

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

from database import DB
from dotenv import load_dotenv

load_dotenv()

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[CeleryIntegration()], traces_sample_rate=1.0
)


class TwitterService:

    def send_tweet_with_media(self, social_account: dict, media_info: dict):
        # social account info
        owner_id = social_account['owner_id']
        social_id = social_account['social_id']
        insta_user_id = social_account['insta_user_id']
        enable_video = social_account['enable_video']
        enable_photo = social_account['enable_photo']
        remove_caption = social_account['remove_caption']
        remove_hashtags = social_account['remove_hashtags']
        auto_post = social_account['auto_post']
        user_plan = social_account['user_plan']

        # media info
        insta_username = media_info['username']
        insta_post_id = media_info['insta_post_id']
        caption = media_info['caption']
        media_type = media_info['media_type']
        permalink = str(media_info['insta_permalink']).replace("www.instagram.com", "instagr.am")
        media_list = media_info['media_list']
        thumbnail_url = media_info['insta_thumbnail_url']
        insta_timestamp = media_info['timestamp']

        db = DB()

        if db.tweeted_before(insta_post_id):
            print("returned here.")
            return

        tweepy_auth = tweepy.OAuth1UserHandler(
            "{}".format(os.environ['TWITTER_CONSUMER_KEY']), "{}".format(os.environ['TWITTER_CONSUMER_SECRET']),
            "{}".format(decrypter.decrypt(social_account['twitter_access_token'])),
            "{}".format(decrypter.decrypt(social_account['twitter_access_token_secret'])))

        twitter = tweepy.API(tweepy_auth)

        if auto_post == 1 or (auto_post == 0 and "#tweetgram".lower() in str(caption).lower()):

            if auto_post == 0:
                caption = str(caption).replace("#tweetgram", '')

            promo_text = " via https://tweetgram.me"

            tweet_caption = ""

            if caption and len(caption) > 210:
                tweet_caption = caption[:210] + "..."
            elif caption and len(caption) < 210:
                tweet_caption = caption
            else:
                tweet_caption = ""

            if str(user_plan).lower() == "free":
                if not caption:
                    tweet_caption = permalink + promo_text
                else:
                    tweet_caption += "\n\n" + permalink + promo_text

            else:
                if remove_caption == 1:
                    tweet_caption = ""

                if remove_hashtags == 1:
                    hashtag_regex = r"#([_a-zA-Z]|[0-9])+"
                    tweet_caption = re.sub(hashtag_regex, "", tweet_caption)

                if not caption:
                    tweet_caption = tweet_caption + permalink
                else:
                    tweet_caption = tweet_caption + "\n\n" + permalink

            # next upload media to twitter and save
            uploaded_ids = []

            if media_type == "video":
                uploaded_media_id = self.upload_twitter_video(twitter_api=twitter, media_id=media_list[0]['media_id'],
                                                              media_url=media_list[0]['media_url'])
                uploaded_ids.append(uploaded_media_id)

            elif media_type == "image":
                uploaded_image = twitter.simple_upload(file=self.get_media_stream(media_list[0]['media_url']),
                                                       filename="image.jpg")
                uploaded_ids.append(uploaded_image.media_id)

            elif media_type == 'carousel_album':
                for child_media in media_list:

                    if child_media['media_type'] == 'image':
                        uploaded_media = twitter.simple_upload(file=self.get_media_stream(child_media['media_url']),
                                                               filename="image.jpg")
                        uploaded_ids.append(uploaded_media.media_id)

                    if child_media['media_type'] == 'video':
                        # send media id and url to ffmpeg api, re-encode and then get and stream new link
                        uploaded_media_id = self.upload_twitter_video(twitter_api=twitter,
                                                                      media_id=child_media['media_id'],
                                                                      media_url=child_media['media_url'])
                        uploaded_ids.append(uploaded_media_id)

            if uploaded_ids:
                tweet = twitter.update_status(status=tweet_caption, media_ids=uploaded_ids)

                db.save_posted_tweet(user_id=owner_id, social_id=social_id, media_type=media_type,
                                     twitter_user_id=tweet.user.id, twitter_username=tweet.user.screen_name,
                                     tweet_id=tweet.id_str,
                                     insta_user_id=insta_user_id, insta_username=insta_username,
                                     insta_post_id=insta_post_id, insta_post_url=permalink,
                                     insta_thumbnail_url=thumbnail_url, insta_post_time=insta_timestamp,
                                     recorded_error="")

                # at this point we are supposed to update the database after each send to Twitter
                # Fields to update: latest_insta_id and timestamp
                db.update_insta_last_id_and_time(post_id=insta_post_id, timestamp=insta_timestamp, social_id=social_id)
            else:
                db.update_insta_last_id_and_time(post_id=insta_post_id, timestamp=insta_timestamp, social_id=social_id)

    def get_media_stream(self, media_url: str):

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/65.0.3325.181 Safari/537.36"

        headers = {'User-Agent': user_agent}
        buffered_stream = io.BytesIO()
        try:
            media_data = requests.get(url=media_url, headers=headers).content
            buffered_stream.write(media_data)
            buffered_stream.seek(0)
        except Exception as e:
            print(str(e))

        return buffered_stream

    def get_fallback_video_url(self, media_id, media_url):
        api_url = "https://video.tweetgram.me/api.php"

        data = {'media_id': media_id, 'media_url': media_url}
        response = requests.get(url=api_url, params=data)
        json = response.json()["video_url"]
        return json

    def upload_twitter_video(self, twitter_api, media_id, media_url):
        uploaded_media_id = 0

        uploaded_media = twitter_api.chunked_upload(file=self.get_media_stream(media_url),
                                                    filename="video.mp4", file_type="video/mp4",
                                                    media_category="tweet_video")

        if uploaded_media.processing_info['state'] != 'failed':
            uploaded_media_id = uploaded_media.media_id
        else:
            uploaded_media = twitter_api.chunked_upload(file=self.get_media_stream(
                self.get_fallback_video_url(media_id=media_id, media_url=media_url)),
                filename="video.mp4", file_type="video/mp4",
                media_category="tweet_video")
            uploaded_media_id = uploaded_media.media_id

        return uploaded_media_id
