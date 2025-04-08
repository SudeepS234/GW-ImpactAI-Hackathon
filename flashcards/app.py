from flask import Flask, request, render_template, jsonify
from qna_generator import generate_qna

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        summary = request.form.get("summary", "")
        if summary.strip():
            flashcards = generate_qna(summary)
            return render_template("index.html", flashcards=flashcards, summary=summary)
    return render_template("index.html", flashcards=None)

if __name__ == "__main__":
    app.run(debug=True,port=5001)
