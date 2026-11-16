/* 首页知识卫星图：canvas 3D，五层结构（我 → 板块 → 分类 → 子分类 → 文章） */
(function () {
  'use strict';

  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

  function readColors(canvas) {
    var css = window.getComputedStyle(canvas);
    return {
      bg: (css.getPropertyValue('--bg') || '#ffffff').trim(),
      text: (css.getPropertyValue('--text') || '#1f2430').trim(),
      soft: (css.getPropertyValue('--text-soft') || '#6b7280').trim(),
      border: (css.getPropertyValue('--border') || '#e8e9f0').trim()
    };
  }

  var RADII = [0, 290, 450, 610, 760];

  function start(root, canvas) {
    var dataEl = root.querySelector('.sat-data');
    if (!dataEl) return null;
    var data;
    try { data = JSON.parse(dataEl.textContent || dataEl.innerText || ''); } catch (e) { return null; }
    if (!data || !data.nodes) return null;

    var ctx = canvas.getContext('2d');
    var rawNodes = data.nodes || [];
    var rawDocs = data.docs || [];

    var w = 0, h = 0, dpr = 1;
    var nodes = [];
    var hubNode = null;

    // ---------- 建树 ----------
    var i;
    for (i = 0; i < rawNodes.length; i++) {
      var rn = rawNodes[i];
      var shortName = rn.name.length > 12 ? rn.name.slice(0, 12) + '…' : rn.name;
      nodes.push({
        kind: rn.depth === 1 ? 'section' : 'dir',
        name: rn.name,
        label: rn.depth === 1
          ? rn.name + (rn.count ? ' ' + rn.count : '')
          : shortName + (rn.count ? ' ' + rn.count : ''),
        color: rn.color,
        depth: rn.depth,
        parentIndex: rn.parent,
        rel: rn.rel || '',
        count: rn.count || 0
      });
    }
    for (i = 0; i < rawDocs.length; i++) {
      var rec = rawDocs[i];
      var pi = rec[2];
      var parentNode = nodes[pi];
      nodes.push({
        kind: 'doc',
        label: rec[0],
        url: rec[1],
        parentIndex: pi,
        tags: rec[3] || [],
        crumb: rec[4] || '',
        color: parentNode ? parentNode.color : '#2563eb',
        depth: (parentNode ? parentNode.depth : 2) + 1,
        r: 2.2
      });
    }

    function place(nd) {
      var rad = RADII[Math.min(nd.depth, RADII.length - 1)] || 260;
      nd.x = Math.cos(nd.angle) * rad;
      nd.z = Math.sin(nd.angle) * rad;
      nd.y = ((nd.depth % 2) ? 1 : -1) * (nd.depth * 6);
      nd.r = nd.kind === 'section' ? 11 : Math.max(3.4, 7.5 - nd.depth);
    }

    function childrenOf(index) {
      var out = [];
      for (var k = 0; k < nodes.length; k++) {
        if (nodes[k].kind === 'dir' && nodes[k].parentIndex === index) out.push(nodes[k]);
      }
      out.sort(function (a, b) { return b.count - a.count; });
      return out;
    }

    function docsOf(index) {
      var out = [];
      for (var k = 0; k < nodes.length; k++) {
        if (nodes[k].kind === 'doc' && nodes[k].parentIndex === index) out.push(nodes[k]);
      }
      return out;
    }

    function layoutChildren(parentIndex, a0, a1) {
      var kids = childrenOf(parentIndex);
      var total = 0, k;
      for (k = 0; k < kids.length; k++) total += Math.max(1, kids[k].count);
      var cur = a0;
      for (k = 0; k < kids.length; k++) {
        var share = (a1 - a0) * (Math.max(1, kids[k].count) / Math.max(1, total));
        kids[k].a0 = cur;
        kids[k].a1 = cur + share;
        kids[k].angle = (kids[k].a0 + kids[k].a1) / 2;
        place(kids[k]);
        layoutChildren(nodes.indexOf(kids[k]), kids[k].a0, kids[k].a1);
        cur += share;
      }
      var ds = docsOf(parentIndex);
      var parentDepth = parentIndex >= 0 ? nodes[parentIndex].depth : 1;
      var baseR = RADII[Math.min(parentDepth, RADII.length - 1)] || 250;
      for (k = 0; k < ds.length; k++) {
        var dn = ds[k];
        var span = Math.max(0.05, a1 - a0);
        var ang = (a0 + a1) / 2 + (((k + 0.5) / Math.max(1, ds.length)) - 0.5) * span * 0.9;
        var rr = baseR + 42 + (k % 4) * 11;
        dn.x = Math.cos(ang) * rr;
        dn.z = Math.sin(ang) * rr;
        dn.y = ((k % 3) - 1) * 14;
      }
    }

    var secIndexes = [];
    for (i = 0; i < nodes.length; i++) if (nodes[i].kind === 'section') secIndexes.push(i);
    var secSpan = (Math.PI * 2) / Math.max(1, secIndexes.length);
    for (i = 0; i < secIndexes.length; i++) {
      var sec = nodes[secIndexes[i]];
      sec.a0 = i * secSpan + 0.12;
      sec.a1 = (i + 1) * secSpan - 0.12;
      sec.angle = (sec.a0 + sec.a1) / 2;
      place(sec);
      layoutChildren(secIndexes[i], sec.a0, sec.a1);
    }

    nodes.push({ kind: 'hub', x: 0, y: 0, z: 0, r: 14, color: '#f59e0b', label: '' });
    hubNode = nodes[nodes.length - 1];

    var selected = null;
    var focusPos = { x: 0, y: 0, z: 0 };

    var yaw = 0.0, pitch = 0.34, dist = 1350, vYaw = 0, vPitch = 0;
    var focal = 640, hover = null, dragging = false;
    var lastX = 0, lastY = 0, moved = 0, downAt = 0, idleAt = 0;
    var raf = 0, lastT = 0, slow = false;
    var pointers = {}, pinch = 0;
    var panX = 0, panY = 0, mode = 'rotate';
    var introAt = (window.performance && performance.now ? performance.now() : Date.now());
    var screen = [];

    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var colorCache = null, colorAt = 0, fontFamily = 'sans-serif';

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth || 600;
      h = canvas.clientHeight || 520;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      focal = Math.min(w, h) * 0.95;
    }

    function readColorsCached() {
      var now = Date.now();
      if (!colorCache || now - colorAt > 600) {
        colorCache = readColors(canvas);
        colorAt = now;
        fontFamily = window.getComputedStyle(document.body).fontFamily || 'sans-serif';
      }
      return colorCache;
    }

    function project() {
      var cy = Math.cos(yaw), sy = Math.sin(yaw);
      var cp = Math.cos(pitch), sp = Math.sin(pitch);
      var cx = w / 2, cyy = h / 2;
      var out = [];
      var nowT = (window.performance && performance.now ? performance.now() : Date.now());
      var prog = clamp((nowT - introAt) / 900, 0, 1);
      var ease = 1 - Math.pow(1 - prog, 3);
      for (var k = 0; k < nodes.length; k++) {
        var nd = nodes[k];
        var wx = nd.x - focusPos.x, wy = nd.y - focusPos.y, wz = nd.z - focusPos.z;
        var x1 = wx * cy - wz * sy;
        var z1 = wx * sy + wz * cy;
        var y1 = wy * cp - z1 * sp;
        var z2 = nd.y * sp + z1 * cp;
        var depth = dist - z2;
        if (depth < 80) continue;
        var s = focal / depth;
        var px = cx + x1 * s + panX;
        var py = cyy + y1 * s + panY;
        px = cx + (px - cx) * ease;
        py = cyy + (py - cyy) * ease;
        out.push({
          node: nd, x: px, y: py, s: s, depth: depth,
          r: clamp(nd.r * s * 2.8, 1.4, 17) * (0.4 + 0.6 * ease)
        });
      }
      out.sort(function (a, b) { return b.depth - a.depth; });
      return out;
    }

    function findScreen(node) {
      for (var k = 0; k < screen.length; k++) if (screen[k].node === node) return screen[k];
      return null;
    }

    function roundRect(x, y, rw, rh, rad) {
      ctx.beginPath();
      ctx.moveTo(x + rad, y);
      ctx.arcTo(x + rw, y, x + rw, y + rh, rad);
      ctx.arcTo(x + rw, y + rh, x, y + rh, rad);
      ctx.arcTo(x, y + rh, x, y, rad);
      ctx.closePath();
    }

    function drawTooltip(item, cl) {
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
      ctx.fillStyle = cl.bg;
      ctx.fill();
      ctx.strokeStyle = cl.border;
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = cl.text;
      ctx.font = '600 13px ' + fontFamily;
      ctx.fillText(title, bx + pad, by + 14);
      if (tagLine) {
        ctx.fillStyle = cl.soft;
        ctx.font = '500 11px ' + fontFamily;
        ctx.fillText(tagLine, bx + pad, by + 32);
      }
    }

    function drawRays() {
      var t = (window.performance && performance.now ? performance.now() : Date.now()) / 1000;
      var cx = w / 2, cy = h / 2;
      var span = Math.max(w, h) * 0.62;
      var halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, span * 0.55);
      halo.addColorStop(0, 'rgba(124,58,237,0.14)');
      halo.addColorStop(0.45, 'rgba(37,99,235,0.06)');
      halo.addColorStop(1, 'rgba(37,99,235,0)');
      ctx.globalAlpha = 1;
      ctx.fillStyle = halo;
      ctx.fillRect(0, 0, w, h);
      ctx.save();
      ctx.translate(cx, cy);
      ctx.globalCompositeOperation = 'lighter';
      var N = 54;
      for (var i = 0; i < N; i++) {
        var a = t * 0.05 + i * Math.PI * 2 / N;
        var len = span * (i % 5 === 0 ? 1.0 : 0.62);
        var g = ctx.createLinearGradient(0, 0, Math.cos(a) * len, Math.sin(a) * len);
        g.addColorStop(0, i % 2 ? 'rgba(37,99,235,0.09)' : 'rgba(124,58,237,0.09)');
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

    function drawRings(cl) {
      var cx = w / 2, cy = h / 2;
      var cyw = Math.cos(yaw), syw = Math.sin(yaw);
      var cp = Math.cos(pitch), sp = Math.sin(pitch);
      var radii = [250, 380, 500, 600];
      for (var r = 0; r < radii.length; r++) {
        ctx.beginPath();
        var started = false;
        for (var k = 0; k <= 72; k++) {
          var a = k / 72 * Math.PI * 2;
          var wx = Math.cos(a) * radii[r], wz = Math.sin(a) * radii[r];
          var x1 = wx * cyw - wz * syw;
          var z1 = wx * syw + wz * cyw;
          var y1 = -z1 * sp;
          var z2 = z1 * cp;
          var depth = dist - z2;
          if (depth < 80) { started = false; continue; }
          var s = focal / depth;
          var px = cx + x1 * s + panX, py = cy + y1 * s + panY;
          if (!started) { ctx.moveTo(px, py); started = true; } else { ctx.lineTo(px, py); }
        }
        ctx.globalAlpha = 0.07;
        ctx.strokeStyle = cl.soft;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }

    function draw() {
      var cl = readColorsCached();
      ctx.clearRect(0, 0, w, h);
      drawRays();
      drawRings(cl);
      screen = project();

      var showDeep = dist < 1500;
      var hub = null;
      for (var i = 0; i < screen.length; i++) if (screen[i].node.kind === 'hub') hub = screen[i];

      // 连线：每个节点连到父节点
      for (i = 0; i < screen.length; i++) {
        var it = screen[i];
        var nd = it.node;
        if (nd.kind === 'hub') continue;
        var parent = null;
        if (nd.kind === 'section') {
          parent = hub;
        } else if (nd.kind === 'doc') {
          if (!showDeep) continue;
          parent = findScreen(nodes[nd.parentIndex]);
        } else {
          parent = nd.parentIndex >= 0 ? findScreen(nodes[nd.parentIndex]) : hub;
        }
        if (!parent) continue;
        if (nd.kind === 'doc') {
          ctx.globalAlpha = 0.16;
          ctx.lineWidth = 1;
        } else if (nd.depth === 1) {
          ctx.globalAlpha = 0.55;
          ctx.lineWidth = 2;
        } else {
          ctx.globalAlpha = nd.depth === 2 ? 0.42 : 0.28;
          ctx.lineWidth = nd.depth === 2 ? 1.6 : 1.1;
        }
        ctx.strokeStyle = nd.depth === 1 ? '#f59e0b' : nd.color;
        ctx.beginPath();
        ctx.moveTo(parent.x, parent.y);
        ctx.lineTo(it.x, it.y);
        ctx.stroke();
      }

      // 节点
      for (i = 0; i < screen.length; i++) {
        var s0 = screen[i];
        var n2 = s0.node;
        if (!showDeep && n2.kind === 'doc' && !(hover && hover.node === n2)) continue;
        var fade = clamp(s0.s * 2.2, 0.22, 1);
        var isHover = hover && hover.node === n2;
        var focusGroup = hover && hover.node.kind !== 'hub' ? hover.node.parentIndex : -2;
        var dim = focusGroup >= -1 && n2.parentIndex !== focusGroup && n2.kind !== 'section' && n2.kind !== 'hub';
        ctx.globalAlpha = (n2.kind === 'doc' ? fade * 0.9 : fade) * (dim ? 0.2 : 1);
        if (n2.kind === 'doc') {
          ctx.shadowColor = n2.color;
          ctx.shadowBlur = isHover ? 16 : 7;
        } else {
          ctx.shadowBlur = 0;
        }
        ctx.beginPath();
        ctx.arc(s0.x, s0.y, isHover ? s0.r * 2.1 : (dim ? s0.r * 0.85 : s0.r), 0, Math.PI * 2);
        ctx.fillStyle = n2.color;
        ctx.fill();
        ctx.shadowBlur = 0;
        if (n2.kind === 'hub') {
          ctx.globalAlpha = 0.9;
          ctx.strokeStyle = n2.color;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(s0.x, s0.y, s0.r + 6, 0, Math.PI * 2);
          ctx.stroke();
        }
      }

      // 标签
      var labels = [];
      for (i = 0; i < screen.length; i++) {
        var c = screen[i];
        if (c.node.kind === 'hub' || c.node.kind === 'doc') continue;
        if (c.s < 0.1) continue;
        if (c.node.depth >= 3) continue;
        if (c.node.depth === 2 && dist > 1900) continue;
        var dx = c.x - w / 2, dy = c.y - h / 2;
        var dl = Math.sqrt(dx * dx + dy * dy) || 1;
        var lx = c.x + dx / dl * (c.r + 14);
        var ly = c.y + dy / dl * (c.r + 14);
        labels.push({
          node: c.node, x0: c.x, y0: c.y, lx: lx, ly: ly,
          alpha: clamp(c.s * 2.4, 0.35, 1),
          w: ctx.measureText(c.node.label).width,
          h: 15,
          big: c.node.depth === 1
        });
      }
      labels.sort(function (a, b) { return a.ly - b.ly || a.lx - b.lx; });
      var boxes = [];
      for (i = 0; i < labels.length; i++) {
        var L = labels[i];
        var guard = 0, overlaps = true;
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
        ctx.font = (L.big ? '700 13px ' : '600 11.5px ') + fontFamily;
        L.w = ctx.measureText(L.node.label).width;
        ctx.globalAlpha = L.alpha * 0.3;
        ctx.strokeStyle = L.node.color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(L.x0, L.y0);
        ctx.lineTo(L.lx, L.ly);
        ctx.stroke();
        ctx.globalAlpha = L.alpha * 0.82;
        ctx.fillStyle = cl.bg;
        roundRect(L.lx - L.w / 2 - 5, L.ly - 10, L.w + 10, 20, 6);
        ctx.fill();
        ctx.globalAlpha = L.alpha;
        ctx.fillStyle = L.node.color;
        ctx.fillText(L.node.label, L.lx, L.ly);
      }

      if (hover) drawTooltip(hover, cl);
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
        if (!reduced && !slow && !hover && t - idleAt > 2200) yaw += 0.00002 * dt;
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
      for (var k = 0; k < screen.length; k++) {
        var it = screen[k];
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

    function setFocus(node) {
      if (!hubNode || node.kind === 'hub') return;
      selected = node;
      focusPos = { x: node.x, y: node.y, z: node.z };
      hubNode.x = node.x; hubNode.y = node.y; hubNode.z = node.z;
      hubNode.color = node.color;
      hubNode.r = 13;
      slow = true;
      idleAt = Date.now();
    }

    function clearFocus() {
      selected = null;
      focusPos = { x: 0, y: 0, z: 0 };
      if (hubNode) {
        hubNode.x = 0; hubNode.y = 0; hubNode.z = 0;
        hubNode.color = '#f59e0b';
        hubNode.r = 14;
      }
      idleAt = Date.now();
    }

    function openNode(node) {
      var url = node.kind === 'doc' ? node.url : node.rel;
      if (!url) return;
      var a = document.createElement('a');
      a.href = url;
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
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
        if (pinch) dist = clamp(dist * (pinch / Math.max(d, 1)), 620, 3600);
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
          panX = clamp(panX + dx, -w * 2.5, w * 2.5);
          panY = clamp(panY + dy, -h * 2.5, h * 2.5);
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

    var lastClickAt = 0, openedAt = 0;

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
      if (wasPan || moved >= 9 || Date.now() - downAt >= 600) return;

      var hit = pick(p.x, p.y);
      var now = Date.now();
      var quick = now - lastClickAt < 650;

      if (hit && hit.node.kind !== 'hub') {
        if (selected === hit.node && quick) {
          openNode(hit.node);
          openedAt = now;
          return;
        }
        setFocus(hit.node);
        lastClickAt = now;
        return;
      }
      if (selected && quick) {
        openNode(selected);
        openedAt = now;
        return;
      }
      if (hit && hit.node.kind === 'hub') return;
      clearFocus();
    }

    function onLeave() {
      hover = null;
      dragging = false;
      pointers = {};
    }

    function onWheel(e) {
      e.preventDefault();
      dist = clamp(dist * Math.pow(1.0018, e.deltaY), 620, 3600);
      idleAt = Date.now();
      slow = true;
    }

    function onReset(e) {
      if (Date.now() - openedAt < 500) return;
      if (selected) {
        openNode(selected);
        openedAt = Date.now();
        return;
      }
      if (e && e.clientX !== undefined) {
        var lp = localXY(e);
        var h2 = pick(lp.x, lp.y);
        if (h2 && h2.node.kind !== 'hub') {
          openNode(h2.node);
          openedAt = Date.now();
          return;
        }
      }
      yaw = 0.0; pitch = 0.34; dist = 1350;
      panX = 0; panY = 0;
      vYaw = vPitch = 0;
      clearFocus();
    }

    canvas.addEventListener('pointerdown', onDown);
    canvas.addEventListener('pointermove', onMove);
    canvas.addEventListener('pointerup', onUp);
    canvas.addEventListener('pointercancel', onUp);
    canvas.addEventListener('pointerleave', onLeave);
    canvas.addEventListener('wheel', onWheel, { passive: false });
    canvas.addEventListener('dblclick', onReset);
    canvas.addEventListener('contextmenu', function (e) { e.preventDefault(); });

    var zoomBtns = root.querySelectorAll('[data-sat-zoom]');
    for (var zb = 0; zb < zoomBtns.length; zb++) {
      (function (btn) {
        btn.addEventListener('click', function () {
          var act = btn.getAttribute('data-sat-zoom');
          if (act === 'in') dist = clamp(dist * 0.82, 620, 3600);
          else if (act === 'out') dist = clamp(dist / 0.82, 620, 3600);
          else onReset();
          idleAt = Date.now();
          slow = true;
        });
      })(zoomBtns[zb]);
    }

    resize();
    window.addEventListener('resize', resize);
    raf = window.requestAnimationFrame(frame);

    return { destroy: destroy };
  }

  var instances = [];

  function init() {
    for (var k = 0; k < instances.length; k++) {
      try { instances[k].destroy(); } catch (e) {}
    }
    instances = [];
    var roots = document.querySelectorAll('.satellite');
    for (var i = 0; i < roots.length; i++) {
      var canvas = roots[i].querySelector('.sat-canvas');
      if (!canvas) continue;
      var inst = start(roots[i], canvas);
      if (inst) instances.push(inst);
    }
  }

  window.BlogSatellite = { init: init };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
