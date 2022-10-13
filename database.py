import datetime
import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime, text, TIMESTAMP, exc, Text

from sqlalchemy.dialects.mysql import INTEGER, BIGINT, TINYINT, LONGTEXT
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = "mysql://{username}:{password}@{hostname}/{databasename}" \
    .format(username=os.environ['MYSQL_USERNAME'],
            password=os.environ['MYSQL_PASSWORD'],
            hostname=os.environ['MYSQL_HOST'],
            databasename=os.environ['MYSQL_DATABASE']
            )

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=True, autocommit=True)

Session.configure(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT(20), primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    email = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False, unique=True)


class SocialAccount(Base):
    __tablename__ = 'social_accounts'

    id = Column(BIGINT(20), primary_key=True)
    social_id = Column(String(255, 'utf8mb4_unicode_ci'))
    owner_id = Column(BIGINT(20))
    insta_user_id = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_username = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_followers = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_access_token = Column(LONGTEXT)
    insta_last_post_id = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_last_timestamp = Column(DateTime)
    insta_access_token_expires = Column(String(100, 'utf8mb4_unicode_ci'))
    insta_last_error = Column(Text(collation='utf8mb4_unicode_ci'))
    tw_user_id = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_username = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_name = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_email = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_access_token = Column(LONGTEXT)
    tw_access_token_secret = Column(LONGTEXT)
    tw_refresh_token = Column(LONGTEXT)
    tw_token_scope = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_access_token_expires = Column(DateTime)
    tw_photo_url = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_location = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_followers = Column(INTEGER(11))
    tw_verified = Column(String(255, 'utf8mb4_unicode_ci'))
    tw_api_version = Column(String(30, 'utf8mb4_unicode_ci'))
    custom_hashtags = Column(String(255, 'utf8mb4_unicode_ci'))
    auto_post = Column(TINYINT(4), nullable=False, server_default=text("1"))
    remove_mentions = Column(TINYINT(4), server_default=text("0"))
    remove_caption = Column(TINYINT(4), server_default=text("0"))
    remove_hashtags = Column(TINYINT(4), server_default=text("0"))
    enable_video = Column(TINYINT(4), server_default=text("1"))
    enable_photo = Column(TINYINT(4), server_default=text("1"))
    status = Column(TINYINT(4), server_default=text("0"))
    created_at = Column(DateTime, server_default=text("current_timestamp()"))
    updated_at = Column(DateTime)


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(BIGINT(20), primary_key=True)
    plan_id = Column(String(255, 'utf8mb4_unicode_ci'))
    amount = Column(String(10, 'utf8mb4_unicode_ci'))
    paddle_checkout_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_subscription_plan_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_subscription_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_update_url = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_cancel_url = Column(String(255, 'utf8mb4_unicode_ci'))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    next_payment_date = Column(DateTime)
    interval = Column(String(255, 'utf8mb4_unicode_ci'))
    status = Column(TINYINT(1), server_default=text("0"))
    owner_id = Column(BIGINT(20))
    created_at = Column(DateTime, server_default=text("current_timestamp()"))
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(BIGINT(20), primary_key=True)
    owner_id = Column(BIGINT(20))
    invoice_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_order_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_subscription_payment_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_checkout_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_receipt_url = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_subscription_plan_id = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_subscription_id = Column(String(255, 'utf8mb4_unicode_ci'))
    amount = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_payment_method = Column(String(255, 'utf8mb4_unicode_ci'))
    card_brand = Column(String(255, 'utf8mb4_unicode_ci'))
    card_last_four = Column(String(255, 'utf8mb4_unicode_ci'))
    card_expiration_date = Column(String(255, 'utf8mb4_unicode_ci'))
    paddle_event_time = Column(DateTime)
    payment_provider = Column(String(255, 'utf8mb4_unicode_ci'))
    status = Column(TINYINT(4), server_default=text("0"))
    created_at = Column(DateTime, server_default=text("current_timestamp()"))
    updated_at = Column(DateTime)


class TweetPosted(Base):
    __tablename__ = 'tweets_posted'

    id = Column(BIGINT(20), primary_key=True)
    owner_id = Column(BIGINT(20))
    social_id = Column(String(255, 'utf8mb4_unicode_ci'))
    media_type = Column(String(255, 'utf8mb4_unicode_ci'))
    sub_media_type = Column(String(255, 'utf8mb4_unicode_ci'))
    twitter_user_id = Column(String(255, 'utf8mb4_unicode_ci'))
    twitter_username = Column(String(255, 'utf8mb4_unicode_ci'))
    tweet_id = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_user_id = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_username = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_post_id = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_post_url = Column(String(255, 'utf8mb4_unicode_ci'))
    insta_thumbnail_url = Column(Text)
    insta_post_time = Column(DateTime)
    recorded_error = Column(String(255, 'utf8mb4_unicode_ci'))
    status = Column(TINYINT(4), server_default=text("1"))
    created_at = Column(DateTime, server_default=text("current_timestamp()"))
    updated_at = Column(DateTime)


class DB:

    @staticmethod
    def is_premium(user_id):
        return session.query(Subscription).filter_by(owner_id=user_id) \
                   .filter_by(status=1).first() is not None

    @staticmethod
    def tweeted_before(insta_post_id):
        return session.query(TweetPosted).filter_by(insta_post_id=insta_post_id) \
                   .first() is not None

    @staticmethod
    def save_posted_tweet(user_id, social_id, media_type, sub_media_type, twitter_user_id, twitter_username,
                          tweet_id, insta_user_id, insta_username, insta_post_id,
                          insta_post_url, insta_thumbnail_url, insta_post_time, recorded_error):
        session.begin()
        tweet_record = TweetPosted(owner_id=user_id, social_id=social_id, media_type=media_type,
                                   sub_media_type=sub_media_type, twitter_user_id=twitter_user_id,
                                   twitter_username=twitter_username, tweet_id=tweet_id, insta_user_id=insta_user_id,
                                   insta_username=insta_username, insta_post_id=insta_post_id,
                                   insta_post_url=insta_post_url, insta_thumbnail_url=insta_thumbnail_url,
                                   insta_post_time=insta_post_time, recorded_error=recorded_error)
        session.add(tweet_record)
        session.commit()

    @staticmethod
    def update_last_insta_post_id(post_id, social_id):
        session.query(SocialAccount).filter_by(social_id=social_id) \
            .update({SocialAccount.insta_last_post_id: post_id})

    @staticmethod
    def update_insta_last_id_and_time(post_id, timestamp, social_id):
        session.query(SocialAccount) \
            .filter_by(social_id=social_id) \
            .update({SocialAccount.insta_last_post_id: post_id, SocialAccount.insta_last_timestamp: timestamp})

    @staticmethod
    def update_social_account_status(status, social_id):
        session.query(SocialAccount).filter_by(social_id=social_id) \
            .update({SocialAccount.status: status})

    @staticmethod
    def update_insta_access_token(new_access_token, token_expires, social_id):
        current_time = datetime.datetime.utcnow()
        current_time.strftime('%Y-%m-%d %H:%M:%S')

        session.query(SocialAccount).filter_by(social_id=social_id) \
            .update({SocialAccount.insta_access_token: new_access_token,
                     SocialAccount.insta_access_token_expires: token_expires,
                     SocialAccount.updated_at: current_time})

    @staticmethod
    def update_last_insta_error(error_msg, social_id):
        session.query(SocialAccount).filter_by(social_id=social_id) \
            .update({SocialAccount.insta_last_error: error_msg})

    @staticmethod
    def fetch_social_accounts():
        return session.query(SocialAccount).all()

    @staticmethod
    def fetch_active_social_accounts():
        return session.query(SocialAccount).filter_by(status=1).all()

    @staticmethod
    def save_failed_refresh(user_id, insta_user_id, message, refresh_date):
        return 0

    @staticmethod
    def fetch_users():
        return session.query(User).all()

    @staticmethod
    def fetch_last_insta_post_id(user_id):
        return session.query(SocialAccount).filter_by(owner_id=user_id).first().insta_last_post_id
