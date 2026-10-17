(function () {
  if (!window.fetch || !window.history || !window.DOMParser) return;
  var main = document.querySelector('main');
  if (!main) return;

  var busy = false;
  var controller = null;
  var sequence = 0;

  function sameOrigin(url) {
    return url.origin === location.origin;
  }

  function isAsset(url) {
    return /\.(?:pdf|zip|rar|7z|mp3|flac|m4a|wav|ogg|jpg|jpeg|png|gif|webp|svg|pptx|docx|xlsx|md|txt)$/i.test(url.pathname);
  }

  function resolveBack(doc, targetUrl) {
    var back = document.querySelector('.topbar .back-btn');
    var next = doc.querySelector('.topbar .back-btn');
    if (!back || !next) return;
    var href = next.getAttribute('href');
    if (href) {
      try { back.href = new URL(href, targetUrl).href; } catch (e) { back.setAttribute('href', href); }
    }
    back.hidden = next.hidden;
  }

  function closeSearch() {
    var overlay = document.getElementById('searchOverlay');
    var trigger = document.getElementById('searchTrigger');
    if (overlay) overlay.hidden = true;
    if (trigger) trigger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  function typesetMath() {
    if (!document.querySelector('.doc-body')) return;
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise().catch(function () {});
      return;
    }
    if (document.querySelector('script[src*="mathjax"]')) return;
    var script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
    script.defer = true;
    script.onload = function () {
      if (window.MathJax && window.MathJax.typesetPromise) window.MathJax.typesetPromise().catch(function () {});
    };
    document.head.appendChild(script);
  }

  function scrollToHash(hash) {
    if (!hash) {
      window.scrollTo(0, 0);
      return;
    }
    var id;
    try { id = decodeURIComponent(hash.slice(1)); } catch (e) { id = hash.slice(1); }
    var target = document.getElementById(id);
    if (target) {
      var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    } else {
      window.scrollTo(0, 0);
    }
  }

  function swap(doc, targetUrl, push) {
    var currentMain = document.querySelector('main');
    var newMain = doc.querySelector('main');
    if (!newMain) throw new Error('no main in response');

    var currentLayout = currentMain.querySelector('.home-layout, .page-layout');
    var newLayout = newMain.querySelector('.home-layout, .page-layout');
    var player = document.getElementById('musicPlayer');

    if (currentLayout && newLayout && player) {
      var currentSide = currentLayout.querySelector('.side-column');
      var newSide = newLayout.querySelector('.side-column');
      var newPlayer = newSide ? newSide.querySelector('#musicPlayer') : null;
      var currentContent = currentLayout.querySelector('.home-content, .page-main');
      var newContent = newLayout.querySelector('.home-content, .page-main');

      if (currentSide && newSide && currentContent && newContent) {
        // 只替换侧栏里除播放器外的卡片；播放器节点留在原位，避免音频被卸载。
        Array.prototype.slice.call(currentSide.children).forEach(function (child) {
          if (child !== player) currentSide.removeChild(child);
        });
        var before = [];
        var after = [];
        var passedPlayer = false;
        Array.prototype.slice.call(newSide.children).forEach(function (child) {
          if (child === newPlayer) { passedPlayer = true; return; }
          (passedPlayer ? after : before).push(child);
        });
        before.forEach(function (node) { currentSide.insertBefore(node, player); });
        var anchor = player.nextSibling;
        after.forEach(function (node) { currentSide.insertBefore(node, anchor); });

        currentContent.replaceWith(newContent);
        currentLayout.className = newLayout.className;
      } else {
        throw new Error('layout mismatch');
      }
    } else {
      throw new Error('missing layout or player');
    }

    currentMain.className = newMain.className;
    document.body.className = doc.body.className;
    document.title = doc.title;
    resolveBack(doc, targetUrl);
    closeSearch();

    if (push) {
      try { history.pushState({ spa: true }, '', targetUrl.href); } catch (e) { history.pushState({ spa: true }, '', targetUrl.pathname + targetUrl.search); }
    }

    if (window.BlogReading) window.BlogReading.init();
    if (window.BlogQuotes) window.BlogQuotes.init();
    typesetMath();
    scrollToHash(targetUrl.hash);

    currentMain.classList.remove('is-page-fading');
    busy = false;
    document.documentElement.classList.remove('is-spa-loading');
  }

  function navigate(targetUrl, push) {
    var url = new URL(targetUrl, location.href);
    if (!sameOrigin(url) || isAsset(url)) {
      location.href = url.href;
      return;
    }
    if (busy && controller) controller.abort();
    var seq = ++sequence;
    busy = true;
    document.documentElement.classList.add('is-spa-loading');
    main.classList.add('is-page-fading');
    controller = window.AbortController ? new AbortController() : null;
    var options = { headers: { 'X-Requested-With': 'spa' } };
    if (controller) options.signal = controller.signal;
    fetch(url.href, options)
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.text();
      })
      .then(function (html) {
        if (seq !== sequence) return;
        var doc = new DOMParser().parseFromString(html, 'text/html');
        swap(doc, url, push);
      })
      .catch(function (error) {
        if (error && error.name === 'AbortError') return;
        if (seq !== sequence) return;
        busy = false;
        document.documentElement.classList.remove('is-spa-loading');
        main.classList.remove('is-page-fading');
        location.href = url.href;
      });
  }

  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var link = event.target.closest && event.target.closest('a[href]');
    if (!link || link.target === '_blank' || link.hasAttribute('download') || link.hasAttribute('data-no-spa')) return;
    var raw = link.getAttribute('href');
    if (!raw || raw.charAt(0) === '#') return;
    var url;
    try { url = new URL(link.href, location.href); } catch (e) { return; }
    if (!sameOrigin(url) || isAsset(url)) return;
    if (url.href === location.href) return;
    event.preventDefault();
    navigate(url.href, true);
  });

  window.addEventListener('popstate', function () {
    navigate(location.href, false);
  });
})();
