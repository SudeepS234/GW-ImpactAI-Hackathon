from transformers import pipeline
from difflib import SequenceMatcher

# Load the models
qg_pipeline = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Similarity checker (to avoid near-duplicates)
def is_similar(q1, q2, threshold=0.85):
    return SequenceMatcher(None, q1.lower(), q2.lower()).ratio() > threshold

def generate_qna(summary_text, max_flashcards=10):
    print("Generating QnA for:", summary_text)
    inputs = f"generate questions: {summary_text}"
    outputs = qg_pipeline(inputs, max_length=256, do_sample=True, top_k=50, top_p=0.95, num_return_sequences=20)

    flashcards = []
    questions_seen = []

    for output in outputs:
        if len(flashcards) >= max_flashcards:
            break

        text = output['generated_text']
        if "?" not in text:
            continue

        split_idx = text.find("?")
        question = text[:split_idx + 1].strip()
        answer = text[split_idx + 1:].strip()

        # Skip exact and similar duplicates
        if any(is_similar(question, seen_q) for seen_q in questions_seen):
            continue

        if not answer or len(answer) < 5:
            try:
                result = qa_pipeline(question=question, context=summary_text)
                answer = result['answer']
            except:
                answer = "Answer not found."

        # Make sure answer is short and to the point
        if len(answer.split()) > 15:
            answer = ' '.join(answer.split()[:15]) + "..."

        flashcards.append({"question": question, "answer": answer})
        questions_seen.append(question)

    print("Generated flashcards:", flashcards)
    return flashcards
