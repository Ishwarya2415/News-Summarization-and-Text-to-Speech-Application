import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from gtts import gTTS
from deep_translator import GoogleTranslator

nltk.download('stopwords')
import nltk
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
def scrape_news(company):
    search_url = f"https://www.bing.com/news/search?q={company}+news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('div', class_='news-card')
    news_list = []

    for article in articles[:10]:
        title_tag = article.find('a', {'class': 'title'})
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        summary_tag = article.find('div', class_='snippet')
        summary = summary_tag.text.strip() if summary_tag else "No Summary"
        sentiment = analyze_sentiment(summary)
        topics = extract_topics(summary)
        news_list.append({"Title": title, "Summary": summary, "Sentiment": sentiment, "Topics": topics})

    return news_list

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def extract_topics(text):
    words = text.lower().split()
    filtered = [w for w in words if w not in stopwords.words('english')]
    return list(set(filtered[:5]))

def generate_hindi_speech(text):
    try:
        hindi_text = GoogleTranslator(source='auto', target='hi').translate(text)
        tts = gTTS(text=hindi_text, lang='hi')
        path = "summary_audio.mp3"
        tts.save(path)
        return path
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def comparative_analysis(articles):
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    all_topics = []

    for article in articles:
        sentiment_counts[article["Sentiment"]] += 1
        all_topics.append(set(article["Topics"]))

    coverage_differences = []
    for i in range(len(articles) - 1):
        comparison = f"Article {i+1} discusses {articles[i]['Topics']}, while Article {i+2} focuses on {articles[i+1]['Topics']}."
        coverage_differences.append({
            "Comparison": comparison,
            "Impact": "Different perspectives highlight contrasting viewpoints on the company."
        })

    common_topics = set.intersection(*all_topics) if all_topics else set()
    unique_topics = [list(topics - common_topics) for topics in all_topics]

    return {
        "Sentiment Distribution": sentiment_counts,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": {
            "Common Topics": list(common_topics),
            "Unique Topics per Article": unique_topics
        }
    }
