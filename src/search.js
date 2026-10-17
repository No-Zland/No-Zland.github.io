(function () {
  var form = document.getElementById('searchForm');
  var overlay = document.getElementById('searchOverlay');
  var trigger = document.getElementById('searchTrigger');

  if (trigger && (!form || !overlay)) {
    trigger.addEventListener('click', function () {
      var home = trigger.getAttribute('data-home') || 'index.html';
      location.href = home + '#search';
    });
    return;
  }
  if (!form || !overlay) return;

  var closeBtn = document.getElementById('searchClose');
  var input = document.getElementById('searchInput');
  var resultsEl = document.getElementById('searchResults');
  var suggestEl = document.getElementById('searchSuggest');
  var clearBtn = document.getElementById('searchClear');
  var modeBtns = document.querySelectorAll('.mode-btn');

  var INDEX_URL = '/assets/search-index.json';
  var indexPromise = null;
  var entries = null;
  var mode = 'fuzzy';
  var timer = null;
  var requestId = 0;
  var query = '';
  var currentLang = 'zh';
  var lastFocus = null;

  var TEXT = {
    zh: {
      placeholder: '搜索标题或正文，例如：指针、数学建模…',
      loading: '正在加载搜索索引…',
      loadError: '搜索索引加载失败，请刷新页面重试。',
      noResults: '没有找到匹配的文章',
      found: '找到 {n} 篇文章 · {mode}',
      more: '仅显示前 30 条，请缩小关键词范围',
      exact: '完全匹配',
      fuzzy: '模糊匹配',
      clear: '清空搜索'
    },
    en: {
      placeholder: 'Search titles or text, e.g. pointers, modeling…',
      loading: 'Loading search index…',
      loadError: 'Could not load the search index. Please refresh and try again.',
      noResults: 'No matching articles',
      found: '{n} articles · {mode}',
      more: 'Showing the first 30 results. Try a narrower keyword.',
      exact: 'Exact',
      fuzzy: 'Fuzzy',
      clear: 'Clear search'
    }
  };

  function t(key) {
    var dict = TEXT[currentLang] || TEXT.zh;
    return dict[key] != null ? dict[key] : key;
  }

  function setLang(lang) {
    currentLang = lang === 'en' ? 'en' : 'zh';
    input.placeholder = t('placeholder');
    clearBtn.setAttribute('aria-label', t('clear'));
  }

  function openSearch() {
    if (!overlay) return;
    lastFocus = document.activeElement;
    overlay.hidden = false;
    document.body.style.overflow = 'hidden';
    if (trigger) trigger.setAttribute('aria-expanded', 'true');
    window.setTimeout(function () {
      input.focus();
      input.select();
    }, 30);
  }

  function closeSearch() {
    if (!overlay || overlay.hidden) return;
    overlay.hidden = true;
    document.body.style.overflow = '';
    if (location.hash === '#search') {
      try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    }
    if (trigger) {
      trigger.setAttribute('aria-expanded', 'false');
      if (trigger.focus) trigger.focus({ preventScroll: true });
    } else if (lastFocus && lastFocus.focus) {
      lastFocus.focus({ preventScroll: true });
    }
  }

  function normalize(value) {
    return String(value || '').toLowerCase().replace(/\s+/g, ' ').trim();
  }

  function termsFor(value) {
    return String(value || '').toLowerCase()
      .split(/[\s,，。.!！?？、;；:：/\\|]+/)
      .filter(Boolean);
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function highlight(text, terms) {
    text = String(text == null ? '' : text);
    var list = terms.filter(Boolean).slice().sort(function (a, b) {
      return b.length - a.length;
    });
    if (!list.length) return escapeHtml(text);
    var re = new RegExp(list.map(escapeRegExp).join('|'), 'gi');
    var out = '';
    var last = 0;
    var m;
    while ((m = re.exec(text)) !== null) {
      out += escapeHtml(text.slice(last, m.index));
      out += '<mark>' + escapeHtml(m[0]) + '</mark>';
      last = m.index + m[0].length;
      if (m[0].length === 0) re.lastIndex++;
    }
    out += escapeHtml(text.slice(last));
    return out;
  }

  function bestSnippet(text, terms) {
    text = String(text == null ? '' : text);
    if (!text) return '';
    var lower = text.toLowerCase();
    var best = -1;
    terms.forEach(function (term) {
      var i = lower.indexOf(String(term).toLowerCase());
      if (i !== -1 && (best === -1 || i < best)) best = i;
    });
    var start = best > 60 ? best - 60 : 0;
    var end = Math.min(text.length, start + 180);
    var s = text.slice(start, end);
    if (start > 0) s = '…' + s;
    if (end < text.length) s += '…';
    return s;
  }

  function modeName() {
    return t(mode === 'exact' ? 'exact' : 'fuzzy');
  }

  function setStatus(message, isError) {
    resultsEl.innerHTML = '<div class="search-status' + (isError ? ' is-error' : '') + '">' +
      escapeHtml(message) + '</div>';
  }

  function updateClear() {
    clearBtn.hidden = input.value.length === 0;
  }

  function loadIndex() {
    if (entries) return Promise.resolve(entries);
    if (indexPromise) return indexPromise;
    indexPromise = fetch(INDEX_URL, { cache: 'no-cache' })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
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

  function renderResults(req) {
    var q = query;
    var qn = normalize(q);
    var terms = termsFor(q);
    if (!qn) return;

    var list = [];
    entries.forEach(function (entry) {
      var title = entry.title || '';
      var text = entry.text || '';
      var titleNorm = normalize(title);
      var textNorm = normalize(text);
      var titleHits = 0;
      var textHits = 0;
      var score = 0;

      if (mode === 'exact') {
        var inTitle = titleNorm.indexOf(qn) !== -1;
        var inText = textNorm.indexOf(qn) !== -1;
        if (!inTitle && !inText) return;
        score = inTitle ? (titleNorm === qn ? 140 : 70) : 20;
        if (inText) score += 10;
      } else {
        if (!terms.length) return;
        terms.forEach(function (term) {
          if (titleNorm.indexOf(term) !== -1) titleHits++;
          if (textNorm.indexOf(term) !== -1) textHits++;
        });
        if (!titleHits && !textHits) return;
        var allTerms = terms.every(function (term) {
          return titleNorm.indexOf(term) !== -1 || textNorm.indexOf(term) !== -1;
        });
        score = titleHits * 40 + textHits * 8 + (allTerms ? 16 : 0);
        if (titleNorm.indexOf(qn) !== -1) score += 30;
        if (textNorm.indexOf(qn) !== -1) score += 10;
      }

      list.push({ entry: entry, score: score });
    });

    list.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      return String(a.entry.title).localeCompare(String(b.entry.title), 'zh');
    });

    // 同一篇文章的多个副本（标题、分类、正文片段都相同）只保留一条
    var seen = {};
    list = list.filter(function (item) {
      var entry = item.entry;
      var key = String(entry.title) + '\u0001' + String(entry.category) + '\u0001' +
        String(entry.text).slice(0, 240);
      if (seen[key]) return false;
      seen[key] = true;
      return true;
    });

    if (req !== requestId) return;

    var total = list.length;
    if (!total) {
      resultsEl.innerHTML = '<div class="search-empty">' + escapeHtml(t('noResults')) + '</div>';
      return;
    }

    var shown = list.slice(0, 30);
    var marks = mode === 'exact' ? [q] : (terms.length ? terms : [q]);
    var html = '<div class="search-status">' +
      escapeHtml(t('found').replace('{n}', String(total)).replace('{mode}', modeName())) +
      '</div>';

    shown.forEach(function (item, index) {
      var entry = item.entry;
      var meta = [];
      if (entry.category) meta.push(escapeHtml(entry.category));
      if (entry.date) meta.push(escapeHtml(entry.date));
      html += '<a class="search-result" style="--i:' + Math.min(index, 8) + '" href="' +
        escapeHtml(entry.url) + '">' +
        '<div class="sr-top"><span class="sr-title">' + highlight(entry.title, marks) +
        '</span><span class="sr-arrow">›</span></div>' +
        (meta.length ? '<div class="sr-meta">' + meta.join(' · ') + '</div>' : '') +
        '<div class="sr-snippet">' + highlight(bestSnippet(entry.text, marks), marks) + '</div>' +
        '</a>';
    });

    if (total > shown.length) {
      html += '<div class="search-more">' + escapeHtml(t('more')) + '</div>';
    }
    resultsEl.innerHTML = html;
  }

  function runSearch() {
    query = input.value.trim();
    updateClear();
    suggestEl.hidden = !!query;
    var req = ++requestId;

    if (!query) {
      resultsEl.innerHTML = '';
      return;
    }

    if (entries) {
      renderResults(req);
      return;
    }

    setStatus(t('loading'));
    loadIndex().then(function () {
      if (req !== requestId) return;
      renderResults(req);
    }).catch(function () {
      if (req !== requestId) return;
      setStatus(t('loadError'), true);
    });
  }

  function setMode(nextMode) {
    mode = nextMode === 'exact' ? 'exact' : 'fuzzy';
    modeBtns.forEach(function (button) {
      var active = button.getAttribute('data-mode') === mode;
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    if (query) runSearch();
  }

  function clearSearch() {
    input.value = '';
    query = '';
    requestId++;
    updateClear();
    suggestEl.hidden = false;
    resultsEl.innerHTML = '';
    input.focus();
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    clearTimeout(timer);
    runSearch();
  });

  input.addEventListener('input', function () {
    updateClear();
    clearTimeout(timer);
    timer = setTimeout(runSearch, 180);
  });

  input.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      event.stopPropagation();
      if (input.value.trim()) clearSearch();
      else closeSearch();
    }
  });

  if (trigger) trigger.addEventListener('click', openSearch);
  if (closeBtn) closeBtn.addEventListener('click', closeSearch);
  if (overlay) {
    overlay.addEventListener('click', function (event) {
      if (event.target === overlay) closeSearch();
    });
  }

  clearBtn.addEventListener('click', clearSearch);

  modeBtns.forEach(function (button) {
    button.addEventListener('click', function () {
      setMode(button.getAttribute('data-mode'));
    });
  });

  suggestEl.addEventListener('click', function (event) {
    var button = event.target.closest('button[data-query]');
    if (!button) return;
    input.value = button.getAttribute('data-query');
    runSearch();
    input.focus();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && overlay && !overlay.hidden) {
      event.stopPropagation();
      closeSearch();
      return;
    }
    if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey) return;
    var tag = (event.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select' || event.target.isContentEditable) return;
    event.preventDefault();
    if (overlay && overlay.hidden) openSearch();
    else {
      input.focus();
      input.select();
    }
  });

  document.addEventListener('langchange', function (event) {
    setLang(event.detail && event.detail.lang);
    if (query) runSearch();
  });

  setLang(document.documentElement.lang);
  setMode(mode);
  updateClear();
  if (location.hash === '#search') openSearch();
})();
