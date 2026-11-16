/* 左侧栏收放：记忆状态，桌面与手机通用 */
(function () {
  'use strict';
  var KEY = 'blog-side-hidden';

  function apply(hidden) {
    document.body.classList.toggle('side-hidden', hidden);
    var restores = document.querySelectorAll('.side-restore');
    for (var i = 0; i < restores.length; i++) restores[i].hidden = !hidden;
    var presses = document.querySelectorAll('.side-toggle-top');
    for (var j = 0; j < presses.length; j++) presses[j].setAttribute('aria-pressed', hidden ? 'true' : 'false');
    try { localStorage.setItem(KEY, hidden ? '1' : '0'); } catch (e) {}
  }

  function init() {
    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch (e) {}
    apply(saved === '1');
    var buttons = document.querySelectorAll('[data-side-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      if (btn.getAttribute('data-bound')) continue;
      btn.setAttribute('data-bound', '1');
      btn.addEventListener('click', function () {
        apply(!document.body.classList.contains('side-hidden'));
      });
    }
  }

  window.BlogSidebar = { init: init };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
