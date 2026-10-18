(function () {
  var KEY = 'blogBrightness.v1';
  var root = document.querySelector('[data-brightness]');
  var dim = document.getElementById('pageDim');
  var range = document.getElementById('brightnessRange');
  var value = document.getElementById('brightnessValue');
  if (!root || !range || !value) return;

  function clamp(n) {
    n = parseInt(n, 10);
    if (!isFinite(n)) n = 85;
    return Math.max(60, Math.min(100, n));
  }

  function apply(level) {
    level = clamp(level);
    var opacity = ((100 - level) / 100) * 0.9;
    if (dim) dim.style.opacity = String(opacity);
    range.value = String(level);
    range.style.setProperty('--brightness', level + '%');
    value.textContent = level + '%';
    range.setAttribute('aria-valuetext', '页面亮度 ' + level + '%');
    root.dataset.level = String(level);
    try { localStorage.setItem(KEY, String(level)); } catch (e) {}
  }

  var saved = 85;
  try {
    var raw = localStorage.getItem(KEY);
    if (raw != null) saved = parseInt(raw, 10);
  } catch (e) {}
  apply(saved);

  range.addEventListener('input', function () { apply(range.value); });
  var icon = root.querySelector('.brightness-icon');
  if (icon) {
    icon.style.cursor = 'pointer';
    icon.title = '恢复 100% 亮度';
    icon.addEventListener('click', function () { apply(100); });
  }
  window.addEventListener('storage', function (event) {
    if (event.key === KEY && event.newValue != null) apply(event.newValue);
  });
})();
