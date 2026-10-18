(function () {
  var DRAFT_KEY = 'blogNoteDrafts.v1';
  var TOKEN_KEY = 'blogNoteToken.v1';
  var OWNER = 'No-Zland';
  var REPO = 'No-Zland.github.io';
  var BRANCH = 'main';

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function safeUrl(url) {
    url = String(url || '').trim();
    if (/^https?:\/\//i.test(url) || /^mailto:/i.test(url) || url.charAt(0) === '#' || url.charAt(0) === '/') return url;
    return '#';
  }

  function inlineMarkdown(text) {
    var html = escapeHtml(text);
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, function (_, alt, url) {
      return '<img src="' + escapeHtml(safeUrl(url)) + '" alt="' + alt + '" loading="lazy">';
    });
    html = html.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (_, label, url) {
      return '<a href="' + escapeHtml(safeUrl(url)) + '" target="_blank" rel="noopener">' + label + '</a>';
    });
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    return html;
  }

  function renderMarkdown(source) {
    var lines = String(source || '').replace(/\r\n?/g, '\n').split('\n');
    var out = [];
    var paragraph = [];
    var list = null;
    var listTag = 'ul';

    function flushParagraph() {
      if (!paragraph.length) return;
      out.push('<p>' + paragraph.map(inlineMarkdown).join('<br>') + '</p>');
      paragraph = [];
    }

    function flushList() {
      if (!list) return;
      out.push('<' + listTag + '>' + list.join('') + '</' + listTag + '>');
      list = null;
    }

    for (var i = 0; i < lines.length; i += 1) {
      var line = lines[i];
      if (/^\s*```/.test(line)) {
        flushParagraph(); flushList();
        var code = [];
        i += 1;
        while (i < lines.length && !/^\s*```/.test(lines[i])) {
          code.push(lines[i]);
          i += 1;
        }
        out.push('<pre><code>' + escapeHtml(code.join('\n')) + '</code></pre>');
        continue;
      }
      if (!line.trim()) {
        flushParagraph(); flushList();
        continue;
      }
      var heading = line.match(/^(#{1,6})\s+(.+)$/);
      if (heading) {
        flushParagraph(); flushList();
        var level = heading[1].length;
        out.push('<h' + level + '>' + inlineMarkdown(heading[2]) + '</h' + level + '>');
        continue;
      }
      if (/^\s*>\s?/.test(line)) {
        flushParagraph(); flushList();
        out.push('<blockquote>' + inlineMarkdown(line.replace(/^\s*>\s?/, '')) + '</blockquote>');
        continue;
      }
      var unordered = line.match(/^\s*[-*+]\s+(.+)$/);
      var ordered = line.match(/^\s*\d+\.\s+(.+)$/);
      if (unordered || ordered) {
        flushParagraph();
        var tag = ordered ? 'ol' : 'ul';
        if (!list || listTag !== tag) {
          flushList();
          list = [];
          listTag = tag;
        }
        list.push('<li>' + inlineMarkdown((unordered || ordered)[1]) + '</li>');
        continue;
      }
      flushList();
      paragraph.push(line.replace(/\s+$/, ''));
    }
    flushParagraph(); flushList();
    return out.join('\n');
  }

  function slugify(title) {
    var value = String(title || '').trim()
      .replace(/[\\/:*?"<>|#]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
    return value.slice(0, 80) || ('note-' + Date.now());
  }

  function toBase64(text) {
    var bytes = new TextEncoder().encode(text);
    var binary = '';
    for (var i = 0; i < bytes.length; i += 1) binary += String.fromCharCode(bytes[i]);
    return btoa(binary);
  }

  function encodePath(path) {
    return path.split('/').map(encodeURIComponent).join('/');
  }

  function init() {
    var root = document.querySelector('[data-note-editor]');
    if (!root || root.dataset.noteReady === '1') return;
    root.dataset.noteReady = '1';

    var sections = Array.isArray(window.NOTE_SECTIONS) ? window.NOTE_SECTIONS : [];
    var titleEl = root.querySelector('[data-note-title]');
    var sectionEl = root.querySelector('[data-note-section]');
    var categoryEl = root.querySelector('[data-note-category]');
    var bodyEl = root.querySelector('[data-note-body]');
    var previewEl = root.querySelector('[data-note-preview]');
    var countEl = root.querySelector('[data-note-count]');
    var draftsEl = root.querySelector('[data-note-drafts]');
    var tokenEl = root.querySelector('[data-note-token]');
    var rememberEl = root.querySelector('[data-note-remember]');
    var statusEl = root.querySelector('[data-note-status]');
    var publishBtn = root.querySelector('[data-note-publish]');
    var drafts = loadDrafts();
    var currentId = null;
    var timer = null;

    function setStatus(message, kind, link) {
      statusEl.className = 'note-status' + (kind ? ' is-' + kind : '');
      statusEl.textContent = '';
      if (link) {
        var a = document.createElement('a');
        a.href = link;
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = message;
        statusEl.appendChild(a);
      } else {
        statusEl.textContent = message;
      }
    }

    function loadDrafts() {
      try {
        var list = JSON.parse(localStorage.getItem(DRAFT_KEY) || '[]');
        return Array.isArray(list) ? list : [];
      } catch (error) {
        return [];
      }
    }

    function persistDrafts() {
      try {
        localStorage.setItem(DRAFT_KEY, JSON.stringify(drafts));
        return true;
      } catch (error) {
        setStatus('本地草稿保存失败：浏览器存储空间可能已满。', 'error');
        return false;
      }
    }

    function currentState() {
      return {
        title: titleEl.value.trim(),
        section: sectionEl.value,
        category: categoryEl.value,
        body: bodyEl.value
      };
    }

    function fillCategories(sectionName, selected) {
      var section = sections.filter(function (item) { return item.slug === sectionName; })[0];
      var cats = section && Array.isArray(section.cats) ? section.cats : [];
      categoryEl.innerHTML = '<option value="">无分类（直接放在板块下）</option>' +
        cats.map(function (cat) { return '<option value="' + escapeHtml(cat) + '">' + escapeHtml(cat) + '</option>'; }).join('');
      if (selected && cats.indexOf(selected) !== -1) categoryEl.value = selected;
    }

    function populateSections() {
      if (!sections.length) {
        sectionEl.innerHTML = '<option value="个人与总结">个人与总结</option>';
      } else {
        sectionEl.innerHTML = sections.map(function (section) {
          return '<option value="' + escapeHtml(section.slug) + '">' + escapeHtml(section.title) + '</option>';
        }).join('');
      }
      fillCategories(sectionEl.value, '');
    }

    function updatePreview() {
      previewEl.innerHTML = renderMarkdown(bodyEl.value);
      countEl.textContent = bodyEl.value.length + ' 字符';
    }

    function saveDraft() {
      var state = currentState();
      if (!state.title && !state.body.trim()) return;
      if (!currentId) currentId = 'd' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      var draft = {
        id: currentId,
        title: state.title || '未命名笔记',
        section: state.section,
        category: state.category,
        body: state.body,
        updated: Date.now()
      };
      var found = false;
      drafts = drafts.map(function (item) {
        if (item.id === currentId) { found = true; return draft; }
        return item;
      });
      if (!found) drafts.unshift(draft);
      drafts.sort(function (a, b) { return (b.updated || 0) - (a.updated || 0); });
      persistDrafts();
      renderDrafts();
    }

    function renderDrafts() {
      if (!drafts.length) {
        draftsEl.innerHTML = '<div class="note-draft-empty">还没有本地草稿。</div>';
        return;
      }
      draftsEl.innerHTML = drafts.map(function (draft) {
        var date = new Date(draft.updated || Date.now());
        return '<button type="button" class="note-draft' + (draft.id === currentId ? ' is-current' : '') + '" data-draft-id="' + escapeHtml(draft.id) + '">' +
          '<span class="note-draft-title">' + escapeHtml(draft.title || '未命名笔记') + '</span>' +
          '<span class="note-draft-meta">' + date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) + ' · ' + escapeHtml(draft.section || '未选板块') + '</span>' +
          '</button>';
      }).join('');
      draftsEl.querySelectorAll('[data-draft-id]').forEach(function (button) {
        button.addEventListener('click', function () {
          loadDraft(button.getAttribute('data-draft-id'));
        });
      });
    }

    function loadDraft(id) {
      var draft = drafts.filter(function (item) { return item.id === id; })[0];
      if (!draft) return;
      currentId = draft.id;
      titleEl.value = draft.title === '未命名笔记' ? '' : (draft.title || '');
      sectionEl.value = draft.section || (sections[0] ? sections[0].slug : '个人与总结');
      fillCategories(sectionEl.value, draft.category || '');
      bodyEl.value = draft.body || '';
      updatePreview();
      renderDrafts();
      setStatus('已载入本地草稿。');
    }

    function newDraft() {
      saveDraft();
      currentId = null;
      titleEl.value = '';
      sectionEl.value = sections[0] ? sections[0].slug : '个人与总结';
      fillCategories(sectionEl.value, '');
      bodyEl.value = '';
      updatePreview();
      renderDrafts();
      setStatus('新建草稿。');
      titleEl.focus();
    }

    function deleteDraft() {
      if (!currentId) { setStatus('当前没有已保存的草稿。', 'error'); return; }
      drafts = drafts.filter(function (item) { return item.id !== currentId; });
      persistDrafts();
      currentId = null;
      titleEl.value = '';
      bodyEl.value = '';
      updatePreview();
      renderDrafts();
      setStatus('草稿已删除。', 'ok');
    }

    function download() {
      var state = currentState();
      var body = state.body.trim();
      var markdown = body.charAt(0) === '#' ? body : ('# ' + (state.title || '未命名笔记') + '\n\n' + body);
      var blob = new Blob([markdown + '\n'], { type: 'text/markdown;charset=utf-8' });
      var link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = slugify(state.title || '未命名笔记') + '.md';
      link.click();
      setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
    }

    function copyBody() {
      if (!navigator.clipboard) { setStatus('当前浏览器不支持剪贴板 API。', 'error'); return; }
      navigator.clipboard.writeText(bodyEl.value).then(function () {
        setStatus('Markdown 已复制。', 'ok');
      }).catch(function () {
        setStatus('复制失败，请手动选择文本复制。', 'error');
      });
    }

    function publish() {
      var state = currentState();
      var token = tokenEl.value.trim();
      if (!state.title) { setStatus('请先填写标题。', 'error'); titleEl.focus(); return; }
      if (!state.body.trim()) { setStatus('正文不能为空。', 'error'); bodyEl.focus(); return; }
      if (!token) { setStatus('请填入 GitHub Token 后再发布。', 'error'); tokenEl.focus(); return; }
      if (rememberEl.checked) { try { sessionStorage.setItem(TOKEN_KEY, token); } catch (error) {} }
      else { try { sessionStorage.removeItem(TOKEN_KEY); } catch (error) {} }
      saveDraft();
      publishBtn.disabled = true;
      setStatus('正在写入 GitHub…');
      var filename = slugify(state.title) + '.md';
      var path = ['content/post', state.section, state.category, filename].filter(Boolean).join('/');
      var body = state.body.trim();
      var markdown = body.charAt(0) === '#' ? body : ('# ' + state.title + '\n\n' + body);
      var api = 'https://api.github.com/repos/' + OWNER + '/' + REPO + '/contents/' + encodePath(path);
      var headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      };

      fetch(api, { headers: headers })
        .then(function (response) {
          if (response.status === 404) return null;
          if (!response.ok) throw new Error('读取文件失败（' + response.status + '）');
          return response.json();
        })
        .then(function (existing) {
          var payload = {
            message: (existing ? 'Update note: ' : 'Add note: ') + state.title,
            content: toBase64(markdown + '\n'),
            branch: BRANCH
          };
          if (existing && existing.sha) payload.sha = existing.sha;
          return fetch(api, {
            method: 'PUT',
            headers: Object.assign({ 'Content-Type': 'application/json' }, headers),
            body: JSON.stringify(payload)
          });
        })
        .then(function (response) {
          if (!response.ok) {
            return response.json().catch(function () { return {}; }).then(function (data) {
              throw new Error((data && data.message) || ('发布失败（' + response.status + '）'));
            });
          }
          return response.json();
        })
        .then(function (data) {
          var html = data && data.commit ? data.commit.html_url : '';
          setStatus('已提交，等待 GitHub Actions 重新构建后出现在博客。', 'ok', html);
        })
        .catch(function (error) {
          setStatus(error.message || '发布失败，请检查 Token 权限。', 'error');
        })
        .finally(function () {
          publishBtn.disabled = false;
        });
    }

    populateSections();
    var token = '';
    try { token = sessionStorage.getItem(TOKEN_KEY) || ''; } catch (error) {}
    if (token) { tokenEl.value = token; rememberEl.checked = true; }
    if (drafts.length) loadDraft(drafts[0].id);
    else {
      sectionEl.value = sections[0] ? sections[0].slug : '个人与总结';
      fillCategories(sectionEl.value, '');
      updatePreview();
      renderDrafts();
    }

    titleEl.addEventListener('input', function () { updatePreview(); clearTimeout(timer); timer = setTimeout(saveDraft, 500); });
    bodyEl.addEventListener('input', function () { updatePreview(); clearTimeout(timer); timer = setTimeout(saveDraft, 500); });
    sectionEl.addEventListener('change', function () { fillCategories(sectionEl.value, ''); clearTimeout(timer); timer = setTimeout(saveDraft, 300); });
    categoryEl.addEventListener('change', function () { clearTimeout(timer); timer = setTimeout(saveDraft, 300); });
    root.querySelector('[data-note-new]').addEventListener('click', newDraft);
    root.querySelector('[data-note-save]').addEventListener('click', function () { saveDraft(); setStatus('草稿已保存到本机。', 'ok'); });
    root.querySelector('[data-note-delete]').addEventListener('click', deleteDraft);
    root.querySelector('[data-note-export]').addEventListener('click', download);
    root.querySelector('[data-note-copy]').addEventListener('click', copyBody);
    publishBtn.addEventListener('click', publish);
  }

  window.BlogNoteEditor = { init: init };
  init();
})();
