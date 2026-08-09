import chromadb
from chromadb.utils import embedding_functions

from config import settings
from .document_processor import process_document
from utils.logger import get_logger


logger = get_logger(__name__)


# Embedding function for ChromaDB using the specified model from settings
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=settings.embedding_model_name
)

# Persistent ChromaDB client to store the vector index on disk
client = chromadb.PersistentClient(
    path=settings.chroma_path
)

# Get or create the ChromaDB collection
def get_collection():
    """
    Get or create the persistent ChromaDB collection.
    """

    return client.get_or_create_collection(
        name="documents",
        embedding_function=embedding_fn
    )


# Indexing
def build_index(
    documents: list[dict],
    force_rebuild: bool = False
):
    """
    Build the vector index from the supplied documents.

    Each document must contain:
        {
            "source": "refunds.md",
            "text": "..."
        }

    Documents are processed into chunks, embedded by ChromaDB,
    and stored together with their source metadata.
    """
    # Force rebuild if requested
    if force_rebuild:
        try:
            client.delete_collection("documents")
            logger.info("Existing collection deleted.")
        except Exception:
            logger.info("No existing collection to delete.")

    # Get or create the collection
    collection = get_collection()

    # Check if the collection already has data and skip rebuild if not forced
    if collection.count() > 0 and not force_rebuild:
        logger.info(
            "Index already exists. Skipping rebuild."
        )
        return

    logger.info("Building ChromaDB index...")

    # Process documents into chunks and prepare for batch insertion
    all_chunks = []
    all_ids = []
    all_metadata = []

    # Process each document
    for document_id, document in enumerate(documents):

        source = document["source"]
        text = document["text"]

        processed_chunks = process_document(
            text,
            source
        )

        for chunk_id, chunk in enumerate(processed_chunks):

            all_chunks.append(
                chunk["text"]
            )

            all_ids.append(
                f"{document_id}_{chunk_id}"
            )

            all_metadata.append(
                {
                    "source": source,
                    "document_id": document_id,
                    "chunk_id": chunk_id
                }
            )

    if not all_chunks:
        logger.warning(
            "No chunks were created. Index remains empty."
        )
        return

    # Batch insert into ChromaDB
    for i in range(
        0,
        len(all_chunks),
        settings.indexing_batch_size
    ):

        batch_end = i + settings.indexing_batch_size

        collection.add(
            documents=all_chunks[i:batch_end],
            ids=all_ids[i:batch_end],
            metadatas=all_metadata[i:batch_end]
        )

    logger.info(
        "Index built with %d chunks.",
        len(all_chunks)
    )



# Retrieval
def search(
    query: str,
    threshold: float | None = None
) -> list[dict]:
    """
    Retrieve relevant chunks from ChromaDB.

    Results below the configured similarity-distance threshold
    are filtered out.
    """

    if threshold is None:
        threshold = settings.similarity_threshold

    collection = get_collection()

    if collection.count() == 0:
        logger.warning(
            "Search requested but the vector index is empty."
        )
        return []

    results = collection.query(
        query_texts=[query],
        n_results=settings.retrieval_top_k,
        include=[
            "documents",
            "distances",
            "metadatas"
        ]
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    logger.info(
        "Query: '%s'",
        query
    )

    logger.info(
        "Retrieved distances: %s",
        distances
    )

    filtered_results = []

    for document, distance, metadata in zip(
        documents,
        distances,
        metadatas
    ):

        if distance < threshold:

            filtered_results.append(
                {
                    "text": document,
                    "distance": distance,
                    "metadata": metadata
                }
            )

    logger.info(
        "Retrieved %d relevant chunks.",
        len(filtered_results)
    )

    logger.info(
        "Returning %d results after threshold %.2f",
        len(filtered_results),
        threshold
    )

    return filtered_results

