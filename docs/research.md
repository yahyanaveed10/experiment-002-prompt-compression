# Research basis

## Main question

How much context can a small embedding model remove before it loses the evidence needed for a question?

This experiment studies extractive context selection. It ranks existing chunks and keeps a subset. It does not rewrite the prompt or generate an answer.

## Questions tested

1. Can dense similarity remove distractors while retaining the answer-bearing chunk?
2. Can a single-vector embedding model retain every fact needed for a multi-hop question?
3. Does the selector preserve exact numbers and negation when those details carry the answer?
4. Does an adaptive similarity threshold preserve evidence more efficiently than a fixed context budget?

## Metrics

- **Context reduction:** `1 - selected words / total words`.
- **Compression ratio:** `total words / selected words`.
- **Evidence recall:** `selected evidence chunks / all evidence chunks`.
- **Relevance score:** cosine similarity between the query and each chunk embedding.

Evidence recall is available only for labeled scenarios. Custom input has no hidden ground truth.

These metrics describe this experiment. They are not results reported by the cited papers.

## Research anchors

- [Dense Passage Retrieval (EMNLP 2020)](https://aclanthology.org/2020.emnlp-main.550/) shows that learned dense representations can retrieve useful passages from a query.
- [LongLLMLingua (ACL 2024)](https://aclanthology.org/2024.acl-long.91/) studies query-aware prompt compression and the cost of irrelevant long context.
- [LLMLingua-2 (Findings ACL 2024)](https://aclanthology.org/2024.findings-acl.57/) treats extractive compression as a classification problem using a smaller bidirectional encoder.
- [HotpotQA (EMNLP 2018)](https://aclanthology.org/D18-1259/) provides sentence-level supporting facts for multi-hop questions, motivating evidence recall as a metric.
- [Adaptive-k context selection (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1017/) uses query-passage similarity thresholds to select a different amount of context for each question.
- [Efficiency vs. Verifiability (CustomNLP4U 2026)](https://aclanthology.org/2026.customnlp4u-1.19/) reports that answer quality can hide much larger losses in citation grounding under compression.

## Limits

- Embedding similarity measures relevance, not whether a final answer is correct.
- Single-vector embeddings can miss exact lexical details or one step of multi-hop evidence.
- The built-in scenarios are demonstrations, not a representative benchmark.
- A later evaluation should use a larger labeled dataset and compare against lexical and late-interaction retrieval baselines.
