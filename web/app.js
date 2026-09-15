const question = document.querySelector('#question');
const ask = document.querySelector('#ask');
const compare = document.querySelector('#compare');
const mode = document.querySelector('#mode');
const status = document.querySelector('#status');
const answer = document.querySelector('#answer');
const answerText = document.querySelector('#answer-text');
const evidence = document.querySelector('#evidence');
const count = document.querySelector('#count');
const comparison = document.querySelector('#comparison');
const comparisonGrid = document.querySelector('#comparison-grid');

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));
}

function renderEvidence(items) {
  count.textContent = `${items.length} chunk${items.length === 1 ? '' : 's'}`;
  evidence.innerHTML = items.length ? items.map((item, index) => `
    <article class="evidence-card">
      <div class="card-top"><span>0${index + 1}</span><b>${escapeHtml(item.section)}</b><small>rank ${index + 1}</small></div>
      <p>${escapeHtml(item.text)}</p>
      <div class="source">${escapeHtml(item.title)} <span>·</span> position ${item.position}</div>
    </article>
  `).join('') : '<div class="empty">No matching evidence found.</div>';
}

async function runQuery() {
  const value = question.value.trim();
  if (!value) return;
  ask.disabled = true;
  status.textContent = 'Retrieving...';
  try {
    const response = await fetch('/query', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: value, limit: 5, mode: mode.value})
    });
    if (!response.ok) throw new Error('Query failed');
    const result = await response.json();
    answerText.textContent = result.answer;
    answer.classList.remove('hidden');
    renderEvidence(result.evidence);
    status.textContent = `${result.retrieved} chunks retrieved`;
  } catch (error) {
    status.textContent = error.message;
  } finally {
    ask.disabled = false;
  }
}

async function compareModes() {
  const value = question.value.trim();
  if (!value) return;
  compare.disabled = true;
  status.textContent = 'Comparing...';
  try {
    const response = await fetch('/compare', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: value, limit: 3})
    });
    if (!response.ok) throw new Error('Comparison failed');
    const results = await response.json();
    comparisonGrid.innerHTML = Object.entries(results).map(([name, result]) => `
      <article class="comparison-card"><div><b>${name}</b><span>${result.retrieved} chunks</span></div>
      <p>${result.evidence[0] ? escapeHtml(result.evidence[0].section) : 'No evidence'}</p>
      <small>${result.grounding.grounded ? 'grounding check passed' : 'inspect grounding'}</small></article>
    `).join('');
    comparison.classList.remove('hidden');
    status.textContent = 'Comparison ready';
  } catch (error) {
    status.textContent = error.message;
  } finally {
    compare.disabled = false;
  }
}

ask.addEventListener('click', runQuery);
compare.addEventListener('click', compareModes);
question.addEventListener('keydown', (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') runQuery();
});
