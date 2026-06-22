// 이 파일의 역할: GitHub 저장소 동기화(Contents API) - 데이터 JSON 업로드/내려받기 (토큰은 별도 보관)
;(function (root) {
  'use strict';
  var WS = (root.WS = root.WS || {});
  WS.Sync = {};

  // UTF-8(한글) 안전 base64
  function b64encode(str) { return root.btoa(unescape(encodeURIComponent(str))); }
  function b64decode(b64) { return decodeURIComponent(escape(root.atob(String(b64).replace(/\s/g, '')))); }

  // *.github.io 호스트면 owner/repo 자동 추정
  WS.Sync.defaults = function () {
    var host = (root.location && root.location.hostname) || '';
    if (/\.github\.io$/.test(host)) return { owner: host.split('.')[0], repo: host, path: 'data/schedule-data.json', branch: 'main' };
    return { owner: '', repo: '', path: 'data/schedule-data.json', branch: 'main' };
  };
  WS.Sync.config = function () {
    var s = (WS.Store.data && WS.Store.data.sync) || {};
    var def = WS.Sync.defaults();
    return {
      owner: (s.owner || def.owner || '').trim(),
      repo: (s.repo || def.repo || '').trim(),
      path: (s.path || def.path || 'data/schedule-data.json').trim(),
      branch: (s.branch || def.branch || 'main').trim()
    };
  };

  function api(method, url, token, body) {
    var headers = { 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    return root.fetch('https://api.github.com' + url, {
      method: method, headers: headers, body: body ? JSON.stringify(body) : undefined
    });
  }
  function safeMsg(res) {
    return res.json().then(function (j) { return (j && j.message) || ''; }).catch(function () { return ''; });
  }
  function contentsPath(c) {
    var enc = c.path.split('/').map(encodeURIComponent).join('/');
    return '/repos/' + c.owner + '/' + c.repo + '/contents/' + enc;
  }

  // 업로드(저장): 기존 파일 sha 조회 후 PUT
  WS.Sync.upload = function (token) {
    var c = WS.Sync.config();
    if (!token) return Promise.reject(new Error('GitHub 토큰을 입력하세요.'));
    if (!c.owner || !c.repo) return Promise.reject(new Error('저장소(owner/repo)를 설정하세요.'));
    var path = contentsPath(c);
    return api('GET', path + '?ref=' + encodeURIComponent(c.branch), token).then(function (getRes) {
      if (getRes.status === 200) return getRes.json().then(function (j) { return j.sha; });
      if (getRes.status === 404) return null;
      return safeMsg(getRes).then(function (msg) { throw new Error('조회 실패(' + getRes.status + ') ' + msg); });
    }).then(function (sha) {
      var body = { message: 'update schedule data', content: b64encode(WS.Store.exportJSON()), branch: c.branch };
      if (sha) body.sha = sha;
      return api('PUT', path, token, body);
    }).then(function (putRes) {
      if (putRes.status === 200 || putRes.status === 201) return true;
      return safeMsg(putRes).then(function (msg) { throw new Error('업로드 실패(' + putRes.status + ') ' + msg); });
    });
  };

  // 내려받기(불러오기): 파일 조회 후 importJSON
  WS.Sync.download = function (token) {
    var c = WS.Sync.config();
    if (!c.owner || !c.repo) return Promise.reject(new Error('저장소(owner/repo)를 설정하세요.'));
    var path = contentsPath(c);
    return api('GET', path + '?ref=' + encodeURIComponent(c.branch), token).then(function (res) {
      if (res.status === 404) throw new Error('저장된 데이터 파일이 없습니다. 먼저 업로드하세요.');
      if (res.status !== 200) return safeMsg(res).then(function (msg) { throw new Error('내려받기 실패(' + res.status + ') ' + msg); });
      return res.json();
    }).then(function (j) {
      WS.Store.importJSON(b64decode(j.content));
      return true;
    });
  };
})(typeof window !== 'undefined' ? window : globalThis);
