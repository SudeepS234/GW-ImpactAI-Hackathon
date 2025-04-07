from transformers import pipeline

qg_pipeline = pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")

def generate_qna(summary_text):
    """
    Generates QnA pairs using a text2text-generation pipeline with T5 model.
    """
    formatted_input = f"generate questions: {summary_text}"

    try:
        output = qg_pipeline(formatted_input, max_length=128, do_sample=False)
        generated_text = output[0]['generated_text']

        qna_pairs = []
        for line in generated_text.strip().split('\n'):
            if ':' in line:
                q, a = line.split(':', 1)
                qna_pairs.append({
                    "question": q.strip(),
                    "answer": a.strip()
                })

        return qna_pairs

    except Exception as e:
        return [{"error": str(e)}]
