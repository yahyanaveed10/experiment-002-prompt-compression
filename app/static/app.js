import { selectInBrowser } from './selector.js';

const elements = {
  form: document.querySelector('[data-form]'),
  scenarios: document.querySelector('[data-scenarios]'),
  researchQuestion: document.querySelector('[data-research-question]'),
  paperLink: document.querySelector('[data-paper-link]'),
  query: document.querySelector('[data-query]'),
  context: document.querySelector('[data-context]'),
  strategy: document.querySelector('[data-strategy]'),
  budget: document.querySelector('[data-budget]'),
  budgetOutput: document.querySelector('[data-budget-output]'),
  budgetControl: document.querySelector('[data-budget-control]'),
  threshold: document.querySelector('[data-threshold]'),
  thresholdOutput: document.querySelector('[data-threshold-output]'),
  thresholdControl: document.querySelector('[data-threshold-control]'),
  run: document.querySelector('[data-run]'),
  placeholder: document.querySelector('[data-placeholder]'),
  results: document.querySelector('[data-results]'),
  method: document.querySelector('[data-method]'),
  metrics: document.querySelector('[data-metrics]'),
  chunkResults: document.querySelector('[data-chunk-results]'),
  selectedContext: document.querySelector('[data-selected-context]'),
  error: document.querySelector('[data-error]'),
};

let scenarios = [];
let activeScenario = null;
let runsInBrowser = false;

async function getJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Request failed with status ${response.status}.`);
  return response.json();
}

async function loadScenarios() {
  try {
    try {
      scenarios = await getJson('./api/scenarios');
    } catch {
      scenarios = await getJson('./scenarios.json');
      runsInBrowser = true;
    }
    renderScenarioButtons();
    if (scenarios.length) selectScenario(scenarios[0]);
  } catch (error) {
    showError('Could not load the research scenarios.');
  }
}

function renderScenarioButtons() {
  elements.scenarios.innerHTML = '';

  scenarios.forEach((scenario, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'scenario-button';
    button.textContent = `${String(index + 1).padStart(2, '0')} / ${scenario.title}`;
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => selectScenario(scenario));
    elements.scenarios.appendChild(button);
  });
}

function selectScenario(scenario) {
  activeScenario = scenario;
  elements.query.value = scenario.question;
  elements.context.value = scenario.chunks.map((chunk) => chunk.text).join('\n\n');
  elements.researchQuestion.textContent = scenario.research_question;
  elements.paperLink.href = scenario.source.url;
  elements.paperLink.textContent = `${scenario.source.label} ↗`;

  [...elements.scenarios.children].forEach((button, index) => {
    button.setAttribute('aria-pressed', String(scenarios[index].id === scenario.id));
  });

  clearResult();
}

function markAsCustom() {
  activeScenario = null;
  elements.researchQuestion.textContent = 'Custom input has no labeled evidence.';
  elements.paperLink.removeAttribute('href');
  elements.paperLink.textContent = '';
  [...elements.scenarios.children].forEach((button) => {
    button.setAttribute('aria-pressed', 'false');
  });
}

function getChunks() {
  const texts = elements.context.value
    .split(/\n\s*\n/)
    .map((text) => text.trim())
    .filter(Boolean);

  if (!activeScenario) return texts.map((text) => ({ text, is_evidence: null }));

  return texts.map((text, index) => ({
    text,
    is_evidence: activeScenario.chunks[index]?.is_evidence ?? null,
  }));
}

async function runExperiment(event) {
  event.preventDefault();
  hideError();
  setLoading(true);

  try {
    const input = {
      query: elements.query.value.trim(),
      chunks: getChunks(),
      strategy: elements.strategy.value,
      budget_percent: Number(elements.budget.value),
      similarity_threshold: Number(elements.threshold.value),
    };
    const result = runsInBrowser
      ? await selectInBrowser(input)
      : await getJson('./api/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });

    renderResult(result);
  } catch (error) {
    showError(error.message);
  } finally {
    setLoading(false);
  }
}

function renderResult(result) {
  elements.placeholder.hidden = true;
  elements.results.hidden = false;
  elements.method.textContent = result.strategy === 'budget'
    ? `${elements.budget.value}% chunk budget`
    : `score ≥ ${Number(elements.threshold.value).toFixed(2)}`;

  renderMetrics(result.metrics);
  renderChunks(result.chunks);
  elements.selectedContext.textContent = result.selected_context;
}

function renderMetrics(metrics) {
  const evidenceValue = metrics.evidence_recall === null
    ? 'Not labeled'
    : `${Math.round(metrics.evidence_recall * 100)}%`;
  const values = [
    [`${Math.round(metrics.context_reduction * 100)}%`, 'context removed'],
    [`${metrics.selected_chunks} / ${metrics.total_chunks}`, 'chunks kept'],
    [evidenceValue, 'evidence recall'],
  ];

  elements.metrics.innerHTML = '';
  values.forEach(([value, label]) => {
    const metric = document.createElement('div');
    metric.className = 'metric';

    const strong = document.createElement('strong');
    strong.textContent = value;
    const span = document.createElement('span');
    span.textContent = label;

    metric.append(strong, span);
    elements.metrics.appendChild(metric);
  });
}

function renderChunks(chunks) {
  elements.chunkResults.innerHTML = '';

  chunks.forEach((chunk) => {
    const item = document.createElement('article');
    item.className = `chunk-result ${chunk.selected ? 'selected' : 'removed'}`;
    if (!chunk.selected && chunk.is_evidence) item.classList.add('evidence-lost');

    const meta = document.createElement('div');
    meta.className = 'chunk-meta';
    const name = document.createElement('span');
    name.textContent = `Chunk ${chunk.index + 1} · score ${chunk.score.toFixed(3)}`;
    const state = document.createElement('span');
    state.className = 'chunk-state';
    state.textContent = chunk.selected
      ? 'Kept'
      : chunk.is_evidence
        ? 'Evidence lost'
        : 'Removed';
    meta.append(name, state);

    const track = document.createElement('div');
    track.className = 'score-track';
    const fill = document.createElement('div');
    fill.className = 'score-fill';
    fill.style.width = `${Math.max(0, Math.min(100, (chunk.score + 1) * 50))}%`;
    track.appendChild(fill);

    const text = document.createElement('p');
    text.textContent = chunk.text;
    item.append(meta, track, text);
    elements.chunkResults.appendChild(item);
  });
}

function syncStrategyControls() {
  const usesBudget = elements.strategy.value === 'budget';
  elements.budgetControl.hidden = !usesBudget;
  elements.thresholdControl.hidden = usesBudget;
}

function clearResult() {
  elements.placeholder.hidden = false;
  elements.results.hidden = true;
  hideError();
}

function setLoading(isLoading) {
  elements.run.disabled = isLoading;
  elements.run.textContent = isLoading ? 'Loading model…' : 'Run selection';
}

function showError(message) {
  elements.error.textContent = message;
  elements.error.hidden = false;
}

function hideError() {
  elements.error.hidden = true;
  elements.error.textContent = '';
}

elements.form.addEventListener('submit', runExperiment);
elements.query.addEventListener('input', markAsCustom);
elements.context.addEventListener('input', markAsCustom);
elements.strategy.addEventListener('change', syncStrategyControls);
elements.budget.addEventListener('input', () => {
  elements.budgetOutput.textContent = `${elements.budget.value}%`;
});
elements.threshold.addEventListener('input', () => {
  elements.thresholdOutput.textContent = Number(elements.threshold.value).toFixed(2);
});

syncStrategyControls();
loadScenarios();
