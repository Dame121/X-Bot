import tweepy
import os
import json
import random
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# Load environment variables
load_dotenv()

# Get API keys and tokens from environment variables
consumer_key = os.getenv("API_KEY")
consumer_secret = os.getenv("API_SECRET_KEY")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Create a Tweepy client using OAuth 2.0 Bearer Token and OAuth 1.0a credentials
client = tweepy.Client(bearer_token=bearer_token,
                       consumer_key=consumer_key,
                       consumer_secret=consumer_secret,
                       access_token=access_token,
                       access_token_secret=access_token_secret)

# Function to load quotes from a JSON file
def load_quotes():
    with open('quotes.json', 'r') as file:
        data = json.load(file)
    return data['quotes']

# Function to select a random unused quote
def select_quote(quotes):
    unused_quotes = [q for q in quotes if not q.get('used', False)]
    if not unused_quotes:
        # Reset all quotes to unused if all have been used
        for q in quotes:
            q['used'] = False
        unused_quotes = quotes
        
    selected = random.choice(unused_quotes)
    selected['used'] = True
    return selected

# Function to save the updated quotes back to the JSON file
def save_quotes(quotes):
    with open('quotes.json', 'w') as file:
        json.dump({'quotes': quotes}, file, indent=4)

# Function to compose a tweet from a quote
def compose_tweet(quote):
    return f'"{quote["text"]}" - {quote["author"]}'

# Function to post a tweet using the v2 API
def post_tweet(text):
    try:
        # Use client.create_tweet() for Twitter API v2 to post the tweet
        response = client.create_tweet(text=text)
        if response.data:
            print(f"Tweeted successfully at {datetime.now()}!")
        else:
            print(f"Error posting tweet: {response.errors}")
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")

# Function to execute the bot's routine
def run_bot():
    print(f"Running bot at {datetime.now()}")
    # Load quotes from the JSON file
    quotes = load_quotes()

    # Select a random quote
    quote = select_quote(quotes)

    # Compose the tweet text
    tweet = compose_tweet(quote)

    # Post the tweet
    post_tweet(tweet)

    # Save the updated quotes back to the file
    save_quotes(quotes)

# Initialize APScheduler
scheduler = BlockingScheduler()

# Schedule the job every day at 9:00 AM
scheduler.add_job(run_bot, 'cron', hour=9, minute=0, id='daily_tweet')

# For testing purposes: Schedule the job to run every minute
# Uncomment the following line to test
# scheduler.add_job(run_bot, 'interval', minutes=1, id='test_tweet')

if __name__ == "__main__":
    print(f"Bot started at {datetime.now()}. Waiting to post daily quotes.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
