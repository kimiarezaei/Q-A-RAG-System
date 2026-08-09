# Decisions

## Assumptions

* The six Markdown files form a small customer-support knowledge base.
* Each document covers one topic and is short and self-contained.
* Answers should be strictly grounded in the provided documents.
* If the answer cannot be found in the knowledge base, the assistant should say `"Not found in document"` rather than guess.
* The filename is used as the source because it identifies the corresponding document.

## What I built and prioritised

* Built an end-to-end RAG pipeline: **document processing → embeddings → ChromaDB → retrieval → Claude → grounded answer**.
* Kept each document as one chunk because the documents are very short and each covers a single topic. I kept the chunking logic separate so it can be replaced with more advanced chunking if the dataset grows.
* Added a similarity threshold to avoid sending clearly irrelevant documents to the LLM.
* Used the retrieved metadata to generate source citations rather than asking the LLM to invent them.
* Separated the LLM wrapper, vector store, RAG logic, prompts, configuration, and API layer.
* Added logging and a smoke test covering both a document-supported and a document-unsupported question.

## What I cut, and why

Given the small dataset and timebox, I did not add:

* Reranking
* Conversation memory
* Complex chunking
* Managed/external vector database infrastructure (e.g. Pinecone, Weaviate Cloud) beyond local ChromaDB
* Authentication or multi-tenancy
* Full observability infrastructure

These would add complexity without providing much value for this dataset.

## How I tested and would evaluate it

- Tested the application in a clean Docker environment using a fresh image build (`--no-cache`).
- Verified the `/health` endpoint and the complete `/ask` RAG pipeline, including retrieval and answer generation.
- Added a smoke test covering both a document-supported and a document-unsupported question.
- For a larger evaluation set, I would measure:
  - **Retrieval:** whether the correct document is retrieved (Recall@K / Precision@K).
  - **Generation:** answer correctness and groundedness.
  - **Refusal:** whether unsupported questions are correctly rejected.
  - **Citations:** whether the cited document actually supports the answer.
- I would create a small labelled evaluation set of representative questions and use it to tune the retrieval threshold.

## With more time / to take it to production

* Improve chunking and retrieval, including reranking and a proper evaluation dataset as the knowledge base grows.
* Add automated tests, CI/CD, model and prompt versioning, and experiment tracking.
* Add LLM/RAG observability for quality, latency, cost and failures.
* Containerise and deploy with authentication, monitoring and scaling.
* Move to a scalable vector database and separate the document ingestion/indexing pipeline.
* For this assessment, I kept the implementation lightweight because the dataset is only six small documents.