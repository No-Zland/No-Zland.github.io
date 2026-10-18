(function () {
  var calendarEl = document.getElementById('calendar');
  if (!calendarEl) return;

  var TASK_KEY = 'blogCalendarTasks.v1';
  var AUTH_KEY = 'blogCalendarAuth.v1';
  var MASTER_KEY = 'blogCalendarMaster.v1';
  var UPDATES = window.BLOG_UPDATES || {};
  var TOTAL_UPDATE_DAYS = Object.keys(UPDATES).length;
  var MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  var I18N = {
    zh: {
      'cal-kicker': '更新日历 · 任务',
      'cal-today': '今天',
      'cal-prev': '上个月',
      'cal-next': '下个月',
      'cal-stats': '本月更新 {days} 天 · {posts} 篇 · 累计 {total} 天',
      'cal-no-updates': '本月暂无更新记录',
      'cal-legend-update': '绿色 = 博客更新',
      'cal-legend-task': '圆点 = 有任务',
      'cal-day-label': '{date} · {posts} 篇更新 · {tasks} 个任务',
      'tasks-title': '{date} · 任务',
      'tasks-hint': '到点提醒 · 保持页面打开',
      'task-placeholder': '写一个任务…',
      'task-time': '提醒时间',
      'task-add': '添加任务',
      'task-empty': '这天还没有任务',
      'task-done': '已完成',
      'task-due': '已到时间',
      'task-remaining': '还有',
      'task-delete': '删除任务',
      'task-reminder': '任务提醒',
      'task-many': '{n} 个任务到时间了',
      'task-need-title': '先写任务内容',
      'task-need-time': '请选择提醒时间',
      'task-close': '关闭提醒',
      'mode-visitor': '访客模式',
      'mode-master': '主人模式',
      'mode-setup': '设置主人密码',
      'mode-login': '主人登录',
      'mode-logout': '退出主人',
      'mode-export': '导出备份',
      'mode-import': '导入备份',
      'mode-note-visitor': '任务清单仅主人可见；访客可以查看更新日历。',
      'mode-note-master': '任务保存在本浏览器，请定期导出备份。',
      'auth-title-setup': '设置主人密码',
      'auth-title-login': '主人登录',
      'auth-note': '密码只保存在本机浏览器，用于隐藏任务界面，不是数据加密。忘记密码只能清除站点数据或导入备份。',
      'auth-pass': '密码（至少 6 位）',
      'auth-confirm': '再输一次',
      'auth-cancel': '取消',
      'auth-submit': '确认',
      'auth-short': '密码至少 6 位',
      'auth-mismatch': '两次输入不一致',
      'auth-wrong': '密码不正确',
      'auth-unsupported': '当前环境不支持安全哈希，请用 HTTPS 或 localhost 打开',
      'auth-saved': '已进入主人模式',
      'auth-logout': '已退出主人模式',
      'import-ok': '任务已导入',
      'import-bad': '备份文件格式不正确',
      'day-unit': '天',
      weekdays: ['一', '二', '三', '四', '五', '六', '日']
    },
    en: {
      'cal-kicker': 'Update calendar · Tasks',
      'cal-today': 'Today',
      'cal-prev': 'Previous month',
      'cal-next': 'Next month',
      'cal-stats': 'This month: {days} days · {posts} posts · {total} days total',
      'cal-no-updates': 'No blog updates this month',
      'cal-legend-update': 'Green = blog updates',
      'cal-legend-task': 'Dot = tasks',
      'cal-day-label': '{date} · {posts} posts · {tasks} tasks',
      'tasks-title': 'Tasks · {date}',
      'tasks-hint': 'Reminders need this page open',
      'task-placeholder': 'Add a task…',
      'task-time': 'Reminder time',
      'task-add': 'Add task',
      'task-empty': 'No tasks for this day',
      'task-done': 'Done',
      'task-due': 'Due now',
      'task-remaining': 'in',
      'task-delete': 'Delete task',
      'task-reminder': 'Task reminder',
      'task-many': '{n} tasks are due',
      'task-need-title': 'Write the task first',
      'task-need-time': 'Choose a reminder time',
      'task-close': 'Dismiss reminder',
      'mode-visitor': 'Visitor mode',
      'mode-master': 'Owner mode',
      'mode-setup': 'Set owner password',
      'mode-login': 'Owner login',
      'mode-logout': 'Log out',
      'mode-export': 'Export backup',
      'mode-import': 'Import backup',
      'mode-note-visitor': 'Tasks are visible to the owner only. Visitors can still see the update calendar.',
      'mode-note-master': 'Tasks are stored in this browser. Export a backup regularly.',
      'auth-title-setup': 'Set owner password',
      'auth-title-login': 'Owner login',
      'auth-note': 'The password is stored in this browser to hide the task UI. It does not encrypt the data. If you forget it, clear site data or import a backup.',
      'auth-pass': 'Password (at least 6 characters)',
      'auth-confirm': 'Repeat password',
      'auth-cancel': 'Cancel',
      'auth-submit': 'Confirm',
      'auth-short': 'Use at least 6 characters',
      'auth-mismatch': 'Passwords do not match',
      'auth-wrong': 'Wrong password',
      'auth-unsupported': 'Secure hashing is unavailable. Open via HTTPS or localhost.',
      'auth-saved': 'Owner mode unlocked',
      'auth-logout': 'Owner mode locked',
      'import-ok': 'Tasks imported',
      'import-bad': 'Invalid backup file',
      'day-unit': 'd',
      weekdays: ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    }
  };

  var currentLang = 'zh';
  var toastTimer = null;
  var state = {
    view: new Date(),
    selected: '',
    tasks: [],
    auth: null,
    master: false,
    ready: false
  };

  function t(key) {
    var dict = I18N[currentLang] || I18N.zh;
    return dict[key] != null ? dict[key] : key;
  }

  function setLang(lang) {
    currentLang = lang === 'en' ? 'en' : 'zh';
  }

  function pad(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function fmtDate(d) {
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }

  function parseDate(s) {
    var a = s.split('-');
    return new Date(parseInt(a[0], 10), parseInt(a[1], 10) - 1, parseInt(a[2], 10));
  }

  function todayKey() {
    return fmtDate(new Date());
  }

  function monthLabel(d) {
    if (currentLang === 'en') return MONTHS_EN[d.getMonth()] + ' ' + d.getFullYear();
    return d.getFullYear() + '年' + (d.getMonth() + 1) + '月';
  }

  function shortDateLabel(key) {
    var d = parseDate(key);
    if (currentLang === 'en') return MONTHS_EN[d.getMonth()] + ' ' + d.getDate();
    return (d.getMonth() + 1) + '月' + d.getDate() + '日';
  }

  function fullDateLabel(key) {
    var d = parseDate(key);
    if (currentLang === 'en') {
      return MONTHS_EN[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
    }
    return d.getFullYear() + '年' + (d.getMonth() + 1) + '月' + d.getDate() + '日';
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function updateCount(key) {
    return UPDATES[key] || 0;
  }

  function updateLevel(n) {
    if (n <= 0) return 0;
    if (n <= 1) return 1;
    if (n <= 3) return 2;
    if (n <= 9) return 3;
    return 4;
  }

  function taskCount(key) {
    return state.tasks.filter(function (task) {
      return task.date === key && !task.done;
    }).length;
  }

  function taskDateTime(task) {
    var d = parseDate(task.date);
    var a = (task.time || '00:00').split(':');
    d.setHours(parseInt(a[0], 10) || 0, parseInt(a[1], 10) || 0, 0, 0);
    return d;
  }

  function formatDuration(ms) {
    var total = Math.floor(ms / 1000);
    var days = Math.floor(total / 86400);
    total -= days * 86400;
    var h = Math.floor(total / 3600);
    total -= h * 3600;
    var m = Math.floor(total / 60);
    var s = total - m * 60;
    var clock = pad(h) + ':' + pad(m) + ':' + pad(s);
    return days > 0 ? days + t('day-unit') + ' ' + clock : clock;
  }

  function countdownText(task) {
    if (task.done) return t('task-done');
    var ms = taskDateTime(task).getTime() - Date.now();
    if (ms <= 0) return t('task-due');
    return t('task-remaining') + ' ' + formatDuration(ms);
  }

  function newId() {
    return 't' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  }

  function normalizeTasks(raw) {
    if (!Array.isArray(raw)) return [];
    return raw.filter(function (x) {
      return x && typeof x.title === 'string' &&
        /^\d{4}-\d{2}-\d{2}$/.test(x.date) &&
        /^\d{2}:\d{2}$/.test(x.time);
    }).map(function (x) {
      return {
        id: String(x.id || newId()),
        date: x.date,
        time: x.time,
        title: String(x.title).slice(0, 80),
        done: !!x.done,
        notified: !!x.notified
      };
    });
  }

  function loadTasks() {
    try {
      return normalizeTasks(JSON.parse(localStorage.getItem(TASK_KEY) || '[]'));
    } catch (e) {
      return [];
    }
  }

  function saveTasks() {
    try {
      localStorage.setItem(TASK_KEY, JSON.stringify(state.tasks));
    } catch (e) {}
  }

  function loadAuth() {
    try {
      var raw = JSON.parse(localStorage.getItem(AUTH_KEY) || 'null');
      if (!raw || typeof raw.salt !== 'string' || typeof raw.hash !== 'string') return null;
      return { salt: raw.salt, hash: raw.hash, iter: parseInt(raw.iter, 10) || 120000 };
    } catch (e) {
      return null;
    }
  }

  function saveAuth(auth) {
    localStorage.setItem(AUTH_KEY, JSON.stringify(auth));
  }

  function bytesToB64(bytes) {
    var out = '';
    for (var i = 0; i < bytes.length; i++) out += String.fromCharCode(bytes[i]);
    return btoa(out);
  }

  function b64ToBytes(value) {
    var raw = atob(value);
    var out = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
    return out;
  }

  async function deriveHash(password, salt, iterations) {
    if (!window.crypto || !window.crypto.subtle) throw new Error('unsupported');
    var enc = new TextEncoder();
    var key = await crypto.subtle.importKey('raw', enc.encode(password), { name: 'PBKDF2' }, false, ['deriveBits']);
    var bits = await crypto.subtle.deriveBits(
      { name: 'PBKDF2', salt: salt, iterations: iterations, hash: 'SHA-256' },
      key,
      256
    );
    return bytesToB64(new Uint8Array(bits));
  }

  function setMaster(value) {
    state.master = !!value;
    try {
      if (state.master) sessionStorage.setItem(MASTER_KEY, '1');
      else sessionStorage.removeItem(MASTER_KEY);
    } catch (e) {}
  }

  function defaultTimeFor(key) {
    var now = new Date();
    if (key !== fmtDate(now)) return '09:00';
    var d = new Date(now.getTime() + 60 * 60 * 1000);
    d.setMinutes(Math.ceil(d.getMinutes() / 5) * 5, 0, 0);
    if (fmtDate(d) !== key) return '23:55';
    return pad(d.getHours()) + ':' + pad(d.getMinutes());
  }

  function setDefaultTime() {
    var input = document.getElementById('taskTime');
    if (input) input.value = defaultTimeFor(state.selected);
  }

  function buildSkeleton() {
    calendarEl.innerHTML =
      '<div class="cal-head">' +
        '<div>' +
          '<div class="cal-kicker" id="calKicker"></div>' +
          '<div class="cal-title" id="calTitle"></div>' +
        '</div>' +
        '<div class="cal-nav">' +
          '<button type="button" class="cal-btn" id="calPrev">&lsaquo;</button>' +
          '<button type="button" class="cal-btn today" id="calToday"></button>' +
          '<button type="button" class="cal-btn" id="calNext">&rsaquo;</button>' +
        '</div>' +
      '</div>' +
      '<div class="cal-week" id="calWeek" aria-hidden="true"></div>' +
      '<div class="cal-grid" id="calGrid"></div>' +
      '<div class="cal-stats" id="calStats"></div>' +
      '<div class="cal-legend">' +
        '<span><i class="legend-swatch"></i><span id="legendUpdate"></span></span>' +
        '<span id="legendTaskWrap"><i class="legend-dot"></i><span id="legendTask"></span></span>' +
      '</div>' +
      '<div class="tasks">' +
        '<div class="tasks-head">' +
          '<div class="tasks-title" id="tasksTitle"></div>' +
          '<div class="tasks-hint" id="tasksHint"></div>' +
        '</div>' +
        '<div class="task-mode-bar">' +
          '<span class="task-mode-badge" id="taskModeLabel"></span>' +
          '<div class="task-mode-actions">' +
            '<button type="button" class="task-mode-btn" id="taskAuthBtn"></button>' +
            '<button type="button" class="task-mode-btn" id="taskLogoutBtn" hidden></button>' +
            '<button type="button" class="task-mode-btn" id="taskExportBtn" hidden></button>' +
            '<button type="button" class="task-mode-btn" id="taskServerSave" hidden>同步到服务器</button>' +
            '<button type="button" class="task-mode-btn" id="taskServerLoad" hidden>从服务器恢复</button>' +
            '<label class="task-mode-btn" id="taskImportLabel" hidden><span id="taskImportText"></span>' +
              '<input type="file" id="taskImport" accept=".json,application/json" hidden>' +
            '</label>' +
          '</div>' +
        '</div>' +
        '<div class="task-mode-note" id="taskModeNote"></div>' +
        '<form class="task-form" id="taskForm" autocomplete="off">' +
          '<input class="task-title" id="taskTitle" type="text" maxlength="80">' +
          '<input class="task-time" id="taskTime" type="time" step="60">' +
          '<button type="submit" class="task-add" id="taskAdd">+</button>' +
        '</form>' +
        '<div class="task-list" id="taskList"></div>' +
      '</div>';

    document.getElementById('calPrev').addEventListener('click', function () { shiftMonth(-1); });
    document.getElementById('calNext').addEventListener('click', function () { shiftMonth(1); });
    document.getElementById('calToday').addEventListener('click', goToday);
    document.getElementById('calGrid').addEventListener('click', function (e) {
      var btn = e.target.closest('.cal-day');
      if (btn) selectDate(btn.getAttribute('data-date'));
    });
    document.getElementById('taskForm').addEventListener('submit', function (e) {
      e.preventDefault();
      addTask();
    });
    document.getElementById('taskList').addEventListener('click', function (e) {
      var del = e.target.closest('.task-del');
      if (!del) return;
      var row = del.closest('.task-item');
      if (row) deleteTask(row.getAttribute('data-task-id'));
    });
    document.getElementById('taskList').addEventListener('change', function (e) {
      if (!e.target.classList.contains('task-check')) return;
      var row = e.target.closest('.task-item');
      if (row) toggleTask(row.getAttribute('data-task-id'), e.target.checked);
    });
    document.getElementById('taskToastClose').addEventListener('click', hideToast);
    document.getElementById('taskAuthBtn').addEventListener('click', openAuthDialog);
    document.getElementById('taskLogoutBtn').addEventListener('click', logoutMaster);
    document.getElementById('taskExportBtn').addEventListener('click', exportTasks);
    document.getElementById('taskServerSave').addEventListener('click', function () { syncTasks('save'); });
    document.getElementById('taskServerLoad').addEventListener('click', function () { syncTasks('load'); });
    document.getElementById('taskImport').addEventListener('change', function (event) {
      var file = event.target.files && event.target.files[0];
      if (file) importTasks(file);
      event.target.value = '';
    });
  }

  function renderLabels() {
    document.getElementById('calKicker').textContent = t('cal-kicker');
    document.getElementById('calToday').textContent = t('cal-today');
    document.getElementById('calPrev').setAttribute('aria-label', t('cal-prev'));
    document.getElementById('calNext').setAttribute('aria-label', t('cal-next'));
    document.getElementById('legendUpdate').textContent = t('cal-legend-update');
    document.getElementById('legendTask').textContent = t('cal-legend-task');
    document.getElementById('tasksHint').textContent = t('tasks-hint');
    var title = document.getElementById('taskTitle');
    var time = document.getElementById('taskTime');
    var add = document.getElementById('taskAdd');
    title.placeholder = t('task-placeholder');
    time.setAttribute('aria-label', t('task-time'));
    add.setAttribute('aria-label', t('task-add'));
    document.getElementById('taskToastClose').setAttribute('aria-label', t('task-close'));
    calendarEl.setAttribute('aria-label', t('cal-kicker'));
  }

  function renderAuth() {
    var master = state.master;
    var modeLabel = document.getElementById('taskModeLabel');
    var authBtn = document.getElementById('taskAuthBtn');
    var logoutBtn = document.getElementById('taskLogoutBtn');
    var exportBtn = document.getElementById('taskExportBtn');
    var serverSaveBtn = document.getElementById('taskServerSave');
    var serverLoadBtn = document.getElementById('taskServerLoad');
    var importLabel = document.getElementById('taskImportLabel');
    var form = document.getElementById('taskForm');
    var list = document.getElementById('taskList');
    var note = document.getElementById('taskModeNote');
    var legendTask = document.getElementById('legendTaskWrap');

    if (!modeLabel) return;
    modeLabel.textContent = master ? t('mode-master') : t('mode-visitor');
    modeLabel.classList.toggle('is-master', master);
    authBtn.textContent = state.auth ? t('mode-login') : t('mode-setup');
    authBtn.hidden = master;
    logoutBtn.textContent = t('mode-logout');
    logoutBtn.hidden = !master;
    exportBtn.textContent = t('mode-export');
    exportBtn.hidden = !master;
    if (serverSaveBtn) serverSaveBtn.hidden = !master;
    if (serverLoadBtn) serverLoadBtn.hidden = !master;
    document.getElementById('taskImportText').textContent = t('mode-import');
    importLabel.hidden = !master;
    form.hidden = !master;
    list.hidden = !master;
    if (legendTask) legendTask.hidden = !master;
    note.textContent = master ? t('mode-note-master') : t('mode-note-visitor');
    note.hidden = false;
  }

  function openAuthDialog() {
    var setup = !state.auth;
    var dialog = document.createElement('dialog');
    dialog.className = 'task-auth-dialog';
    dialog.innerHTML =
      '<form class="task-auth-form" method="dialog">' +
        '<h3 id="taskAuthTitle"></h3>' +
        '<p class="task-auth-note" id="taskAuthNote"></p>' +
        '<label class="task-auth-field"><span></span>' +
          '<input id="taskAuthPass" type="password" autocomplete="' + (setup ? 'new-password' : 'current-password') + '" maxlength="64"></label>' +
        (setup ? '<label class="task-auth-field" id="taskAuthConfirmWrap"><span></span>' +
          '<input id="taskAuthConfirm" type="password" autocomplete="new-password" maxlength="64"></label>' : '') +
        '<div class="task-auth-error" id="taskAuthError" role="alert"></div>' +
        '<div class="task-auth-actions">' +
          '<button type="button" class="task-mode-btn" id="taskAuthCancel"></button>' +
          '<button type="submit" class="task-auth-submit" id="taskAuthSubmit"></button>' +
        '</div>' +
      '</form>';

    document.body.appendChild(dialog);
    dialog.querySelector('#taskAuthTitle').textContent = setup ? t('auth-title-setup') : t('auth-title-login');
    dialog.querySelector('#taskAuthNote').textContent = t('auth-note');
    var labels = dialog.querySelectorAll('.task-auth-field > span');
    if (labels[0]) labels[0].textContent = t('auth-pass');
    if (labels[1]) labels[1].textContent = t('auth-confirm');
    dialog.querySelector('#taskAuthCancel').textContent = t('auth-cancel');
    dialog.querySelector('#taskAuthSubmit').textContent = t('auth-submit');

    var pass = dialog.querySelector('#taskAuthPass');
    var confirm = dialog.querySelector('#taskAuthConfirm');
    var error = dialog.querySelector('#taskAuthError');
    var submit = dialog.querySelector('#taskAuthSubmit');

    function close() { dialog.close(); }
    dialog.querySelector('#taskAuthCancel').addEventListener('click', close);
    dialog.addEventListener('close', function () { dialog.remove(); });
    dialog.addEventListener('cancel', function (event) {
      event.preventDefault();
      close();
    });

    dialog.querySelector('form').addEventListener('submit', async function (event) {
      event.preventDefault();
      error.textContent = '';
      var password = pass.value;
      if (password.length < 6) {
        error.textContent = t('auth-short');
        pass.focus();
        return;
      }
      if (setup && password !== confirm.value) {
        error.textContent = t('auth-mismatch');
        confirm.focus();
        return;
      }
      submit.disabled = true;
      try {
        if (setup) {
          var salt = new Uint8Array(16);
          crypto.getRandomValues(salt);
          var saltB64 = bytesToB64(salt);
          var hash = await deriveHash(password, salt, 120000);
          state.auth = { salt: saltB64, hash: hash, iter: 120000 };
          saveAuth(state.auth);
          setMaster(true);
          close();
          renderAuth();
          renderCalendar();
          renderTasks();
          checkDueTasks();
          showToast(t('mode-master'), t('auth-saved'));
        } else {
          var candidate = await deriveHash(password, b64ToBytes(state.auth.salt), state.auth.iter);
          if (candidate !== state.auth.hash) {
            error.textContent = t('auth-wrong');
            pass.select();
            return;
          }
          setMaster(true);
          close();
          renderAuth();
          renderCalendar();
          renderTasks();
          checkDueTasks();
          showToast(t('mode-master'), t('auth-saved'));
        }
      } catch (e) {
        error.textContent = t('auth-unsupported');
      } finally {
        submit.disabled = false;
      }
    });

    dialog.showModal();
    pass.focus();
  }

  function logoutMaster() {
    setMaster(false);
    renderAuth();
    renderCalendar();
    renderTasks();
    hideToast();
    showToast(t('mode-visitor'), t('auth-logout'));
  }

  function syncTasks(action) {
    if (!state.master) return;
    var url = '/api/tasks';
    var options = { credentials: 'same-origin', headers: { 'Content-Type': 'application/json' } };
    if (action === 'save') {
      options.method = 'PUT';
      options.body = JSON.stringify({ tasks: state.tasks });
    } else {
      options.method = 'GET';
    }
    fetch(url, options)
      .then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (data) {
          if (!response.ok) throw new Error(data.detail || ('服务器返回 ' + response.status));
          return data;
        });
      })
      .then(function (data) {
        if (action === 'load') {
          state.tasks = normalizeTasks(Array.isArray(data.tasks) ? data.tasks : []);
          saveTasks();
          renderCalendar();
          renderTasks();
          showToast(t('mode-master'), '已从服务器恢复 ' + state.tasks.length + ' 个任务');
        } else {
          showToast(t('mode-master'), '已同步 ' + state.tasks.length + ' 个任务到服务器');
        }
      })
      .catch(function (error) {
        var message = error && error.message ? error.message : '同步失败';
        if (/401|登录/.test(message)) message = '请先到 /写笔记/ 登录博客服务器';
        showToast(t('mode-master'), message);
      });
  }

  function exportTasks() {
    if (!state.master) return;
    var payload = {
      version: 1,
      exportedAt: new Date().toISOString(),
      tasks: state.tasks
    };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'blog-tasks-' + fmtDate(new Date()) + '.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function importTasks(file) {
    if (!state.master) return;
    var reader = new FileReader();
    reader.onload = function () {
      try {
        var data = JSON.parse(String(reader.result || ''));
        var raw = Array.isArray(data) ? data : (data && data.tasks);
        if (!Array.isArray(raw)) throw new Error('bad');
        state.tasks = normalizeTasks(raw);
        saveTasks();
        renderTasks();
        renderCalendar();
        showToast(t('mode-master'), t('import-ok'));
      } catch (e) {
        showToast(t('mode-master'), t('import-bad'));
      }
    };
    reader.onerror = function () { showToast(t('mode-master'), t('import-bad')); };
    reader.readAsText(file);
  }

  function renderCalendar() {
    var y = state.view.getFullYear();
    var m = state.view.getMonth();
    document.getElementById('calTitle').textContent = monthLabel(state.view);

    var weekdays = t('weekdays');
    var weekHtml = '';
    for (var w = 0; w < 7; w++) weekHtml += '<span>' + weekdays[w] + '</span>';
    document.getElementById('calWeek').innerHTML = weekHtml;

    var first = new Date(y, m, 1);
    var start = (first.getDay() + 6) % 7; // Monday first
    var days = new Date(y, m + 1, 0).getDate();
    var today = todayKey();
    var html = '';
    for (var b = 0; b < start; b++) html += '<span class="cal-blank"></span>';

    var daysWithUpdates = 0;
    var postsThisMonth = 0;

    for (var day = 1; day <= days; day++) {
      var key = y + '-' + pad(m + 1) + '-' + pad(day);
      var count = updateCount(key);
      var nTasks = state.master ? taskCount(key) : 0;
      if (count > 0) {
        daysWithUpdates++;
        postsThisMonth += count;
      }
      var cls = 'cal-day';
      if (count > 0) cls += ' has-update level-' + updateLevel(count);
      if (key === state.selected) cls += ' is-selected';
      if (key === today) cls += ' is-today';
      var label = t('cal-day-label')
        .replace('{date}', fullDateLabel(key))
        .replace('{posts}', String(count))
        .replace('{tasks}', String(nTasks));
      html += '<button type="button" class="' + cls + '" data-date="' + key +
        '" aria-label="' + escapeHtml(label) + '" title="' + escapeHtml(label) + '"' +
        (key === state.selected ? ' aria-pressed="true"' : '') + '>' +
        '<span>' + day + '</span>' +
        (nTasks > 0 ? '<span class="cal-task-dot" aria-hidden="true"></span>' : '') +
        '</button>';
    }
    for (var t2 = start + days; t2 < 42; t2++) html += '<span class="cal-blank"></span>';
    document.getElementById('calGrid').innerHTML = html;

    var statsEl = document.getElementById('calStats');
    if (daysWithUpdates === 0) {
      statsEl.textContent = t('cal-no-updates');
    } else {
      statsEl.innerHTML = t('cal-stats')
        .replace('{days}', '<b>' + daysWithUpdates + '</b>')
        .replace('{posts}', '<b>' + postsThisMonth + '</b>')
        .replace('{total}', '<b>' + TOTAL_UPDATE_DAYS + '</b>');
    }
  }

  function renderTasks() {
    document.getElementById('tasksTitle').textContent =
      t('tasks-title').replace('{date}', shortDateLabel(state.selected));

    if (!state.master) {
      var locked = document.getElementById('taskList');
      if (locked) locked.innerHTML = '';
      return;
    }

    var list = state.tasks.filter(function (task) {
      return task.date === state.selected;
    }).sort(function (a, b) {
      if (a.done !== b.done) return a.done ? 1 : -1;
      return a.time.localeCompare(b.time);
    });

    var listEl = document.getElementById('taskList');
    if (!list.length) {
      listEl.innerHTML = '<div class="task-empty">' + escapeHtml(t('task-empty')) + '</div>';
      return;
    }

    var now = Date.now();
    var html = '';
    list.forEach(function (task) {
      var isDue = !task.done && taskDateTime(task).getTime() <= now;
      var cls = 'task-item' + (task.done ? ' done' : '') + (isDue ? ' is-due' : '');
      html += '<div class="' + cls + '" data-task-id="' + escapeHtml(task.id) + '">' +
        '<input type="checkbox" class="task-check"' + (task.done ? ' checked' : '') +
        ' aria-label="' + escapeHtml(t('task-done')) + '">' +
        '<div class="task-main">' +
          '<div class="task-line">' +
            '<span class="task-time">' + escapeHtml(task.time) + '</span>' +
            '<span class="task-name">' + escapeHtml(task.title) + '</span>' +
          '</div>' +
          '<span class="task-countdown" data-countdown="' + escapeHtml(task.id) + '">' +
            escapeHtml(countdownText(task)) +
          '</span>' +
        '</div>' +
        '<button type="button" class="task-del" aria-label="' + escapeHtml(t('task-delete')) + '">&times;</button>' +
      '</div>';
    });
    listEl.innerHTML = html;
  }

  function updateCountdowns() {
    var now = Date.now();
    var nodes = document.querySelectorAll('[data-countdown]');
    for (var i = 0; i < nodes.length; i++) {
      var id = nodes[i].getAttribute('data-countdown');
      var task = null;
      for (var j = 0; j < state.tasks.length; j++) {
        if (state.tasks[j].id === id) { task = state.tasks[j]; break; }
      }
      if (!task) continue;
      nodes[i].textContent = countdownText(task);
      var row = nodes[i].closest('.task-item');
      if (row) {
        var due = !task.done && taskDateTime(task).getTime() <= now;
        row.classList.toggle('is-due', due);
      }
    }
  }

  function checkDueTasks() {
    if (!state.master) return;
    var now = Date.now();
    var due = state.tasks.filter(function (task) {
      return !task.done && !task.notified && taskDateTime(task).getTime() <= now;
    });
    if (!due.length) return;

    due.forEach(function (task) { task.notified = true; });
    saveTasks();

    if (due.length === 1) {
      showToast(t('task-reminder'), due[0].time + ' · ' + due[0].title);
      systemNotify(due[0]);
    } else {
      showToast(t('task-reminder'), t('task-many').replace('{n}', String(due.length)));
      due.slice(0, 3).forEach(systemNotify);
    }
    renderTasks();
    renderCalendar();
  }

  function showToast(title, message) {
    var el = document.getElementById('taskToast');
    if (!el) return;
    document.getElementById('taskToastTitle').textContent = title;
    document.getElementById('taskToastMsg').textContent = message;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(hideToast, 9000);
  }

  function hideToast() {
    var el = document.getElementById('taskToast');
    if (el) el.classList.remove('show');
    clearTimeout(toastTimer);
    toastTimer = null;
  }

  function systemNotify(task) {
    try {
      if ('Notification' in window && Notification.permission === 'granted') {
        var n = new Notification(t('task-reminder'), {
          body: task.time + ' · ' + task.title,
          tag: 'blog-task-' + task.id
        });
        n.onclick = function () {
          window.focus();
          n.close();
        };
      }
    } catch (e) {}
  }

  function requestNotify() {
    try {
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
      }
    } catch (e) {}
  }

  function addTask() {
    if (!state.master) return;
    var titleEl = document.getElementById('taskTitle');
    var timeEl = document.getElementById('taskTime');
    var title = titleEl.value.trim();
    var time = timeEl.value;
    if (!title) {
      showToast(t('task-reminder'), t('task-need-title'));
      titleEl.focus();
      return;
    }
    if (!time) {
      showToast(t('task-reminder'), t('task-need-time'));
      timeEl.focus();
      return;
    }
    state.tasks.push({
      id: newId(),
      date: state.selected,
      time: time,
      title: title,
      done: false,
      notified: false
    });
    saveTasks();
    titleEl.value = '';
    setDefaultTime();
    renderTasks();
    renderCalendar();
    titleEl.focus();
    requestNotify();
  }

  function deleteTask(id) {
    if (!state.master) return;
    state.tasks = state.tasks.filter(function (task) { return task.id !== id; });
    saveTasks();
    renderTasks();
    renderCalendar();
  }

  function toggleTask(id, checked) {
    if (!state.master) return;
    for (var i = 0; i < state.tasks.length; i++) {
      if (state.tasks[i].id === id) {
        state.tasks[i].done = !!checked;
        state.tasks[i].notified = !!checked;
        break;
      }
    }
    saveTasks();
    renderTasks();
    renderCalendar();
  }

  function selectDate(key) {
    if (!key) return;
    state.selected = key;
    var d = parseDate(key);
    if (d.getFullYear() !== state.view.getFullYear() || d.getMonth() !== state.view.getMonth()) {
      state.view = new Date(d.getFullYear(), d.getMonth(), 1);
    }
    setDefaultTime();
    renderCalendar();
    renderTasks();
  }

  function shiftMonth(delta) {
    state.view = new Date(state.view.getFullYear(), state.view.getMonth() + delta, 1);
    var selected = parseDate(state.selected);
    if (selected.getFullYear() !== state.view.getFullYear() ||
        selected.getMonth() !== state.view.getMonth()) {
      state.selected = fmtDate(state.view);
      setDefaultTime();
    }
    renderCalendar();
    renderTasks();
  }

  function goToday() {
    var now = new Date();
    state.view = new Date(now.getFullYear(), now.getMonth(), 1);
    state.selected = fmtDate(now);
    setDefaultTime();
    renderCalendar();
    renderTasks();
  }

  function renderAll() {
    renderLabels();
    renderAuth();
    renderCalendar();
    renderTasks();
  }

  function init() {
    var now = new Date();
    state.view = new Date(now.getFullYear(), now.getMonth(), 1);
    state.selected = fmtDate(now);
    state.tasks = loadTasks();
    state.auth = loadAuth();
    try {
      state.master = !!state.auth && sessionStorage.getItem(MASTER_KEY) === '1';
    } catch (e) {
      state.master = false;
    }
    setLang(document.documentElement.lang);
    buildSkeleton();
    state.ready = true;
    setDefaultTime();
    renderAll();
    checkDueTasks();
    window.setInterval(function () {
      updateCountdowns();
      checkDueTasks();
    }, 1000);
  }

  document.addEventListener('langchange', function (e) {
    setLang(e.detail && e.detail.lang);
    renderAll();
  });

  window.addEventListener('storage', function (e) {
    if (e.key !== TASK_KEY) return;
    state.tasks = loadTasks();
    renderCalendar();
    renderTasks();
  });

  init();
})();
