import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from transformers import pipeline
import re

# Load summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Helper to extract video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# Get transcript
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except TranscriptsDisabled:
        return None

# Generate summary
def summarize_text(text, max_chunk=1000):
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summarized = [summarizer(chunk)[0]['summary_text'] for chunk in chunks]
    return " ".join(summarized)

# Detect if educational content
def is_educational(text):
    keywords = ['learn', 'lesson', 'education', 'course', 'lecture', 'tutorial', 'student']
    return any(keyword in text.lower() for keyword in keywords)

# Generate notes (basic structure)
def generate_notes(text):
    lines = text.split('. ')
    bullet_points = [f"- {line.strip()}" for line in lines if len(line.strip()) > 20]
    return "\n".join(bullet_points)

# Streamlit UI
st.title("🎥 YouTube Video Summarizer & Note Generator")

url = st.text_input("Enter YouTube Video Link")

if st.button("Generate Summary and Notes"):
    if url:
        video_id = extract_video_id(url)
        if video_id:
            transcript = get_transcript(video_id)
            if transcript:
                st.info("Transcription retrieved. Summarizing...")
                summary = summarize_text(transcript)
                st.subheader("🔍 Summary")
                st.write(summary)

                if is_educational(transcript):
                    st.subheader("📘 Educational Notes")
                    notes = generate_notes(summary)
                    st.text(notes)
                else:
                    st.warning("Video does not appear to be educational.")
            else:
                st.error("Transcript not available for this video.")
        else:
            st.error("Invalid YouTube link.")
    else:
        st.warning("Please enter a video link.")
