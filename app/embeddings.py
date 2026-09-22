"""Local embedding model adapter."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Sequence

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "sentence-transformers is not installed. Run 'pip install -e .'."
            ) from error

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> Sequence[Sequence[float]]:
        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformerEmbedder:
    model_name = os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL)
    return SentenceTransformerEmbedder(model_name)
