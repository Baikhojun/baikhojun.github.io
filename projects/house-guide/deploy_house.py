# -*- coding: utf-8 -*-
"""신혼부부 내집마련 정석 웹 배포본 생성 — 오프라인 HTML(원본)에 웹 서빙 전용 코드를 주입해 /house/ 구조로 출력.
- PC(index.html): 모바일 UA → m/ 자동 이동(?pc 로 우회, 해시 딥링크 유지) + 푸터 '모바일 버전 보기' + GoatCounter + 숨김 카운터
- 모바일(m/index.html): 푸터 'PC 버전 보기'(../?pc) + GoatCounter + 숨김 카운터
- file:// 로 열면(오프라인) 아무 요청도 하지 않음. 원본 파일은 수정하지 않는다.
사용법: python deploy_house.py <출력루트>   → <출력루트>/house/index.html, <출력루트>/house/m/index.html"""
import sys, os, glob

PC = sorted(glob.glob('신혼부부_내집마련_정석_2*.html'))[-1]
MO = sorted(glob.glob('신혼부부_내집마련_정석_모바일_*.html'))[-1]
out = sys.argv[1] if len(sys.argv) > 1 else '_deploy'

REDIRECT = r'''<script>
/* 웹 서빙일 때만: 모바일 기기는 m/ 으로 자동 이동 (?pc 로 우회, file:// 오프라인에서는 비활성, #딥링크 유지) */
(function(){try{
  if(location.protocol!=="http:"&&location.protocol!=="https:")return;
  if(/[?&]pc(=|&|$)/.test(location.search))return;
  if(!/Android|iPhone|iPod|Windows Phone|Mobile/i.test(navigator.userAgent))return;
  var p=location.pathname;
  if(/\/m\/?(index\.html)?$/.test(p))return;
  location.replace(p.replace(/[^\/]*$/,"")+"m/"+location.hash);
}catch(e){}
})();
</script>
'''
HITBOX = '<span id="hitbox" style="display:block;margin-top:8px;min-height:14px;color:transparent;user-select:all;-webkit-user-select:all;font-family:var(--mono);font-size:10px" aria-hidden="true"></span>'

def web_script(link_js):
    return r'''<script>
/* 웹 서빙일 때만: PC↔모바일 링크 + 방문자 집계(GoatCounter) + 드래그하면 보이는 숨김 카운터 (file:// 에서는 아무 요청 없음) */
(function(){
  if(location.protocol!=="http:"&&location.protocol!=="https:")return;
  ''' + link_js + r'''
  var gc=document.createElement("script");
  gc.setAttribute("data-goatcounter","https://unfade.goatcounter.com/count");
  gc.async=true;gc.src="https://gc.zgo.at/count.js";
  document.head.appendChild(gc);
  (async function(){
    var el=document.getElementById("hitbox");if(!el)return;
    var cnt=async function(p,qs){try{
      var r=await fetch("https://unfade.goatcounter.com/counter/"+p+".json"+(qs||""));
      if(!r.ok)return "-";
      return String((await r.json()).count||"-").replace(/[\s  ]/g,",");
    }catch(e){return "-"}};
    var d=new Date();
    var today=d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
    var r=await Promise.all([cnt("TOTAL"),cnt("TOTAL","?start="+today),cnt(location.pathname)]);
    el.textContent="UNFADE STATS · TODAY(전체) "+r[1]+" · 이 페이지 누적 "+r[2]+" · 사이트 전체 누적 "+r[0];
  })();
})();
</script>
'''

def inject(src, dst, is_pc):
    h = open(src, encoding='utf-8').read()
    assert h.count('</footer>') == 1 and h.count('</body></html>') == 1, src
    if is_pc:
        assert h.count('<title>') == 1
        h = h.replace('<title>', REDIRECT + '<title>', 1)
        link = '<span id="molink"></span>'
        js = ('var ml=document.getElementById("molink");'
              'if(ml)ml.innerHTML=\' · <a href="m/\'+location.hash+\'" style="color:inherit;font-weight:700">📱 모바일 버전 보기</a>\';')
    else:
        link = '<span id="pclink"></span>'
        js = ('var pl=document.getElementById("pclink");'
              'if(pl)pl.innerHTML=\'<br><a href="../?pc\'+location.hash+\'" style="color:inherit;font-weight:700">🖥️ PC 버전 보기</a>\';')
    h = h.replace('</footer>', link + '\n' + HITBOX + '\n</footer>', 1)
    h = h.replace('</body></html>', web_script(js) + '</body></html>', 1)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8', newline='\n').write(h)
    print('생성:', dst, len(h.encode('utf-8')), 'bytes  ←', src)

inject(PC, os.path.join(out, 'house', 'index.html'), True)
inject(MO, os.path.join(out, 'house', 'm', 'index.html'), False)
