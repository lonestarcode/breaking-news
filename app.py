import os
import logging
from dotenv import load_dotenv
import tweepy
import ollama
import requests
from bs4 import BeautifulSoup

# ----- LOAD ENVIRONMENT VARIABLES -----
load_dotenv()

# ----- SET UP LOGGING -----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ----- INIT TWITTER CLIENT -----
client = tweepy.Client(
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
    consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
    consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)

# ----- ACCOUNTS TO MONITOR -----
accounts_to_monitor = ['user_id_1', 'user_id_2', 'user_id_3', 'user_id_4', 'user_id_5']

# ----- KEYWORDS TO MONITOR (OPTIONAL) -----
keywords = ["Breaking", "Breaking News"]

# ----- DATA STRUCTURE TO TRACK STORIES -----
story_dict = {}

def extract_story_key_from_tweet(tweet_text):
    import re
    url_pattern = re.compile(r'(https?://\S+)')
    urls_in_tweet = url_pattern.findall(tweet_text)
    return urls_in_tweet[0].lower() if urls_in_tweet else None

def scrape_article_text(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            return " ".join([p.get_text() for p in paragraphs])
    except Exception as e:
        logger.error(f"Error scraping article text from {url}: {e}")
    return ""

def summarize_with_llama3(text):
    prompt = f"Summarize the following breaking news into a structured, concise report:\n\n{text}"
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

class MyStreamListener(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        if tweet.text.startswith("RT @"):
            return
        if not any(keyword.lower() in tweet.text.lower() for keyword in keywords):
            return
        author_id = tweet.author_id
        story_key = extract_story_key_from_tweet(tweet.text)
        if not story_key:
            return
        if story_key not in story_dict:
            story_dict[story_key] = {'tweets': [], 'accounts': set()}
        story_entry = story_dict[story_key]
        if author_id not in story_entry['accounts']:
            story_entry['tweets'].append(tweet.text)
            story_entry['accounts'].add(author_id)
            if len(story_entry['accounts']) >= 3:
                logger.info("3 or more accounts have tweeted about the same story. Generating Breaking News summary...")
                combined_text = " ".join(story_entry['tweets'])
                summary = summarize_with_llama3(combined_text)
                breaking_news_message = f"BREAKING NEWS:\n{summary}"
                logger.info(f"Breaking News Summary:\n{breaking_news_message}")

    def on_error(self, status_code):
        logger.error(f"Stream encountered an error: {status_code}")
        if status_code == 420 or status_code == 429:
            return False

def start_stream():
    stream_listener = MyStreamListener(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))
    existing_rules = stream_listener.get_rules().data
    if existing_rules is not None:
        rule_ids = [rule.id for rule in existing_rules]
        stream_listener.delete_rules(rule_ids)
    rules = [tweepy.StreamRule(f"from:{user_id}") for user_id in accounts_to_monitor]
    stream_listener.add_rules(rules)
    stream_listener.filter(expansions='author_id', threaded=True)

if __name__ == "__main__":
    logger.info("Starting Twitter stream...")
    start_stream()
