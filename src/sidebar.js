/* 左侧栏收放：记忆状态，桌面与手机通用 */
(function () {
  'use strict';
  var KEY = 'blog-side-hidden';

  function apply(hidden) {
    document.body.classList.toggle('side-hidden', hidden);
    var restores = document.querySelectorAll('.side-tab-restore');
    for (var i = 0; i < restores.length; i++) restores[i].hidden = !hidden;

    try { localStorage.setItem(KEY, hidden ? '1' : '0'); } catch (e) {}
  }

  function placeTab() {
    var col = document.querySelector('.side-column');
    if (!col) return;
    var rect = col.getBoundingClientRect();
    document.documentElement.style.setProperty('--side-edge', Math.round(rect.right) + 'px');
  }

  function init() {
    placeTab();
    window.addEventListener('resize', placeTab);
    window.addEventListener('load', placeTab);
    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch (e) {}
    // 默认收起：没有记录过就当作收起
    apply(saved === null ? true : saved === '1');
    placeTab();
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
