"""Embedding-based context selection and metrics."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, sqrt
from typing import Protocol, Sequence


class Embedder(Protocol):
    """Minimal interface used by the selector."""

    def encode(self, texts: list[str]) -> Sequence[Sequence[float]]:
        """Return one vector for each input string."""


@dataclass(frozen=True)
class ContextChunk:
    text: str
    is_evidence: bool | None = None


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity for two non-empty vectors."""
    if len(left) != len(right) or not left:
        raise ValueError("Embedding vectors must have the same non-zero length.")

    dot_product = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        raise ValueError("Embedding vectors must not be zero vectors.")

    return dot_product / (left_norm * right_norm)


def select_context(
    query: str,
    chunks: Sequence[ContextChunk],
    embedder: Embedder,
    *,
    strategy: str = "budget",
    budget_percent: int = 40,
    similarity_threshold: float = 0.4,
) -> dict:
    """Score chunks, select a subset, and calculate transparent metrics."""
    clean_query = query.strip()
    clean_chunks = [
        ContextChunk(chunk.text.strip(), chunk.is_evidence)
        for chunk in chunks
        if chunk.text.strip()
    ]

    if not clean_query:
        raise ValueError("Query must not be empty.")
    if not clean_chunks:
        raise ValueError("At least one context chunk is required.")
    if strategy not in {"budget", "adaptive"}:
        raise ValueError("Strategy must be 'budget' or 'adaptive'.")
    if not 1 <= budget_percent <= 100:
        raise ValueError("Budget percent must be between 1 and 100.")
    if not -1 <= similarity_threshold <= 1:
        raise ValueError("Similarity threshold must be between -1 and 1.")

    vectors = embedder.encode([clean_query, *[chunk.text for chunk in clean_chunks]])
    if len(vectors) != len(clean_chunks) + 1:
        raise ValueError("Embedding model returned an unexpected number of vectors.")

    query_vector = vectors[0]
    scores = [
        cosine_similarity(query_vector, chunk_vector)
        for chunk_vector in vectors[1:]
    ]

    ranked_indices = sorted(range(len(clean_chunks)), key=scores.__getitem__, reverse=True)

    if strategy == "budget":
        keep_count = max(1, ceil(len(clean_chunks) * budget_percent / 100))
        selected_indices = set(ranked_indices[:keep_count])
    else:
        selected_indices = {
            index for index, score in enumerate(scores) if score >= similarity_threshold
        }
        if not selected_indices:
            selected_indices = {ranked_indices[0]}

    results = [
        {
            "index": index,
            "text": chunk.text,
            "score": round(scores[index], 4),
            "selected": index in selected_indices,
            "is_evidence": chunk.is_evidence,
        }
        for index, chunk in enumerate(clean_chunks)
    ]

    total_words = sum(_word_count(chunk.text) for chunk in clean_chunks)
    selected_words = sum(
        _word_count(chunk.text)
        for index, chunk in enumerate(clean_chunks)
        if index in selected_indices
    )
    evidence_total = sum(chunk.is_evidence is True for chunk in clean_chunks)
    evidence_kept = sum(
        chunk.is_evidence is True
        for index, chunk in enumerate(clean_chunks)
        if index in selected_indices
    )

    return {
        "strategy": strategy,
        "chunks": results,
        "selected_context": "\n\n".join(
            chunk.text
            for index, chunk in enumerate(clean_chunks)
            if index in selected_indices
        ),
        "metrics": {
            "total_chunks": len(clean_chunks),
            "selected_chunks": len(selected_indices),
            "total_words": total_words,
            "selected_words": selected_words,
            "context_reduction": round(1 - selected_words / total_words, 4),
            "compression_ratio": round(total_words / selected_words, 2),
            "evidence_recall": (
                round(evidence_kept / evidence_total, 4) if evidence_total else None
            ),
            "evidence_kept": evidence_kept if evidence_total else None,
            "evidence_total": evidence_total if evidence_total else None,
        },
    }


def _word_count(text: str) -> int:
    return len(text.split())
