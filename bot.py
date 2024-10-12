import tweepy
import os
import json
import random
from dotenv import load_dotenv
import schedule
import time

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

# Function to select a quote by theme
def select_quote_by_theme(quotes, selected_theme):
    themed_quotes = [q for q in quotes if q.get('theme') == selected_theme and not q.get('used', False)]
    
    if not themed_quotes:
        for q in quotes:
            if q.get('theme') == selected_theme:
                q['used'] = False
        themed_quotes = [q for q in quotes if q.get('theme') == selected_theme]
    
    selected = random.choice(themed_quotes)
    selected['used'] = True
    return selected

# Function to save quotes back to the JSON file
def save_quotes(quotes):
    with open('quotes.json', 'w') as file:
        json.dump({'quotes': quotes}, file, indent=4)

# Function to compose a tweet
def compose_tweet(quote):
    return f'"{quote["text"]}" - {quote["author"]}'

# Function to post a tweet using X API v2
def post_tweet(text):
    try:
        response = client.create_tweet(text=text)
        if response.data:
            print("Tweeted successfully!")
        else:
            print(f"Error posting tweet: {response.errors}")
    except tweepy.TweepyException as e:
        print(f"Error posting tweet: {e}")

# Function to execute the bot's routine with random theme selection
def job():
    quotes = load_quotes()
    themes = list(set(q['theme'] for q in quotes))
    selected_theme = random.choice(themes)
    print(f"Selected Theme: {selected_theme}")
    quote = select_quote_by_theme(quotes, selected_theme)
    tweet = compose_tweet(quote)
    post_tweet(tweet)
    save_quotes(quotes)

# Function to add a new quote from the CLI
def add_quote_from_cli():
    text = input("Enter the quote: ")
    author = input("Enter the author: ")
    theme = input("Enter the theme: ")
    
    new_quote = {
        "text": text,
        "author": author,
        "theme": theme,
        "used": False
    }
    
    quotes = load_quotes()
    quotes.append(new_quote)
    save_quotes(quotes)
    print("Quote added successfully!")

# Schedule the bot to run daily at a specific time
schedule_time = "19:00"
schedule.every().day.at(schedule_time).do(job)

if __name__ == "__main__":
    action = input("Type 'add' to add a new quote, or press Enter to run the bot: ").strip().lower()
    
    if action == 'add':
        add_quote_from_cli()
    else:
        print(f"Bot is scheduled to run daily at {schedule_time}")
        while True:
            schedule.run_pending()
            time.sleep(30)