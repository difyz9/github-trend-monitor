const state = { repositories: [], filtered: [] };
const $ = (id) => document.getElementById(id);

const formatNumber = (value) => new Intl.NumberFormat('en-US', { notation: value > 9999 ? 'compact' : 'standard', maximumFractionDigits: 1 }).format(value);
const escapeHtml = (value) => String(value || '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
const renderMarkdown = (value) => value.split('\n').map((line) => {
  const safe = escapeHtml(line).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  if (safe.startsWith('# ')) return `<h1>${safe.slice(2)}</h1>`;
  if (safe.startsWith('## ')) return `<h2>${safe.slice(3)}</h2>`;
  if (safe.startsWith('### ')) return `<h3>${safe.slice(4)}</h3>`;
  if (safe.startsWith('- ')) return `<li>${safe.slice(2)}</li>`;
  return safe ? `<p>${safe}</p>` : '';
}).join('').replace(/(<li>.*?<\/li>)+/g, (items) => `<ul>${items}</ul>`);

function populateSelect(id, values) {
  const select = $(id);
  values.forEach((value) => select.insertAdjacentHTML('beforeend', `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
}

function renderStats(repositories) {
  $('repo-count').textContent = formatNumber(repositories.length);
  $('star-count').textContent = formatNumber(repositories.reduce((sum, repo) => sum + repo.stars, 0));
  const active = repositories.filter((repo) => repo.is_active).length;
  $('active-rate').textContent = repositories.length ? `${Math.round(active / repositories.length * 100)}%` : '0%';
  $('language-count').textContent = new Set(repositories.map((repo) => repo.language).filter((language) => language !== 'Unknown')).size;
}

function renderRepositories() {
  const query = $('search').value.trim().toLowerCase();
  const domain = $('domain').value;
  const language = $('language').value;
  const sort = $('sort').value;
  state.filtered = state.repositories.filter((repo) => {
    const haystack = [repo.name, repo.description, ...repo.topics, ...repo.domains].join(' ').toLowerCase();
    return (!query || haystack.includes(query)) && (domain === 'all' || repo.domains.includes(domain)) && (language === 'all' || repo.language === language);
  });
  state.filtered.sort((a, b) => sort === 'forks' ? b.forks - a.forks : sort === 'recent' ? String(b.first_seen).localeCompare(String(a.first_seen)) : b.stars - a.stars);
  const domainLabel = domain === 'all' ? '全部项目' : domain;
  $('result-title').textContent = domainLabel;
  $('result-count').textContent = `${state.filtered.length} projects`;
  $('empty').hidden = state.filtered.length !== 0;
  $('repo-grid').innerHTML = state.filtered.map((repo) => {
    const topics = repo.topics.slice(0, 3).map((topic) => `<span class="topic">${escapeHtml(topic)}</span>`).join('');
    return `<article class="repo"><div class="repo-top"><span class="repo-domain">${escapeHtml(repo.domains[0] || 'TRACKED')}</span><span class="language">${escapeHtml(repo.language)}</span></div><h3><a href="${escapeHtml(repo.url)}" target="_blank" rel="noreferrer">${escapeHtml(repo.name)}</a></h3><p>${escapeHtml(repo.description || '暂无项目描述')}</p><div class="topic-list">${topics}</div><div class="repo-foot"><div class="repo-metrics"><span>★ <b>${formatNumber(repo.stars)}</b></span><span>⑂ <b>${formatNumber(repo.forks)}</b></span></div><span>${escapeHtml(repo.first_seen || '—')}</span></div></article>`;
  }).join('');
}

async function loadData() {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) throw new Error('data request failed');
    const data = await response.json();
    state.repositories = data.repositories || [];
    populateSelect('domain', data.domains || []);
    populateSelect('language', data.languages || []);
    renderStats(state.repositories);
    $('signal-text').textContent = `${state.repositories.length} 个项目已从本地 CSV 索引载入`;
    $('refresh-time').textContent = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    renderRepositories();
  } catch (error) {
    $('status-text').textContent = 'DATA ERROR';
    $('signal-text').textContent = '无法读取数据，请确认服务从项目根目录启动';
    $('empty').hidden = false;
  }
}

['search', 'domain', 'language', 'sort'].forEach((id) => $(id).addEventListener('input', renderRepositories));
$('reset').addEventListener('click', () => { $('search').value = ''; $('domain').value = 'all'; $('language').value = 'all'; $('sort').value = 'stars'; renderRepositories(); });
$('generate-insights').addEventListener('click', async () => {
  const button = $('generate-insights');
  button.disabled = true;
  button.textContent = 'AI 正在分析…';
  $('insights-meta').textContent = '正在调用 OpenRouter，分析高信号项目与可执行机会。';
  try {
    const response = await fetch('/api/insights', { method: 'POST' });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'AI 分析失败');
    $('insights-content').innerHTML = renderMarkdown(result.content);
    $('insights-meta').textContent = `分析完成 · ${result.repository_count} 个项目 · ${result.model} · ${result.generated_at}`;
  } catch (error) {
    $('insights-content').innerHTML = `<span class="insights-placeholder">${escapeHtml(error.message)}</span>`;
    $('insights-meta').textContent = '分析未完成';
  } finally {
    button.disabled = false;
    button.textContent = '重新生成洞察 ↗';
  }
});
$('today').textContent = new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'short', day: '2-digit' }).format(new Date()).toUpperCase();
loadData();
