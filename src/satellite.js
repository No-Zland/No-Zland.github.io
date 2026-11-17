/* 首页知识图谱：canvas 3D，五层结构（板块 → 分类 → 子分类 → 文章）
   板块各自成团、同团同色，几团挤在一起互不重叠；亮色/暗色两套底色都走 CSS 变量。 */
(function () {
  'use strict';

  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

  function hexToRgb(hex) {
    var h = String(hex || '').replace('#', '');
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    if (h.length !== 6) return [120, 140, 200];
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }

  function mixWhite(hex, t) {
    var c = hexToRgb(hex);
    var r = Math.round(c[0] + (255 - c[0]) * t);
    var g = Math.round(c[1] + (255 - c[1]) * t);
    var b = Math.round(c[2] + (255 - c[2]) * t);
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  function mixBlack(hex, t) {
    var c = hexToRgb(hex);
    var r = Math.round(c[0] * (1 - t));
    var g = Math.round(c[1] * (1 - t));
    var b = Math.round(c[2] * (1 - t));
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  function rgba(hex, a) {
    var c = hexToRgb(hex);
    return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a + ')';
  }

  // 从 CSS 变量读色：亮色/暗色两套主题各自定义，canvas 里跟着变
  function readColors(el) {
    var css = window.getComputedStyle(el);
    function v(name, fallback) {
      var raw = (css.getPropertyValue(name) || '').trim();
      return raw || fallback;
    }
    return {
      dark: document.documentElement.getAttribute('data-theme') === 'dark',
      ink: v('--sat-ink', '#1f2430'),
      soft: v('--sat-soft', '#5f6b80'),
      chip: v('--sat-chip', 'rgba(255,255,255,.88)'),
      star: v('--sat-star', 'rgba(31,36,48,.35)'),
      ring: v('--sat-ring', 'rgba(31,36,48,.18)'),
      tipBg: v('--sat-tip-bg', 'rgba(255,255,255,.97)'),
      tipBorder: v('--sat-tip-border', 'rgba(31,36,48,.14)')
    };
  }

  var ISLAND_R = 480;                       // 每个板块中心到原点的距离
  var BASE_R = [0, 0, 168, 286, 398];       // 以板块中心为原点的局部半径
  var DOC_OFFSET = 52;                      // 文章比同类目录再往外一点

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
    var stars = [];

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
        color: parentNode ? parentNode.color : '#5b8def',
        depth: (parentNode ? parentNode.depth : 2) + 1,
        r: 2.2
      });
    }
    for (i = 0; i < nodes.length; i++) nodes[i].idx = i;

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

    // ---------- 布局：每个板块一圈自己的扇形，互不共用中心 ----------
    function placeAround(anchor, angle, rad, dy) {
      return {
        x: anchor.x + Math.cos(angle) * rad,
        y: anchor.y + dy,
        z: anchor.z + Math.sin(angle) * rad
      };
    }

    function layoutBranch(parentIndex, a0, a1, anchor) {
      var kids = childrenOf(parentIndex);
      var total = 0, k;
      for (k = 0; k < kids.length; k++) total += Math.max(1, kids[k].count);
      var cur = a0;
      for (k = 0; k < kids.length; k++) {
        var kid = kids[k];
        var share = (a1 - a0) * (Math.max(1, kid.count) / Math.max(1, total));
        kid.a0 = cur;
        kid.a1 = cur + share;
        kid.angle = (kid.a0 + kid.a1) / 2;
        var rad = BASE_R[Math.min(kid.depth, BASE_R.length - 1)];
        var p = placeAround(anchor, kid.angle, rad, (kid.depth % 2 ? 13 : -9) + (k % 3 - 1) * 5);
        kid.x = p.x; kid.y = p.y; kid.z = p.z;
        kid.r = Math.max(3.6, 8 - kid.depth * 0.45);
        layoutBranch(kid.idx, kid.a0, kid.a1, anchor);
        cur += share;
      }

      var ds = docsOf(parentIndex);
      var pNode = nodes[parentIndex];
      var baseRad = BASE_R[Math.min(pNode.depth + 1, BASE_R.length - 1)] + DOC_OFFSET;
      for (k = 0; k < ds.length; k++) {
        var dn = ds[k];
        var span = Math.max(0.05, a1 - a0);
        var ang = (a0 + a1) / 2 + (((k + 0.5) / Math.max(1, ds.length)) - 0.5) * span * 0.92;
        var rr = baseRad + (k % 4) * 11;
        var q = placeAround(anchor, ang, rr, ((k % 3) - 1) * 12);
        dn.x = q.x; dn.y = q.y; dn.z = q.z;
      }
    }

    var secIndexes = [];
    for (i = 0; i < nodes.length; i++) if (nodes[i].kind === 'section') secIndexes.push(i);
    var secCount = Math.max(1, secIndexes.length);
    for (i = 0; i < secIndexes.length; i++) {
      var sec = nodes[secIndexes[i]];
      var baseAngle = ((i + 0.5) / secCount) * Math.PI * 2 - Math.PI / 2;
      var anchor = {
        x: Math.cos(baseAngle) * ISLAND_R,
        y: Math.sin(i * 1.7) * 190,
        z: Math.sin(baseAngle) * ISLAND_R
      };
      sec.x = anchor.x; sec.y = anchor.y; sec.z = anchor.z;
      sec.angle = baseAngle;
      sec.r = 11;
      var half = (Math.PI / secCount) * 0.84;
      layoutBranch(secIndexes[i], baseAngle - half, baseAngle + half, anchor);
    }

    // ---------- 团簇布局：每团按自身大小摊成一个圆盘，五团紧贴成「汇聚但相斥」的一坨星云 ----------
    function bubbleLayout() {
      var n = nodes.length;
      var owner = new Int32Array(n);
      var ci, cj, k, q;
      for (ci = 0; ci < secIndexes.length; ci++) {
        var stack = [secIndexes[ci]];
        while (stack.length) {
          var cur = stack.pop();
          owner[cur] = ci;
          for (q = 0; q < n; q++) if (nodes[q].parentIndex === cur) stack.push(q);
        }
      }

      var members = [];
      for (ci = 0; ci < secIndexes.length; ci++) members.push([]);
      for (k = 0; k < n; k++) members[owner[k]].push(k);

      var R = [];
      for (ci = 0; ci < members.length; ci++) {
        R.push(14 + 16 * Math.sqrt(Math.max(1, members[ci].length)));
      }

      // 先大后小，逐个贴着已有的团摆，找一个离中心最近的空位
      var centers = [];
      for (ci = 0; ci < members.length; ci++) centers.push(null);
      var placed = [];
      var order = [];
      for (ci = 0; ci < members.length; ci++) order.push(ci);
      order.sort(function (a, b) { return R[b] - R[a]; });

      for (var oi = 0; oi < order.length; oi++) {
        var idx = order[oi];
        if (!placed.length) {
          centers[idx] = { x: 0, y: 0 };
          placed.push(idx);
          continue;
        }
        var bestT = 1e9, bestA = 0;
        for (var ai = 0; ai < 128; ai++) {
          var ang = (ai / 128) * Math.PI * 2;
          var ux = Math.cos(ang), uy = Math.sin(ang);
          var t = 0;
          for (var pj = 0; pj < placed.length; pj++) {
            var p = centers[placed[pj]];
            var proj = p.x * ux + p.y * uy;
            var perp2 = p.x * p.x + p.y * p.y - proj * proj;
            var rr = R[placed[pj]] + R[idx] + 18;
            var disc = rr * rr - perp2;
            if (disc <= 0) continue;
            var tt = proj + Math.sqrt(disc);
            if (tt > t) t = tt;
          }
          if (t < bestT) { bestT = t; bestA = ang; }
        }
        centers[idx] = { x: Math.cos(bestA) * bestT, y: Math.sin(bestA) * bestT };
        placed.push(idx);
      }

      // 团内：父节点靠中心，文章往外撒，黄金角排均匀
      var GOLD = 2.399963229728653;
      for (ci = 0; ci < members.length; ci++) {
        var list = members[ci].slice();
        list.sort(function (a, b) {
          var da = nodes[a].kind === 'section' ? 0 : nodes[a].depth;
          var db = nodes[b].kind === 'section' ? 0 : nodes[b].depth;
          if (da !== db) return da - db;
          return a - b;
        });
        var c = centers[ci];
        for (var ii = 0; ii < list.length; ii++) {
          var nd = nodes[list[ii]];
          if (nd.kind === 'section') {
            nd.x = c.x; nd.y = c.y; nd.z = 0;
            nd.bubbleR = R[ci];
            continue;
          }
          var rel = (ii + 0.5) / list.length;
          var rad = R[ci] * Math.sqrt(rel);
          var aa = ii * GOLD;
          nd.x = c.x + Math.cos(aa) * rad;
          nd.y = c.y + Math.sin(aa) * rad;
          nd.z = (((ii * 37) % 9) - 4) * 3;
        }
      }

      // 整体居中
      var ox = 0, oy = 0, oz = 0;
      for (k = 0; k < n; k++) { ox += nodes[k].x / n; oy += nodes[k].y / n; oz += nodes[k].z / n; }
      for (k = 0; k < n; k++) { nodes[k].x -= ox; nodes[k].y -= oy; nodes[k].z -= oz; }
    }

    bubbleLayout();
    var homeCenter = { x: 0, y: 0, z: 0 };

    var selected = null;
    var focusPos = { x: homeCenter.x, y: homeCenter.y, z: homeCenter.z };

    var yaw = 0.0, pitch = -0.34, dist = 1500, fitDist = 1500, vYaw = 0, vPitch = 0;
    var focal = 640, hover = null, dragging = false;
    var lastX = 0, lastY = 0, moved = 0, downAt = 0, idleAt = 0;
    var raf = 0, lastT = 0, slow = false;
    var pointers = {}, pinch = 0;
    var panX = 0, panY = 0, mode = 'rotate';
    var introAt = (window.performance && performance.now ? performance.now() : Date.now());
    var screen = [];

    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var colorCache = null, colorAt = 0, fontFamily = 'sans-serif';

    function buildStars() {
      stars = [];
      var seed = 20261117;
      function rnd() {
        seed = (seed * 1664525 + 1013904223) % 4294967296;
        return seed / 4294967296;
      }
      var n = Math.round(clamp((w * h) / 7600, 40, 220));
      for (var k = 0; k < n; k++) {
        stars.push({
          x: rnd() * w,
          y: rnd() * h,
          r: 0.4 + rnd() * 1.3,
          a: 0.12 + rnd() * 0.5,
          p: rnd() * Math.PI * 2
        });
      }
    }

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth || 600;
      h = canvas.clientHeight || 520;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      focal = Math.min(w, h) * 1.02;
      buildStars();
      fitView(w < 560 ? 34 : 70);
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

    // 量一遍当前视角下所有节点的屏幕范围，用来把整张图装进画布
    function measureBounds() {
      var cy = Math.cos(yaw), sy = Math.sin(yaw);
      var cp = Math.cos(pitch), sp = Math.sin(pitch);
      var minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
      var showDocs = dist < 2000;
      for (var k = 0; k < nodes.length; k++) {
        var nd = nodes[k];
        if (nd.kind === 'doc' && !showDocs) continue;
        var wx = nd.x - focusPos.x, wy = nd.y - focusPos.y, wz = nd.z - focusPos.z;
        var x1 = wx * cy - wz * sy;
        var z1 = wx * sy + wz * cy;
        var y1 = wy * cp - z1 * sp;
        var z2 = wy * sp + z1 * cp;
        var depth = dist - z2;
        if (depth < 80) continue;
        var s = focal / depth;
        if (x1 * s < minX) minX = x1 * s;
        if (x1 * s > maxX) maxX = x1 * s;
        if (y1 * s < minY) minY = y1 * s;
        if (y1 * s > maxY) maxY = y1 * s;
      }
      if (minX > maxX) return null;
      return { minX: minX, maxX: maxX, minY: minY, maxY: maxY };
    }

    // 把整团的「主轴」转到水平，宽画布能装得更满
    function alignYaw() {
      var cnt = nodes.length;
      if (!cnt) return;
      var sx = 0, sz = 0, sxx = 0, szz = 0, sxz = 0;
      for (var k = 0; k < cnt; k++) {
        var nd = nodes[k];
        sx += nd.x; sz += nd.z;
        sxx += nd.x * nd.x; szz += nd.z * nd.z; sxz += nd.x * nd.z;
      }
      var mx = sx / cnt, mz = sz / cnt;
      var vxx = sxx / cnt - mx * mx;
      var vzz = szz / cnt - mz * mz;
      var vxz = sxz / cnt - mx * mz;
      yaw = -0.5 * Math.atan2(2 * vxz, vxx - vzz);
    }

    function fitView(pad) {
      if (!w || !h) return;
      panX = 0;
      panY = 0;
      for (var pass = 0; pass < 4; pass++) {
        var b = measureBounds();
        if (!b) return;
        var bw = Math.max(1, b.maxX - b.minX);
        var bh = Math.max(1, b.maxY - b.minY);
        var fit = Math.min((w - pad * 2) / bw, (h - pad * 2) / bh);
        if (!isFinite(fit) || fit <= 0) return;
        if (Math.abs(Math.log(fit)) < 0.02) break;
        dist = clamp(dist / fit, 460, 4200);
      }
      fitDist = dist;
      var b2 = measureBounds();
      if (b2) {
        panX = -(b2.minX + b2.maxX) / 2;
        panY = -(b2.minY + b2.maxY) / 2;
      }
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
        var z2 = wy * sp + z1 * cp;
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

    function drawStars(cl) {
      var t = (window.performance && performance.now ? performance.now() : Date.now()) / 1000;
      for (var k = 0; k < stars.length; k++) {
        var st = stars[k];
        var a = st.a * (0.55 + 0.45 * Math.sin(t * 0.6 + st.p)) * (cl.dark ? 1 : 0.55);
        if (a <= 0.02) continue;
        ctx.globalAlpha = a;
        ctx.fillStyle = cl.star;
        ctx.beginPath();
        ctx.arc(st.x, st.y, st.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

    function drawIslandGlow(cl) {
      var strong = cl.dark ? 0.20 : 0.11;
      var mid = cl.dark ? 0.07 : 0.04;
      for (var k = 0; k < screen.length; k++) {
        var it = screen[k];
        if (it.node.kind !== 'section') continue;
        var rad = clamp(300 * it.s, 90, 460);
        var g = ctx.createRadialGradient(it.x, it.y, 0, it.x, it.y, rad);
        g.addColorStop(0, rgba(it.node.color, strong));
        g.addColorStop(0.55, rgba(it.node.color, mid));
        g.addColorStop(1, rgba(it.node.color, 0));
        ctx.fillStyle = g;
        ctx.globalAlpha = 1;
        ctx.beginPath();
        ctx.arc(it.x, it.y, rad, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // 板块之间连一圈虚线：读起来是一个知识体系，而不是五个孤岛
    function drawIslandRing(cl) {
      var secs = [];
      for (var k = 0; k < screen.length; k++) if (screen[k].node.kind === 'section') secs.push(screen[k]);
      if (secs.length < 3) return;
      secs.sort(function (a, b) { return a.node.angle - b.node.angle; });
      ctx.globalAlpha = 0.30;
      ctx.strokeStyle = cl.ring;
      ctx.lineWidth = 1;
      if (ctx.setLineDash) ctx.setLineDash([3, 7]);
      ctx.beginPath();
      for (var i = 0; i < secs.length; i++) {
        var A = secs[i], B = secs[(i + 1) % secs.length];
        ctx.moveTo(A.x, A.y);
        ctx.lineTo(B.x, B.y);
      }
      ctx.stroke();
      if (ctx.setLineDash) ctx.setLineDash([]);
      ctx.globalAlpha = 1;
    }

    function drawLinks(showDeep) {
      for (var i = 0; i < screen.length; i++) {
        var it = screen[i];
        var nd = it.node;
        if (nd.kind === 'section') continue;
        var parent = null;
        if (nd.kind === 'doc') {
          if (!showDeep) continue;
          parent = findScreen(nodes[nd.parentIndex]);
          if (!parent) continue;
          ctx.globalAlpha = 0.30;
          ctx.lineWidth = 1;
        } else {
          parent = nd.parentIndex >= 0 ? findScreen(nodes[nd.parentIndex]) : null;
          if (!parent) continue;
          ctx.globalAlpha = nd.depth === 2 ? 0.55 : 0.36;
          ctx.lineWidth = nd.depth === 2 ? 1.6 : 1.1;
        }
        ctx.strokeStyle = nd.color;
        ctx.beginPath();
        ctx.moveTo(parent.x, parent.y);
        ctx.lineTo(it.x, it.y);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }

    function showDeepNow() { return dist < 1500; }

    // 悬停时只提亮「这一支 + 它的上游」，其余压暗
    function dimmed(n2) {
      if (!hover) return false;
      if (hover.node === n2) return false;
      if (hover.node.kind === 'section') return n2.kind !== 'section' && n2.parentIndex !== hover.node.idx;
      var cur = hover.node;
      var guard = 0;
      while (cur && guard++ < 12) {
        if (cur === n2) return false;
        cur = cur.parentIndex >= 0 ? nodes[cur.parentIndex] : null;
      }
      return n2.parentIndex !== hover.node.idx;
    }

    function drawNodes(cl) {
      var showDeep = showDeepNow();
      for (var i = 0; i < screen.length; i++) {
        var s0 = screen[i];
        var n2 = s0.node;
        if (!showDeep && n2.kind === 'doc' && !(hover && hover.node === n2)) continue;
        var fade = clamp(s0.s * 2.2, 0.22, 1);
        var isHover = hover && hover.node === n2;
        var isSel = selected === n2;
        var dim = dimmed(n2);
        ctx.globalAlpha = (n2.kind === 'doc' ? fade * 0.95 : fade) * (dim ? 0.16 : 1);
        ctx.shadowColor = n2.color;
        ctx.shadowBlur = isHover ? 16 : (n2.kind === 'section' ? 22 : 8);
        ctx.beginPath();
        ctx.arc(s0.x, s0.y, isHover ? s0.r * 2.1 : (dim ? s0.r * 0.85 : s0.r), 0, Math.PI * 2);
        ctx.fillStyle = (n2.kind === 'section' && cl.dark) ? mixWhite(n2.color, 0.22) : n2.color;
        ctx.fill();
        ctx.shadowBlur = 0;
        if (isSel) {
          ctx.globalAlpha = 0.9 * (dim ? 0.4 : 1);
          ctx.strokeStyle = cl.dark ? mixWhite(n2.color, 0.55) : mixBlack(n2.color, 0.22);
          ctx.lineWidth = 1.6;
          ctx.beginPath();
          ctx.arc(s0.x, s0.y, s0.r + 7, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
      ctx.globalAlpha = 1;
    }

    function drawTooltip(item, cl) {
      var title = item.node.label || '';
      var tags = item.node.tags || [];
      var tagLine = tags.length ? tags.join(' · ') : (item.node.crumb || '');
      var pad = 10;
      ctx.font = '600 13px ' + fontFamily;
      var tw = ctx.measureText(title).width;
      ctx.font = '500 11px ' + fontFamily;
      var gw = tagLine ? ctx.measureText(tagLine).width : 0;
      var boxW = Math.max(tw, gw) + pad * 2;
      var boxH = tagLine ? 46 : 30;
      var bx = clamp(item.x + 14, 6, Math.max(6, w - boxW - 6));
      var by = clamp(item.y - 16, 6, Math.max(6, h - boxH - 6));
      ctx.globalAlpha = 1;
      roundRect(bx, by, boxW, boxH, 9);
      ctx.fillStyle = cl.tipBg;
      ctx.fill();
      ctx.strokeStyle = cl.tipBorder;
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = cl.ink;
      ctx.font = '600 13px ' + fontFamily;
      ctx.fillText(title, bx + pad, by + 15);
      if (tagLine) {
        ctx.fillStyle = cl.soft;
        ctx.font = '500 11px ' + fontFamily;
        ctx.fillText(tagLine, bx + pad, by + 33);
      }
    }

    function drawLabels(cl) {
      var labels = [];
      var i, j;
      for (i = 0; i < screen.length; i++) {
        var c = screen[i];
        if (c.node.kind === 'doc') continue;
        if (c.s < 0.1) continue;
        if (c.node.depth >= 3) continue;
        if (c.node.depth === 2 && !(hover && owner[c.node.idx] === owner[hover.node.idx]) && dist > fitDist * 0.78) continue;
        if (hover && dimmed(c.node)) continue;
        var dx = c.x - w / 2, dy = c.y - h / 2;
        var dl = Math.sqrt(dx * dx + dy * dy) || 1;
        var lx, ly;
        if (c.node.depth === 1) {
          lx = c.x;
          ly = c.y - ((c.node.bubbleR || 40) * c.s + 20);
        } else {
          lx = c.x + dx / dl * (c.r + 14);
          ly = c.y + dy / dl * (c.r + 14);
        }
        labels.push({
          node: c.node, x0: c.x, y0: c.y, lx: lx, ly: ly,
          alpha: clamp(c.s * 2.4, 0.4, 1),
          w: ctx.measureText(c.node.label).width,
          h: 16,
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
          for (j = 0; j < boxes.length; j++) {
            var B = boxes[j];
            if (Math.abs(L.lx - B.x) < (L.w + B.w) / 2 + 6 &&
                Math.abs(L.ly - B.y) < (L.h + B.h) / 2 + 3) {
              L.ly += L.h + 4;
              overlaps = true;
            }
          }
        }
        boxes.push({ x: L.lx, y: L.ly, w: L.w, h: L.h });
        ctx.font = (L.big ? '700 13px ' : '600 11.5px ') + fontFamily;
        L.w = ctx.measureText(L.node.label).width;
        ctx.globalAlpha = L.alpha * 0.35;
        ctx.strokeStyle = cl.dark ? mixWhite(L.node.color, 0.3) : mixBlack(L.node.color, 0.2);
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(L.x0, L.y0);
        ctx.lineTo(L.lx, L.ly);
        ctx.stroke();
        ctx.globalAlpha = L.alpha * (cl.dark ? 0.9 : 0.92);
        ctx.fillStyle = cl.chip;
        roundRect(L.lx - L.w / 2 - 7, L.ly - 10, L.w + 14, 21, 7);
        ctx.fill();
        ctx.globalAlpha = L.alpha;
        ctx.fillStyle = cl.dark
          ? mixWhite(L.node.color, L.big ? 0.62 : 0.5)
          : mixBlack(L.node.color, L.big ? 0.28 : 0.16);
        ctx.fillText(L.node.label, L.lx, L.ly);
      }
      ctx.globalAlpha = 1;
    }

    function draw() {
      var cl = readColorsCached();
      ctx.clearRect(0, 0, w, h);
      drawStars(cl);
      screen = project();
      drawIslandGlow(cl);
      drawIslandRing(cl);
      drawLinks(showDeepNow());
      drawNodes(cl);
      drawLabels(cl);
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
      selected = node;
      focusPos = { x: node.x, y: node.y, z: node.z };
      slow = true;
      idleAt = Date.now();
    }

    function clearFocus() {
      selected = null;
      focusPos = { x: homeCenter.x, y: homeCenter.y, z: homeCenter.z };
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
        if (pinch) dist = clamp(dist * (pinch / Math.max(d, 1)), 460, 4000);
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

      if (hit) {
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
      clearFocus();
    }

    function onLeave() {
      hover = null;
      dragging = false;
      pointers = {};
    }

    function onWheel(e) {
      e.preventDefault();
      dist = clamp(dist * Math.pow(1.0018, e.deltaY), 460, 4000);
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
        if (h2) {
          openNode(h2.node);
          openedAt = Date.now();
          return;
        }
      }
      yaw = 0.0; pitch = -0.34; dist = 1500;
      panX = 0; panY = 0;
      vYaw = vPitch = 0;
      clearFocus();
      fitView(70);
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
          if (act === 'in') dist = clamp(dist * 0.82, 460, 4000);
          else if (act === 'out') dist = clamp(dist / 0.82, 460, 4000);
          else onReset();
          idleAt = Date.now();
          slow = true;
        });
      })(zoomBtns[zb]);
    }

    resize();
    alignYaw();
    fitView(w < 560 ? 34 : 70);
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
