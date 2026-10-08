# RAG-based Q&A service

The application:

* Loads Markdown documents from `data/`
* Chunks and embeds them using Sentence Transformers
* Stores and retrieves documents with ChromaDB
* Uses Anthropic Claude to generate grounded answers
* Returns the source used for each answer
* Refuses questions that are not covered by the knowledge base

## Structure

* `app.py` — Flask API (`/health`, `/ask`)
* `src/document_processor.py` — document processing and chunking
* `src/vector_store.py` — ChromaDB indexing and retrieval
* `src/rag.py` — RAG pipeline
* `src/llm.py` — Claude API wrapper
* `src/prompts.py` — RAG prompt
* `config.py` — configuration
* `smoke_test.py` — basic end-to-end tests

## Setup

Create a `.env` file:

```text
ANTHROPIC_API_KEY=your_api_key
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Then run the tests in another terminal:

```bash
python smoke_test.py
```

## API

`POST /ask`

```json
{
  "question": "How long is the return window?"
}
```

Example:

```json
{
  "answer": "30 days from the date of delivery.",
  "sources": ["Returns and Refunds"]
}
```

For questions outside the knowledge base:

```json
{
  "answer": "Not found in document",
  "sources": []
}
```
