import os

from flask import Flask, request, jsonify

from src.rag import answer_question
from src.vector_store import build_index
from utils.logger import get_logger


app = Flask(__name__)

logger = get_logger(__name__)

DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "data"
)


def load_documents() -> list[dict]:
    """
    Load Markdown documents while preserving their filenames
    for source attribution.
    """

    documents = []

    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith(".md"):
            continue

        path = os.path.join(DATA_DIR, filename)

        with open(path, "r", encoding="utf-8") as file:
            text = file.read().strip()

        documents.append(
            {
                "source": filename,
                "text": text,
            }
        )

        logger.info("Loaded document: %s", filename)

    return documents



def initialize_application():
    """
    Load documents and build the vector index.
    """

    documents = load_documents()

    logger.info(
        "Loaded %d documents.",
        len(documents)
    )

    build_index(
        documents,
        force_rebuild=False
    )


@app.route("/health")
def health():
    return jsonify({
        "ok": True
    })


@app.route("/ask", methods=["POST"])
def ask():

    payload = request.get_json(
        silent=True
    ) or {}

    question = (
        payload.get("question") or ""
    ).strip()

    if not question:
        return jsonify({
            "error": 'send JSON like {"question": "..."}'
        }), 400

    try:
        answer = answer_question(
            question
        )

        return jsonify(answer)

    except Exception:
        logger.exception(
            "Question answering failed"
        )

        return jsonify({
            "error": "Internal server error"
        }), 500




if __name__ == "__main__":

    initialize_application()

    app.run(
        host="0.0.0.0",
        port=5000
    )