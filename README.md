# Experiment 002: what context matters?

A small, open experiment in embedding-based context selection.

Give it a question and several context chunks. A local embedding model ranks each chunk and keeps a subset. The interface shows how much context was removed and whether known evidence survived.

No generative LLM or API key is required.

Try the standalone experiment at
<https://yahyanaveed10.github.io/experiment-002-prompt-compression/>.
The public version runs the embedding model in the browser. The Python app uses
the same model and scenarios locally.

## Research question

> How much context can a small embedding model remove before it loses the evidence needed for a question?

The built-in scenarios test three common failure modes:

1. removing irrelevant distractors;
2. preserving every step of multi-hop evidence;
3. retaining exact details such as numbers and negation.

Read [the research basis](docs/research.md) for the papers, metrics, and limits.

## Run locally

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>.

The first selection downloads `sentence-transformers/all-MiniLM-L6-v2`. Later runs use the local model cache.

## Run with Docker

```bash
docker build -t experiment-002 .
docker run --rm -p 8000:8000 experiment-002
```

Open <http://127.0.0.1:8000>.

## Test

```bash
pip install -e '.[dev]'
pytest
node --check app/static/app.js
node --check app/static/selector.js
```

Tests use a fake embedder, so they do not download a model.

## How it works

```text
question + chunks
        ↓
local sentence embeddings
        ↓
cosine similarity per chunk
        ↓
fixed budget or adaptive threshold
        ↓
selected context + evidence metrics
```

The backend is FastAPI. The frontend is plain HTML, CSS, and JavaScript. On
GitHub Pages, Transformers.js runs an ONNX version of MiniLM directly in the
visitor's browser. Both modes use the same scenario data.

Set `EMBEDDING_MODEL` to use another Sentence Transformers model:

```bash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 uvicorn app.main:app
```

## What this does not prove

Embedding similarity does not verify that a final answer is correct. Evidence recall is available only for the labeled scenarios. Custom input has no hidden ground truth.

A later optional reader could compare final answers using full and selected context. It is deliberately outside this small first experiment.

## License

MIT
