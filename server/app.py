from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import pipeline
import fitz  # PyMuPDF
import os
import tempfile
import json
from tts_model import generate_speech
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flashcards.qna_generator import generate_qna


app = Flask(__name__)
CORS(app)

# Summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Directory to store TTS audio files
AUDIO_OUTPUT_DIR = "tts_chunks"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def split_into_chunks(text, max_words=700):
    words = text.split()
    chunks = []
    current_chunk = []
    count = 0
    for word in words:
        count += 1
        current_chunk.append(word)
        if count >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            count = 0
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def summarize_large_text(text):
    chunks = split_into_chunks(text, max_words=700)
    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=200, min_length=60, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            summaries.append(f"[Error summarizing chunk: {e}]")
    return "\n\n".join(summaries)

@app.route('/summary', methods=['POST'])
def summarize_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    options_json = request.form.get("options")
    
    try:
        options = json.loads(options_json) if options_json else {}
        
    except Exception as e:
        return jsonify({'error': f'Invalid options format: {e}'}), 400

    summary_enabled = options.get("summary", False)
    audio_enabled = options.get("audio", False)
    flashcards_enabled = options.get("flashcards", False)


    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file_path = tmp.name
        file.save(file_path)
        text = extract_text_from_pdf(file_path)

    os.remove(file_path)

    if not text.strip():
        return jsonify({'error': 'Empty or unreadable PDF'}), 400

    if not summary_enabled:
        return jsonify({'summary': 'summary disabled'}), 200

    final_summary = summarize_large_text(text)
    flashcards = []
    if flashcards_enabled:
        try:
            flashcards = generate_qna(final_summary)
        except Exception as e:
            print("Flashcard generation error:", e)
            flashcards = []

    audio_url = None
    if audio_enabled:
        try:
            audio_path = generate_speech(final_summary)
            audio_filename = os.path.basename(audio_path)
            audio_url = f"/audio/{audio_filename}"
        except Exception as e:
            print(f"Audio generation error: {e}")
            audio_url = None

    return jsonify({
        'summary': final_summary,
        'audio_url': audio_url,
        'flashcards': flashcards  # ✅ Add this line
    }), 200




@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True,port=5000)
