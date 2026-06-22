// 이 파일의 역할: 모달 UI - 일정/휴가 편집, 기간 일괄추가, 설정(공정·색상·공휴일·동기화), 월선택/복사, 검색, 통계
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});
  WS.Editor = {};

  var DOW = ['일', '월', '화', '수', '목', '금', '토'];
  function pad(n) { return String(n).padStart(2, '0'); }
  function dowOf(dateStr) { var p = dateStr.split('-').map(Number); return DOW[new Date(p[0], p[1] - 1, p[2]).getDay()]; }
  function $(id) { return document.getElementById(id); }
  function nextDate(dateStr) { var p = dateStr.split('-').map(Number); var d = new Date(p[0], p[1] - 1, p[2] + 1); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }

  function openModal(title, bodyHtml, footerHtml, wide) {
    var rootEl = $('modal-root');
    rootEl.innerHTML =
      '<div class="modal-overlay" data-close="1">' +
        '<div class="modal-card' + (wide ? ' wide' : '') + '" role="dialog">' +
          '<div class="modal-head"><h3>' + WS.esc(title) + '</h3><button class="modal-x" data-close="1" title="닫기">✕</button></div>' +
          '<div class="modal-body">' + bodyHtml + '</div>' +
          (footerHtml ? '<div class="modal-foot">' + footerHtml + '</div>' : '') +
        '</div>' +
      '</div>';
    rootEl.querySelectorAll('[data-close]').forEach(function (b) {
      b.addEventListener('click', function (e) { if (e.target === b) WS.Editor.close(); });
    });
    return rootEl.querySelector('.modal-card');
  }
  WS.Editor.close = function () { $('modal-root').innerHTML = ''; };

  // ============ 날짜별 일정/휴가 편집 ============
  WS.Editor.openDay = function (dateStr) {
    var st = WS.App.state;
    var data = st.data;
    var key = dateStr.slice(0, 7);
    var month = WS.Store.getMonth(key, true);
    var d = Number(dateStr.split('-')[2]);
    var dim = WS.daysInMonth(st.year, st.month);
    var editingId = null;

    function catOptions(sel) {
      return data.categories.map(function (c, i) {
        return '<option value="' + c.id + '"' + (c.id === sel ? ' selected' : '') + '>' + WS.circled(i) + ' ' + WS.esc(c.name) + '</option>';
      }).join('');
    }
    function leaveOptions(sel) {
      var o = '<option value="">없음(근무)</option>';
      WS.LEAVE_TYPES.forEach(function (t) { o += '<option value="' + t.key + '"' + (sel === t.key ? ' selected' : '') + '>' + t.key + '</option>'; });
      return o;
    }
    function shiftOptions(sel) {
      var o = '<option value="">없음</option>';
      WS.SHIFT_TYPES.forEach(function (t) { o += '<option value="' + t.key + '"' + (sel === t.key ? ' selected' : '') + '>' + t.abbr + ' · ' + t.key + '</option>'; });
      return o;
    }
    function curShift() { var s = (month.shifts || []).filter(function (x) { return x.date === dateStr; })[0]; return s ? s.type : ''; }
    function sameDateEvents() { return month.events.filter(function (e) { return e.date === dateStr; }); }
    function eventRows() {
      var evs = sameDateEvents();
      if (!evs.length) return '<div class="muted">등록된 일정이 없습니다.</div>';
      return evs.map(function (e, pos) {
        var i = data.categories.map(function (c) { return c.id; }).indexOf(e.catId);
        var col = WS.catColor(WS.Store.findCategory(e.catId), i < 0 ? 0 : i);
        var cat = WS.Store.findCategory(e.catId);
        return '<div class="ev-row" data-ev="' + e.id + '">' +
          '<span class="dot" style="background:' + col.bd + '"></span>' +
          '<span class="ev-row-text">' + (e.major ? '★ ' : '') + WS.esc(e.text) + (e.time ? ' <em>(' + WS.esc(e.time) + ')</em>' : '') +
          ' <small>· ' + WS.esc(cat ? cat.short || cat.name : '(삭제된 공정)') + '</small></span>' +
          '<button class="mini" data-mv="-1" data-id="' + e.id + '"' + (pos === 0 ? ' disabled' : '') + '>↑</button>' +
          '<button class="mini" data-mv="1" data-id="' + e.id + '"' + (pos === evs.length - 1 ? ' disabled' : '') + '>↓</button>' +
          '<button class="mini" data-edit="' + e.id + '">수정</button>' +
          '<button class="mini danger" data-del="' + e.id + '">삭제</button>' +
        '</div>';
      }).join('');
    }
    function holidayName() { var h = (month.holidays || []).filter(function (x) { return x.date === dateStr; })[0]; return h ? h.name : ''; }
    function curLeave() { return (month.leaves || []).filter(function (x) { return x.date === dateStr; })[0]; }

    function body() {
      var lv = curLeave();
      return '' +
        '<div class="field"><label>공휴일 / 휴무 (비우면 평일)</label><input id="ed-holiday" type="text" placeholder="예: 어린이날" value="' + WS.esc(holidayName()) + '"></div>' +
        '<div class="field-row">' +
          '<div class="field"><label>휴가 / 근무형태</label><select id="ed-leave">' + leaveOptions(lv ? lv.type : '') + '</select></div>' +
          '<div class="field"><label>교대근무</label><select id="ed-shift">' + shiftOptions(curShift()) + '</select></div>' +
        '</div>' +
        '<div class="section-label">이 날의 일정</div>' +
        '<div id="ed-list">' + eventRows() + '</div>' +
        '<div class="ed-form">' +
          '<div class="section-label" id="ed-form-title">＋ 일정 추가</div>' +
          '<div class="field"><label>공정 분류 <button type="button" class="linkbtn" id="ed-addcat">＋ 새 공정</button></label><select id="ed-cat">' + catOptions(data.categories[0] && data.categories[0].id) + '</select></div>' +
          '<div class="field"><label>내용</label><input id="ed-text" type="text" placeholder="예: AI보고서 작성" maxlength="40"></div>' +
          '<div class="field-row">' +
            '<div class="field"><label>시간</label><select id="ed-time"><option value="">없음</option><option value="오전">오전</option><option value="오후">오후</option></select></div>' +
            '<div class="field check"><label><input id="ed-major" type="checkbox"> 마일스톤(강조)</label></div>' +
          '</div>' +
          '<div class="field check"><label><input id="ed-range" type="checkbox"> 여러 날에 한 번에 추가</label></div>' +
          '<div id="ed-range-opts" style="display:none;">' +
            '<div class="field-row">' +
              '<div class="field"><label>종료일</label><input id="ed-end" type="date" min="' + dateStr + '" max="' + (st.year + '-' + pad(st.month) + '-' + pad(dim)) + '" value="' + dateStr + '"></div>' +
              '<div class="field check"><label><input id="ed-weekday" type="checkbox" checked> 평일만</label><label><input id="ed-skiphol" type="checkbox" checked> 공휴일 제외</label></div>' +
            '</div>' +
          '</div>' +
          '<div class="btn-row"><button class="btn primary" id="ed-add">추가</button><button class="btn ghost" id="ed-cancel" style="display:none;">편집 취소</button></div>' +
        '</div>';
    }

    var card = openModal(st.month + '월 ' + d + '일 (' + dowOf(dateStr) + ') 일정', body(), null, true);

    function refreshList() { $('ed-list').innerHTML = eventRows(); bindList(); }
    function resetForm() {
      editingId = null;
      $('ed-text').value = ''; $('ed-time').value = ''; $('ed-major').checked = false;
      $('ed-form-title').textContent = '＋ 일정 추가';
      $('ed-add').textContent = '추가'; $('ed-cancel').style.display = 'none';
    }
    function rebuildCatSelect(sel) { $('ed-cat').innerHTML = catOptions(sel); }
    function bindList() {
      $('ed-list').querySelectorAll('[data-del]').forEach(function (b) {
        b.addEventListener('click', function () {
          var id = b.getAttribute('data-del');
          month.events = month.events.filter(function (e) { return e.id !== id; });
          WS.Store.save(); WS.App.refresh(); refreshList(); resetForm();
        });
      });
      $('ed-list').querySelectorAll('[data-edit]').forEach(function (b) {
        b.addEventListener('click', function () {
          var e = month.events.filter(function (x) { return x.id === b.getAttribute('data-edit'); })[0];
          if (!e) return;
          editingId = e.id;
          $('ed-cat').value = e.catId; $('ed-text').value = e.text; $('ed-time').value = e.time || ''; $('ed-major').checked = !!e.major;
          $('ed-form-title').textContent = '✎ 일정 수정'; $('ed-add').textContent = '저장'; $('ed-cancel').style.display = '';
          if ($('ed-range')) { $('ed-range').checked = false; $('ed-range-opts').style.display = 'none'; }
          $('ed-text').focus();
        });
      });
      $('ed-list').querySelectorAll('[data-mv]').forEach(function (b) {
        b.addEventListener('click', function () {
          var id = b.getAttribute('data-id'), dir = Number(b.getAttribute('data-mv'));
          var evs = month.events;
          var same = []; evs.forEach(function (e, i) { if (e.date === dateStr) same.push(i); });
          var order = same.map(function (i) { return evs[i].id; });
          var p = order.indexOf(id), q = p + dir;
          if (p < 0 || q < 0 || q >= same.length) return;
          var a = same[p], bIdx = same[q], tmp = evs[a]; evs[a] = evs[bIdx]; evs[bIdx] = tmp;
          WS.Store.save(); WS.App.refresh(); refreshList();
        });
      });
    }

    $('ed-addcat').addEventListener('click', function () {
      var name = root.prompt('새 공정 분류 이름(정식 명칭):', '');
      if (!name) return;
      var shortName = root.prompt('짧은 표기(달력 표시용):', name.slice(0, 6)) || name.slice(0, 6);
      var nc = { id: WS.uid('c'), name: name.trim(), short: shortName.trim() };
      data.categories.push(nc);
      WS.Store.save(); WS.App.refresh();
      rebuildCatSelect(nc.id);
    });

    $('ed-range').addEventListener('change', function () { $('ed-range-opts').style.display = this.checked ? '' : 'none'; });

    $('ed-add').addEventListener('click', function () {
      var text = $('ed-text').value.trim();
      if (!text) { $('ed-text').focus(); return; }
      var payload = { catId: $('ed-cat').value, text: text, time: $('ed-time').value, major: $('ed-major').checked };

      if ($('ed-range').checked && !editingId) {
        var end = $('ed-end').value;
        if (!end || end < dateStr) { root.alert('종료일을 시작일 이후로 선택하세요.'); return; }
        var weekdayOnly = $('ed-weekday').checked, skipHol = $('ed-skiphol').checked;
        var hset = {}; (month.holidays || []).forEach(function (h) { hset[h.date] = true; });
        var cur = dateStr, added = 0;
        while (cur <= end && cur.slice(0, 7) === key) {
          var p = cur.split('-').map(Number), wd = new Date(p[0], p[1] - 1, p[2]).getDay();
          var ok = true;
          if (weekdayOnly && (wd === 0 || wd === 6)) ok = false;
          if (skipHol && hset[cur]) ok = false;
          if (ok) { month.events.push({ id: WS.uid('e'), date: cur, catId: payload.catId, text: payload.text, time: payload.time, major: payload.major }); added++; }
          cur = nextDate(cur);
        }
        WS.Store.save(); WS.App.refresh(); WS.App.toast(added + '일에 일정을 추가했습니다.'); WS.Editor.close(); return;
      }

      if (editingId) {
        var e = month.events.filter(function (x) { return x.id === editingId; })[0];
        if (e) { e.catId = payload.catId; e.text = payload.text; e.time = payload.time; e.major = payload.major; }
      } else {
        month.events.push({ id: WS.uid('e'), date: dateStr, catId: payload.catId, text: payload.text, time: payload.time, major: payload.major });
      }
      WS.Store.save(); WS.App.refresh(); refreshList(); resetForm();
    });
    $('ed-cancel').addEventListener('click', resetForm);
    $('ed-text').addEventListener('keydown', function (e) { if (e.key === 'Enter') $('ed-add').click(); });

    $('ed-holiday').addEventListener('change', function () {
      var name = $('ed-holiday').value.trim();
      month.holidays = (month.holidays || []).filter(function (x) { return x.date !== dateStr; });
      if (name) month.holidays.push({ date: dateStr, name: name });
      WS.Store.save(); WS.App.refresh();
    });
    $('ed-leave').addEventListener('change', function () {
      var type = $('ed-leave').value;
      month.leaves = (month.leaves || []).filter(function (x) { return x.date !== dateStr; });
      if (type) month.leaves.push({ id: WS.uid('l'), date: dateStr, type: type });
      WS.Store.save(); WS.App.refresh();
    });
    $('ed-shift').addEventListener('change', function () {
      var type = $('ed-shift').value;
      month.shifts = (month.shifts || []).filter(function (x) { return x.date !== dateStr; });
      if (type) month.shifts.push({ date: dateStr, type: type });
      WS.Store.save(); WS.App.refresh();
    });

    bindList();
  };

  // ============ 설정 ============
  WS.Editor.openSettings = function () {
    var st = WS.App.state;
    var data = st.data;
    var month = WS.Store.getMonth(st.key, true);

    function catRows() {
      var inactive = month.inactiveCats || [];
      return data.categories.map(function (c, i) {
        var eff = WS.catColor(c, i).bd;
        var active = inactive.indexOf(c.id) < 0;
        return '<div class="grid-row catrow' + (active ? '' : ' off') + '" data-cid="' + c.id + '">' +
          '<label class="tiny" title="이번 달 표시(해제 시 이 달 범례·진행률에서 숨김)"><input type="checkbox" class="set-cat-active"' + (active ? ' checked' : '') + '> 표시</label>' +
          '<input type="color" class="set-cat-color" value="' + (c.color || eff) + '" title="색상">' +
          '<label class="tiny"><input type="checkbox" class="set-cat-custom"' + (c.color ? ' checked' : '') + '> 커스텀</label>' +
          '<input class="set-cat-name" value="' + WS.esc(c.name) + '" placeholder="정식 명칭">' +
          '<input class="set-cat-short" value="' + WS.esc(c.short) + '" placeholder="짧은 표기">' +
          '<button class="mini" data-up="' + c.id + '">↑</button>' +
          '<button class="mini" data-down="' + c.id + '">↓</button>' +
          '<button class="mini danger" data-delcat="' + c.id + '" title="완전 삭제(일정도 함께)">삭제</button></div>';
      }).join('');
    }
    function holRows() {
      return (month.holidays || []).slice().sort(function (a, b) { return a.date < b.date ? -1 : 1; }).map(function (h) {
        return '<div class="grid-row" data-hdate="' + h.date + '">' +
          '<input class="set-hol-date" type="date" value="' + h.date + '">' +
          '<input class="set-hol-name" value="' + WS.esc(h.name) + '" placeholder="휴일명">' +
          '<button class="mini danger" data-delhol="' + h.date + '">삭제</button></div>';
      }).join('') || '<div class="muted">등록된 공휴일이 없습니다.</div>';
    }
    function readCatInputs() {
      $('set-cats').querySelectorAll('.catrow').forEach(function (rowEl) {
        var c = WS.Store.findCategory(rowEl.getAttribute('data-cid')); if (!c) return;
        c.name = rowEl.querySelector('.set-cat-name').value.trim() || c.name;
        c.short = rowEl.querySelector('.set-cat-short').value.trim() || c.short;
        if (rowEl.querySelector('.set-cat-custom').checked) c.color = rowEl.querySelector('.set-cat-color').value;
        else delete c.color;
      });
    }

    var cfg = WS.Sync.config();
    var body = '' +
      '<div class="section-label">기본 정보</div>' +
      '<div class="field-row">' +
        '<div class="field"><label>부서명</label><input id="set-dept" value="' + WS.esc(data.meta.dept) + '"></div>' +
        '<div class="field"><label>작성자</label><input id="set-author" value="' + WS.esc(data.meta.author) + '"></div>' +
      '</div>' +
      '<div class="section-label">공정 분류 — \'표시\' 해제 시 이번 달(' + st.month + '월) 범례·진행률에서 숨김 (삭제 아님, 과거 달·일정은 유지)</div>' +
      '<div id="set-cats">' + catRows() + '</div>' +
      '<button class="btn ghost sm" id="set-addcat">＋ 공정 추가</button>' +
      '<div class="section-label">이번 달 공휴일 (' + st.month + '월)</div>' +
      '<div id="set-hols">' + holRows() + '</div>' +
      '<div class="btn-row"><button class="btn ghost sm" id="set-addhol">＋ 공휴일 추가</button><button class="btn ghost sm" id="set-autohol">한국 공휴일 자동 채우기</button></div>' +
      '<div class="section-label">푸터 안내문</div>' +
      '<textarea id="set-footer" rows="2" placeholder="예: ※ 회의 일자는 협의 후 조정 가능">' + WS.esc(month.footerNote || '') + '</textarea>' +
      '<div class="section-label">GitHub 동기화 (여러 기기 공유)</div>' +
      '<div class="sync-warn">⚠ <b>공개 저장소</b>에 올리면 일정 데이터가 인터넷에 공개됩니다. 민감 정보는 비공개 저장소를 쓰세요. 토큰은 이 브라우저에만 저장되고 내보내기 파일에는 포함되지 않습니다.</div>' +
      '<div class="field-row">' +
        '<div class="field"><label>owner</label><input id="sync-owner" value="' + WS.esc(cfg.owner) + '" placeholder="baikhojun"></div>' +
        '<div class="field"><label>repo</label><input id="sync-repo" value="' + WS.esc(cfg.repo) + '" placeholder="baikhojun.github.io"></div>' +
      '</div>' +
      '<div class="field-row">' +
        '<div class="field"><label>파일 경로</label><input id="sync-path" value="' + WS.esc(cfg.path) + '"></div>' +
        '<div class="field"><label>브랜치</label><input id="sync-branch" value="' + WS.esc(cfg.branch) + '"></div>' +
      '</div>' +
      '<div class="field"><label>GitHub 토큰 (PAT, repo 권한)</label><input id="sync-token" type="password" value="' + WS.esc(WS.Store.getToken()) + '" placeholder="ghp_..."></div>' +
      '<div class="btn-row"><button class="btn" id="sync-up">⬆ GitHub에 저장</button><button class="btn" id="sync-down">⬇ GitHub에서 불러오기</button></div>' +
      '<div id="sync-status" class="sync-status"></div>' +
      '<div class="section-label danger-label">데이터</div>' +
      '<button class="btn ghost sm danger" id="set-reset">전체 초기화(기본 예시로 되돌리기)</button>';

    var footer = '<button class="btn ghost" id="set-cancel">취소</button><button class="btn primary" id="set-save">저장</button>';
    var card = openModal('설정', body, footer, true);

    function bindCats() {
      $('set-cats').querySelectorAll('[data-delcat]').forEach(function (b) {
        b.addEventListener('click', function () {
          var id = b.getAttribute('data-delcat');
          if (data.categories.length <= 1) { root.alert('최소 1개의 공정은 필요합니다.'); return; }
          var used = 0;
          Object.keys(data.months).forEach(function (k) { used += data.months[k].events.filter(function (e) { return e.catId === id; }).length; });
          if (used > 0 && !root.confirm('이 공정을 사용하는 일정 ' + used + '건도 함께 삭제됩니다.\n범례·진행률 표에서도 제거됩니다. 계속할까요?')) return;
          readCatInputs();
          data.categories = data.categories.filter(function (c) { return c.id !== id; });
          Object.keys(data.months).forEach(function (k) {
            var mo = data.months[k];
            mo.events = mo.events.filter(function (e) { return e.catId !== id; });
            if (mo.progressOverride) delete mo.progressOverride[id];
          });
          WS.Store.save(); WS.App.refresh();
          $('set-cats').innerHTML = catRows(); bindCats();
        });
      });
      function move(id, dir) {
        readCatInputs();
        var i = data.categories.map(function (c) { return c.id; }).indexOf(id), j = i + dir;
        if (i < 0 || j < 0 || j >= data.categories.length) return;
        var t = data.categories[i]; data.categories[i] = data.categories[j]; data.categories[j] = t;
        $('set-cats').innerHTML = catRows(); bindCats();
      }
      $('set-cats').querySelectorAll('[data-up]').forEach(function (b) { b.addEventListener('click', function () { move(b.getAttribute('data-up'), -1); }); });
      $('set-cats').querySelectorAll('[data-down]').forEach(function (b) { b.addEventListener('click', function () { move(b.getAttribute('data-down'), 1); }); });
      $('set-cats').querySelectorAll('.set-cat-active').forEach(function (chk) {
        chk.addEventListener('change', function () {
          var rowEl = chk.closest('.catrow'), id = rowEl.getAttribute('data-cid');
          month.inactiveCats = month.inactiveCats || [];
          var idx = month.inactiveCats.indexOf(id);
          if (chk.checked) { if (idx >= 0) month.inactiveCats.splice(idx, 1); }
          else { if (idx < 0) month.inactiveCats.push(id); }
          rowEl.classList.toggle('off', !chk.checked);
          WS.Store.save(); WS.App.refresh();
        });
      });
    }
    function bindHolDel() {
      $('set-hols').querySelectorAll('[data-delhol]').forEach(function (b) {
        b.addEventListener('click', function () {
          month.holidays = (month.holidays || []).filter(function (h) { return h.date !== b.getAttribute('data-delhol'); });
          $('set-hols').innerHTML = holRows(); bindHolDel();
        });
      });
    }
    bindCats(); bindHolDel();

    card.querySelector('#set-cancel').addEventListener('click', WS.Editor.close);
    $('set-addcat').addEventListener('click', function () { readCatInputs(); data.categories.push({ id: WS.uid('c'), name: '새 공정', short: '새 공정' }); $('set-cats').innerHTML = catRows(); bindCats(); });
    $('set-addhol').addEventListener('click', function () { month.holidays = month.holidays || []; month.holidays.push({ date: st.year + '-' + pad(st.month) + '-01', name: '휴일' }); $('set-hols').innerHTML = holRows(); bindHolDel(); });
    $('set-autohol').addEventListener('click', function () {
      var auto = WS.holidaysForMonth(st.year, st.month), have = {};
      (month.holidays || []).forEach(function (h) { have[h.date] = true; });
      month.holidays = month.holidays || [];
      auto.forEach(function (h) { if (!have[h.date]) month.holidays.push({ date: h.date, name: h.name }); });
      $('set-hols').innerHTML = holRows(); bindHolDel(); WS.App.toast('공휴일을 채웠습니다. 확인 후 조정하세요.');
    });
    $('set-reset').addEventListener('click', function () {
      if (root.confirm('모든 데이터를 삭제하고 기본 예시로 되돌립니다. 계속할까요?')) {
        WS.Store.resetAll(); WS.Editor.close(); WS.App.reloadData(); WS.App.toast('초기화되었습니다.');
      }
    });

    function readSyncCfg() {
      data.sync = data.sync || {};
      data.sync.owner = $('sync-owner').value.trim(); data.sync.repo = $('sync-repo').value.trim();
      data.sync.path = $('sync-path').value.trim() || 'data/schedule-data.json'; data.sync.branch = $('sync-branch').value.trim() || 'main';
    }
    function setSyncStatus(msg) { $('sync-status').textContent = msg; }
    $('sync-up').addEventListener('click', function () {
      readSyncCfg(); var token = $('sync-token').value.trim(); WS.Store.setToken(token); WS.Store.save();
      setSyncStatus('업로드 중...');
      WS.Sync.upload(token).then(function () { setSyncStatus('✅ GitHub 저장 완료'); WS.App.toast('GitHub에 저장했습니다.'); })
        .catch(function (e) { setSyncStatus('❌ ' + e.message); });
    });
    $('sync-down').addEventListener('click', function () {
      readSyncCfg(); var token = $('sync-token').value.trim(); WS.Store.setToken(token); WS.Store.save();
      if (!root.confirm('GitHub의 데이터로 현재 내용을 덮어씁니다. 계속할까요?')) return;
      setSyncStatus('내려받는 중...');
      WS.Sync.download(token).then(function () { WS.Editor.close(); WS.App.reloadData(); WS.App.toast('GitHub에서 불러왔습니다.'); })
        .catch(function (e) { setSyncStatus('❌ ' + e.message); });
    });

    $('set-save').addEventListener('click', function () {
      data.meta.dept = $('set-dept').value.trim(); data.meta.author = $('set-author').value.trim();
      readCatInputs();
      var newHols = [];
      $('set-hols').querySelectorAll('.grid-row').forEach(function (rowEl) {
        var date = rowEl.querySelector('.set-hol-date').value, name = rowEl.querySelector('.set-hol-name').value.trim();
        if (date && name) newHols.push({ date: date, name: name });
      });
      month.holidays = newHols;
      month.footerNote = $('set-footer').value.trim();
      readSyncCfg();
      WS.Store.save(); WS.App.refresh(); WS.Editor.close(); WS.App.toast('저장되었습니다.');
    });
  };

  // ============ 월 이동 / 기록 / 복사 ============
  WS.Editor.openMonths = function () {
    var st = WS.App.state;
    function listHtml() {
      var keys = WS.Store.savedMonthKeys();
      return keys.length ? keys.map(function (k) {
        var p = k.split('-').map(Number), mo = WS.Store.getMonth(k);
        return '<button class="month-item' + (k === st.key ? ' active' : '') + '" data-go="' + k + '"><b>' + p[0] + '년 ' + p[1] + '월</b><span>' + mo.events.length + '건</span></button>';
      }).join('') : '<div class="muted">저장된 월이 없습니다.</div>';
    }
    var prevKey = (function () { var m = st.month - 1, y = st.year; if (m < 1) { m = 12; y--; } return WS.monthKey(y, m); })();
    var canCopy = !!WS.Store.data.months[prevKey];

    var body = '<div class="section-label">이동할 월</div>' +
      '<div class="field-row">' +
        '<div class="field"><label>연도</label><input id="mv-year" type="number" value="' + st.year + '" min="2000" max="2100"></div>' +
        '<div class="field"><label>월</label><input id="mv-month" type="number" value="' + st.month + '" min="1" max="12"></div>' +
        '<div class="field" style="align-self:flex-end;"><button class="btn primary" id="mv-go">이동</button></div>' +
      '</div>' +
      (canCopy ? '<div class="btn-row"><button class="btn ghost sm" id="mv-copy">↩ 지난 달(' + prevKey + ') 일정 복사해 채우기</button></div>' : '') +
      '<div class="section-label">저장된 기록</div>' +
      '<div class="month-list">' + listHtml() + '</div>';

    var card = openModal('월 이동 / 기록', body);
    $('mv-go').addEventListener('click', function () {
      var y = Number($('mv-year').value), m = Number($('mv-month').value);
      if (y >= 2000 && m >= 1 && m <= 12) { WS.Editor.close(); WS.App.go(y, m); }
    });
    if (canCopy) $('mv-copy').addEventListener('click', function () {
      var hasData = WS.Store.data.months[st.key] && WS.Store.data.months[st.key].events.length;
      if (hasData && !root.confirm('현재 달에 일정이 있습니다. 지난 달 내용으로 덮어쓸까요?')) return;
      WS.Store.copyMonth(prevKey, st.key); WS.Store.save(); WS.Editor.close(); WS.App.refresh(); WS.App.toast('지난 달 일정을 복사했습니다.');
    });
    card.querySelectorAll('[data-go]').forEach(function (b) {
      b.addEventListener('click', function () { var p = b.getAttribute('data-go').split('-').map(Number); WS.Editor.close(); WS.App.go(p[0], p[1]); });
    });
  };

  // ============ 검색 ============
  WS.Editor.openSearch = function () {
    var data = WS.App.state.data;
    var body = '<div class="field"><input id="sc-q" type="text" placeholder="일정 내용 또는 공정명 검색..." autocomplete="off"></div><div id="sc-results" class="search-results"></div>';
    openModal('일정 검색', body);
    function run() {
      var q = $('sc-q').value.trim().toLowerCase();
      var box = $('sc-results');
      if (!q) { box.innerHTML = '<div class="muted">검색어를 입력하세요.</div>'; return; }
      var hits = [];
      WS.Store.savedMonthKeys().forEach(function (k) {
        var mo = data.months[k];
        mo.events.forEach(function (e) {
          var cat = WS.Store.findCategory(e.catId);
          var hay = (e.text + ' ' + (cat ? cat.name + ' ' + cat.short : '')).toLowerCase();
          if (hay.indexOf(q) >= 0) hits.push({ key: k, date: e.date, text: e.text, cat: cat });
        });
      });
      hits.sort(function (a, b) { return a.date < b.date ? -1 : 1; });
      if (!hits.length) { box.innerHTML = '<div class="muted">결과가 없습니다.</div>'; return; }
      box.innerHTML = hits.slice(0, 100).map(function (h) {
        var p = h.date.split('-').map(Number);
        return '<button class="sc-item" data-date="' + h.date + '"><b>' + p[1] + '/' + p[2] + '</b> ' + WS.esc(h.text) +
          ' <small>' + WS.esc(h.cat ? h.cat.short : '') + '</small></button>';
      }).join('');
      box.querySelectorAll('[data-date]').forEach(function (b) {
        b.addEventListener('click', function () {
          var ds = b.getAttribute('data-date'), p = ds.split('-').map(Number);
          WS.Editor.close(); WS.App.go(p[0], p[1]); WS.Editor.openDay(ds);
        });
      });
    }
    $('sc-q').addEventListener('input', run);
    $('sc-q').focus();
  };

  // ============ 통계 ============
  WS.Editor.openStats = function () {
    var st = WS.App.state, data = st.data;
    var month = WS.Store.getMonth(st.key);
    var s = WS.Stats.compute(month, data.categories, st.year, st.month);
    var catRows = data.categories.map(function (c, i) {
      var col = WS.catColor(c, i), st2 = s.perCat.filter(function (x) { return x.id === c.id; })[0] || { days: 0, events: 0 };
      return '<tr><td class="cat-name" style="border-left:3px solid ' + col.bd + ';">' + WS.circled(i) + ' ' + WS.esc(c.short || c.name) + '</td><td>' + st2.days + '일</td><td>' + st2.events + '건</td></tr>';
    }).join('');
    var leaveRows = s.leaves.length ? s.leaves.map(function (l) { return '<tr><td class="cat-name">' + WS.esc(l.type) + '</td><td>' + l.count + '회</td></tr>'; }).join('') : '<tr><td class="muted" colspan="2">휴가 기록 없음</td></tr>';
    var body =
      '<div class="stat-cards">' +
        '<div class="stat-card"><div class="n">' + s.workdays + '</div><div class="l">근무일(평일-공휴일)</div></div>' +
        '<div class="stat-card"><div class="n">' + s.totalEvents + '</div><div class="l">총 일정 수</div></div>' +
        '<div class="stat-card"><div class="n">' + s.leaveDays + '</div><div class="l">휴가 일수</div></div>' +
        '<div class="stat-card"><div class="n">' + s.holidays + '</div><div class="l">공휴일</div></div>' +
      '</div>' +
      '<div class="section-label">공정별 투입</div>' +
      '<table class="stat-table"><thead><tr><th style="text-align:left;">공정</th><th>투입일수</th><th>일정수</th></tr></thead><tbody>' + catRows + '</tbody></table>' +
      '<div class="section-label">휴가 / 근무형태</div>' +
      '<table class="stat-table"><thead><tr><th style="text-align:left;">유형</th><th>횟수</th></tr></thead><tbody>' + leaveRows + '</tbody></table>' +
      (s.shifts && s.shifts.length ?
        '<div class="section-label">교대근무</div><table class="stat-table"><thead><tr><th style="text-align:left;">유형</th><th>일수</th></tr></thead><tbody>' +
        s.shifts.map(function (x) { var stt = WS.shiftType(x.type) || {}; return '<tr><td class="cat-name" style="border-left:3px solid ' + (stt.color || '#64748b') + ';">' + x.abbr + ' · ' + x.type + '</td><td>' + x.count + '일</td></tr>'; }).join('') +
        '</tbody></table>' : '');
    openModal(st.year + '년 ' + st.month + '월 통계', body);
  };

  // ============ 교대근무 월 일괄 입력 ============
  WS.Editor.openShifts = function () {
    var st = WS.App.state, key = st.key;
    var month = WS.Store.getMonth(key, true);
    function shiftOf(date) { var s = month.shifts.filter(function (x) { return x.date === date; })[0]; return s ? s.type : ''; }
    function legendHtml() {
      return '<div class="legend" style="grid-template-columns:repeat(4,1fr);">' + WS.SHIFT_TYPES.map(function (t) {
        return '<div class="legend-item"><div class="legend-swatch" style="background:' + t.color + ';"></div>' + t.abbr + ' · ' + t.key + '</div>';
      }).join('') + '</div>';
    }
    function gridHtml() {
      var firstDow = new Date(st.year, st.month - 1, 1).getDay();
      var days = WS.daysInMonth(st.year, st.month);
      var rows = Math.ceil((firstDow + days) / 7), cells = rows * 7;
      var h = '<div class="sg-dow"><div class="sun">일</div><div>월</div><div>화</div><div>수</div><div>목</div><div>금</div><div class="sat">토</div></div><div class="sg-body">';
      for (var i = 0; i < cells; i++) {
        var d = i - firstDow + 1;
        if (d < 1 || d > days) { h += '<div class="sg-cell empty"></div>'; continue; }
        var date = st.year + '-' + pad(st.month) + '-' + pad(d);
        var stt = WS.shiftType(shiftOf(date));
        var style = stt ? ' style="background:' + stt.color + ';color:#fff;border-color:' + stt.color + ';"' : '';
        h += '<button class="sg-cell" data-date="' + date + '"' + style + '><b>' + d + '</b><span>' + (stt ? stt.abbr : '') + '</span></button>';
      }
      return h + '</div>';
    }
    var body = '<div class="muted">날짜를 클릭하면 D → E → N → Off → 없음 순서로 바뀝니다. (하루 1개)</div>' +
      legendHtml() + '<div class="shift-grid">' + gridHtml() + '</div>' +
      '<div class="btn-row"><button class="btn ghost sm danger" id="sh-clear">이 달 교대 전체 지우기</button></div>';
    var card = openModal('🌓 교대근무 입력 (' + st.year + '년 ' + st.month + '월)', body, null, true);

    var order = ['', 'Day', 'Evening', 'Night', 'Off'];
    function rerender() { card.querySelector('.shift-grid').innerHTML = gridHtml(); bindCells(); }
    function bindCells() {
      card.querySelectorAll('.sg-cell[data-date]').forEach(function (b) {
        b.addEventListener('click', function () {
          var date = b.getAttribute('data-date'), cur = shiftOf(date);
          var next = order[(order.indexOf(cur) + 1) % order.length];
          month.shifts = month.shifts.filter(function (x) { return x.date !== date; });
          if (next) month.shifts.push({ date: date, type: next });
          WS.Store.save(); WS.App.refresh(); rerender();
        });
      });
    }
    bindCells();
    card.querySelector('#sh-clear').addEventListener('click', function () {
      if (!root.confirm('이 달의 교대근무 입력을 모두 지울까요?')) return;
      month.shifts = []; WS.Store.save(); WS.App.refresh(); rerender();
    });
  };
})(typeof window !== 'undefined' ? window : globalThis);
