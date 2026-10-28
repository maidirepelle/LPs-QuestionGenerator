import hashlib
import random
import re
from pathlib import Path

from flask import Flask, abort, render_template, make_response

app = Flask(
    __name__,
    template_folder="../templates"
)

QUESTIONS_FILE = Path(__file__).resolve().parent.parent / "LPsQuestions.txt"

questions = {}

with QUESTIONS_FILE.open("r", encoding="utf-8") as f:
    for line in f:
        questions[hashlib.md5(line.encode("utf-8")).hexdigest()] = line

@app.route("/", defaults={"question_hash": None})
@app.route("/<question_hash>")
def main(question_hash):
    if not questions:
        abort(500, "No questions loaded")

    if question_hash is None:
        question_hash = random.choice(list(questions.keys()))
    elif question_hash not in questions:
        abort(404)

    question = questions[question_hash]

    match = re.search(r"#([\D\d]+)#(.+)", question)

    if not match:
        abort(500, "Invalid question format")

    leadership_principle = match.group(1)
    real_question = match.group(2)

    response = make_response(
        render_template(
            "index.html",
            question=real_question,
            leadership_principle=leadership_principle,
            question_hash=question_hash,
        )
    )

    response.headers["X-question-Hash"] = question_hash
    return response
