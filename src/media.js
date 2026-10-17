(function () {
  var lightbox = null;
  var lastFocus = null;

  function ensureLightbox() {
    if (lightbox) return lightbox;
    lightbox = document.createElement('div');
    lightbox.className = 'media-lightbox';
    lightbox.hidden = true;
    lightbox.innerHTML = '<button type="button" class="media-lightbox-close" aria-label="关闭图片">&times;</button><img alt="">';
    lightbox.addEventListener('click', function (event) {
      if (event.target === lightbox || event.target.classList.contains('media-lightbox-close')) {
        closeLightbox();
      }
    });
    document.body.appendChild(lightbox);
    return lightbox;
  }

  function openLightbox(src, alt) {
    var box = ensureLightbox();
    var img = box.querySelector('img');
    img.src = src;
    img.alt = alt || '';
    lastFocus = document.activeElement;
    box.hidden = false;
    document.body.style.overflow = 'hidden';
    box.querySelector('.media-lightbox-close').focus();
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.hidden = true;
    lightbox.querySelector('img').removeAttribute('src');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click', function (event) {
    var img = event.target.closest && event.target.closest('.doc-body img');
    if (!img) return;
    event.preventDefault();
    openLightbox(img.getAttribute('src'), img.getAttribute('alt'));
  });

  var viewer = document.getElementById('pdfViewer');
  var frame = document.getElementById('pdfViewerFrame');
  var viewerTitle = document.getElementById('pdfViewerTitle');
  var viewerLink = document.getElementById('pdfViewerLink');

  function closePdf() {
    if (!viewer) return;
    viewer.hidden = true;
    if (frame) frame.removeAttribute('src');
    document.body.style.overflow = '';
  }

  document.addEventListener('click', function (event) {
    var trigger = event.target.closest && event.target.closest('[data-pdf-open]');
    if (!trigger) return;
    var url = trigger.getAttribute('data-pdf-url');
    var title = trigger.getAttribute('data-pdf-title') || 'PDF';
    if (!url) return;
    if (!viewer || !frame) {
      window.open(url, '_blank', 'noopener');
      return;
    }
    viewerTitle.textContent = title;
    viewerLink.href = url;
    frame.src = url;
    viewer.hidden = false;
    document.body.style.overflow = 'hidden';
    viewerLink.focus();
  });

  if (viewer) {
    viewer.addEventListener('click', function (event) {
      if (event.target === viewer) closePdf();
    });
    var close = document.getElementById('pdfViewerClose');
    if (close) close.addEventListener('click', closePdf);
  }

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (lightbox && !lightbox.hidden) closeLightbox();
    if (viewer && !viewer.hidden) closePdf();
  });
})();
