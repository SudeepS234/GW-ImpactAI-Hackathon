from transformers import pipeline
import fitz  # PyMuPDF

# Load summarizer once globally
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_pdf_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        return full_text
    except Exception as e:
        print(f"[ERROR] PDF read failed: {e}")
        return ""

def split_into_chunks(text, max_words=500):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def summarize_chunk_safe(chunk):
    """
    Try summarizing a chunk. If it fails due to size, recursively split it smaller.
    """
    try:
        return summarizer(chunk, max_length=200, min_length=60, do_sample=False)[0]['summary_text']
    except Exception as e:
        print(f"[WARNING] Chunk too large or failed: {e}")
        words = chunk.split()
        if len(words) <= 100:
            return "[Skipped chunk due to size or format issues]"
        mid = len(words) // 2
        return (
            summarize_chunk_safe(" ".join(words[:mid])) + "\n" +
            summarize_chunk_safe(" ".join(words[mid:]))
        )

def summarize_large_text(text):
    chunks = split_into_chunks(text, max_words=500)
    summaries = []
    for chunk in chunks:
        summary = summarize_chunk_safe(chunk)
        summaries.append(summary)
    return "\n\n".join(summaries)
