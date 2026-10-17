(function () {
  function init() {
    var quotes = Array.isArray(window.BLOG_QUOTES) ? window.BLOG_QUOTES : [];
    var quoteEl = document.getElementById('homeQuote');
    var authorEl = document.getElementById('homeQuoteAuthor');
    var button = document.getElementById('quoteRefresh');
    if (!quoteEl || !quotes.length) return;

    var index = -1;

    function render(next, animate) {
      index = (next + quotes.length) % quotes.length;
      var quote = quotes[index] || {};
      quoteEl.textContent = quote.text || '';
      authorEl.textContent = quote.author ? '—— ' + quote.author : '';
      if (animate) {
        quoteEl.classList.remove('quote-swap');
        void quoteEl.offsetWidth;
        quoteEl.classList.add('quote-swap');
      }
    }

    // 用当前分钟做种子，再叠加随机数：每次打开都不同，但同一分钟内也有变化。
    var seed = Math.floor(Date.now() / 60000);
    render((seed + Math.floor(Math.random() * quotes.length)) % quotes.length, false);

    if (button) {
      if (quotes.length < 2) {
        button.hidden = true;
      } else {
        button.addEventListener('click', function () {
          var next = index;
          while (next === index) next = Math.floor(Math.random() * quotes.length);
          render(next, true);
        });
      }
    }
  }

  window.BlogQuotes = { init: init };
  init();
})();
