This system monitors tweets from trusted Twitter accounts in real time, detects when at least three accounts share the same news story, summarizes the aggregated tweets using LLaMA 3 via Ollama, and automatically tweets the concise breaking news alert.

## Features

- **Real-Time Twitter Monitoring:**  
  Streams tweets from a list of trusted accounts using the Twitter API.

- **Story Matching:**  
  Detects breaking news when three or more accounts mention the same story (by matching URLs found in tweets).

- **Content Summarization:**  
  Aggregates related tweets and uses the LLaMA 3 model (via Ollama) to generate a structured, concise summary.

- **Automatic Tweeting:**  
  Once a summary is generated, the system automatically tweets the breaking news alert using your configured Twitter account.

- **Logging:**  
  Logs activity and errors for monitoring and debugging purposes.

## Prerequisites

- **Python 3.7+**  
- **Twitter Developer Account:**  
  Obtain your API credentials (Bearer Token, Consumer Key/Secret, Access Token/Secret).

- **Ollama & LLaMA 3:**  
  - [Ollama](https://ollama.ai/) must be installed and configured.
  - Pull the LLaMA 3 model locally using:
    ```bash
    brew install ollama  # For macOS
    ollama pull llama3
    ```

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/lonestarcode/breaking-news.git
   cd breaking-news

	2.	Install Python Dependencies:

pip install tweepy python-dotenv requests beautifulsoup4


	3.	Configure Environment Variables:
Create a .env file in the root directory and add your Twitter API credentials:

TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret


	4.	(Optional) Configure Accounts and Keywords:
Edit the script to adjust the list of trusted accounts and keywords to monitor:

# List of trusted Twitter account IDs to monitor
accounts_to_monitor = ['user_id_1', 'user_id_2', 'user_id_3', 'user_id_4', 'user_id_5']

# Keywords that trigger news story detection
keywords = ["Breaking", "Breaking News"]



Running the Program

Simply run the script to start the stream and automatic tweeting:

python breaking_news_alert.py

The system will:
	1.	Start streaming tweets from the specified trusted accounts.
	2.	Monitor for tweets containing specified keywords.
	3.	Aggregate tweets referencing the same story (via URL detection).
	4.	Generate a concise summary using LLaMA 3 via Ollama when three or more unique accounts report the story.
	5.	Automatically tweet the summary using your Twitter API credentials.

How It Works
	1.	Tweet Collection:
The script streams tweets in real time using Tweepy. Tweets from trusted accounts are filtered based on keywords (e.g., “Breaking”, “Breaking News”).
	2.	Story Detection:
Each tweet is analyzed for a URL. Tweets sharing the same URL are grouped together. When three or more unique accounts mention the same URL, it is flagged as a breaking news event.
	3.	Summarization:
The collected tweets are combined into a single text block, which is sent to LLaMA 3 via Ollama with a prompt to generate a concise news summary.
	4.	Automatic Tweeting:
The generated summary is posted as a tweet using the configured Twitter API credentials. Logs are maintained for successful posts and any errors encountered.

Notes and Considerations
	•	Tweet Length:
Keep in mind Twitter’s 280-character limit per tweet. If summaries exceed this limit, you may need to implement logic for splitting the tweet into a thread or further summarizing the content.
	•	Rate Limits:
Be aware of Twitter API rate limits for both streaming and posting tweets. Implement error handling and retry logic if necessary.
	•	Error Logging:
The script logs key events and errors to help you troubleshoot issues during runtime.

Contributing

If you’d like to contribute or suggest improvements, feel free to open an issue or submit a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for details.

