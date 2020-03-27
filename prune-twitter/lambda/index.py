import boto3
import datetime
import json
import os
import tweepy

def handler(event, context):
    days_to_prune = int(os.environ["DAYS_TO_PRUNE"])

    assert days_to_prune != 0

    if days_to_prune >= 0:
        days_to_prune = days_to_prune * -1

    auth = tweepy.OAuthHandler(
            os.environ["CONSUMER_KEY"],
            os.environ["CONSUMER_SECRET"]
            )
            
    auth.set_access_token(
            os.environ["ACCESS_KEY"],
            os.environ["ACCESS_SECRET"]
            )
            
    api = tweepy.API(auth, wait_on_rate_limit=True)

    floor_date = datetime.datetime.now() + datetime.timedelta(days=days_to_prune)

    s3 = boto3.client('s3')

    print("Checking User Timeline")

    for status in tweepy.Cursor(api.user_timeline, tweet_mode='extended').items():
        if floor_date >= status.created_at:
            print(f"Status ID: {status.id} Created At: {status.created_at}")

            s3.put_object(
                Bucket=os.environ["BACKUP_BUCKET"],
                Key=f"tweets/{status.id_str}",
                Body=json.dumps(status._json)
            )

            print(f"api.destroy_status({status.id})")
            #api.destroy_status(status.id)

    print("Checking User Favorites")

    for status in tweepy.Cursor(api.favorites).items():
        if floor_date >= status.created_at:
            print(f"Status ID: {status.id} Created At: {status.created_at}")

            s3.put_object(
                Bucket=os.environ["BACKUP_BUCKET"],
                Key=f"favorites/{status.id_str}",
                Body=json.dumps(status._json)
            )
