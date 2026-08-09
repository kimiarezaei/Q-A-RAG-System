from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.logger import get_logger
from config import settings


logger = get_logger(__name__)


def create_chunks(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None
) -> list[str]:
    """
    Split a document into retrieval chunks.

    Strategy:
    - Short documents are kept as a single semantic chunk.
    - Larger documents are split using RecursiveCharacterTextSplitter.
    - Markdown headings are preserved to maintain context.

    This allows the pipeline to work for both the current small dataset
    and larger documents in the future.
    """

    text = text.strip()

    if not text:
        logger.warning("Empty document received.")
        return []

    chunk_size = (
    settings.chunk_size
    if chunk_size is None
    else chunk_size
    )

    chunk_overlap = (
        settings.chunk_overlap
        if chunk_overlap is None
        else chunk_overlap
    )
    
    # Keep short documents intact
    if len(text) <= chunk_size:
        logger.info(
            "Document kept as a single chunk (length=%d).",
            len(text)
        )
        return [text]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_text(text)

    logger.info(
        "Document split into %d chunks.",
        len(chunks)
    )

    return chunks



def process_document(text: str, source: str) -> list[dict]:
    """
    Process a document into chunks with metadata.

    Returns:
        [
            {
                "text": "...",
                "metadata": {
                    "source": "Account and Data.md",
                    "chunk_id": 0
                }
            }
        ]
    """

    chunks = create_chunks(text)

    processed_chunks = []

    for index, chunk in enumerate(chunks):
        processed_chunks.append(
            {
                "text": chunk,
                "metadata": {
                    "source": source,
                    "chunk_id": index
                }
            }
        )

    logger.info(
        "Processed document '%s' into %d chunks.",
        source,
        len(processed_chunks)
    )

    return processed_chunks