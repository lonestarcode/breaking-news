# Breaking News Alert System

## Overview
This project tracks tweets from trusted accounts and detects when at least three accounts share the same news story. It then uses **LLaMA 3 via Ollama** to summarize the updates into a concise breaking news alert.

## Features
- **Monitors Twitter in real-time** for breaking news updates.
- **Tracks tweets from trusted accounts** and detects when they reference the same news story.
- **Extracts story context** using links or textual similarity.
- **Summarizes breaking news** using **LLaMA 3 via Ollama** for structured, concise reports.
- **Logs breaking news summaries** for further use.

## Installation
### 1. Install Required Dependencies
Ensure you have Python and install the necessary packages:
```bash
pip install tweepy python-dotenv requests beautifulsoup4
```

### 2. Install Ollama & LLaMA 3
To run **LLaMA 3 locally**, install Ollama:
```bash
brew install ollama  # For macOS
```
Then, pull the LLaMA 3 model:
```bash
ollama pull llama3
```

### 3. Set Up Environment Variables
Create a `.env` file and add the following credentials:
```
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

## Running the Program
Run the script to start monitoring Twitter for breaking news:
```bash
python breaking_news_alert.py
```

## How It Works
1. **Real-Time Tweet Collection**
   - The program streams tweets from trusted accounts.
   - Detects when three or more accounts mention the same news story.

2. **Story Matching**
   - Extracts URLs from tweets.
   - Groups tweets discussing the same article or event.

3. **Summarization with LLaMA 3**
   - Combines relevant tweets into a single document.
   - Uses **LLaMA 3 via Ollama** to generate a concise news summary.

4. **Breaking News Alert Logging**
   - Summarized news is logged for review and further use.

## Example Output
```
🔴 BREAKING NEWS:
A 7.8 magnitude earthquake has struck California. The governor has declared a state of emergency, and emergency response teams are en route. USGS warns of aftershocks within the next 24 hours.
```

## Performance Optimization
For better speed and efficiency on **Apple Silicon (M1/M2/M3)**:
```bash
OLLAMA_ACCELERATE=1 ollama run llama3
```
If memory usage is high, enable **half-precision mode**:
```bash
OLLAMA_PRECISION=fp16 ollama run llama3
```

## Future Enhancements
- Improve **story matching** using **text embeddings**.
- Implement **database storage** for historical tracking.
- Integrate **automated notifications** (Slack, Email, etc.).

## License
MIT License


