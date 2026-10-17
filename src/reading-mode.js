(function () {
  var roots = document.querySelectorAll('[data-reading-root]');
  if (!roots.length) return;
  roots.forEach(init);

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function init(root) {
    var stack = root.querySelector('[data-doc-stack]');
    if (!stack) return;
    var articles = Array.prototype.slice.call(stack.querySelectorAll(':scope > .doc'));
    if (!articles.length) return;

    var tocCard = document.querySelector('[data-reading-toc-card]');
    var tocEl = document.querySelector('[data-reading-toc]');
    var listCard = document.querySelector('[data-reading-list-card]');
    var listEl = document.querySelector('[data-reading-list]');
    var pagerCard = document.querySelector('[data-reading-pager-card]');
    var pagerTitle = document.querySelector('[data-reading-pager-title]');
    var pagerCount = document.querySelector('[data-reading-count]');
    var prevBtn = document.querySelector('[data-reading-prev]');
    var nextBtn = document.querySelector('[data-reading-next]');
    var current = 0;

    function articleTitle(index) {
      return articles[index].getAttribute('data-title') || ('文章 ' + (index + 1));
    }

    function scrollToArticle() {
      var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var top = articles[current].getBoundingClientRect().top + window.scrollY - 90;
      window.scrollTo({ top: top, behavior: reduce ? 'auto' : 'smooth' });
    }

    function renderPager() {
      if (!pagerCard) return;
      if (articles.length < 2) {
        pagerCard.hidden = true;
        return;
      }
      pagerCard.hidden = false;
      if (pagerTitle) pagerTitle.textContent = articleTitle(current);
      if (pagerCount) pagerCount.textContent = '第 ' + (current + 1) + ' / ' + articles.length + ' 篇';
      if (prevBtn) prevBtn.disabled = current === 0;
      if (nextBtn) nextBtn.disabled = current === articles.length - 1;
    }

    function renderList() {
      if (!listCard || !listEl) return;
      if (articles.length < 2) {
        listCard.hidden = true;
        return;
      }
      listCard.hidden = false;
      listEl.innerHTML = articles.map(function (article, index) {
        return '<button type="button" class="reading-list-item" data-reading-index="' + index + '">' +
          '<span class="reading-list-num">' + String(index + 1).padStart(2, '0') + '</span>' +
          '<span class="reading-list-name">' + escapeHtml(articleTitle(index)) + '</span>' +
          '</button>';
      }).join('');
      listEl.querySelectorAll('[data-reading-index]').forEach(function (button) {
        button.addEventListener('click', function () {
          show(parseInt(button.getAttribute('data-reading-index'), 10) || 0, { hash: true, scroll: true });
        });
      });
    }

    function updateListActive() {
      if (!listEl) return;
      listEl.querySelectorAll('[data-reading-index]').forEach(function (button) {
        button.classList.toggle('is-current', parseInt(button.getAttribute('data-reading-index'), 10) === current);
      });
    }

    function renderToc() {
      if (!tocCard || !tocEl) return;
      var body = articles[current].querySelector('.doc-body');
      var headings = body ? Array.prototype.slice.call(body.querySelectorAll('h2, h3')) : [];
      if (!headings.length) {
        tocCard.hidden = true;
        tocEl.innerHTML = '';
        return;
      }
      tocCard.hidden = false;
      tocEl.innerHTML = headings.map(function (heading, index) {
        var id = heading.id || ('toc-' + articles[current].id + '-' + index);
        heading.id = id;
        return '<a class="reading-toc-link" href="#' + escapeHtml(id) + '">' +
          escapeHtml(heading.textContent.trim()) + '</a>';
      }).join('');
    }

    function show(index, options) {
      current = Math.max(0, Math.min(articles.length - 1, index));
      articles.forEach(function (article, i) { article.hidden = i !== current; });
      renderPager();
      renderToc();
      updateListActive();
      if (options && options.hash) {
        try {
          history.replaceState(null, '', '#' + articles[current].id);
        } catch (error) {
          location.hash = articles[current].id;
        }
      }
      if (options && options.scroll) scrollToArticle();
    }

    if (tocEl) {
      tocEl.addEventListener('click', function (event) {
        var link = event.target.closest('a[href^="#"]');
        if (!link) return;
        var target = document.getElementById(link.getAttribute('href').slice(1));
        if (!target) return;
        event.preventDefault();
        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      });
    }
    if (prevBtn) prevBtn.addEventListener('click', function () { show(current - 1, { hash: true, scroll: true }); });
    if (nextBtn) nextBtn.addEventListener('click', function () { show(current + 1, { hash: true, scroll: true }); });

    var hash = location.hash ? location.hash.slice(1) : '';
    var initial = -1;
    if (hash) {
      var hashEl = document.getElementById(hash);
      if (hashEl) {
        var hashArticle = hashEl.closest('.doc');
        if (hashArticle) initial = articles.indexOf(hashArticle);
      }
    }
    if (initial < 0) {
      for (var i = 0; i < articles.length; i += 1) {
        if (articles[i].id === hash) { initial = i; break; }
      }
    }
    renderList();
    if (initial >= 0) show(initial, { scroll: true });
    else show(0, {});
  }
})();
