from transformers import pipeline

# Load the question generation model (e.g., T5 or similar)
qg_pipeline = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")

# Also the QA model for fallback answers
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def generate_qna(summary_text):
    print("Generating QnA for:", summary_text)
    inputs = f"generate questions: {summary_text}"
    outputs = qg_pipeline(inputs, max_length=256, do_sample=True, top_k=50, top_p=0.95, num_return_sequences=5)

    flashcards = []
    for output in outputs:
        text = output['generated_text']
        print("Model output:", text)

        if "?" in text:
            split_idx = text.find("?")
            question = text[:split_idx + 1].strip()
            answer = text[split_idx + 1:].strip()

            if not answer or len(answer) < 5:
                # Use QA model to get answer from context
                try:
                    result = qa_pipeline(question=question, context=summary_text)
                    answer = result['answer']
                except:
                    answer = "Answer not found."

            flashcards.append({"question": question, "answer": answer})
        else:
            print("Skipped due to no '?':", text)

    print("Generated flashcards:", flashcards)
    return flashcards
