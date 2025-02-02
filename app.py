import os
import logging
import re
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
# This client is used both for streaming and posting tweets.
client = tweepy.Client(
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
    consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
    consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)

# ----- CONFIGURATION -----
# List of trusted Twitter account IDs to monitor.
accounts_to_monitor = ['user_id_1', 'user_id_2', 'user_id_3', 'user_id_4', 'user_id_5']

# Keywords that trigger the breaking news detection.
keywords = ["Breaking", "Breaking News"]

# Data structure to track stories.
story_dict = {}


def extract_story_key_from_tweet(tweet_text):
    """
    Extracts the first URL from the tweet text to use as a unique key for the news story.
    """
    url_pattern = re.compile(r'(https?://\S+)')
    urls_in_tweet = url_pattern.findall(tweet_text)
    return urls_in_tweet[0].lower() if urls_in_tweet else None


def scrape_article_text(url):
    """
    Optionally scrapes the full text of an article from its URL.
    """
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
    """
    Uses the LLaMA 3 model via Ollama to generate a concise summary of the breaking news.
    """
    prompt = f"Summarize the following breaking news into a structured, concise report:\n\n{text}"
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']


def tweet_breaking_news(breaking_news_message):
    """
    Posts the generated breaking news summary as a tweet using the configured Twitter API credentials.
    """
    try:
        response = client.create_tweet(text=breaking_news_message)
        tweet_id = response.get('data', {}).get('id', 'N/A')
        logger.info("Tweet posted successfully. Tweet ID: %s", tweet_id)
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")


class MyStreamListener(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        # Skip retweets.
        if tweet.text.startswith("RT @"):
            return

        # Ensure the tweet contains at least one of the specified keywords.
        if not any(keyword.lower() in tweet.text.lower() for keyword in keywords):
            return

        author_id = tweet.author_id
        story_key = extract_story_key_from_tweet(tweet.text)
        if not story_key:
            return

        # Initialize the story entry if it doesn't already exist.
        if story_key not in story_dict:
            story_dict[story_key] = {'tweets': [], 'accounts': set()}

        story_entry = story_dict[story_key]
        # Only add tweets from unique accounts.
        if author_id not in story_entry['accounts']:
            story_entry['tweets'].append(tweet.text)
            story_entry['accounts'].add(author_id)

            # Once three or more unique accounts have tweeted about the same story, generate a summary.
            if len(story_entry['accounts']) >= 3:
                logger.info("3 or more accounts have tweeted about the same story. Generating breaking news summary...")
                combined_text = " ".join(story_entry['tweets'])
                summary = summarize_with_llama3(combined_text)
                breaking_news_message = f"🔴 BREAKING NEWS:\n{summary}"
                logger.info("Breaking News Summary:\n%s", breaking_news_message)

                # Automatically tweet the summarized breaking news.
                tweet_breaking_news(breaking_news_message)

    def on_error(self, status_code):
        logger.error(f"Stream encountered an error: {status_code}")
        # Disconnect the stream if rate limits are exceeded.
        if status_code in (420, 429):
            return False


def start_stream():
    """
    Initializes the Twitter stream listener, sets filtering rules, and begins streaming tweets.
    """
    stream_listener = MyStreamListener(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))

    # Remove any existing stream rules.
    existing_rules = stream_listener.get_rules().data
    if existing_rules is not None:
        rule_ids = [rule.id for rule in existing_rules]
        stream_listener.delete_rules(rule_ids)

    # Set new rules to monitor tweets from the specified trusted accounts.
    rules = [tweepy.StreamRule(f"from:{user_id}") for user_id in accounts_to_monitor]
    stream_listener.add_rules(rules)

    # Begin streaming tweets (running in a separate thread).
    stream_listener.filter(expansions='author_id', threaded=True)


if __name__ == "__main__":
    logger.info("Starting Twitter stream for Breaking News Alert System...")
    start_stream()