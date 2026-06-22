// 이 파일의 역할: 모달 UI - 날짜별 일정 추가/수정/삭제, 설정(부서·카테고리·공휴일), 월 선택(기록)
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});
  WS.Editor = {};

  var DOW = ['일', '월', '화', '수', '목', '금', '토'];
  function pad(n) { return String(n).padStart(2, '0'); }
  function dowOf(dateStr) { var p = dateStr.split('-').map(Number); return DOW[new Date(p[0], p[1] - 1, p[2]).getDay()]; }
  function $(id) { return document.getElementById(id); }

  function openModal(title, bodyHtml, footerHtml) {
    var rootEl = $('modal-root');
    rootEl.innerHTML =
      '<div class="modal-overlay" data-close="1">' +
        '<div class="modal-card" role="dialog">' +
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

  // ---------- 날짜별 일정 편집 ----------
  WS.Editor.openDay = function (dateStr) {
    var st = WS.App.state;
    var data = st.data;
    var month = WS.Store.getMonth(st.key, true);
    var d = Number(dateStr.split('-')[2]);
    var editingId = null;

    function catOptions(sel) {
      return data.categories.map(function (c, i) {
        return '<option value="' + c.id + '"' + (c.id === sel ? ' selected' : '') + '>' + WS.circled(i) + ' ' + WS.esc(c.name) + '</option>';
      }).join('');
    }
    function eventRows() {
      var evs = month.events.filter(function (e) { return e.date === dateStr; });
      if (!evs.length) return '<div class="muted">등록된 일정이 없습니다.</div>';
      return evs.map(function (e) {
        var i = data.categories.map(function (c) { return c.id; }).indexOf(e.catId);
        var col = WS.color(i < 0 ? 0 : i);
        var cat = WS.Store.findCategory(e.catId);
        return '<div class="ev-row" data-ev="' + e.id + '">' +
          '<span class="dot" style="background:' + col.bd + '"></span>' +
          '<span class="ev-row-text">' + (e.major ? '★ ' : '') + WS.esc(e.text) + (e.time ? ' <em>(' + WS.esc(e.time) + ')</em>' : '') +
          ' <small>· ' + WS.esc(cat ? cat.short || cat.name : '') + '</small></span>' +
          '<button class="mini" data-edit="' + e.id + '">수정</button>' +
          '<button class="mini danger" data-del="' + e.id + '">삭제</button>' +
        '</div>';
      }).join('');
    }
    function holidayName() {
      var h = (month.holidays || []).filter(function (x) { return x.date === dateStr; })[0];
      return h ? h.name : '';
    }

    function body() {
      return '' +
        '<div class="field"><label>공휴일 / 휴무 (비우면 평일)</label>' +
          '<input id="ed-holiday" type="text" placeholder="예: 어린이날" value="' + WS.esc(holidayName()) + '"></div>' +
        '<div class="section-label">이 날의 일정</div>' +
        '<div id="ed-list">' + eventRows() + '</div>' +
        '<div class="ed-form">' +
          '<div class="section-label" id="ed-form-title">＋ 일정 추가</div>' +
          '<div class="field"><label>공정 분류</label><select id="ed-cat">' + catOptions(data.categories[0] && data.categories[0].id) + '</select></div>' +
          '<div class="field"><label>내용</label><input id="ed-text" type="text" placeholder="예: AI보고서 작성" maxlength="40"></div>' +
          '<div class="field-row">' +
            '<div class="field"><label>시간</label><select id="ed-time"><option value="">없음</option><option value="오전">오전</option><option value="오후">오후</option></select></div>' +
            '<div class="field check"><label><input id="ed-major" type="checkbox"> 마일스톤(강조)</label></div>' +
          '</div>' +
          '<div class="btn-row"><button class="btn primary" id="ed-add">추가</button>' +
          '<button class="btn ghost" id="ed-cancel" style="display:none;">편집 취소</button></div>' +
        '</div>';
    }

    var card = openModal(st.month + '월 ' + d + '일 (' + dowOf(dateStr) + ') 일정', body());

    function refreshList() {
      $('ed-list').innerHTML = eventRows();
      bindList();
    }
    function resetForm() {
      editingId = null;
      $('ed-text').value = ''; $('ed-time').value = ''; $('ed-major').checked = false;
      $('ed-form-title').textContent = '＋ 일정 추가';
      $('ed-add').textContent = '추가';
      $('ed-cancel').style.display = 'none';
    }
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
          var id = b.getAttribute('data-edit');
          var e = month.events.filter(function (x) { return x.id === id; })[0];
          if (!e) return;
          editingId = id;
          $('ed-cat').value = e.catId; $('ed-text').value = e.text; $('ed-time').value = e.time || '';
          $('ed-major').checked = !!e.major;
          $('ed-form-title').textContent = '✎ 일정 수정';
          $('ed-add').textContent = '저장';
          $('ed-cancel').style.display = '';
          $('ed-text').focus();
        });
      });
    }

    $('ed-add').addEventListener('click', function () {
      var text = $('ed-text').value.trim();
      if (!text) { $('ed-text').focus(); return; }
      var payload = { catId: $('ed-cat').value, text: text, time: $('ed-time').value, major: $('ed-major').checked };
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

    bindList();
  };

  // ---------- 설정 ----------
  WS.Editor.openSettings = function () {
    var st = WS.App.state;
    var data = st.data;
    var month = WS.Store.getMonth(st.key, true);

    function catRows() {
      return data.categories.map(function (c, i) {
        var col = WS.color(i);
        return '<div class="grid-row" data-cid="' + c.id + '">' +
          '<span class="dot" style="background:' + col.bd + '"></span>' +
          '<input class="set-cat-name" value="' + WS.esc(c.name) + '" placeholder="정식 명칭">' +
          '<input class="set-cat-short" value="' + WS.esc(c.short) + '" placeholder="짧은 표기">' +
          '<button class="mini danger" data-delcat="' + c.id + '">삭제</button></div>';
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

    var body = '' +
      '<div class="section-label">기본 정보</div>' +
      '<div class="field-row">' +
        '<div class="field"><label>부서명</label><input id="set-dept" value="' + WS.esc(data.meta.dept) + '"></div>' +
        '<div class="field"><label>작성자</label><input id="set-author" value="' + WS.esc(data.meta.author) + '"></div>' +
      '</div>' +
      '<div class="section-label">공정 분류 (색상은 순서대로 자동 배정)</div>' +
      '<div id="set-cats">' + catRows() + '</div>' +
      '<button class="btn ghost sm" id="set-addcat">＋ 공정 추가</button>' +
      '<div class="section-label">이번 달 공휴일 (' + st.month + '월)</div>' +
      '<div id="set-hols">' + holRows() + '</div>' +
      '<div class="btn-row"><button class="btn ghost sm" id="set-addhol">＋ 공휴일 추가</button>' +
      '<button class="btn ghost sm" id="set-autohol">한국 공휴일 자동 채우기</button></div>' +
      '<div class="section-label">푸터 안내문</div>' +
      '<textarea id="set-footer" rows="2" placeholder="예: ※ 회의 일자는 협의 후 조정 가능">' + WS.esc(month.footerNote || '') + '</textarea>' +
      '<div class="section-label danger-label">데이터</div>' +
      '<button class="btn ghost sm danger" id="set-reset">전체 초기화(기본 예시로 되돌리기)</button>';

    var footer = '<button class="btn ghost" data-close="1" id="set-cancel">취소</button><button class="btn primary" id="set-save">저장</button>';
    var card = openModal('설정', body, footer);

    card.querySelector('#set-cancel').addEventListener('click', WS.Editor.close);
    card.querySelector('#set-addcat').addEventListener('click', function () {
      data.categories.push({ id: WS.uid('c'), name: '새 공정', short: '새 공정' });
      $('set-cats').innerHTML = catRows(); bindCatDel();
    });
    card.querySelector('#set-addhol').addEventListener('click', function () {
      var def = st.year + '-' + pad(st.month) + '-01';
      month.holidays = month.holidays || [];
      month.holidays.push({ date: def, name: '휴일' });
      $('set-hols').innerHTML = holRows(); bindHolDel();
    });
    card.querySelector('#set-autohol').addEventListener('click', function () {
      var auto = WS.holidaysForMonth(st.year, st.month);
      var have = {}; (month.holidays || []).forEach(function (h) { have[h.date] = true; });
      month.holidays = month.holidays || [];
      auto.forEach(function (h) { if (!have[h.date]) month.holidays.push({ date: h.date, name: h.name }); });
      $('set-hols').innerHTML = holRows(); bindHolDel();
      WS.App.toast('공휴일을 채웠습니다. 확인 후 조정하세요.');
    });
    card.querySelector('#set-reset').addEventListener('click', function () {
      if (root.confirm('모든 데이터를 삭제하고 기본 예시로 되돌립니다. 계속할까요?')) {
        WS.Store.resetAll(); WS.Editor.close();
        WS.App.go(2026, 5); WS.App.toast('초기화되었습니다.');
      }
    });

    function bindCatDel() {
      $('set-cats').querySelectorAll('[data-delcat]').forEach(function (b) {
        b.addEventListener('click', function () {
          var id = b.getAttribute('data-delcat');
          var used = Object.keys(data.months).some(function (k) {
            return data.months[k].events.some(function (e) { return e.catId === id; });
          });
          if (used) { root.alert('이 공정을 사용하는 일정이 있어 삭제할 수 없습니다. 먼저 해당 일정을 변경/삭제하세요.'); return; }
          if (data.categories.length <= 1) { root.alert('최소 1개의 공정은 필요합니다.'); return; }
          data.categories = data.categories.filter(function (c) { return c.id !== id; });
          $('set-cats').innerHTML = catRows(); bindCatDel();
        });
      });
    }
    function bindHolDel() {
      $('set-hols').querySelectorAll('[data-delhol]').forEach(function (b) {
        b.addEventListener('click', function () {
          var date = b.getAttribute('data-delhol');
          month.holidays = (month.holidays || []).filter(function (h) { return h.date !== date; });
          $('set-hols').innerHTML = holRows(); bindHolDel();
        });
      });
    }
    bindCatDel(); bindHolDel();

    card.querySelector('#set-save').addEventListener('click', function () {
      data.meta.dept = $('set-dept').value.trim();
      data.meta.author = $('set-author').value.trim();
      // 카테고리 입력 반영
      $('set-cats').querySelectorAll('.grid-row').forEach(function (rowEl) {
        var id = rowEl.getAttribute('data-cid');
        var c = WS.Store.findCategory(id);
        if (c) { c.name = rowEl.querySelector('.set-cat-name').value.trim() || c.name; c.short = rowEl.querySelector('.set-cat-short').value.trim() || c.short; }
      });
      // 공휴일 입력 반영
      var newHols = [];
      $('set-hols').querySelectorAll('.grid-row').forEach(function (rowEl) {
        var date = rowEl.querySelector('.set-hol-date').value;
        var name = rowEl.querySelector('.set-hol-name').value.trim();
        if (date && name) newHols.push({ date: date, name: name });
      });
      month.holidays = newHols;
      month.footerNote = $('set-footer').value.trim();
      WS.Store.save(); WS.App.refresh(); WS.Editor.close(); WS.App.toast('저장되었습니다.');
    });
  };

  // ---------- 월 선택 / 기록 ----------
  WS.Editor.openMonths = function () {
    var st = WS.App.state;
    var keys = WS.Store.savedMonthKeys();
    var listHtml = keys.length ? keys.map(function (k) {
      var p = k.split('-').map(Number);
      var mo = WS.Store.getMonth(k);
      var cnt = mo.events.length;
      var active = k === st.key ? ' active' : '';
      return '<button class="month-item' + active + '" data-go="' + k + '">' +
        '<b>' + p[0] + '년 ' + p[1] + '월</b><span>' + cnt + '건</span></button>';
    }).join('') : '<div class="muted">저장된 월이 없습니다.</div>';

    var body = '<div class="section-label">이동할 월</div>' +
      '<div class="field-row">' +
        '<div class="field"><label>연도</label><input id="mv-year" type="number" value="' + st.year + '" min="2000" max="2100"></div>' +
        '<div class="field"><label>월</label><input id="mv-month" type="number" value="' + st.month + '" min="1" max="12"></div>' +
        '<div class="field" style="align-self:flex-end;"><button class="btn primary" id="mv-go">이동</button></div>' +
      '</div>' +
      '<div class="section-label">저장된 기록</div>' +
      '<div class="month-list">' + listHtml + '</div>';

    var card = openModal('월 이동 / 기록', body);
    card.querySelector('#mv-go').addEventListener('click', function () {
      var y = Number($('mv-year').value), m = Number($('mv-month').value);
      if (y >= 2000 && m >= 1 && m <= 12) { WS.Editor.close(); WS.App.go(y, m); }
    });
    card.querySelectorAll('[data-go]').forEach(function (b) {
      b.addEventListener('click', function () {
        var p = b.getAttribute('data-go').split('-').map(Number);
        WS.Editor.close(); WS.App.go(p[0], p[1]);
      });
    });
  };
})(typeof window !== 'undefined' ? window : globalThis);
