import streamlit as st
import requests
from transformers import pipeline

# --- CONFIG ---
st.set_page_config(page_title="🧠 Smart News Feed", layout="wide")
NEWS_API_KEY = "NEWS_APIKEY"

@st.cache_resource
def load_sentiment_model():
    return pipeline("sentiment-analysis")

sentiment_analyzer = load_sentiment_model()

@st.cache_data(ttl=300)
def fetch_news(country=None, keyword=None):
    base_url = "https://newsapi.org/v2/top-headlines" if not keyword else "https://newsapi.org/v2/everything"
    params = {
        "apiKey": NEWS_API_KEY,
        "country": country if not keyword else None,
        "q": keyword,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        st.error(f"API Error {response.status_code}: {response.json().get('message')}")
        return []

def analyze_sentiment(text):
    if not text:
        return "Neutral"
    result = sentiment_analyzer(text[:512])[0]
    label = result['label']
    score = round(result['score'] * 100, 2)
    return f"**Sentiment:** 🧠 {label} ({score}%)"

# --- UI ---
st.markdown("<h1 style='text-align: center;'>🧠 Real-Time News & Sentiment Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Powered by NewsAPI + HuggingFace</p>", unsafe_allow_html=True)

# --- Filter UI ---
col1, col2 = st.columns(2)
with col1:
    country = st.selectbox("🌍 Select Country", ["None", "us", "in", "gb", "au", "ca", "za"], index=1)
    country = None if country == "None" else country
with col2:
    keyword = st.text_input("🔍 Enter Keyword (e.g., AI, conflict, economy)")

articles = fetch_news(country, keyword)

# --- Style ---
st.markdown("""
<style>
.card {
    background-color: #181818;
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid #333;
    height: 100%;
}
.title {
    font-size: 1.1rem;
    font-weight: bold;
    color: #fff;
    margin-bottom: 0.5rem;
}
.desc {
    font-size: 0.9rem;
    color: #ccc;
    margin-bottom: 0.75rem;
}
.sentiment {
    color: #58a6ff;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# --- Display News in Two Columns Side by Side ---
for i in range(0, len(articles), 2):
    col_a, col_b = st.columns(2)
    for idx, col in enumerate([col_a, col_b]):
        if i + idx < len(articles):
            article = articles[i + idx]
            with col:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<div class="title">{article.get("title", "No Title")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="desc">{article.get("description", "No Description")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="sentiment">{analyze_sentiment(article.get("description", ""))}</div>', unsafe_allow_html=True)
                st.markdown(f'<a href="{article.get("url", "#")}" target="_blank">🔗 Read More</a>', unsafe_allow_html=True)
                if article.get("urlToImage"):
                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <img src="{article['urlToImage']}" style="width:70%; border-radius: 8px; margin-top: 0.75rem;" />
                        </div>
                        """,
                        unsafe_allow_html=True    
                    )
                st.markdown('</div>', unsafe_allow_html=True)

if not articles:
    st.info("No articles found. Try a different keyword or region.")
