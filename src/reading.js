(function () {
  var MIN_CHARS = 6000;
  var BLOCK_SPLIT = 4000;
  var MAX_BLOCKS_PER_PAGE = 10;
  var pagers = [];
  var currentLang = 'zh';

  var TEXT = {
    zh: {
      badge: '分章阅读',
      prev: '上一页',
      next: '下一页',
      select: '选择分页',
      page: '第 {n} / {total} 页',
      pageOnly: '第 {n} 页'
    },
    en: {
      badge: 'Paged reading',
      prev: 'Previous',
      next: 'Next',
      select: 'Choose page',
      page: 'Page {n} / {total}',
      pageOnly: 'Page {n}'
    }
  };

  function t(key) {
    var dict = TEXT[currentLang] || TEXT.zh;
    return dict[key] != null ? dict[key] : key;
  }

  function textLength(node) {
    return (node.textContent || '').replace(/\s+/g, '').length;
  }

  function shortLabel(label) {
    label = String(label || '').trim();
    if (label.length > 34) label = label.slice(0, 34) + '…';
    return label;
  }

  function makeBlock(label, nodes, size) {
    return { label: label || '', nodes: nodes || [], size: size || 0 };
  }

  function buildBlocks(body) {
    var nodes = Array.prototype.slice.call(body.childNodes);
    var blocks = [];
    var cur = makeBlock('开头', [], 0);

    nodes.forEach(function (node) {
      if (node.nodeType === 3 && !node.nodeValue.trim()) return;
      var tag = node.nodeType === 1 ? node.tagName : '';
      var isHeading = /^H[1-4]$/.test(tag);

      if (isHeading && cur.nodes.length) {
        blocks.push(cur);
        cur = makeBlock(node.textContent.trim(), [], 0);
      } else if (isHeading && !cur.nodes.length) {
        cur.label = node.textContent.trim();
      }

      cur.nodes.push(node);
      cur.size += textLength(node);

      if (cur.size >= BLOCK_SPLIT && tag &&
          /^(P|PRE|TABLE|UL|OL|BLOCKQUOTE|DIV|HR|FIGURE)$/.test(tag)) {
        blocks.push(cur);
        cur = makeBlock(cur.label, [], 0);
      }
    });

    if (cur.nodes.length) blocks.push(cur);
    return blocks;
  }

  function groupBlocks(blocks, target, maxBlocks) {
    var pages = [];
    var page = { label: '', nodes: [], size: 0 };
    var maxPerPage = maxBlocks || MAX_BLOCKS_PER_PAGE;

    blocks.forEach(function (block) {
      if (page.nodes.length &&
          (page.size + block.size > target || page.nodes.length >= maxPerPage)) {
        pages.push(page);
        page = { label: '', nodes: [], size: 0 };
      }
      if (!page.label) page.label = block.label;
      page.nodes = page.nodes.concat(block.nodes);
      page.size += block.size;
    });

    if (page.nodes.length) pages.push(page);
    return pages;
  }

  function makePager(pageLabels, top, totalPages) {
    var el = document.createElement('div');
    el.className = 'doc-pager' + (top ? ' doc-pager-top' : ' doc-pager-bottom');

    if (top) {
      var select = document.createElement('select');
      select.setAttribute('data-pager-select', '');
      pageLabels.forEach(function (label, index) {
        var opt = document.createElement('option');
        opt.value = String(index);
        opt.textContent = (index + 1) + '. ' + shortLabel(label);
        select.appendChild(opt);
      });
      select.setAttribute('aria-label', t('select'));

      var main = document.createElement('div');
      main.className = 'doc-pager-main';
      main.innerHTML = '<span class="doc-pager-badge" data-pager-badge></span>' +
        '<span class="doc-pager-label" data-pager-label aria-live="polite"></span>';

      var controls = document.createElement('div');
      controls.className = 'doc-pager-controls';
      var prev = document.createElement('button');
      prev.type = 'button';
      prev.setAttribute('data-pager-prev', '');
      var next = document.createElement('button');
      next.type = 'button';
      next.setAttribute('data-pager-next', '');
      controls.appendChild(prev);
      controls.appendChild(select);
      controls.appendChild(next);

      el.appendChild(main);
      el.appendChild(controls);
    } else {
      el.innerHTML = '<div class="doc-pager-main"><span class="doc-pager-label" data-pager-label></span></div>' +
        '<div class="doc-pager-controls">' +
        '<button type="button" data-pager-prev></button>' +
        '<button type="button" data-pager-next></button>' +
        '</div>';
    }
    return el;
  }

  function initPaginator(body) {
    if (body.getAttribute('data-paged')) return;
    var totalChars = textLength(body);
    var htmlLength = body.innerHTML.length;
    var imageCount = body.querySelectorAll('img').length;
    var imageHeavy = imageCount >= 8 || htmlLength > 300000;
    if (totalChars < MIN_CHARS && !imageHeavy) return;

    var article = body.closest('article.doc');
    if (!article) return;
    var docTitle = article.getAttribute('data-title') || '';

    var blocks = buildBlocks(body);
    if (blocks.length < 2) return;

    var pages;
    if (imageHeavy && totalChars < MIN_CHARS) {
      pages = groupBlocks(blocks, Number.MAX_VALUE, 1);
    } else {
      var target;
      if (totalChars > 1000000) target = 30000;
      else if (totalChars > 300000) target = 22000;
      else target = Math.max(5000, Math.min(12000, Math.round(totalChars * 0.65)));
      pages = groupBlocks(blocks, target);
    }
    if (pages.length < 2) return;

    var pageLabels = pages.map(function (page, index) {
      var label = page.label;
      if ((!label || label === '开头') && docTitle) label = docTitle;
      return label || t('pageOnly').replace('{n}', String(index + 1));
    });

    var wrap = document.createElement('div');
    wrap.className = 'doc-pages';
    var pageEls = [];

    pages.forEach(function (page, index) {
      var el = document.createElement('div');
      el.className = 'doc-page';
      if (index !== 0) el.hidden = true;
      page.nodes.forEach(function (node) { el.appendChild(node); });
      wrap.appendChild(el);
      pageEls.push(el);
    });

    var topPager = makePager(pageLabels, true, pages.length);
    var bottomPager = makePager(pageLabels, false, pages.length);
    article.insertBefore(topPager, body);
    body.appendChild(wrap);
    article.appendChild(bottomPager);
    body.setAttribute('data-paged', '1');

    var current = 0;

    function renderPage(index, scroll) {
      current = Math.max(0, Math.min(pageEls.length - 1, index));
      pageEls.forEach(function (el, i) { el.hidden = i !== current; });

      var label = pageLabels[current] || '';
      var pageText = t('page').replace('{n}', String(current + 1)).replace('{total}', String(pageEls.length));
      var fullLabel = pageText + (label ? ' · ' + label : '');

      [topPager, bottomPager].forEach(function (pager) {
        var badge = pager.querySelector('[data-pager-badge]');
        if (badge) badge.textContent = t('badge');
        pager.querySelectorAll('[data-pager-label]').forEach(function (el) {
          el.textContent = fullLabel;
        });
        pager.querySelectorAll('[data-pager-prev]').forEach(function (btn) {
          btn.textContent = t('prev');
          btn.disabled = current === 0;
        });
        pager.querySelectorAll('[data-pager-next]').forEach(function (btn) {
          btn.textContent = t('next');
          btn.disabled = current === pageEls.length - 1;
        });
        var select = pager.querySelector('[data-pager-select]');
        if (select) {
          select.value = String(current);
          select.setAttribute('aria-label', t('select'));
        }
      });

      if (scroll) {
        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var top = article.getBoundingClientRect().top + window.scrollY - 74;
        window.scrollTo({ top: top, behavior: reduce ? 'auto' : 'smooth' });
      }
    }

    topPager.querySelector('[data-pager-prev]').addEventListener('click', function () {
      renderPage(current - 1, true);
    });
    topPager.querySelector('[data-pager-next]').addEventListener('click', function () {
      renderPage(current + 1, true);
    });
    bottomPager.querySelector('[data-pager-prev]').addEventListener('click', function () {
      renderPage(current - 1, true);
    });
    bottomPager.querySelector('[data-pager-next]').addEventListener('click', function () {
      renderPage(current + 1, true);
    });
    topPager.querySelector('[data-pager-select]').addEventListener('change', function (event) {
      renderPage(parseInt(event.target.value, 10) || 0, true);
    });

    pagers.push({
      update: function () { renderPage(current, false); }
    });

    renderPage(0, false);

    if (location.hash) {
      var targetEl = document.getElementById(location.hash.slice(1));
      if (targetEl && article.contains(targetEl)) {
        var page = targetEl.closest('.doc-page');
        if (page) {
          var idx = pageEls.indexOf(page);
          if (idx > 0) renderPage(idx, false);
        }
      }
    }
  }

  function setLang(lang) {
    currentLang = lang === 'en' ? 'en' : 'zh';
    pagers.forEach(function (pager) { pager.update(); });
  }

  document.addEventListener('langchange', function (event) {
    setLang(event.detail && event.detail.lang);
  });

  setLang(document.documentElement.lang);
  document.querySelectorAll('article.doc .doc-body').forEach(initPaginator);
})();
