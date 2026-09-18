# experiment-002-prompt-compression

An interactive tool for measuring how prompt compression affects LLM output quality — token by token.

## What this does

You give it a prompt. It compresses it (multiple strategies). It sends both versions to a model. It shows you — **at the logit level** — where the model's confidence shifts, where it diverges, and where it breaks.

This is not a visualization of someone else's research. This is the experiment itself.

## How it works

```
User prompt → Compression (multiple strategies) → Model inference (full + compressed)
                                                 → Compare outputs token-by-token
                                                 → Visualize logprob shifts
```

### Compression strategies (planned)
- **Chunk pruning** — Remove retrieved context chunks by relevance score
- **Summarization** — Condense sections via a smaller model
- **Token filtering** — Remove low-information tokens (LLMLingua-style)
- **Truncation** — Simple prefix/suffix cutting (baseline)

### What you see
- Each output token colored by log-probability (green = confident → red = uncertain)
- Side-by-side: full prompt output vs. compressed prompt output
- Divergence markers — exact token positions where the top prediction flips
- Compression ratio vs. quality curve

## Architecture

```
┌─────────────────────────────────────┐
│  Frontend (static HTML/CSS/JS)      │
│  - Prompt input                     │
│  - Strategy selector                │
│  - Token-level logprob visualizer   │
│  - Divergence comparison view       │
└──────────────┬──────────────────────┘
               │ HTTP
┌──────────────▼──────────────────────┐
│  Backend (Python / FastAPI)         │
│  - Compression pipeline             │
│  - Model inference (Ollama / API)   │
│  - Logprob extraction               │
│  - Response comparison              │
└─────────────────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Model provider                     │
│  - Ollama (local, free, full logits)│
│  - OpenAI (logprobs=True, top-20)   │
│  - Bring your own key               │
└─────────────────────────────────────┘
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai/) with any pulled model (e.g. `ollama pull llama3.1:8b`)
- No API keys required for local mode

## Status

🚧 **Groundwork laid.** Backend and frontend are not yet implemented. See the research context below for the empirical motivation.

## Research context

This tool is motivated by findings from:

- **Jiang et al.** — *LongLLMLingua* (ACL 2024). [arXiv:2310.06839](https://arxiv.org/abs/2310.06839)
  - 4x compression **improved** NaturalQuestions accuracy by 21.4% — removing distractor documents helps.
  - The "lost in the middle" failure mode means more context can be worse than less.

- **Pan et al.** — *LLMLingua-2* (ACL 2024). [arXiv:2403.12968](https://arxiv.org/abs/2403.12968)
  - Token classification (not perplexity) achieves 2x compression with <2% quality drop.
  - 3–6x faster than perplexity-based methods.

- **Li et al.** — *Prompt Compression for Large Language Models: A Survey* (NAACL 2025). [arXiv:2410.12388](https://arxiv.org/abs/2410.12388)
  - Taxonomy: hard prompts (token filtering) vs. soft prompts (learned embeddings).
  - Hybrid approaches emerging. Prefix caching changes the cost calculus for static prompt components.

## License

MIT
