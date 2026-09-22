from fastapi.testclient import TestClient

import app.main as main


class FakeEmbedder:
    def encode(self, texts):
        return [[1.0, 0.0], *[[1.0 - index * 0.1, index * 0.1] for index in range(len(texts) - 1)]]


client = TestClient(main.app)


def test_home_and_scenarios_are_available():
    assert client.get("/").status_code == 200

    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_selection_endpoint_uses_injected_embedder(monkeypatch):
    monkeypatch.setattr(main, "get_embedder", lambda: FakeEmbedder())

    response = client.post(
        "/api/select",
        json={
            "query": "Which context matters?",
            "chunks": [
                {"text": "Relevant context", "is_evidence": True},
                {"text": "Distractor", "is_evidence": False},
            ],
            "strategy": "budget",
            "budget_percent": 50,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]["selected_chunks"] == 1
    assert payload["metrics"]["evidence_recall"] == 1.0


def test_invalid_payload_returns_validation_error():
    response = client.post("/api/select", json={"query": "", "chunks": []})
    assert response.status_code == 422
