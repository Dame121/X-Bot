from flask import Flask, render_template, request, redirect, url_for
import os
import json
import random
import tweepy
from dotenv import load_dotenv
import schedule
import time
import threading

app = Flask(__name__)

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

# Function to compose a tweet
def compose_tweet(quote):
    return f'"{quote["text"]}" - {quote["author"]}'

# Background scheduler function
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

# Flask routes

@app.route('/')
def home():
    quotes = load_quotes()
    return render_template('index.html', quotes=quotes)

@app.route('/add', methods=['GET', 'POST'])
def add_quote():
    if request.method == 'POST':
        text = request.form['text']
        author = request.form['author']
        theme = request.form['theme']
        
        new_quote = {
            "text": text,
            "author": author,
            "theme": theme,
            "used": False
        }
        
        quotes = load_quotes()
        quotes.append(new_quote)
        save_quotes(quotes)
        
        return redirect(url_for('home'))
    
    return render_template('add_quote.html')

@app.route('/theme', methods=['POST'])
def select_theme():
    selected_theme = request.form['theme']
    quotes = load_quotes()
    quote = select_quote_by_theme(quotes, selected_theme)
    tweet = compose_tweet(quote)
    post_tweet(tweet)
    save_quotes(quotes)
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    # Start the background scheduler
    schedule_time = "19:02"
    schedule.every().day.at(schedule_time).do(job)
    
    # Run the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()
    
    # Start Flask app
    app.run(debug=True)
