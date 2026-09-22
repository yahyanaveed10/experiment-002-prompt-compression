import pytest

from app.selector import ContextChunk, cosine_similarity, select_context


class FakeEmbedder:
    def __init__(self, vectors):
        self.vectors = vectors

    def encode(self, texts):
        assert len(texts) == len(self.vectors)
        return self.vectors


def test_budget_selection_keeps_highest_scores_in_source_order():
    result = select_context(
        "question",
        [
            ContextChunk("first evidence", True),
            ContextChunk("second distractor", False),
            ContextChunk("third evidence", True),
            ContextChunk("fourth distractor", False),
        ],
        FakeEmbedder(
            [
                [1.0, 0.0],
                [0.9, 0.1],
                [0.1, 0.9],
                [0.8, 0.2],
                [0.0, 1.0],
            ]
        ),
        strategy="budget",
        budget_percent=50,
    )

    selected = [chunk["index"] for chunk in result["chunks"] if chunk["selected"]]
    assert selected == [0, 2]
    assert result["selected_context"] == "first evidence\n\nthird evidence"
    assert result["metrics"]["context_reduction"] == 0.5
    assert result["metrics"]["evidence_recall"] == 1.0


def test_adaptive_selection_uses_threshold_and_keeps_one_chunk_minimum():
    embedder = FakeEmbedder(
        [[1.0, 0.0], [0.8, 0.2], [0.2, 0.8], [0.0, 1.0]]
    )
    chunks = [ContextChunk("one"), ContextChunk("two"), ContextChunk("three")]

    selected = select_context(
        "question",
        chunks,
        embedder,
        strategy="adaptive",
        similarity_threshold=0.7,
    )
    fallback = select_context(
        "question",
        chunks,
        embedder,
        strategy="adaptive",
        similarity_threshold=0.99,
    )

    assert selected["metrics"]["selected_chunks"] == 1
    assert fallback["metrics"]["selected_chunks"] == 1
    assert fallback["chunks"][0]["selected"] is True


def test_custom_input_has_no_evidence_metric():
    result = select_context(
        "question",
        [ContextChunk("one"), ContextChunk("two")],
        FakeEmbedder([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]),
        budget_percent=50,
    )

    assert result["metrics"]["evidence_recall"] is None


def test_invalid_input_is_rejected():
    with pytest.raises(ValueError, match="Query"):
        select_context(" ", [ContextChunk("context")], FakeEmbedder([]))

    with pytest.raises(ValueError, match="same non-zero length"):
        cosine_similarity([1.0], [1.0, 0.0])
