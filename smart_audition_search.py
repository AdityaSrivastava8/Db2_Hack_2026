
"""
Smart Audition Search for RASA AI.

Uses Haystack 2.x BM25 keyword retrieval to find relevant
records from the saved audition library.
"""

from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever


def _display(value):
    """Convert a value to searchable text."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return str(value)
    return str(value)


def _audition_content(item):
    """Build searchable text using the app's existing record fields."""
    fields = [
        ("Actor", item.get("actor_label")),
        ("Video file", item.get("video_file")),
        ("Character", item.get("selected_character")),
        ("Review status", item.get("reviewer_decision", "Not reviewed")),
        ("Shortlisted", item.get("shortlisted", False)),
        ("Reviewer notes", item.get("reviewer_notes")),
        ("Duration seconds", item.get("duration_seconds_estimate")),
        ("Pose detection rate", item.get("pose_detection_rate")),
        ("Face detection rate", item.get("face_detection_rate")),
        (
            "Mean normalized landmark movement index",
            item.get("mean_normalized_landmark_movement_index"),
        ),
        ("Mean shoulder tilt index", item.get("mean_shoulder_tilt_index")),
        (
            "Mean torso lateral offset",
            item.get("mean_torso_lateral_offset"),
        ),
        (
            "Fraction samples with wrist above shoulder",
            item.get("fraction_samples_with_wrist_above_shoulder"),
        ),
        ("Mean mouth opening ratio", item.get("mean_mouth_opening_ratio")),
        ("Mouth opening variability", item.get("mouth_opening_variability")),
        ("Mean eye openness proxy", item.get("mean_eye_openness_proxy")),
        ("Eye openness variability", item.get("eye_openness_variability")),
        ("Mean brow eye spacing proxy", item.get("mean_brow_eye_spacing_proxy")),
        ("Brow eye spacing variability", item.get("brow_eye_spacing_variability")),
        ("Evidence quality notes", item.get("evidence_quality_notes")),
        ("Analysis method", item.get("analysis_method")),
    ]

    parts = [
        f"{label}: {_display(value)}"
        for label, value in fields
        if value not in (None, "", [], {})
    ]

    # Include recorded observations where available.
    observations = item.get(
        "sample_observations",
        item.get("samples", []),
    )

    if isinstance(observations, list):
        for observation in observations[:100]:
            if not isinstance(observation, dict):
                continue

            cue_parts = []

            for key in (
                "timestamp_seconds",
                "pose_detected",
                "movement_since_previous_sample_index",
                "wrist_above_shoulder",
                "shoulder_tilt_index",
                "torso_lateral_offset",
                "mouth_opening_ratio",
                "eye_openness_proxy",
                "brow_eye_spacing_proxy",
                "model_expression_label",
            ):
                if observation.get(key) is not None:
                    cue_parts.append(
                        f"{key}: {observation[key]}"
                    )

            if cue_parts:
                parts.append(
                    "Timestamped observation: "
                    + ", ".join(cue_parts)
                )

    return "\n".join(parts)


def search_auditions(items, query, top_k=10):
    """
    Search saved audition dictionaries.

    Args:
        items: List of audition dictionaries.
        query: Search text.
        top_k: Maximum number of results.

    Returns:
        A list of dictionaries containing library_index, score,
        and content. library_index identifies the original record.
    """
    if not isinstance(query, str) or not query.strip():
        return []

    if not items:
        return []

    documents = []

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue

        content = _audition_content(item)

        if not content.strip():
            continue

        documents.append(
            Document(
                id=f"audition-{index}",
                content=content,
                meta={"library_index": index},
            )
        )

    if not documents:
        return []

    document_store = InMemoryDocumentStore()
    document_store.write_documents(documents)

    retriever = InMemoryBM25Retriever(
        document_store=document_store
    )

    response = retriever.run(
        query=query.strip(),
        top_k=min(max(1, int(top_k)), len(documents)),
    )

    results = []

    for document in response.get("documents", []):
        library_index = document.meta.get("library_index")

        if library_index is None:
            continue

        results.append(
            {
                "library_index": int(library_index),
                "score": float(document.score or 0.0),
                "content": document.content,
            }
        )

    return results
