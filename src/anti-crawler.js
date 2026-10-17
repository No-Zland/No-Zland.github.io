(function () {
  var BOT_PATTERN = /GPTBot|ChatGPT-User|OAI-SearchBot|CCBot|ClaudeBot|anthropic-ai|Bytespider|PerplexityBot|Google-Extended|Applebot-Extended|meta-externalagent|Amazonbot|cohere-ai|Diffbot|Omgilibot|Scrapy|python-requests|curl\/|wget\//i;

  if (BOT_PATTERN.test(navigator.userAgent || '')) {
    document.documentElement.classList.add('is-bot');
  }

  function currentDoc(node) {
    var el = node && (node.nodeType === 1 ? node : node.parentElement);
    return el && el.closest ? el.closest('.doc') : null;
  }

  function sourceOf(doc) {
    if (!doc) return { title: document.title, url: location.href };
    var link = doc.querySelector('.copyright-meta a');
    return {
      title: doc.getAttribute('data-title') || document.title,
      url: link ? link.href : location.href
    };
  }

  document.addEventListener('copy', function (event) {
    var selection = window.getSelection();
    if (!selection || selection.isCollapsed) return;
    var doc = currentDoc(selection.anchorNode);
    if (!doc) return;
    var text = selection.toString();
    if (!text) return;
    var source = sourceOf(doc);
    var notice = '\n\n—— 摘自《' + source.title + '》｜梁双宇的个人博客\n' + source.url + '\n未经授权禁止商业转载或批量抓取。';
    if (event.clipboardData) {
      event.clipboardData.setData('text/plain', text + notice);
      event.preventDefault();
    }
  });

  document.addEventListener('dragstart', function (event) {
    var img = event.target.closest && event.target.closest('.doc-body img');
    if (img) event.preventDefault();
  });
})();
