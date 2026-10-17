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

  function getViewer() {
    return document.getElementById('pdfViewer');
  }

  function closePdf() {
    var viewer = getViewer();
    if (!viewer) return;
    viewer.hidden = true;
    var frame = document.getElementById('pdfViewerFrame');
    if (frame) frame.removeAttribute('src');
    document.body.style.overflow = '';
  }

  function bindViewer(viewer) {
    if (!viewer || viewer.dataset.mediaBound === '1') return;
    viewer.dataset.mediaBound = '1';
    viewer.addEventListener('click', function (event) {
      if (event.target === viewer) closePdf();
    });
    var close = document.getElementById('pdfViewerClose');
    if (close) close.addEventListener('click', closePdf);
  }

  document.addEventListener('click', function (event) {
    var trigger = event.target.closest && event.target.closest('[data-pdf-open]');
    if (!trigger) return;
    var url = trigger.getAttribute('data-pdf-url');
    var title = trigger.getAttribute('data-pdf-title') || 'PDF';
    if (!url) return;
    var viewer = getViewer();
    if (!viewer) {
      window.open(url, '_blank', 'noopener');
      return;
    }
    var frame = document.getElementById('pdfViewerFrame');
    var viewerTitle = document.getElementById('pdfViewerTitle');
    var viewerLink = document.getElementById('pdfViewerLink');
    if (!frame) {
      window.open(url, '_blank', 'noopener');
      return;
    }
    bindViewer(viewer);
    if (viewerTitle) viewerTitle.textContent = title;
    if (viewerLink) viewerLink.href = url;
    frame.src = url;
    viewer.hidden = false;
    document.body.style.overflow = 'hidden';
    if (viewerLink) viewerLink.focus();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (lightbox && !lightbox.hidden) closeLightbox();
    closePdf();
  });
})();
