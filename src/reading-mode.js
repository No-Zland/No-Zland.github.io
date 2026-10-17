(function () {
  var roots = document.querySelectorAll('[data-reading-mode]');
  if (!roots.length) return;

  roots.forEach(init);

  function init(root) {
    var stack = root.querySelector('[data-doc-stack]');
    if (!stack) return;

    var articles = Array.prototype.slice.call(stack.querySelectorAll(':scope > .doc'));
    if (articles.length < 2) return;

    var count = root.querySelector('[data-read-count]');
    var title = root.querySelector('[data-read-title]');
    var prev = root.querySelector('[data-read-prev]');
    var next = root.querySelector('[data-read-next]');
    var select = root.querySelector('[data-read-select]');
    var modeButtons = root.querySelectorAll('[data-read-mode]');
    var current = 0;
    var mode = 'paged';

    function articleTitle(index) {
      return articles[index].getAttribute('data-title') || ('文章 ' + (index + 1));
    }

    function updateControls() {
      if (prev) prev.disabled = current === 0;
      if (next) next.disabled = current === articles.length - 1;
      if (select) select.value = String(current);
    }

    function scrollToArticle() {
      var target = articles[current];
      if (!target) return;
      var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var top = target.getBoundingClientRect().top + window.scrollY - 90;
      window.scrollTo({ top: top, behavior: reduce ? 'auto' : 'smooth' });
    }

    function setMode(value, scroll) {
      mode = value === 'continuous' ? 'continuous' : 'paged';
      root.setAttribute('data-mode', mode);
      stack.setAttribute('data-mode', mode);
      modeButtons.forEach(function (btn) {
        btn.setAttribute('aria-pressed', btn.getAttribute('data-read-mode') === mode ? 'true' : 'false');
      });

      if (mode === 'paged') {
        articles.forEach(function (article, index) { article.hidden = index !== current; });
        if (count) count.textContent = '第 ' + (current + 1) + ' / ' + articles.length + ' 篇';
        if (title) title.textContent = articleTitle(current);
        updateControls();
      } else {
        articles.forEach(function (article) { article.hidden = false; });
        if (count) count.textContent = '共 ' + articles.length + ' 篇';
        if (title) title.textContent = '连续阅读';
      }
      if (scroll) scrollToArticle();
    }

    function show(index, options) {
      current = Math.max(0, Math.min(articles.length - 1, index));
      if (mode === 'paged') {
        articles.forEach(function (article, i) { article.hidden = i !== current; });
        if (count) count.textContent = '第 ' + (current + 1) + ' / ' + articles.length + ' 篇';
        if (title) title.textContent = articleTitle(current);
      }
      updateControls();
      if (options && options.hash) {
        try {
          history.replaceState(null, '', '#' + articles[current].id);
        } catch (error) {
          location.hash = articles[current].id;
        }
      }
      if (options && options.scroll) scrollToArticle();
    }

    modeButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setMode(btn.getAttribute('data-read-mode'), true);
      });
    });

    if (prev) prev.addEventListener('click', function () { show(current - 1, { hash: true, scroll: true }); });
    if (next) next.addEventListener('click', function () { show(current + 1, { hash: true, scroll: true }); });
    if (select) select.addEventListener('change', function (event) {
      show(parseInt(event.target.value, 10) || 0, { hash: true, scroll: true });
    });

    var hash = location.hash ? location.hash.slice(1) : '';
    var initial = -1;
    for (var i = 0; i < articles.length; i += 1) {
      if (articles[i].id === hash) { initial = i; break; }
    }
    if (initial >= 0) current = initial;

    setMode('paged', false);
    if (initial >= 0) show(initial, { hash: false, scroll: true });
  }
})();
