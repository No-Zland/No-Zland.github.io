/* 让左侧导航跟着当前文章走：展开到文章所在目录并高亮 */
(function () {
  'use strict';

  function links() {
    return document.querySelectorAll('.page-nav a[href*="#"]');
  }

  function sync() {
    var hash = location.hash ? location.hash.slice(1) : '';
    if (!hash) return;
    var target = null;
    var all = links();
    for (var i = 0; i < all.length; i++) {
      var href = all[i].getAttribute('href') || '';
      if (href.split('#')[1] === hash) { target = all[i]; break; }
    }
    if (!target) return;

    var active = document.querySelectorAll('.page-nav .page-nav-doc.is-active');
    for (var k = 0; k < active.length; k++) active[k].classList.remove('is-active');
    target.classList.add('is-active');

    var node = target.parentElement;
    while (node && node !== document.body) {
      if (node.tagName === 'DETAILS') node.open = true;
      node = node.parentElement;
    }
    if (target.scrollIntoView) target.scrollIntoView({ block: 'nearest' });
  }

  window.BlogNavSync = { init: sync };
  window.addEventListener('hashchange', sync);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', sync);
  else sync();
})();
