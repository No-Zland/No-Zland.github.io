/* 首页知识卫星图：canvas 3D，可拖动旋转、滚轮缩放、点击进入文章 */
(function () {
  'use strict';

  var current = null;

  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

  function fibDir(i, n) {
    var y = 1 - (i + 0.5) * 2 / n;
    var r = Math.sqrt(Math.max(0, 1 - y * y));
    var phi = i * Math.PI * (3 - Math.sqrt(5));
    return [Math.cos(phi) * r, y, Math.sin(phi) * r];
  }

  function cross(a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  }

  function norm(v) {
    var l = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) || 1;
    return [v[0] / l, v[1] / l, v[2] / l];
  }

  function basis(d) {
    var axis = Math.abs(d[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
    var e1 = norm(cross(axis, d));
    var e2 = cross(d, e1);
    return [e1, e2];
  }

  function readColors(canvas) {
    var css = window.getComputedStyle(canvas);
    return {
      bg: (css.getPropertyValue('--bg') || '#ffffff').trim(),
      text: (css.getPropertyValue('--text') || '#1f2430').trim(),
      soft: (css.getPropertyValue('--text-soft') || '#6b7280').trim(),
      border: (css.getPropertyValue('--border') || '#e8e9f0').trim()
    };
  }

  function start(root, canvas) {
    var dataEl = root.querySelector('.sat-data');
    if (!dataEl) return null;
    var data;
    try { data = JSON.parse(dataEl.textContent || dataEl.innerText || ''); } catch (e) { return null; }
    if (!data || !data.cats || !data.docs) return null;

    var ctx = canvas.getContext('2d');
    var cats = data.cats;
    var nodes = [];
    var w = 0, h = 0, dpr = 1;

    // ---- 布局：中心是「我」，两侧各一个星系（知识库 / 实战库），分类绕星系，文章绕分类 ----
    var secs = data.sections || [{ name: '知识库', color: '#2563eb' }];
    var GALAXY_R = 300, CAT_R = 126, DOC_R0 = 70, DOC_R1 = 168;
    var secPos = [];
    for (var s = 0; s < secs.length; s++) {
      var ga = Math.PI * s;                    // 两个星系分居左右
      secPos.push([Math.cos(ga) * GALAXY_R, 0, Math.sin(ga) * GALAXY_R]);
    }

    var maxCount = 1;
    var i;
    for (i = 0; i < cats.length; i++) maxCount = Math.max(maxCount, cats[i].count || 1);

    var catPos = [];
    for (i = 0; i < cats.length; i++) {
      var d = fibDir(i, cats.length);
      var base = secPos[cats[i].sec || 0] || [0, 0, 0];
      catPos.push([
        base[0] + d[0] * CAT_R,
        base[1] + d[1] * CAT_R,
        base[2] + d[2] * CAT_R
      ]);
      nodes.push({
        kind: 'cat', x: catPos[i][0], y: catPos[i][1], z: catPos[i][2],
        r: 6, color: cats[i].color,
        label: cats[i].name + ' ' + cats[i].count,
        name: cats[i].name, ci: i
      });
    }

    var dirs = [], bases = [];
    for (i = 0; i < cats.length; i++) { dirs.push(fibDir(i, cats.length)); bases.push(basis(dirs[i])); }
    var seen = {};
    for (i = 0; i < data.docs.length; i++) {
      var rec = data.docs[i];
      var ci = rec[2] || 0;
      var total = cats[ci] ? cats[ci].count : 1;
      var k = seen[ci] || 0;
      seen[ci] = k + 1;
      var t = (k + 0.5) / Math.max(1, total);
      var ang = k * 2.399963 + ci * 0.7;
      var capA = 0.45 + 0.35 * Math.sqrt(total / maxCount);
      var cosT = 1 - t * (1 - Math.cos(capA));
      var sinT = Math.sqrt(Math.max(0, 1 - cosT * cosT));
      var b = bases[ci % bases.length] || [[1, 0, 0], [0, 0, 1]];
      var dd = dirs[ci % dirs.length] || [0, 0, 1];
      var rad = DOC_R0 + (DOC_R1 - DOC_R0) * t;
      var nx = cosT * dd[0] + sinT * (Math.cos(ang) * b[0][0] + Math.sin(ang) * b[1][0]);
      var ny = cosT * dd[1] + sinT * (Math.cos(ang) * b[0][1] + Math.sin(ang) * b[1][1]);
      var nz = cosT * dd[2] + sinT * (Math.cos(ang) * b[0][2] + Math.sin(ang) * b[1][2]);
      var origin = catPos[ci] || [0, 0, 0];
      nodes.push({
        kind: 'doc',
        x: origin[0] + nx * rad,
        y: origin[1] + ny * rad,
        z: origin[2] + nz * rad,
        r: 2.2, color: cats[ci] ? cats[ci].color : '#2563eb',
        label: rec[0], url: rec[1], ci: ci, tags: rec[3] || [], crumb: rec[4] || ''
      });
    }

    for (i = 0; i < secs.length; i++) {
      nodes.push({
        kind: 'galaxy', x: secPos[i][0], y: secPos[i][1], z: secPos[i][2],
        r: 11, color: secs[i].color, label: secs[i].name, name: secs[i].name, si: i
      });
    }
    nodes.push({ kind: 'hub', x: 0, y: 0, z: 0, r: 14, color: '#f59e0b', label: '', name: 'me' });

    var yaw = 0.0, pitch = 0.34, dist = 980, vYaw = 0, vPitch = 0;
    var focal = 640, hover = null, dragging = false;
    var lastX = 0, lastY = 0, moved = 0, downAt = 0, idleAt = 0;
    var raf = 0, lastT = 0, slow = false;
    var pointers = {}, pinch = 0;
    var panX = 0, panY = 0, mode = 'rotate';
    var screen = [];

    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var colorCache = null, colorAt = 0, fontFamily = 'sans-serif';

    function colors() {
      var now = Date.now();
      if (!colorCache || now - colorAt > 600) {
        colorCache = readColors(canvas);
        colorAt = now;
        fontFamily = window.getComputedStyle(document.body).fontFamily || 'sans-serif';
      }
      return colorCache;
    }

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth || 600;
      h = canvas.clientHeight || 520;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      focal = Math.min(w, h) * 0.95;
    }

    function project() {
      var cy = Math.cos(yaw), sy = Math.sin(yaw);
      var cp = Math.cos(pitch), sp = Math.sin(pitch);
      var cx = w / 2, cyy = h / 2;
      var out = [];
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        var x1 = n.x * cy - n.z * sy;
        var z1 = n.x * sy + n.z * cy;
        var y1 = n.y * cp - z1 * sp;
        var z2 = n.y * sp + z1 * cp;
        var depth = dist - z2;
        if (depth < 80) continue;
        var s = focal / depth;
        out.push({
          node: n, x: cx + x1 * s + panX, y: cyy + y1 * s + panY, s: s, depth: depth,
          r: clamp(n.r * s * 2.8, 1.4, 17)
        });
      }
      out.sort(function (a, b) { return b.depth - a.depth; });
      return out;
    }

    function roundRect(x, y, rw, rh, rad) {
      ctx.beginPath();
      ctx.moveTo(x + rad, y);
      ctx.arcTo(x + rw, y, x + rw, y + rh, rad);
      ctx.arcTo(x + rw, y + rh, x, y + rh, rad);
      ctx.arcTo(x, y + rh, x, y, rad);
      ctx.arcTo(x, y, x + rw, y, rad);
      ctx.closePath();
    }

    function drawTooltip(item, colors) {
      var title = item.node.label || '';
      var tags = item.node.tags || [];
      var tagLine = tags.length ? tags.join(' · ') : (item.node.crumb || '');
      var pad = 9;

      ctx.font = '600 13px ' + fontFamily;
      var tw = ctx.measureText(title).width;
      ctx.font = '500 11px ' + fontFamily;
      var gw = tagLine ? ctx.measureText(tagLine).width : 0;
      var boxW = Math.max(tw, gw) + pad * 2;
      var boxH = tagLine ? 44 : 28;

      var bx = clamp(item.x + 14, 6, Math.max(6, w - boxW - 6));
      var by = clamp(item.y - 16, 6, Math.max(6, h - boxH - 6));

      ctx.globalAlpha = 1;
      roundRect(bx, by, boxW, boxH, 8);
      ctx.fillStyle = colors.bg;
      ctx.fill();
      ctx.strokeStyle = colors.border;
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = colors.text;
      ctx.font = '600 13px ' + fontFamily;
      ctx.fillText(title, bx + pad, by + 14);

      if (tagLine) {
        ctx.fillStyle = colors.soft;
        ctx.font = '500 11px ' + fontFamily;
        ctx.fillText(tagLine, bx + pad, by + 32);
      }
    }

    function drawRays(colors) {
      var t = (window.performance && performance.now ? performance.now() : Date.now()) / 1000;
      var cx = w / 2, cy = h / 2;
      var span = Math.max(w, h) * 0.62;

      // 中心光晕
      var halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, span * 0.55);
      halo.addColorStop(0, 'rgba(124,58,237,0.16)');
      halo.addColorStop(0.45, 'rgba(37,99,235,0.07)');
      halo.addColorStop(1, 'rgba(37,99,235,0)');
      ctx.globalAlpha = 1;
      ctx.fillStyle = halo;
      ctx.fillRect(0, 0, w, h);

      // 缓慢旋转的光芒
      ctx.save();
      ctx.translate(cx, cy);
      ctx.globalCompositeOperation = 'lighter';
      var N = 54;
      for (var i = 0; i < N; i++) {
        var a = t * 0.05 + i * Math.PI * 2 / N;
        var len = span * (i % 5 === 0 ? 1.0 : 0.62);
        var g = ctx.createLinearGradient(0, 0, Math.cos(a) * len, Math.sin(a) * len);
        g.addColorStop(0, i % 2 ? 'rgba(37,99,235,0.10)' : 'rgba(124,58,237,0.10)');
        g.addColorStop(0.55, i % 2 ? 'rgba(37,99,235,0.03)' : 'rgba(124,58,237,0.03)');
        g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.strokeStyle = g;
        ctx.lineWidth = i % 5 === 0 ? 2.2 : 1;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a) * 16, Math.sin(a) * 16);
        ctx.lineTo(Math.cos(a) * len, Math.sin(a) * len);
        ctx.stroke();
      }
      ctx.restore();
      ctx.globalCompositeOperation = 'source-over';
    }

    function draw() {
      var colors = colorCache || readColors(canvas);
      ctx.clearRect(0, 0, w, h);
      drawRays(colors);
      screen = project();

      var hub = null;
      for (var i = 0; i < screen.length; i++) if (screen[i].node.kind === 'hub') hub = screen[i];

      // 我 -> 星系 -> 分类 的连线
      ctx.lineWidth = 1;
      for (i = 0; i < screen.length; i++) {
        var it = screen[i];
        if (!hub) break;
        if (it.node.kind === 'galaxy') {
          ctx.globalAlpha = 0.35;
          ctx.strokeStyle = it.node.color;
          ctx.beginPath();
          ctx.moveTo(hub.x, hub.y);
          ctx.lineTo(it.x, it.y);
          ctx.stroke();
        } else if (it.node.kind === 'cat') {
          var gp = null;
          for (var k = 0; k < screen.length; k++) {
            if (screen[k].node.kind === 'galaxy' && screen[k].node.si === (cats[it.node.ci] || {}).sec) {
              gp = screen[k];
              break;
            }
          }
          if (!gp) continue;
          ctx.globalAlpha = 0.14;
          ctx.strokeStyle = it.node.color;
          ctx.beginPath();
          ctx.moveTo(gp.x, gp.y);
          ctx.lineTo(it.x, it.y);
          ctx.stroke();
        }
      }

      for (i = 0; i < screen.length; i++) {
        var s0 = screen[i];
        var n = s0.node;
        var fade = clamp(s0.s * 2.2, 0.22, 1);
        var isHover = hover && hover.node === n;
        ctx.globalAlpha = n.kind === 'doc' ? fade * 0.85 : fade;

        if (n.kind === 'galaxy' || n.kind === 'hub') {
          ctx.shadowColor = n.color;
          ctx.shadowBlur = n.kind === 'hub' ? 26 : 18;
        } else {
          ctx.shadowBlur = 0;
        }

        ctx.beginPath();
        ctx.arc(s0.x, s0.y, isHover ? s0.r * 1.8 : s0.r, 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.fill();
        ctx.shadowBlur = 0;

        if (n.kind === 'hub') {
          ctx.globalAlpha = 0.9;
          ctx.strokeStyle = n.color;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(s0.x, s0.y, s0.r + 6, 0, Math.PI * 2);
          ctx.stroke();
        }
      }

      // 星系名字（知识库 / 实战库）
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = '700 13px ' + fontFamily;
      for (i = 0; i < screen.length; i++) {
        var g0 = screen[i];
        if (g0.node.kind !== 'galaxy') continue;
        ctx.globalAlpha = clamp(g0.s * 2.6, 0.5, 1);
        ctx.lineWidth = 4;
        ctx.strokeStyle = colors.bg;
        var sgn = g0.x >= w / 2 ? 1 : -1;
        ctx.textAlign = sgn > 0 ? 'left' : 'right';
        var lx = g0.x + sgn * (g0.r + 10);
        var ly = g0.y - g0.r - 10;
        ctx.strokeText(g0.node.label, lx, ly);
        ctx.fillStyle = g0.node.color;
        ctx.fillText(g0.node.label, lx, ly);
        ctx.textAlign = 'center';
      }

      // 分类标签最后画，并做一次简单的避让（重叠就往下错位）
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = '600 11.5px ' + fontFamily;
      var labels = [];
      for (i = 0; i < screen.length; i++) {
        var c = screen[i];
        if (c.node.kind !== 'cat' || c.s < 0.12) continue;
        var dx = c.x - w / 2, dy = c.y - h / 2;
        var dl = Math.sqrt(dx * dx + dy * dy) || 1;
        var lx = c.x + dx / dl * (c.r + 9);
        var ly = c.y + dy / dl * (c.r + 9);
        // 别压在中心的“知识库”上：离中心太近就沿径向外推
        var cx0 = lx - w / 2, cy0 = ly - h / 2;
        var cd = Math.sqrt(cx0 * cx0 + cy0 * cy0);
        if (cd < 118) {
          var scale = 118 / (cd || 1);
          lx = w / 2 + cx0 * scale;
          ly = h / 2 + cy0 * scale;
        }
        labels.push({
          node: c.node,
          alpha: clamp(c.s * 2.4, 0.35, 1),
          lx: lx,
          ly: ly,
          w: ctx.measureText(c.node.label).width,
          h: 15
        });
      }
      labels.sort(function (a, b) { return a.ly - b.ly || a.lx - b.lx; });
      var boxes = [];
      for (i = 0; i < labels.length; i++) {
        var L = labels[i];
        var guard = 0;
        var overlaps = true;
        while (overlaps && guard++ < 6) {
          overlaps = false;
          for (var j = 0; j < boxes.length; j++) {
            var B = boxes[j];
            if (Math.abs(L.lx - B.x) < (L.w + B.w) / 2 + 4 &&
                Math.abs(L.ly - B.y) < (L.h + B.h) / 2 + 2) {
              L.ly += L.h + 3;
              overlaps = true;
            }
          }
        }
        boxes.push({ x: L.lx, y: L.ly, w: L.w, h: L.h });
        ctx.globalAlpha = L.alpha;
        ctx.lineWidth = 4;
        ctx.strokeStyle = colors.bg;
        ctx.strokeText(L.node.label, L.lx, L.ly);
        ctx.fillStyle = L.node.color;
        ctx.fillText(L.node.label, L.lx, L.ly);
      }

      if (hover) drawTooltip(hover, colors);
      ctx.globalAlpha = 1;
    }

    function frame(t) {
      raf = window.requestAnimationFrame(frame);
      if (!canvas.isConnected) { stop(); return; }
      var dt = Math.min(48, t - (lastT || t));
      lastT = t;

      if (!dragging) {
        yaw += vYaw;
        pitch = clamp(pitch + vPitch, -1.2, 1.2);
        vYaw *= 0.93;
        vPitch *= 0.93;
        if (!reduced && !slow && t - idleAt > 2200) yaw += 0.00002 * dt;
      }
      draw();
    }

    function stop() {
      if (raf) window.cancelAnimationFrame(raf);
      raf = 0;
    }

    function destroy() {
      stop();
      canvas.removeEventListener('pointerdown', onDown);
      canvas.removeEventListener('pointermove', onMove);
      canvas.removeEventListener('pointerup', onUp);
      canvas.removeEventListener('pointercancel', onUp);
      canvas.removeEventListener('pointerleave', onLeave);
      canvas.removeEventListener('wheel', onWheel);
      canvas.removeEventListener('dblclick', onReset);
      window.removeEventListener('resize', resize);
    }

    function pick(x, y) {
      var best = null, bestD = 1e9;
      for (var i = 0; i < screen.length; i++) {
        var it = screen[i];
        var dx = it.x - x, dy = it.y - y;
        var d = Math.sqrt(dx * dx + dy * dy);
        var lim = Math.max(12, it.r + 9);
        if (d < lim && d < bestD) { bestD = d; best = it; }
      }
      return best;
    }

    function localXY(e) {
      var rect = canvas.getBoundingClientRect();
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    }

    function onDown(e) {
      var p = localXY(e);
      pointers[e.pointerId] = p;
      dragging = true;
      slow = true;
      moved = 0;
      downAt = Date.now();
      lastX = p.x; lastY = p.y;
      vYaw = vPitch = 0;
      mode = (e.button === 2 || e.shiftKey || e.button === 1) ? 'pan' : 'rotate';
      canvas.setPointerCapture && canvas.setPointerCapture(e.pointerId);
      canvas.style.cursor = 'grabbing';
    }

    function onMove(e) {
      var p = localXY(e);
      if (pointers[e.pointerId]) pointers[e.pointerId] = p;

      var ids = Object.keys(pointers);
      if (ids.length === 2) {
        var a = pointers[ids[0]], b = pointers[ids[1]];
        var d = Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
        if (pinch) dist = clamp(dist * (pinch / Math.max(d, 1)), 430, 2600);
        pinch = d;
        panX += (a.x + b.x) / 2 - lastX;
        panY += (a.y + b.y) / 2 - lastY;
        lastX = (a.x + b.x) / 2;
        lastY = (a.y + b.y) / 2;
        return;
      }

      if (dragging) {
        var dx = p.x - lastX, dy = p.y - lastY;
        moved += Math.abs(dx) + Math.abs(dy);
        if (mode === 'pan') {
          panX += dx;
          panY += dy;
          panX = clamp(panX, -w * 0.8, w * 0.8);
          panY = clamp(panY, -h * 0.8, h * 0.8);
        } else {
          yaw += dx * 0.007;
          pitch = clamp(pitch + dy * 0.007, -1.2, 1.2);
          vYaw = dx * 0.0016;
          vPitch = dy * 0.0016;
        }
        lastX = p.x; lastY = p.y;
        idleAt = Date.now();
        return;
      }

      var hit = pick(p.x, p.y);
      hover = hit;
      canvas.style.cursor = hit ? 'pointer' : 'grab';
    }

    function onUp(e) {
      delete pointers[e.pointerId];
      if (Object.keys(pointers).length < 2) pinch = 0;
      var wasPan = mode === 'pan';
      dragging = false;
      mode = 'rotate';
      canvas.style.cursor = 'grab';
      idleAt = Date.now();

      var p;
      try { p = localXY(e); } catch (err) { return; }
      if (!wasPan && moved < 9 && Date.now() - downAt < 600) {
        var hit = pick(p.x, p.y);
        if (hit && hit.node.kind === 'doc' && hit.node.url) open(hit.node.url);
        else if (hit && hit.node.kind === 'cat') open(catUrl(hit.node.ci));
        else if (hit && hit.node.kind === 'galaxy') open(secUrl(hit.node.si));
      }
    }

    function onLeave() {
      hover = null;
      dragging = false;
      pointers = {};
    }

    function onWheel(e) {
      e.preventDefault();
      dist = clamp(dist * Math.pow(1.0018, e.deltaY), 430, 2400);
      idleAt = Date.now();
      slow = true;
    }

    function onReset() {
      yaw = 0.0; pitch = 0.34; dist = 980;
      panX = 0; panY = 0;
      vYaw = vPitch = 0;
    }

    function catUrl(ci) {
      var cat = cats[ci];
      return cat && cat.rel ? cat.rel : null;
    }

    function secUrl(si) {
      var s = secs[si];
      return s && s.rel ? s.rel : null;
    }

    function open(url) {
      if (!url) return;
      var a = document.createElement('a');
      a.href = url;
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }

    canvas.addEventListener('pointerdown', onDown);
    canvas.addEventListener('pointermove', onMove);
    canvas.addEventListener('pointerup', onUp);
    canvas.addEventListener('pointercancel', onUp);
    canvas.addEventListener('pointerleave', onLeave);
    canvas.addEventListener('wheel', onWheel, { passive: false });
    canvas.addEventListener('dblclick', onReset);
    canvas.addEventListener('contextmenu', function (e) { e.preventDefault(); });
    window.addEventListener('resize', resize);

    resize();
    idleAt = Date.now();
    raf = window.requestAnimationFrame(frame);

    return { destroy: destroy, resize: resize };
  }

  function init() {
    if (current && current.destroy) current.destroy();
    current = null;
    var root = document.querySelector('.satellite');
    if (!root) return;
    var canvas = root.querySelector('.sat-canvas');
    if (!canvas || !canvas.getContext) return;
    current = start(root, canvas);
  }

  window.BlogSatellite = { init: init };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
