from flask import Flask, request, jsonify
from qna_generator import generate_qna

app = Flask(__name__)

@app.route('/generate_flashcards', methods=['POST'])
def generate_flashcards():
    data = request.get_json()

    if not data or 'summary' not in data:
        return jsonify({"error": "Missing 'summary' field in request"}), 400

    summary_text = data['summary']
    qna_pairs = generate_qna(summary_text)

    return jsonify({"flashcards": qna_pairs})

if __name__ == '__main__':
    app.run(debug=True)
