
"""
Smart Audition Search using Haystack 2.x.

Searches the existing audition library using BM25 keyword relevance.
No LLM, API key, or external service is required.
"""

from typing import Any

from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever


def _get_value(record: dict, *keys: str, default: str = "") -> str:
    """Return the first available non-empty value from a record."""
    for key in keys:
        value = record.get(key)
        if value is not None and value != "":
            if isinstance(value, (dict, list)):
                return str(value)
            return str(value)
    return default


def _record_to_text(record: dict) -> str:
    """Build searchable text from an audition record."""
    searchable_fields = [
        "actor_name",
        "actor",
        "name",
        "video_name",
        "video_path",
        "filename",
        "character",
        "character_name",
        "role",
        "status",
        "reviewer_status",
        "reviewer_notes",
        "notes",
        "shortlist",
        "shortlisted",
        "analysis_method",
        "evidence_quality",
        "observations",
        "metrics",
        "timestamp",
        "created_at",
    ]

    parts = []

    for key in searchable_fields:
        value = record.get(key)
        if value is not None and value != "":
            parts.append(f"{key.replace('_', ' ')}: {value}")

    # Include other scalar fields so new metadata remains searchable.
    for key, value in record.items():
        if key not in searchable_fields and isinstance(
            value, (str, int, float, bool)
        ):
            if value != "":
                parts.append(f"{key.replace('_', ' ')}: {value}")

    return "\n".join(parts)


def search_auditions(
    auditions: list[dict[str, Any]],
    query: str,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """
    Search audition records using Haystack's in-memory BM25 retriever.

    Args:
        auditions: List of audition dictionaries from your JSON library.
        query: Search text entered by the user.
        top_k: Maximum number of results to return.

    Returns:
        A list of dictionaries containing the original audition fields,
        plus search_score and search_text.
    """
    if not isinstance(query, str) or not query.strip():
        return []

    if not auditions:
        return []

    documents = []
    original_records = {}

    for index, record in enumerate(auditions):
        if not isinstance(record, dict):
            continue

        content = _record_to_text(record)
        if not content.strip():
            continue

        document_id = str(index)
        original_records[document_id] = record

        documents.append(
            Document(
                id=document_id,
                content=content,
                meta={"record_index": index},
            )
        )

    if not documents:
        return []

    document_store = InMemoryDocumentStore()
    document_store.write_documents(documents)

    retriever = InMemoryBM25Retriever(document_store=document_store)

    results = retriever.run(
        query=query.strip(),
        top_k=max(1, int(top_k)),
    )

    matches = []

    for document in results.get("documents", []):
        record = original_records.get(document.id)

        if record is None:
            continue

        result = dict(record)
        result["search_score"] = float(document.score or 0.0)
        result["search_text"] = document.content
        matches.append(result)

    return matches


def search_audition_library(
    auditions: list[dict[str, Any]],
    query: str,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Compatibility alias for callers using this function name."""
    return search_auditions(auditions, query, top_k)
