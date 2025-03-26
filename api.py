

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from utils import scrape_news, comparative_analysis, generate_hindi_speech
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanyRequest(BaseModel):
    company: str

@app.post("/get-news")
def get_news(data: CompanyRequest):
    company = data.company
    articles = scrape_news(company)

    if not articles:
        return {"error": "No articles found."}

    comparison = comparative_analysis(articles)

    combined_summary = " ".join([article["Summary"] for article in articles if article["Summary"] != "No Summary"])
    audio_path = generate_hindi_speech(combined_summary)

    final_sentiment = (
        "Tesla’s latest news coverage is mostly positive. Potential stock growth expected."
        if comparison["Sentiment Distribution"]["Positive"] >= max(comparison["Sentiment Distribution"].values())
        else "Overall sentiment is mostly neutral or mixed."
    )

    return {
        "Company": company,
        "Articles": articles,
        "Comparative Sentiment Score": comparison,
        "Final Sentiment Analysis": final_sentiment,
        "Audio": "Play Hindi Speech",  # 👈 label only
        "AudioPath": audio_path         # 👈 actual path for Streamlit to use
    }

@app.get("/audio")
def get_audio():
    audio_file = "summary_audio.mp3"
    if os.path.exists(audio_file):
        return FileResponse(audio_file, media_type="audio/mpeg", filename="summary_audio.mp3")
    return {"error": "Audio not found"}
