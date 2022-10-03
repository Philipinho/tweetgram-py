from database import DB
from service.twitter_service import TwitterService
from instagram_basic_display import InstagramBasicDisplay


class InstagramService:

    def process_media(self):

        twitter = TwitterService()
        db = DB()
        ig = InstagramBasicDisplay.InstagramBasicDisplay(app_id="", app_secret="", redirect_url="")

        social_accounts = db.fetch_social_accounts()

        for account in social_accounts:
            ig.set_access_token(account.insta_access_token)

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
                "caption": "",
                "media_urls": [],
                "media_type": "",
                "insta_post_id": "",
                "insta_permalink": "",
                "timestamp": "",
                "username": "",
            }

            insta_media = ig.get_user_media(account.insta_user_id)

            for media in insta_media['data']:
                if 'caption' in media:
                    insta_media_info['caption'] = media['caption']

                insta_media_info['insta_post_id'] = media['id']
                insta_media_info['insta_permalink'] = media['permalink']
                insta_media_info['media_type'] = media['media_type']
                insta_media_info['sub_media_type'] = media['media_type']
                insta_media_info['timestamp'] = media['timestamp']
                insta_media_info['username'] = media['username']

                media_urls = []

                if media['id'] == account.insta_last_post_id:
                    print("end of discussion. No new post")
                    break

                # LocalDateTime currentTimestamp = LocalDateTime.parse(data.getTimestamp().split("\\+")[0]);
                # LocalDateTime previousTimestamp = LocalDateTime.parse(lastInstaTimestamp)
                # if (currentTimestamp.isBefore(previousTimestamp) | | currentTimestamp.isEqual(previousTimestamp)){
                # break; }

                if media['media_type'] == 'CAROUSEL_ALBUM':
                    child_media_types = []
                    for child_media in media['children']['data']:
                        child_media_types.append(str(child_media['media_type']).lower())

                    # You can not mix Twitter images with videos
                    # the below code will make the best decision

                    if 'video' in child_media_types:
                        # if videos and images, are present in the carousel album,
                        # if the video is the first media, upload the video alone
                        # if not, select the other images upto 4

                        if media['children']['data'][0]['media_type'] == 'VIDEO':
                            media_urls.append(media['children']['data'][0]['media_url'])
                            insta_media_info['sub_media_type'] = "CAROUSEL_ALBUM/VIDEO"
                        else:
                            for child_media in media['children']['data']:
                                if child_media['media_type'] == 'IMAGE':
                                    media_urls.append(child_media['media_url'])

                            insta_media_info['sub_media_type'] = "CAROUSEL_ALBUM/IMAGES"
                            media_urls = media_urls[0:4]  # fetch top 4 images
                    else:
                        # if no video in the carousel, upload first 4 images
                        # Upload top 4 images to Twitter
                        for child_media in media['children']['data']:
                            media_urls.append(child_media['media_url'])

                        insta_media_info['sub_media_type'] = "CAROUSEL_ALBUM/IMAGES"
                        media_urls = media_urls[0:4]
                        # get first four images inside the media_urls
                        # send to twitter

                else:
                    # if we land here, it means that it is a single media, video or image
                    media_urls.append(media['media_url'])

                insta_media_info['media_urls'] = media_urls

                twitter.send_tweet_with_media(social_account_info, insta_media_info)

                # send to twitter
                # at this point we are supposed to update the database after each send to Twitter
                # Fields to update: latest_insta_id and timestamp

        # next could be a try catch block to parse and handle errors

    def send_tweet_task(self, social_account: dict, media_info: dict):
        twitter = TwitterService()
        twitter.send_tweet_with_media(social_account, media_info)


#insta = InstagramService()
#insta.process_media()
