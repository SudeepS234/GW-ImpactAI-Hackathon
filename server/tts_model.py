
import os
import requests
import time
import nltk
from pydub import AudioSegment
from nltk.tokenize.punkt import PunktSentenceTokenizer

nltk.download('punkt')

ELEVENLABS_API_KEY = "sk_4fd3cdb2976c556538e86e7a7e84edea3cbae3c1e5446e09"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

HEADERS = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}

def sent_tokenize(text):
    tokenizer = PunktSentenceTokenizer()
    return tokenizer.tokenize(text)

def split_text(text, max_words=200):
    sentences = sent_tokenize(text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len((current + sentence).split()) <= max_words:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())
    return chunks

def generate_speech(text, output_dir="tts_chunks", output_file="output.mp3"):
    os.makedirs(output_dir, exist_ok=True)
    chunks = split_text(text)
    combined = AudioSegment.empty()

    print(f"Generating {len(chunks)} audio chunks using ElevenLabs...")

    for i, chunk in enumerate(chunks, 1):
        payload = {
            "text": chunk,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            chunk_path = os.path.join(output_dir, f"chunk_{i}.mp3")
            with open(chunk_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved chunk_{i}.mp3")
            segment = AudioSegment.from_file(chunk_path, format="mp3")
            combined += segment
            time.sleep(1)
        else:
            print(f"❌ Failed to generate chunk {i}: {response.status_code}, {response.text}")

    final_path = os.path.join(output_dir, output_file)
    combined.export(final_path, format="mp3")
    print(f"🎧 Final audio saved as {final_path}")
    return final_path
