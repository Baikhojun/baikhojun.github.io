// 이 파일의 역할: 앱 진입점 - 초기화, 월 이동, 툴바/시트 이벤트 연결, 내보내기/가져오기, 토스트
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});
  var doc = root.document;
  function $(id) { return doc.getElementById(id); }
  function pad(n) { return String(n).padStart(2, '0'); }

  WS.App = {
    state: { data: null, year: 2026, month: 5, key: '2026-05' },

    init: function () {
      var data = WS.Store.load();
      this.state.data = data;
      var last = (data.ui && data.ui.lastMonth) || '2026-05';
      var p = last.split('-').map(Number);
      this.state.year = p[0]; this.state.month = p[1]; this.state.key = last;
      this.bindToolbar();
      this.bindSheet();
      this.refresh();
      var self = this;
      // 레이아웃이 안정된 뒤 화면맞춤(초기 캔버스 너비 0 방지)
      root.requestAnimationFrame(function () { root.requestAnimationFrame(function () { WS.Print.fit(); }); });
      root.addEventListener('load', function () { WS.Print.fit(); });
      root.addEventListener('resize', function () { WS.Print.reapply(); });
      root.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          var mr = $('modal-root');
          if (mr && mr.firstChild) { e.preventDefault(); WS.Editor.close(); return; }
        }
        var t = e.target, tag = t && t.tagName;
        var typing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (t && t.isContentEditable);
        if ((e.ctrlKey || e.metaKey) && (e.key === 'z' || e.key === 'Z') && !typing) { e.preventDefault(); self.undo(); }
      });
      this.updateMonthLabel();
    },

    // 동기화/초기화 후 데이터 재적용 + 마지막 달로 이동
    reloadData: function () {
      this.state.data = WS.Store.data;
      var last = (WS.Store.data.ui && WS.Store.data.ui.lastMonth) || WS.Store.savedMonthKeys()[0] || '2026-05';
      var p = last.split('-').map(Number);
      this.go(p[0], p[1]);
    },

    undo: function () {
      if (WS.Store.undo()) { this.state.data = WS.Store.data; this.refresh(); this.toast('실행취소했습니다.'); }
      else this.toast('되돌릴 작업이 없습니다.');
    },

    savePng: function () {
      var self = this;
      this.toast('이미지 생성 중...');
      var name = (this.state.data.meta.dept || '') + '_' + (this.state.data.meta.author || '') + '_' + this.state.year + '년_' + this.state.month + '월_업무일정표.png';
      name = name.replace(/\s+/g, '');
      WS.Print.png(name).then(function () { self.toast('PNG로 저장했습니다.'); })
        .catch(function (e) { console.error('[savePng] %s', e && e.message); self.toast(e && e.message || 'PNG 저장 실패'); });
    },

    setMonth: function (y, m) {
      this.state.year = y; this.state.month = m; this.state.key = WS.monthKey(y, m);
      this.state.data.ui = this.state.data.ui || {};
      this.state.data.ui.lastMonth = this.state.key;
      WS.Store.save();
    },

    go: function (y, m) {
      this.setMonth(y, m);
      this.refresh();
      WS.Print.fit();
    },

    prev: function () {
      var m = this.state.month - 1, y = this.state.year;
      if (m < 1) { m = 12; y -= 1; }
      this.go(y, m);
    },
    next: function () {
      var m = this.state.month + 1, y = this.state.year;
      if (m > 12) { m = 1; y += 1; }
      this.go(y, m);
    },
    today: function () {
      var d = new Date();
      this.go(d.getFullYear(), d.getMonth() + 1);
    },

    updateMonthLabel: function () {
      var lbl = $('month-label');
      if (lbl) lbl.textContent = this.state.year + '년 ' + this.state.month + '월';
      var saved = !!this.state.data.months[this.state.key];
      var badge = $('save-badge');
      if (badge) badge.textContent = saved ? '저장됨' : '새 달(미입력)';
      var undoBtn = $('btn-undo');
      if (undoBtn) undoBtn.disabled = !WS.Store.canUndo();
    },

    refresh: function () {
      WS.renderSheet($('sheet'), this.state);
      this.updateMonthLabel();
      WS.Print.reapply();
    },

    toast: function (msg) {
      var t = $('toast');
      if (!t) return;
      t.textContent = msg;
      t.classList.add('show');
      clearTimeout(this._tt);
      this._tt = setTimeout(function () { t.classList.remove('show'); }, 2200);
    },

    bindToolbar: function () {
      var self = this;
      $('btn-prev').addEventListener('click', function () { self.prev(); });
      $('btn-next').addEventListener('click', function () { self.next(); });
      $('btn-today').addEventListener('click', function () { self.today(); });
      $('month-label').addEventListener('click', function () { WS.Editor.openMonths(); });
      $('btn-add').addEventListener('click', function () {
        var d = new Date();
        var day = (d.getFullYear() === self.state.year && d.getMonth() + 1 === self.state.month) ? d.getDate() : 1;
        WS.Editor.openDay(self.state.year + '-' + pad(self.state.month) + '-' + pad(day));
      });
      $('btn-settings').addEventListener('click', function () { WS.Editor.openSettings(); });
      $('btn-search').addEventListener('click', function () { WS.Editor.openSearch(); });
      $('btn-stats').addEventListener('click', function () { WS.Editor.openStats(); });
      $('btn-shift').addEventListener('click', function () { WS.Editor.openShifts(); });
      $('btn-undo').addEventListener('click', function () { self.undo(); });
      $('btn-png').addEventListener('click', function () { self.savePng(); });
      $('btn-print').addEventListener('click', function () { WS.Print.print(); });
      $('btn-export').addEventListener('click', function () { self.exportData(); });
      $('btn-import').addEventListener('click', function () { $('file-input').click(); });
      $('file-input').addEventListener('change', function (e) { self.importData(e); });
      $('btn-zin').addEventListener('click', function () { WS.Print.zoomIn(); });
      $('btn-zout').addEventListener('click', function () { WS.Print.zoomOut(); });
      $('btn-zfit').addEventListener('click', function () { WS.Print.fit(); });
    },

    bindSheet: function () {
      var self = this;
      var sheet = $('sheet');
      sheet.addEventListener('click', function (e) {
        if (e.target.closest('.prog-cell')) return; // 진행률 셀은 인라인 편집
        var cell = e.target.closest('.cell[data-date]');
        if (cell) WS.Editor.openDay(cell.getAttribute('data-date'));
      });
      // 진행률 셀 인라인 편집 저장
      sheet.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && e.target.classList.contains('prog-cell')) { e.preventDefault(); e.target.blur(); }
      });
      sheet.addEventListener('focusout', function (e) {
        if (!e.target.classList || !e.target.classList.contains('prog-cell')) return;
        var cid = e.target.getAttribute('data-cat');
        var week = Number(e.target.getAttribute('data-week'));
        var n = parseInt(String(e.target.textContent).replace(/[^0-9]/g, ''), 10);
        if (isNaN(n)) n = 0;
        n = Math.max(0, Math.min(100, n));
        var month = WS.Store.getMonth(self.state.key, true);
        month.progressOverride = month.progressOverride || {};
        month.progressOverride[cid] = month.progressOverride[cid] || [];
        month.progressOverride[cid][week] = n;
        WS.Store.save();
        self.refresh();
      });
    },

    exportData: function () {
      try {
        var json = WS.Store.exportJSON();
        var blob = new root.Blob([json], { type: 'application/json' });
        var url = root.URL.createObjectURL(blob);
        var a = doc.createElement('a');
        var d = new Date();
        a.href = url;
        a.download = '업무일정표_데이터_' + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + '.json';
        doc.body.appendChild(a); a.click(); doc.body.removeChild(a);
        root.URL.revokeObjectURL(url);
        this.toast('JSON 파일로 내보냈습니다.');
      } catch (e) {
        console.error('[exportData] 실패: %s', e && e.message);
        this.toast('내보내기에 실패했습니다.');
      }
    },

    importData: function (e) {
      var self = this;
      var file = e.target.files && e.target.files[0];
      if (!file) return;
      if (!root.confirm('현재 데이터를 가져온 파일로 덮어씁니다. 계속할까요? (먼저 내보내기로 백업을 권장)')) {
        e.target.value = ''; return;
      }
      var reader = new root.FileReader();
      reader.onload = function () {
        try {
          WS.Store.importJSON(String(reader.result));
          self.state.data = WS.Store.data;
          var last = (WS.Store.data.ui && WS.Store.data.ui.lastMonth) || WS.Store.savedMonthKeys()[0] || '2026-05';
          var p = last.split('-').map(Number);
          self.go(p[0], p[1]);
          self.toast('데이터를 가져왔습니다.');
        } catch (err) {
          console.error('[importData] 실패: %s', err && err.message);
          root.alert('가져오기 실패: ' + (err && err.message));
        }
        e.target.value = '';
      };
      reader.onerror = function () { root.alert('파일을 읽지 못했습니다.'); e.target.value = ''; };
      reader.readAsText(file, 'utf-8');
    }
  };

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', function () { WS.App.init(); });
  } else {
    WS.App.init();
  }
})(typeof window !== 'undefined' ? window : globalThis);
