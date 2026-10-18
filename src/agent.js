(function () {
  var root = document.getElementById('noteAgent');
  if (!root) return;
  var toggle = document.getElementById('agentToggle');
  var panel = document.getElementById('agentPanel');
  var closeBtn = document.getElementById('agentClose');
  var messages = document.getElementById('agentMessages');
  var form = document.getElementById('agentForm');
  var input = document.getElementById('agentInput');
  var mini = root.querySelector('[data-agent-avatar]');
  if (!toggle || !panel || !messages || !form || !input) return;

  var indexPromise = null;
  var entries = null;
  var welcomed = false;

  if (mini) mini.innerHTML = toggle.querySelector('svg').outerHTML;

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function scrollBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  function add(role, html) {
    var box = document.createElement('div');
    box.className = 'agent-msg ' + (role === 'user' ? 'is-user' : 'is-bot');
    if (role === 'user') box.textContent = html;
    else box.innerHTML = html;
    messages.appendChild(box);
    scrollBottom();
    return box;
  }

  function loadIndex() {
    if (entries) return Promise.resolve(entries);
    if (indexPromise) return indexPromise;
    indexPromise = fetch('/assets/search-index.json', { cache: 'force-cache' })
      .then(function (response) {
        if (!response.ok) throw new Error('索引加载失败');
        return response.json();
      })
      .then(function (data) {
        entries = Array.isArray(data) ? data : [];
        return entries;
      })
      .catch(function (error) {
        indexPromise = null;
        throw error;
      });
    return indexPromise;
  }

  function openPanel() {
    panel.hidden = false;
    toggle.setAttribute('aria-expanded', 'true');
    if (!welcomed) {
      welcomed = true;
      add('bot', '<p>你好，我是小双。可以问我「数学建模」「ADC」「通信协议」「最近更新」这类问题，我会从博客笔记里找内容，并给出原文链接。</p>');
    }
    setTimeout(function () { input.focus(); }, 30);
  }

  function closePanel() {
    panel.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
  }

  function excerpt(text, query) {
    var raw = String(text || '').replace(/\s+/g, ' ').trim();
    if (!raw) return '';
    var at = raw.toLowerCase().indexOf(query.toLowerCase());
    if (at < 0) at = 0;
    var start = Math.max(0, at - 55);
    var piece = raw.slice(start, start + 150);
    if (start > 0) piece = '…' + piece;
    if (start + 150 < raw.length) piece += '…';
    return piece;
  }

  function scoreEntry(entry, query, tokens) {
    var title = String(entry.title || '').toLowerCase();
    var text = String(entry.text || '').toLowerCase();
    var category = String(entry.category || '').toLowerCase();
    var score = 0;
    var q = query.toLowerCase();
    if (title.indexOf(q) !== -1) score += 60;
    if (category.indexOf(q) !== -1) score += 18;
    if (text.indexOf(q) !== -1) score += 12;
    tokens.forEach(function (token) {
      if (token.length < 2) return;
      if (title.indexOf(token) !== -1) score += 15;
      if (category.indexOf(token) !== -1) score += 4;
      if (text.indexOf(token) !== -1) score += 2;
    });
    return score;
  }

  function resultHtml(items, title) {
    var html = '<p>' + title + '</p><div class="agent-results">';
    items.forEach(function (entry) {
      html += '<a class="agent-result" href="' + escapeHtml(entry.url) + '">' +
        '<strong>' + escapeHtml(entry.title) + '</strong>' +
        '<small>' + escapeHtml(entry.category || '未分类') + (entry.date ? ' · ' + escapeHtml(entry.date) : '') + '</small>' +
        '<span>' + escapeHtml(excerpt(entry.text, entry._query || '')) + '</span>' +
        '</a>';
    });
    html += '</div>';
    return html;
  }

  function answer(query) {
    var q = query.trim();
    if (!q) return;
    if (/^(你好|您好|hi|hello|嗨|在吗)/i.test(q)) {
      add('bot', '<p>你好！我是小双，负责从站内笔记里找内容。试试问我：<br>「数学建模」「ADC」「最近更新」「通信协议」。</p>');
      return;
    }
    if (/你能做什么|帮助|怎么用|who are you|能干嘛/i.test(q)) {
      add('bot', '<p>我可以按关键词检索博客笔记，返回相关文章、摘要和原文链接。比如问「数学建模」「C++ 指针」「最近更新」。<br>我只引用站内笔记，不会凭空编造。</p>');
      return;
    }
    var typing = add('bot', '<span class="agent-typing">正在翻笔记…</span>');
    loadIndex().then(function (list) {
      if (!list.length) {
        typing.innerHTML = '<p>笔记索引还是空的。</p>';
        return;
      }
      var queryLower = q.toLowerCase();
      if (/最近|最新|更新/.test(q)) {
        var latest = list.slice().sort(function (a, b) { return String(b.date || '').localeCompare(String(a.date || '')); }).slice(0, 5);
        typing.innerHTML = resultHtml(latest, '最近更新的笔记：');
        return;
      }
      var tokens = queryLower.split(/[\s,，。.!！?？、;；:：]+/).filter(Boolean);
      if (tokens.length === 1 && queryLower.length >= 3) {
        for (var i = 0; i < queryLower.length - 1; i += 2) tokens.push(queryLower.slice(i, i + 2));
      }
      var hits = list.map(function (entry) {
        var item = Object.assign({}, entry);
        item._score = scoreEntry(entry, queryLower, tokens);
        item._query = queryLower;
        return item;
      }).filter(function (entry) { return entry._score > 0; })
        .sort(function (a, b) { return b._score - a._score; })
        .slice(0, 4);
      if (!hits.length) {
        typing.innerHTML = '<p>没有在笔记里找到「' + escapeHtml(q) + '」。可以换一个关键词，例如「数学建模」「ADC」「指针」。</p>';
        return;
      }
      typing.innerHTML = resultHtml(hits, '我在笔记里找到 ' + hits.length + ' 篇相关内容：');
    }).catch(function () {
      typing.innerHTML = '<p>笔记索引加载失败，请刷新页面后重试。</p>';
    });
  }

  toggle.addEventListener('click', function () {
    if (panel.hidden) openPanel(); else closePanel();
  });
  if (closeBtn) closeBtn.addEventListener('click', closePanel);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !panel.hidden) closePanel();
  });
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var value = input.value.trim();
    if (!value) return;
    add('user', value);
    input.value = '';
    answer(value);
  });
})();
