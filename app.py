import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
from gtts import gTTS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

# Set Streamlit page configuration
st.set_page_config(page_title="🔍 News Summarization and Text-to-Speech Application")

st.title("🔍 News Summarization and Text-to-Speech Application")
company = st.text_input("Enter Company Name:")

# News Fetching Function
def get_news(company_name):
    # Replace with actual news scraping logic or API call
    url = f'https://news.google.com/search?q={company_name}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('article', limit=10):  # Fetching 10 articles
        title = item.find('h3').get_text()
        summary = item.find('p').get_text() if item.find('p') else ''
        articles.append({'title': title, 'summary': summary})
    return articles

# Sentiment Analysis Function
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    if sentiment['compound'] >= 0.05:
        return "Positive"
    elif sentiment['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# TTS Function
def generate_tts(text, language='hi'):
    tts = gTTS(text=text, lang=language)
    tts.save("output.mp3")
    return "output.mp3"

# Streamlit App Logic
if st.button("Fetch News"):
    if company:
        with st.spinner("Fetching and analyzing news..."):
            try:
                # Get news articles for the company
                articles = get_news(company)
                
                if articles:
                    result = {"Company": company, "Articles": []}

                    # Analyze each article
                    for article in articles:
                        sentiment = analyze_sentiment(article['summary'])
                        result["Articles"].append({
                            "Title": article['title'],
                            "Summary": article['summary'],
                            "Sentiment": sentiment,
                            "Topics": ["Topic 1", "Topic 2"]  # You can add topic extraction logic here
                        })

                    # 🔥 Display the structured result in JSON format
                    st.subheader(f"📄 JSON Output for {result['Company']}")
                    formatted_json = json.dumps(result, indent=4, ensure_ascii=False)
                    st.code(formatted_json, language='json')

                    # Generate TTS for the summary
                    tts_file = generate_tts(f"Sentiment analysis complete for {company}.")
                    st.subheader("🔉 Hindi Audio Summary")
                    st.audio(tts_file)

                else:
                    st.warning("No news articles found.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please enter a company name.")
