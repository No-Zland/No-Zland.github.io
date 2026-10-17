(function () {
  var player = document.getElementById('musicPlayer');
  var audio = document.getElementById('musicAudio');
  if (!player || !audio) return;

  var playlist = Array.isArray(window.MUSIC_PLAYLIST) ? window.MUSIC_PLAYLIST : [];
  var base = window.MUSIC_BASE || '';
  var titleEl = player.querySelector('[data-music-title]');
  var artistEl = player.querySelector('[data-music-artist]');
  var modeEl = player.querySelector('[data-music-mode]');
  var modeBtn = player.querySelector('[data-music-mode-btn]');
  var playBtn = player.querySelector('[data-music-play]');
  var prevBtn = player.querySelector('[data-music-prev]');
  var nextBtn = player.querySelector('[data-music-next]');
  var lyricsBtn = player.querySelector('[data-music-lyrics]');
  var playlistBtn = player.querySelector('[data-music-playlist-btn]');
  var playlistEl = player.querySelector('[data-music-playlist]');
  var seekEl = player.querySelector('[data-music-seek]');
  var timeEl = player.querySelector('[data-music-time]');
  var isSeeking = false;
  var lyricIndex = -1;
  var lyricData = [];
  var lyricPanel = null;
  var currentLang = 'zh';
  var current = 0;
  var mode = 'sequence';
  var MODE_KEY = 'blogMusicMode.v1';

  var TEXT = {
    zh: {
      play: '播放', pause: '暂停', sequence: '顺序', random: '随机', loop: '单曲循环',
      lyrics: '歌词', playlist: '播放歌单', noLyrics: '暂无歌词', lyricsHint: '把 .lrc 放到 music/，并在 playlist.json 里填写 lyrics。',
      empty: '暂无曲目', error: '加载失败', loading: '加载中…', closeLyrics: '关闭歌词', drag: '拖动歌词'
    },
    en: {
      play: 'Play', pause: 'Pause', sequence: 'Sequence', random: 'Shuffle', loop: 'Repeat one',
      lyrics: 'Lyrics', playlist: 'Playlist', noLyrics: 'No lyrics yet', lyricsHint: 'Put an .lrc file in music/ and set its name in playlist.json.',
      empty: 'No tracks', error: 'Failed to load', loading: 'Loading…', closeLyrics: 'Close lyrics', drag: 'Drag lyrics'
    }
  };

  function t(key) {
    return (TEXT[currentLang] || TEXT.zh)[key] || key;
  }

  function resolve(src) {
    if (!src) return '';
    if (/^https?:\/\//i.test(src) || /^data:/i.test(src)) return src;
    return (base ? base.replace(/\/$/, '') + '/' : '') + src;
  }

  function fmt(seconds) {
    if (!isFinite(seconds) || seconds < 0) return '0:00';
    var m = Math.floor(seconds / 60);
    var s = Math.floor(seconds % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function renderPlaylist() {
    if (!playlistEl) return;
    if (!playlist.length) {
      playlistEl.innerHTML = '<div class="music-playlist-empty">' + t('empty') + '</div>';
      return;
    }
    playlistEl.innerHTML = playlist.map(function (entry, index) {
      var active = index === current ? ' is-current' : '';
      return '<button type="button" class="music-playlist-item' + active + '" data-track-index="' + index + '">' +
        '<span class="music-playlist-name">' + escapeHtml(entry.title || ('Track ' + (index + 1))) + '</span>' +
        '<span class="music-playlist-artist">' + escapeHtml(entry.artist || '') + '</span>' +
        '</button>';
    }).join('');
    playlistEl.querySelectorAll('[data-track-index]').forEach(function (item) {
      item.addEventListener('click', function () {
        setTrack(parseInt(item.getAttribute('data-track-index'), 10) || 0, true);
      });
    });
  }

  function updateMode() {
    var key = mode === 'random' ? 'random' : (mode === 'loop' ? 'loop' : 'sequence');
    var symbol = key === 'random' ? '⇄' : (key === 'loop' ? '↻' : '→');
    modeEl.textContent = symbol;
    modeEl.title = t(key);
    modeBtn.textContent = symbol;
    modeBtn.title = t(key);
    modeBtn.setAttribute('aria-label', t('sequence') + ' / ' + t('random') + ' / ' + t('loop'));
    try { localStorage.setItem(MODE_KEY, mode); } catch (e) {}
  }

  function setLyricsPlaceholder() {
    if (!lyricPanel) return;
    var body = lyricPanel.querySelector('[data-lyrics-body]');
    if (!body) return;
    body.innerHTML = '<div class="lyrics-empty">' + t('noLyrics') + '<br>' + t('lyricsHint') + '</div>';
  }

  function parseLrc(text) {
    var lines = [];
    String(text || '').split(/\r?\n/).forEach(function (line) {
      var match = line.match(/^\[(\d{1,2}):(\d{1,2}(?:\.\d+)?)\](.*)$/);
      if (!match) return;
      var body = match[3].trim();
      if (!body) return;
      lines.push({ time: parseInt(match[1], 10) * 60 + parseFloat(match[2]), text: body });
    });
    lines.sort(function (a, b) { return a.time - b.time; });
    return lines;
  }

  function renderLyrics() {
    if (!lyricPanel) return;
    var body = lyricPanel.querySelector('[data-lyrics-body]');
    if (!body) return;
    if (!lyricData.length) {
      setLyricsPlaceholder();
      return;
    }
    body.innerHTML = lyricData.map(function (line, i) {
      return '<div class="lyrics-line" data-lyric-index="' + i + '">' + escapeHtml(line.text) + '</div>';
    }).join('');
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function loadLyrics(entry) {
    lyricData = [];
    lyricIndex = -1;
    if (!entry || !entry.lyrics) {
      renderLyrics();
      return;
    }
    fetch(resolve(entry.lyrics)).then(function (response) {
      if (!response.ok) throw new Error('lyrics');
      return response.text();
    }).then(function (text) {
      lyricData = parseLrc(text);
      renderLyrics();
    }).catch(function () {
      lyricData = [];
      renderLyrics();
    });
  }

  function updateLyrics(time) {
    if (!lyricData.length || !lyricPanel) return;
    var next = -1;
    for (var i = 0; i < lyricData.length; i++) {
      if (lyricData[i].time <= time + 0.15) next = i;
      else break;
    }
    if (next === lyricIndex) return;
    lyricIndex = next;
    var lines = lyricPanel.querySelectorAll('.lyrics-line');
    for (var j = 0; j < lines.length; j++) {
      lines[j].classList.toggle('active', j === lyricIndex);
    }
    var active = lyricPanel.querySelector('.lyrics-line.active');
    if (active && active.scrollIntoView) {
      active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }

  function saveLyricsPosition(panel) {
    try {
      localStorage.setItem('blogLyricsPos.v1', JSON.stringify({
        left: parseInt(panel.style.left, 10),
        top: parseInt(panel.style.top, 10)
      }));
    } catch (e) {}
  }

  function ensureLyricsPanel() {
    if (lyricPanel) return lyricPanel;
    lyricPanel = document.createElement('div');
    lyricPanel.className = 'lyrics-float';
    lyricPanel.hidden = true;
    lyricPanel.innerHTML =
      '<div class="lyrics-head" data-lyrics-drag>' +
        '<span class="lyrics-kicker">' + t('lyrics') + '</span>' +
        '<span class="lyrics-title" data-lyrics-title></span>' +
        '<button type="button" class="lyrics-close" data-lyrics-close aria-label="' + t('closeLyrics') + '">&times;</button>' +
      '</div>' +
      '<div class="lyrics-body" data-lyrics-body></div>';
    document.body.appendChild(lyricPanel);

    var close = lyricPanel.querySelector('[data-lyrics-close]');
    close.addEventListener('click', function () { lyricPanel.hidden = true; });

    var head = lyricPanel.querySelector('[data-lyrics-drag]');
    var drag = null;
    head.addEventListener('pointerdown', function (event) {
      if (event.target.closest('button')) return;
      var rect = lyricPanel.getBoundingClientRect();
      drag = { x: event.clientX - rect.left, y: event.clientY - rect.top };
      head.setPointerCapture(event.pointerId);
      event.preventDefault();
    });
    head.addEventListener('pointermove', function (event) {
      if (!drag) return;
      var width = lyricPanel.offsetWidth;
      var height = lyricPanel.offsetHeight;
      var left = Math.max(8, Math.min(window.innerWidth - width - 8, event.clientX - drag.x));
      var top = Math.max(8, Math.min(window.innerHeight - height - 8, event.clientY - drag.y));
      lyricPanel.style.left = left + 'px';
      lyricPanel.style.top = top + 'px';
      lyricPanel.style.right = 'auto';
      lyricPanel.style.bottom = 'auto';
    });
    head.addEventListener('pointerup', function (event) {
      if (!drag) return;
      drag = null;
      try { head.releasePointerCapture(event.pointerId); } catch (e) {}
      saveLyricsPosition(lyricPanel);
    });
    head.addEventListener('pointercancel', function () { drag = null; });

    try {
      var saved = JSON.parse(localStorage.getItem('blogLyricsPos.v1') || 'null');
      if (saved && isFinite(saved.left) && isFinite(saved.top)) {
        lyricPanel.style.left = Math.max(8, Math.min(window.innerWidth - 300, saved.left)) + 'px';
        lyricPanel.style.top = Math.max(8, Math.min(window.innerHeight - 200, saved.top)) + 'px';
        lyricPanel.style.right = 'auto';
        lyricPanel.style.bottom = 'auto';
      }
    } catch (e) {}
    if (!lyricPanel.style.left) {
      lyricPanel.style.right = '24px';
      lyricPanel.style.bottom = '24px';
    }
    return lyricPanel;
  }

  function toggleLyrics() {
    var panel = ensureLyricsPanel();
    if (!panel.hidden) {
      panel.hidden = true;
      return;
    }
    var entry = playlist[current];
    panel.querySelector('[data-lyrics-title]').textContent = entry ? entry.title : t('empty');
    if (!lyricData.length) setLyricsPlaceholder();
    panel.hidden = false;
    renderLyrics();
  }

  function updateMeta(entry) {
    titleEl.textContent = entry ? entry.title : t('empty');
    artistEl.textContent = entry ? (entry.artist || '—') : '—';
    if (lyricPanel) lyricPanel.querySelector('[data-lyrics-title]').textContent = entry ? entry.title : t('empty');
  }

  function setTrack(nextIndex, autoPlay) {
    if (!playlist.length) {
      player.classList.add('is-empty');
      updateMeta(null);
      playBtn.disabled = true;
      prevBtn.disabled = true;
      nextBtn.disabled = true;
      modeBtn.disabled = true;
      lyricsBtn.disabled = true;
      playlistBtn.disabled = true;
      if (seekEl) seekEl.disabled = true;
      renderPlaylist();
      return;
    }
    player.classList.remove('is-empty');
    playBtn.disabled = false;
    prevBtn.disabled = false;
    nextBtn.disabled = false;
    modeBtn.disabled = false;
    lyricsBtn.disabled = false;
    playlistBtn.disabled = false;
    if (seekEl) seekEl.disabled = false;
    current = (nextIndex + playlist.length) % playlist.length;
    var entry = playlist[current];
    updateMeta(entry);
    renderPlaylist();
    if (seekEl) {
      seekEl.value = '0';
      seekEl.style.setProperty('--music-seek', '0%');
    }
    audio.src = resolve(entry.src);
    audio.load();
    lyricData = [];
    lyricIndex = -1;
    if (lyricPanel) setLyricsPlaceholder();
    loadLyrics(entry);
    if (autoPlay) {
      audio.play().catch(function () {});
    }
  }

  function playPause() {
    if (!playlist.length) return;
    if (audio.paused) {
      audio.play().catch(function () { artistEl.textContent = t('error'); });
    } else {
      audio.pause();
    }
  }

  function nextTrack(manual) {
    if (!playlist.length) return;
    if (mode === 'random' && playlist.length > 1) {
      var next = current;
      while (next === current) next = Math.floor(Math.random() * playlist.length);
      setTrack(next, true);
      return;
    }
    if (current === playlist.length - 1) {
      if (manual) setTrack(0, true);
      else {
        audio.pause();
        audio.currentTime = 0;
      }
      return;
    }
    setTrack(current + 1, true);
  }

  function prevTrack() {
    if (!playlist.length) return;
    if (mode === 'random' && playlist.length > 1) {
      var next = current;
      while (next === current) next = Math.floor(Math.random() * playlist.length);
      setTrack(next, true);
      return;
    }
    setTrack(current - 1, true);
  }

  playBtn.addEventListener('click', playPause);
  nextBtn.addEventListener('click', function () { nextTrack(true); });
  prevBtn.addEventListener('click', prevTrack);
  modeBtn.addEventListener('click', function () {
    mode = mode === 'sequence' ? 'random' : (mode === 'random' ? 'loop' : 'sequence');
    updateMode();
  });
  lyricsBtn.addEventListener('click', toggleLyrics);
  if (playlistBtn && playlistEl) {
    playlistBtn.addEventListener('click', function () {
      playlistEl.hidden = !playlistEl.hidden;
      playlistBtn.setAttribute('aria-expanded', playlistEl.hidden ? 'false' : 'true');
      if (!playlistEl.hidden) renderPlaylist();
    });
  }
  if (seekEl) {
    seekEl.addEventListener('input', function () {
      isSeeking = true;
      var duration = audio.duration || 0;
      if (!duration) return;
      var ratio = Math.max(0, Math.min(1, parseInt(seekEl.value, 10) / 1000));
      audio.currentTime = ratio * duration;
      seekEl.style.setProperty('--music-seek', (ratio * 100) + '%');
      timeEl.textContent = fmt(audio.currentTime);
    });
    seekEl.addEventListener('change', function () { isSeeking = false; });
  }

  audio.addEventListener('play', function () {
    playBtn.textContent = '⏸';
    playBtn.setAttribute('aria-label', t('pause'));
    playBtn.title = t('pause');
  });
  audio.addEventListener('pause', function () {
    playBtn.textContent = '▶';
    playBtn.setAttribute('aria-label', t('play'));
    playBtn.title = t('play');
  });
  audio.addEventListener('timeupdate', function () {
    var duration = audio.duration || 0;
    var ratio = duration ? Math.min(1, audio.currentTime / duration) : 0;
    if (seekEl && !isSeeking) {
      seekEl.value = String(Math.round(ratio * 1000));
      seekEl.style.setProperty('--music-seek', (ratio * 100) + '%');
    }
    timeEl.textContent = fmt(audio.currentTime);
    updateLyrics(audio.currentTime);
  });
  audio.addEventListener('loadedmetadata', function () {
    timeEl.textContent = fmt(audio.currentTime);
    if (seekEl) {
      seekEl.value = String(Math.round((audio.currentTime / (audio.duration || 1)) * 1000));
      seekEl.style.setProperty('--music-seek', '0%');
    }
  });
  audio.addEventListener('ended', function () {
    if (mode === 'loop') {
      audio.currentTime = 0;
      audio.play().catch(function () {});
    } else {
      nextTrack(false);
    }
  });
  audio.addEventListener('error', function () {
    if (playlist[current]) artistEl.textContent = t('error');
  });

  function applyLabels() {
    playBtn.textContent = audio.paused ? '▶' : '⏸';
    playBtn.setAttribute('aria-label', audio.paused ? t('play') : t('pause'));
    playBtn.title = audio.paused ? t('play') : t('pause');
    lyricsBtn.textContent = '♪';
    lyricsBtn.setAttribute('aria-label', t('lyrics'));
    lyricsBtn.title = t('lyrics');
    if (playlistBtn) {
      playlistBtn.textContent = '≡';
      playlistBtn.setAttribute('aria-label', t('playlist'));
      playlistBtn.title = t('playlist');
      playlistBtn.setAttribute('aria-expanded', playlistEl && !playlistEl.hidden ? 'true' : 'false');
    }
    updateMode();
    if (lyricPanel) {
      lyricPanel.querySelector('.lyrics-kicker').textContent = t('lyrics');
      lyricPanel.querySelector('[data-lyrics-close]').setAttribute('aria-label', t('closeLyrics'));
      if (!lyricData.length) setLyricsPlaceholder();
    }
  }

  document.addEventListener('langchange', function (event) {
    currentLang = event.detail && event.detail.lang === 'en' ? 'en' : 'zh';
    applyLabels();
  });

  currentLang = document.documentElement.lang === 'en' ? 'en' : 'zh';
  try { mode = localStorage.getItem(MODE_KEY) || 'sequence'; } catch (e) {}
  if (mode !== 'random' && mode !== 'loop') mode = 'sequence';
  applyLabels();
  if (playlist.length) setTrack(0, false);
  else setTrack(-1, false);
})();
