import os
import re
import requests
import tweepy
import io

from database import DB
from dotenv import load_dotenv

load_dotenv()


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
        insta_post_id = media_info['insta_post_id']
        caption = media_info['caption']
        media_type = str(media_info['media_type']).lower()
        sub_media_type = str(media_info['sub_media_type']).lower()
        permalink = str(media_info['insta_permalink']).replace("www.instagram.com", "instagr.am")
        media_urls = media_info['media_urls']
        insta_username = media_info['username']
        insta_timestamp = media_info['timestamp']

        db = DB()

        if db.tweeted_before(insta_post_id):
            return

        tweepy_auth = tweepy.OAuth1UserHandler(
            "{}".format(os.environ['TWITTER_CONSUMER_KEY']), "{}".format(os.environ['TWITTER_CONSUMER_SECRET']),
            "{}".format(social_account['twitter_access_token']),
            "{}".format(social_account['twitter_access_token_secret']))

        twitter = tweepy.API(tweepy_auth)

        # print(twitter.verify_credentials)

        if auto_post == 1 or (auto_post == 0 and "#tweetgram" in caption):

            if auto_post == 0:
                caption = str(caption).replace("#tweetgram", '')

            promo_text = " via https://tweetgram.me"

            tweet_caption = ""

            if caption and len(caption) > 180:
                tweet_caption = caption[:180] + "..."
            elif caption and len(caption) < 180:
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

            # single video upload
            if media_type == "video" or sub_media_type == "carousel_album/video":
                uploaded_media = twitter.chunked_upload(file=self.get_media_stream(media_urls[0]), filename="video.mp4",
                                                        file_type="video/mp4")
                uploaded_ids.append(uploaded_media.media_id)
                # if media upload is successful add the media id to the tweet object status.setMediaIds(mediaIds);

            else:
                # for pictures
                # get array of pictures and loop through them
                # add the uploaded media ids to a new array list

                for image in media_urls:
                    uploaded_image = twitter.simple_upload(file=self.get_media_stream(image), filename="image.jpg")

                    if uploaded_image is not None:
                        uploaded_ids.append(uploaded_image.media_id)

            if uploaded_ids:
                tweet = twitter.update_status(status=tweet_caption, media_ids=uploaded_ids)

                db.save_posted_tweet(user_id=owner_id, social_id=social_id, media_type=media_type,
                                     sub_media_type=sub_media_type,
                                     twitter_user_id=tweet.user.id, twitter_username=tweet.user.screen_name,
                                     tweet_id=tweet.id_str,
                                     insta_user_id=insta_user_id, insta_username=insta_username,
                                     insta_post_id=insta_post_id, insta_post_url=permalink,
                                     insta_post_time=insta_timestamp, recorded_error="None")
                # at this point we are supposed to update the database after each send to Twitter
                # Fields to update: latest_insta_id and timestamp
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
