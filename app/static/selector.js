let extractorPromise;

async function getExtractor() {
  if (!extractorPromise) {
    extractorPromise = import(
      'https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.0'
    ).then(({ env, pipeline }) => {
      env.allowLocalModels = false;
      return pipeline(
        'feature-extraction',
        'onnx-community/all-MiniLM-L6-v2-ONNX',
      );
    });
  }

  return extractorPromise;
}

function cosineSimilarity(left, right) {
  const dotProduct = left.reduce((sum, value, index) => {
    return sum + value * right[index];
  }, 0);
  const leftNorm = Math.sqrt(left.reduce((sum, value) => sum + value ** 2, 0));
  const rightNorm = Math.sqrt(right.reduce((sum, value) => sum + value ** 2, 0));

  return dotProduct / (leftNorm * rightNorm);
}

function wordCount(text) {
  return text.trim().split(/\s+/).length;
}

export async function selectInBrowser(input) {
  const extractor = await getExtractor();
  const output = await extractor(
    [input.query, ...input.chunks.map((chunk) => chunk.text)],
    { pooling: 'mean', normalize: true },
  );
  const [queryVector, ...chunkVectors] = output.tolist();
  const scores = chunkVectors.map((vector) => cosineSimilarity(queryVector, vector));
  const rankedIndices = scores
    .map((_, index) => index)
    .sort((left, right) => scores[right] - scores[left]);

  let selectedIndices;
  if (input.strategy === 'budget') {
    const keepCount = Math.max(
      1,
      Math.ceil(input.chunks.length * input.budget_percent / 100),
    );
    selectedIndices = new Set(rankedIndices.slice(0, keepCount));
  } else {
    selectedIndices = new Set(
      rankedIndices.filter((index) => scores[index] >= input.similarity_threshold),
    );
    if (!selectedIndices.size) selectedIndices.add(rankedIndices[0]);
  }

  const chunks = input.chunks.map((chunk, index) => ({
    index,
    text: chunk.text,
    score: Number(scores[index].toFixed(4)),
    selected: selectedIndices.has(index),
    is_evidence: chunk.is_evidence,
  }));
  const selectedChunks = chunks.filter((chunk) => chunk.selected);
  const totalWords = chunks.reduce((sum, chunk) => sum + wordCount(chunk.text), 0);
  const selectedWords = selectedChunks.reduce(
    (sum, chunk) => sum + wordCount(chunk.text),
    0,
  );
  const evidence = chunks.filter((chunk) => chunk.is_evidence === true);
  const evidenceKept = selectedChunks.filter(
    (chunk) => chunk.is_evidence === true,
  ).length;

  return {
    strategy: input.strategy,
    chunks,
    selected_context: selectedChunks.map((chunk) => chunk.text).join('\n\n'),
    metrics: {
      total_chunks: chunks.length,
      selected_chunks: selectedChunks.length,
      total_words: totalWords,
      selected_words: selectedWords,
      context_reduction: Number((1 - selectedWords / totalWords).toFixed(4)),
      compression_ratio: Number((totalWords / selectedWords).toFixed(2)),
      evidence_recall: evidence.length
        ? Number((evidenceKept / evidence.length).toFixed(4))
        : null,
      evidence_kept: evidence.length ? evidenceKept : null,
      evidence_total: evidence.length || null,
    },
  };
}
