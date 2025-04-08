from transformers import pipeline
import fitz  # PyMuPDF
import math

# Load summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", tokenizer="facebook/bart-large-cnn")

def extract_pdf_text(pdf_path):
    """Extract text from PDF"""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            print(f"[INFO] Page {page_num + 1}: {len(page_text)} characters")
            full_text += page_text
        doc.close()
        return full_text
    except Exception as e:
        print(f"[ERROR] PDF read failed: {e}")
        return ""

def split_into_chunks(text, max_words=700):
    """Split text into word chunks around 700 words"""
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def summarize_large_text(text):
    """Summarize large text by chunking"""
    chunks = split_into_chunks(text, max_words=700)
    print(f"[INFO] Total words: {len(text.split())} | Chunks created: {len(chunks)}")

    summaries = []
    for i, chunk in enumerate(chunks):
        try:
            summary = summarizer(chunk, max_length=200, min_length=60, do_sample=False)[0]['summary_text']
            print(f"[INFO] ✔️ Chunk {i + 1} summarized")
            summaries.append(summary)
        except Exception as e:
            print(f"[ERROR] Chunk {i + 1} failed: {e}")
            continue

    return "\n\n".join(summaries)


pdf_path = "UNIT-1.pdf"
text_from_pdf = extract_pdf_text(pdf_path)

# text = "direct input text here if needed."

if text_from_pdf.strip():
    final_summary = summarize_large_text(text_from_pdf)

    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(final_summary)

    print("\n✅ Final summary saved to summary.txt")
else:
    print("[ERROR] No valid text found.")
