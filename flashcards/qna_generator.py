import os
from transformers import pipeline
from tavily import TavilyClient
from dotenv import load_dotenv
from difflib import SequenceMatcher

# Load env vars
load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Load local models
qg_pipeline = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def is_similar(q1, q2, threshold=0.85):
    return SequenceMatcher(None, q1.lower(), q2.lower()).ratio() > threshold

def deduplicate_questions(questions):
    unique = []
    for q in questions:
        if not any(is_similar(q, uq) for uq in unique):
            unique.append(q)
    return unique

def get_web_answer_tavily(question):
    try:
        result = tavily.search(query=question, search_depth="advanced", include_answer=True)
        if result and result.get("answer"):
            return result["answer"][:100]  # truncate if long
    except Exception as e:
        print("Tavily error:", e)
    return "Answer not found."

def generate_qna(summary_text, max_flashcards=10):
    print("Generating QnA for:", summary_text)
    inputs = f"generate questions: {summary_text}"
    outputs = qg_pipeline(inputs, max_length=256, do_sample=True, top_k=50, top_p=0.95, num_return_sequences=15)

    raw_questions = [o['generated_text'].split("?")[0] + '?' for o in outputs if '?' in o['generated_text']]
    unique_questions = deduplicate_questions(raw_questions)[:max_flashcards]

    flashcards = []
    for question in unique_questions:
        try:
            result = qa_pipeline(question=question, context=summary_text)
            answer = result['answer'].strip()

            if not answer or len(answer) < 5 or answer.lower() == question.lower():
                answer = get_web_answer_tavily(question)

            # Truncate answer if needed
            if len(answer.split()) > 15:
                answer = ' '.join(answer.split()[:15]) + '...'

            flashcards.append({"question": question, "answer": answer})
        except Exception as e:
            print("Error processing question:", question, e)

    print("Generated flashcards:", flashcards)
    return flashcards
