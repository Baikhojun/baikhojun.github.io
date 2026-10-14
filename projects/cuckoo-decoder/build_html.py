# -*- coding: utf-8 -*-
import json
DB = json.load(open('/home/claude/out/cuckoo-products.json', encoding='utf-8'))
slim = []
for r in DB:
    slim.append({
        "m": r["model"], "hp": r["pressure"], "dz": r["design"], "ht": r["heating"],
        "tp": r["twin_pressure"], "ls": r["low_sugar"], "pc": r["pot_code"],
        "pt": r["pot"], "pg": r["pot_grade"], "vr": r["variant"], "cp": r["capacity"],
        "dc": r["dist_code"], "dp": r["display"], "cl": r["color"], "sf": r["suffix"],
        "lp": r["list_price"], "sp": r["sale_price"], "dr": r["discount_rate"],
        "ct": r["categories"], "st": r["status"], "cf": r["confidence"],
        "fl": r["flags"], "of": r["official_features"],
    })

HTML = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>쿠쿠 밥솥 모델코드 해독기</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
:root{
  --steel:#E9ECEF; --steel-2:#DCE1E5; --line:#C3CBD1; --line-2:#AEB8C0;
  --ink:#13171A; --muted:#69737B; --paper:#FBFCFC;
  --lcd:#0D2A25; --lcd-2:#123B33; --lcd-fg:#9CE6C7; --lcd-dim:#4E8A76;
  --seal:#A81E27; --brass:#B0803A; --ok:#1F6F52;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--steel);
  background-image:repeating-linear-gradient(90deg,rgba(255,255,255,.5) 0 1px,transparent 1px 3px);
  color:var(--ink);
  font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Malgun Gothic",sans-serif;
  font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:880px;margin:0 auto;padding:28px 18px 80px}

/* ── 헤더 ── */
.mast{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;
  border-bottom:2px solid var(--ink);padding-bottom:10px;margin-bottom:26px;flex-wrap:wrap}
.mast h1{margin:0;font-size:20px;font-weight:800;letter-spacing:-.02em}
.mast .sub{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.04em}

/* ── 입력 ── */
.console{background:var(--paper);border:1px solid var(--line);
  box-shadow:0 1px 0 #fff inset,0 2px 6px rgba(20,30,40,.06);padding:18px;position:relative}
.console label{display:block;font-size:11px;font-weight:700;letter-spacing:.12em;
  color:var(--muted);text-transform:uppercase;margin-bottom:8px}
.inrow{display:flex;gap:8px}
#q{flex:1;font-family:var(--mono);font-size:19px;font-weight:600;letter-spacing:.06em;
  padding:12px 14px;border:2px solid var(--line-2);background:#fff;color:var(--ink);
  text-transform:uppercase;min-width:0}
#q:focus{outline:none;border-color:var(--lcd);box-shadow:0 0 0 3px rgba(13,42,37,.12)}
#q::placeholder{color:#B2BBC2;font-weight:400;letter-spacing:.04em}
.btn{font-family:inherit;font-size:14px;font-weight:700;padding:12px 18px;cursor:pointer;
  border:2px solid var(--ink);background:var(--ink);color:#fff;white-space:nowrap}
.btn:hover{background:#000}
.btn.ghost{background:#fff;color:var(--ink)}
.btn.ghost:hover{background:var(--steel-2)}
.hint{margin-top:9px;font-size:12px;color:var(--muted)}
.hint b{font-family:var(--mono);color:var(--ink);font-weight:600;cursor:pointer;border-bottom:1px dotted var(--line-2)}
.hint b:hover{color:var(--seal)}
#ac{position:absolute;left:18px;right:18px;top:100%;margin-top:-6px;z-index:30;
  background:#fff;border:2px solid var(--ink);max-height:280px;overflow:auto;display:none}
#ac div{padding:8px 12px;font-family:var(--mono);font-size:13px;cursor:pointer;
  display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid var(--steel-2)}
#ac div:hover,#ac div.on{background:var(--lcd);color:var(--lcd-fg)}
#ac span{font-family:Pretendard,sans-serif;font-size:11px;opacity:.7}

/* ── 시그니처: 코드 해부 스트립 ── */
.anat{margin-top:26px}
.anat-head{display:flex;align-items:baseline;gap:10px;margin-bottom:10px}
.anat-head h2{margin:0;font-size:13px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.anat-head .note{font-size:12px;color:var(--muted)}
.strip{display:flex;flex-wrap:wrap;gap:5px;align-items:stretch}
.seg{background:#fff;border:1.5px solid var(--line-2);min-width:46px;position:relative;
  animation:pop .32s cubic-bezier(.2,.9,.3,1.2) backwards}
.seg .ch{display:block;font-family:var(--mono);font-size:22px;font-weight:700;letter-spacing:.04em;
  text-align:center;padding:9px 9px 4px}
.seg .lb{display:block;font-size:9.5px;font-weight:700;text-align:center;padding:0 6px 6px;
  color:var(--muted);letter-spacing:.02em;white-space:nowrap}
.seg.key{border-color:var(--lcd);border-width:2px;background:#F3FAF7}
.seg.key .ch{color:var(--lcd)}
.seg.key .lb{color:var(--lcd)}
.seg.warn{border-color:var(--seal);background:#FDF4F4}
.seg.warn .ch,.seg.warn .lb{color:var(--seal)}
.seg.mute{opacity:.5}
@keyframes pop{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
.legend{margin-top:10px;display:grid;gap:5px}
.legend div{display:grid;grid-template-columns:56px 1fr;gap:10px;font-size:13px;
  padding:5px 0;border-top:1px solid var(--steel-2)}
.legend .k{font-family:var(--mono);font-weight:700;font-size:13px}
.legend .v strong{font-weight:700}
.legend .v em{font-style:normal;color:var(--muted)}

/* ── LCD 판정 패널 ── */
.lcd{margin-top:24px;background:var(--lcd);
  background-image:linear-gradient(var(--lcd-2),var(--lcd));
  border:3px solid #061815;padding:18px 20px;color:var(--lcd-fg);
  box-shadow:0 0 0 1px rgba(255,255,255,.25) inset}
.lcd .tag{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;color:var(--lcd-dim);margin-bottom:6px}
.lcd .title{font-size:23px;font-weight:800;letter-spacing:-.01em;line-height:1.25}
.lcd .line{margin-top:12px;display:flex;flex-wrap:wrap;gap:7px}
.chip{border:1px solid var(--lcd-dim);padding:3px 9px;font-size:12px;font-weight:600;border-radius:2px}
.chip.on{background:var(--lcd-fg);color:var(--lcd);border-color:var(--lcd-fg)}
.chip.off{opacity:.42;text-decoration:line-through}
.lcd .meta{margin-top:14px;padding-top:12px;border-top:1px dashed var(--lcd-dim);
  display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:12px}
.lcd .meta div span{display:block;font-size:10.5px;color:var(--lcd-dim);letter-spacing:.08em}
.lcd .meta div b{display:block;font-size:15px;font-weight:700;margin-top:2px}

/* ── 카드 ── */
.card{margin-top:22px;background:var(--paper);border:1px solid var(--line);padding:18px}
.card h3{margin:0 0 4px;font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.card .cap{font-size:12px;color:var(--muted);margin-bottom:14px}

/* 가격 게이지 */
.gauge{position:relative;height:38px;background:var(--steel-2);border:1px solid var(--line-2);margin:22px 0 8px}
.gauge .zone{position:absolute;top:0;bottom:0}
.gauge .z-good{background:rgba(31,111,82,.24)}
.gauge .z-ok{background:rgba(176,128,58,.22)}
.gauge .z-bad{background:rgba(168,30,39,.16)}
.gauge .mk{position:absolute;top:-9px;bottom:-9px;width:2px;background:var(--ink)}
.gauge .mk b{position:absolute;top:-19px;left:50%;transform:translateX(-50%);
  font-family:var(--mono);font-size:10.5px;font-weight:700;white-space:nowrap;background:var(--ink);color:#fff;padding:1px 5px}
.glab{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);font-family:var(--mono)}
.prices{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1px;
  background:var(--line);border:1px solid var(--line);margin-top:16px}
.prices div{background:#fff;padding:11px 13px}
.prices span{display:block;font-size:11px;color:var(--muted);letter-spacing:.05em}
.prices b{display:block;font-family:var(--mono);font-size:18px;font-weight:700;margin-top:3px}
.prices b.good{color:var(--ok)} .prices b.bad{color:var(--seal)} .prices b.strike{text-decoration:line-through;color:var(--muted);font-size:15px}

/* 표 */
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);
  padding:7px 8px;border-bottom:2px solid var(--ink);white-space:nowrap}
td{padding:8px;border-bottom:1px solid var(--steel-2);vertical-align:top}
td.mono,th.mono{font-family:var(--mono)}
tr.self td{background:#F3FAF7;font-weight:700}
tr.cheap td.p{color:var(--ok);font-weight:700}
tr:hover td{background:var(--steel)}
.lnk{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line-2);cursor:pointer}
.lnk:hover{color:var(--seal);border-color:var(--seal)}

/* 알림 */
.alert{margin-top:18px;border-left:4px solid var(--seal);background:#FDF5F5;padding:12px 14px;font-size:13px}
.alert.warn{border-color:var(--brass);background:#FCF8F0}
.alert.info{border-color:var(--lcd);background:#F2F8F6}
.alert b{display:block;margin-bottom:3px}
.alert ul{margin:6px 0 0;padding-left:18px}

/* 브라우저 */
.filters{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.filters button{font:inherit;font-size:12px;font-weight:600;padding:5px 11px;cursor:pointer;
  border:1.5px solid var(--line-2);background:#fff;color:var(--muted)}
.filters button.on{border-color:var(--ink);background:var(--ink);color:#fff}
.scroll{max-height:460px;overflow:auto;border:1px solid var(--steel-2)}
.scroll table{font-size:12.5px}
.scroll th{position:sticky;top:0;background:var(--paper);z-index:2}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:11.5px;color:var(--muted)}
.empty{padding:36px 10px;text-align:center;color:var(--muted)}
.empty b{display:block;font-size:15px;color:var(--ink);margin-bottom:6px}
@media(max-width:560px){
  .lcd .title{font-size:19px}
  .seg .ch{font-size:18px;padding:7px 6px 3px}
  .seg{min-width:38px}
  .mast h1{font-size:17px}
}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<div class="wrap">

  <div class="mast">
    <h1>쿠쿠 밥솥 모델코드 해독기</h1>
    <div class="sub">206 MODELS · 2026-08 · CUCKOO OFFICIAL</div>
  </div>

  <div class="console">
    <label for="q">모델명을 입력하세요</label>
    <div class="inrow">
      <input id="q" placeholder="CRP-DHP0610FD" autocomplete="off" spellcheck="false">
      <button class="btn" id="go">해독</button>
    </div>
    <div class="hint">
      등록되지 않은 새 모델도 코드 규칙으로 해독합니다. 예시:
      <b data-ex="CRP-DHP0610FD">CRP-DHP0610FD</b> ·
      <b data-ex="CRP-LHTR0610FWM">CRP-LHTR0610FWM</b> ·
      <b data-ex="CRP-DHAS069FB">CRP-DHAS069FB</b> ·
      <b data-ex="CRP-ST0615FGSM">CRP-ST0615FGSM</b>
    </div>
    <div id="ac"></div>
  </div>

  <div id="result"></div>

  <div class="card" style="margin-top:34px">
    <h3>전체 모델 훑어보기</h3>
    <div class="cap">쿠쿠 공식몰 기준 206개. 가격 낮은 순. 모델명을 누르면 해독합니다.</div>
    <div class="filters" id="filters"></div>
    <div class="scroll"><table id="browse"></table></div>
  </div>

  <footer>
    데이터 출처: 쿠쿠 공식몰(cuckoo.co.kr) 카테고리 페이지, 2026년 8월 수집 · 대용량밥솥 제외<br>
    가격은 공식몰 표기 기준이며 실제 판매가는 시점과 채널에 따라 달라집니다. 구매 전 반드시 현재 가격을 직접 확인하세요.<br>
    최대기압 · 에너지효율등급 · 소비전력은 모델명 코드에 포함되지 않아 이 도구로 판별할 수 없습니다.
  </footer>
</div>

<script>
const DB = __DB__;

/* ═══ 코드 테이블 ═══ */
const DESIGN={AH:["A형","구형 라인"],BH:["B형","구형 라인"],CH:["C형","10인용 주력"],
 DH:["D형","6인용 주력"],EH:["E형","3인용 전용"],FH:["F형","중상급"],JH:["J형","중급"],
 KH:["K형","트윈프레셔 중상급"],LH:["L형","마스터셰프"],MH:["M형","쁘띠/소용량"],
 NH:["N형","사일런스"],OH:["O형","사일런스 오브제"],PH:["P형","사일런스 프로"],
 QH:["Q형","사일런스 큐브"],BDH:["BD형","타철명장"],BCH:["BC형","타철명장"]};
const DESIGN_OLD={HQ:["HQ형","구형"],HU:["HU형","구형"],HV:["HV형","구형"],HW:["HW형","구형"],HM:["HM형","구형"]};
const PLATE={ST:[1,"더 라이트"],UT:[1,"사일런스 어반"],TT:[1,"트윈프레셔 미니"],RT:[1,"열판 트윈프레셔"],
 QK:[0,"Q형 열판압력"],PK:[0,"P형 열판압력"],RK:[0,"R형 열판압력"],P:[0,"P형 열판압력"],
 R:[0,"R형 열판압력"],T:[0,"미니 열판압력"]};
const POT=[["AS","올스테인리스 무코팅 (와이드앤플랫)",5],["AR","올스테인리스 무코팅 (라운드)",5],
 ["XB","일반 코팅 (다이아 계열)",1],["R","투톤코팅 + 라운드(커브드)",4],["S","하단 투톤코팅 (에코스텐)",3],
 ["P","스테인리스 외피 코팅내솥",2],["B","일반 코팅 (다이아쉴드/블랙)",1],["F","타철명장/플랫 (구형)",1]];
const VAR={NL:"구세대 변형",FF:"신세대 변형 (2026)"};
const DISP={F:"LCD(퍼지) 디스플레이",S:"일반 숫자·램프 표시",B:"버튼식·일반 표시",M:"구형 소형 표시"};
const COLOR={W:"화이트",S:"실버",B:"블랙",D:"다크실버",G:"그레이",I:"아이보리",P:"핑크",
 T:"테라코타",R:"로즈/레드",C:"캐비어블루",GW:"그레이스화이트",GB:"그레이스블랙",
 GI:"그레이스아이보리",GG:"어반그레이",MG:"메탈릭그린",LB:"루미다크실버",GPS:"그레이스핑크실버",
 WS:"화이트스톤",BS:"블랙실버",BB:"블랙브라운",WG:"화이트그레이",GS:"그레이실버",LS:"루미실버",
 PS:"핑크실버",BE:"베이지(추정)",BD:"다크블랙(추정)",PP:"핑크",WM:"화이트무광(추정)",
 DB:"다크블랙(추정)",V:"바이올렛(추정)",UG:"미확정",E:"미확정",EL:"미확정",SDB:"미확정",FR:"미확정"};
const CAP={"01":1,"02":2,"03":3,"04":4,"06":6,"08":8,"10":10,"35":35};

/* ═══ 디코더 ═══ */
function decode(raw){
  let m=(raw||"").toUpperCase().replace(/\s/g,"").replace(/\(.*?\)$/,"");
  if(m && !m.includes("-")){ const g=m.match(/^(CRP|CR)(.+)$/); if(g) m=g[1]+"-"+g[2]; }
  const R={input:raw,model:m,seg:[],flags:[],ok:true};
  let core;
  if(m.startsWith("CRP-")){R.pressure="전기압력밥솥";core=m.slice(4);R.seg.push(["CRP","압력식",1]);}
  else if(m.startsWith("CR-")){R.pressure="전기보온밥솥 (비압력)";core=m.slice(3);R.seg.push(["CR","비압력",1]);}
  else{R.ok=false;R.err="CRP- 또는 CR- 로 시작하는 쿠쿠 밥솥 모델명이 아닙니다.";return R;}

  const di=core.search(/\d/);
  if(di<0){R.ok=false;R.err="용량 숫자를 찾을 수 없습니다. 모델명이 잘렸는지 확인하세요.";return R;}
  let L=core.slice(0,di), rest=core.slice(di);

  if(R.pressure.includes("비압력")){
    R.design="-";R.designNote="보온 전용";R.heating="비압력 (열판 보온)";
    R.twin=false;R.low=false;R.potCode="-";R.pot="논스틱 코팅 (기본)";R.potGrade=0;R.variant="";
  }else{
    let d=null;
    if(DESIGN[L.slice(0,3)]){d=DESIGN[L.slice(0,3)];R.seg.push([L.slice(0,3),"디자인+IH",2]);L=L.slice(3);R.heating="IH 압력";}
    else if(DESIGN[L.slice(0,2)]){d=DESIGN[L.slice(0,2)];R.seg.push([L.slice(0,2),"디자인+IH",2]);L=L.slice(2);R.heating="IH 압력";}
    else if(DESIGN_OLD[L.slice(0,2)]){d=DESIGN_OLD[L.slice(0,2)];R.seg.push([L.slice(0,2),"디자인(구형)",2]);L=L.slice(2);R.heating="IH 압력";R.flags.push("구형 명명체계(H가 앞) 모델입니다. 세부 스펙은 상세페이지 확인을 권합니다.");}
    else{
      const ks=Object.keys(PLATE).sort((a,b)=>b.length-a.length);
      for(const k of ks) if(L.startsWith(k)){d=[k+"형",PLATE[k][1]];R.seg.push([k,"디자인(열판)",2]);L=L.slice(k.length);R.heating="열판 압력";R._pt=!!PLATE[k][0];break;}
    }
    if(!d){R.ok=false;R.err="디자인 코드를 인식하지 못했습니다: "+L+" — 신규 코드이거나 오타일 수 있습니다.";return R;}
    R.design=d[0];R.designNote=d[1];

    R.variant="";
    for(const v in VAR) if(L.includes(v)){R.variant=v;R.seg.push([v,"세대 변형",4]);L=L.replace(v,"");}

    let tp=!!R._pt, ls=false;
    if(L.startsWith("T")){tp=true;R.seg.push(["T","트윈프레셔",1]);L=L.slice(1);}
    else if(L.startsWith("L")){ls=true;tp=true;R.seg.push(["L","저당취사",1]);L=L.slice(1);}
    R.twin=tp;R.low=ls;

    let pot=POT.find(p=>L.startsWith(p[0]));
    if(pot){R.potCode=pot[0];R.pot=pot[1];R.potGrade=pot[2];R.seg.push([pot[0],"내솥",1]);L=L.slice(pot[0].length);}
    else{R.potCode="-";R.pot="미표기 (기본 코팅)";R.potGrade=0;}
    if(L){R.flags.push("해독하지 못한 문자가 남았습니다: "+L);R.seg.push([L,"미해독",3]);}
  }

  const dm=rest.match(/^(\d+)/); const digits=dm[1]; let tail=rest.slice(digits.length);
  const capc=digits.slice(0,2);
  R.capacity=CAP[capc]||null;
  R.seg.push([capc,"용량",1]);
  if(!R.capacity) R.flags.push("용량 코드를 알 수 없습니다: "+capc);
  R.dist=digits.slice(2);
  if(R.dist) R.seg.push([R.dist,"유통(무시)",0]);

  R.suffix="";
  if(tail.length>2 && tail.endsWith("M") && !COLOR[tail]){R.suffix="M";tail=tail.slice(0,-1);}
  if(tail.length>1 && DISP[tail[0]] && COLOR[tail.slice(1)]){
    R.dispCode=tail[0];R.disp=DISP[tail[0]];R.colorCode=tail.slice(1);R.color=COLOR[tail.slice(1)];
    R.seg.push([tail[0],"표시창",1]);R.seg.push([tail.slice(1),"색상",0]);
  }else if(COLOR[tail]){
    R.dispCode="-";R.disp="표시창 코드 생략";R.colorCode=tail;R.color=COLOR[tail];
    R.seg.push([tail,"색상",0]);
  }else if(tail){
    R.dispCode=tail[0];R.disp=DISP[tail[0]]||"미상";R.colorCode=tail.slice(1);
    R.color=COLOR[tail.slice(1)]||"미등록 색상";
    R.seg.push([tail[0],"표시창",1]);if(tail.slice(1))R.seg.push([tail.slice(1),"색상",0]);
    if(!COLOR[tail.slice(1)]) R.flags.push("색상 코드가 사전에 없습니다: "+tail.slice(1)+" (성능과 무관)");
  }else{R.dispCode="-";R.disp="-";R.colorCode="-";R.color="-";}
  if(R.suffix) R.seg.push(["M","서픽스",4]);
  return R;
}

/* ═══ 유틸 ═══ */
const W=n=>n==null?"—":n.toLocaleString("ko-KR")+"원";
const med=a=>{const s=[...a].sort((x,y)=>x-y);const h=s.length>>1;return s.length%2?s[h]:Math.round((s[h-1]+s[h])/2);};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function peersOf(d){
  let p=DB.filter(r=>r.sp&&r.ht===d.heating&&r.tp===d.twin&&r.ls===d.low&&r.pc===d.potCode&&r.cp===d.capacity);
  let lvl="같은 가열방식·압력선택·내솥·용량";
  if(p.length<2){p=DB.filter(r=>r.sp&&r.ht===d.heating&&r.tp===d.twin&&r.ls===d.low&&r.cp===d.capacity);lvl="같은 가열방식·압력선택·용량";}
  if(p.length<2){p=DB.filter(r=>r.sp&&r.ht===d.heating&&r.cp===d.capacity);lvl="같은 가열방식·용량";}
  return {list:p,level:lvl};
}

/* ═══ 결과 렌더 ═══ */
function render(raw){
  const box=document.getElementById("result");
  const d=decode(raw);
  if(!d.ok){
    box.innerHTML=`<div class="card"><div class="empty"><b>해독할 수 없습니다</b>${esc(d.err)}<br><br>
      모델명은 밥솥 앞면 또는 바닥 라벨에 있습니다. 예: CRP-DHP0610FD</div></div>`;
    box.scrollIntoView({behavior:"smooth",block:"start"});return;
  }
  const hit=DB.find(r=>r.m===d.model);
  const {list:peers,level}=peersOf(d);
  const base=peers.length?med(peers.map(r=>r.sp)):null;
  const target=base?Math.round(base*0.87/1000)*1000:null;
  const cap=base?Math.round(base*1.12/1000)*1000:null;
  const H=[];

  /* 코드 해부 */
  const cls=["mute","","key","warn","warn"];
  H.push(`<div class="anat"><div class="anat-head"><h2>코드 해부</h2>
    <span class="note">초록 = 성능을 결정하는 자리 · 회색 = 무시해도 되는 자리</span></div>
    <div class="strip">${d.seg.map((s,i)=>
      `<div class="seg ${cls[s[2]]}" style="animation-delay:${i*45}ms">
        <span class="ch">${esc(s[0])}</span><span class="lb">${esc(s[1])}</span></div>`).join("")}</div>`);

  const rows=[["CRP/CR",d.pressure,""],
    [d.design,`<strong>${esc(d.designNote)}</strong>`,""],
    ["가열",`<strong>${esc(d.heating)}</strong>`, d.heating.startsWith("IH")?"내솥 전체를 유도가열. 2기압 이상 가능":"바닥만 가열. 1.7~1.8기압"],
    ["압력선택",d.twin?"<strong>트윈프레셔 있음</strong>":"없음",d.twin?"고압/무압 선택. 볶음밥·냉동밥에 유리":"압력 고정"],
    ["저당",d.low?"<strong>저당취사 있음</strong>":"없음",d.low?"트레이로 밥물 배출. 찰기는 줄어듦":""],
    [d.potCode,`<strong>${esc(d.pot)}</strong>`,d.potGrade?`내솥 등급 ${d.potGrade}/5`:""],
    ["용량",d.capacity?`<strong>${d.capacity}인용</strong>`:"미상",""],
    ["표시창",esc(d.disp),""],["색상",esc(d.color),"성능과 무관"]];
  if(d.variant) rows.splice(5,0,[d.variant,`<strong>${VAR[d.variant]}</strong>`,"의미 미확정. 같은 스펙 쌍이 존재"]);
  if(d.suffix) rows.push(["M","서픽스","가격·스펙 동일 확인. 외관 변형 추정"]);
  H.push(`<div class="legend">${rows.map(r=>
    `<div><span class="k">${esc(r[0])}</span><span class="v">${r[1]}${r[2]?` <em>— ${esc(r[2])}</em>`:""}</span></div>`).join("")}</div></div>`);

  /* LCD */
  const chips=[["IH 가열",d.heating.startsWith("IH")],["트윈프레셔",d.twin],["저당취사",d.low],
    ["올스테인리스",d.potCode==="AS"||d.potCode==="AR"],["라운드 내솥",d.potCode==="R"||d.potCode==="AR"]];
  H.push(`<div class="lcd"><div class="tag">${hit?"공식몰 등록 모델":"미등록 — 코드 규칙으로 해독"}</div>
    <div class="title">${esc(d.model)}</div>
    <div class="line">${chips.map(c=>`<span class="chip ${c[1]?"on":"off"}">${c[0]}</span>`).join("")}</div>
    <div class="meta">
      <div><span>용량</span><b>${d.capacity?d.capacity+"인용":"미상"}</b></div>
      <div><span>라인</span><b>${esc(d.designNote)}</b></div>
      <div><span>내솥 등급</span><b>${d.potGrade?d.potGrade+" / 5":"—"}</b></div>
      <div><span>상태</span><b>${hit?esc(hit.st):"미등록"}</b></div>
    </div></div>`);

  /* 가격 */
  if(base){
    const off=hit&&hit.sp?hit.sp:null;
    const lo=Math.round(base*0.70), hi=Math.round(base*1.35), span=hi-lo;
    const pct=v=>Math.max(0,Math.min(100,(v-lo)/span*100));
    const gt=pct(target), gc=pct(cap), gb=pct(base);
    H.push(`<div class="card"><h3>얼마면 살 만한가</h3>
      <div class="cap">${esc(level)}이 같은 공식몰 모델 ${peers.length}개의 중앙값을 기준으로 산출했습니다.</div>
      <div class="gauge">
        <div class="zone z-good" style="left:0;width:${gt}%"></div>
        <div class="zone z-ok" style="left:${gt}%;width:${gc-gt}%"></div>
        <div class="zone z-bad" style="left:${gc}%;right:0"></div>
        <div class="mk" style="left:${gb}%"><b>기준 ${W(base)}</b></div>
        ${off?`<div class="mk" style="left:${pct(off)}%;background:var(--seal)"><b style="background:var(--seal);top:auto;bottom:-19px">공식몰 ${W(off)}</b></div>`:""}
      </div>
      <div class="glab"><span>싸다</span><span>적정</span><span>비싸다</span></div>
      <div class="prices">
        ${hit&&hit.lp?`<div><span>쿠쿠 정가</span><b class="strike">${W(hit.lp)}</b></div>`:""}
        ${off?`<div><span>쿠쿠몰 할인가${hit.dr?" ("+hit.dr+"%↓)":""}</span><b>${W(off)}</b></div>`:""}
        <div><span>동급 기준가 (중앙값)</span><b>${W(base)}</b></div>
        <div><span>오픈마켓 목표가</span><b class="good">${W(target)} 이하</b></div>
        <div><span>이 이상이면 보류</span><b class="bad">${W(cap)}</b></div>
      </div>
      <div class="alert info"><b>목표가는 어떻게 나온 값인가</b>
        쿠쿠 공식몰 할인가는 정가 대비 평균 37% 낮습니다. 오픈마켓은 통상 공식몰보다 한 단계 더 저렴해,
        동급 중앙값의 약 87%를 현실적인 목표로 잡았습니다. 추정치이므로 참고선으로만 쓰세요.</div>
    </div>`);
  }

  /* 색상 형제 */
  if(hit){
    const stem=hit.m.slice(0,hit.m.length-(String(hit.cl).length>0?0:0));
    const pre=hit.m.replace(/[A-Z]*$/,"");
    const sib=DB.filter(r=>r.m!==hit.m&&r.m.startsWith(pre)&&r.cp===hit.cp&&r.pc===hit.pc&&r.tp===hit.tp);
    if(sib.length){
      const all=[hit,...sib].filter(r=>r.sp).sort((a,b)=>a.sp-b.sp);
      if(all.length>1&&all[all.length-1].sp-all[0].sp>0){
        H.push(`<div class="card"><h3>색상만 다른 같은 제품</h3>
          <div class="cap">성능은 동일합니다. 색상 선택만으로 ${W(all[all.length-1].sp-all[0].sp)} 차이가 납니다.</div>
          <table><thead><tr><th class="mono">모델</th><th>색상</th><th style="text-align:right">쿠쿠몰가</th></tr></thead><tbody>
          ${all.map(r=>`<tr class="${r.m===hit.m?"self":""} ${r.sp===all[0].sp?"cheap":""}">
            <td class="mono"><span class="lnk" data-go="${r.m}">${r.m}</span></td>
            <td>${esc(r.cl)}</td><td class="p" style="text-align:right">${W(r.sp)}</td></tr>`).join("")}
          </tbody></table></div>`);
      }
    }
  }

  /* 동급 대안 */
  if(peers.length>1){
    const sorted=peers.slice().sort((a,b)=>a.sp-b.sp).slice(0,8);
    H.push(`<div class="card"><h3>같은 스펙 다른 모델</h3>
      <div class="cap">${esc(level)}이 같습니다. 더 싼 게 있으면 굳이 비싼 걸 살 이유가 없습니다.</div>
      <table><thead><tr><th class="mono">모델</th><th>라인</th><th>색상</th><th style="text-align:right">쿠쿠몰가</th></tr></thead><tbody>
      ${sorted.map(r=>`<tr class="${r.m===d.model?"self":""} ${r.sp===sorted[0].sp?"cheap":""}">
        <td class="mono"><span class="lnk" data-go="${r.m}">${r.m}</span></td>
        <td>${esc(r.dz)}</td><td>${esc(r.cl)}</td>
        <td class="p" style="text-align:right">${W(r.sp)}</td></tr>`).join("")}
      </tbody></table></div>`);
  }

  /* 경고 */
  const al=[];
  if(d.variant==="NL") al.push("이 모델은 <b style='display:inline'>구세대(NL)</b>입니다. 신세대(FF) 짝이 있다면 정가는 같지만 NL 쪽에만 할인이 붙는 경우가 많아, 실구매가는 NL이 유리합니다. 다만 단종 수순이라 부품 수급을 감안하세요.");
  if(d.variant==="FF") al.push("이 모델은 <b style='display:inline'>신세대(FF)</b>입니다. 출시 초기라 할인이 거의 없습니다. 급하지 않다면 구세대(NL) 모델의 실구매가를 함께 비교해 보세요.");
  if(d.heating==="열판 압력"&&d.twin) al.push("트윈프레셔가 있지만 <b style='display:inline'>IH가 아닌 열판식</b>입니다. 이름과 기능만 보고 상급으로 오해하기 쉬운 지점입니다.");
  if(d.potCode==="AS"||d.potCode==="AR") al.push("올스테인리스 무코팅은 코팅 벗겨짐 걱정이 없는 대신 <b style='display:inline'>밥알이 잘 눌어붙어 세척이 번거롭습니다.</b> 세척 편의가 우선이라면 코팅 내솥을 고려하세요.");
  if(d.low) al.push("저당 취사는 제조사 기준 당질 30~40% 저감이며, 찰기와 단맛도 함께 줄어듭니다. 혈당 관리가 목적이라면 밥솥에만 의존하지 말고 의사·영양사 상담과 병행하세요.");
  if(hit&&hit.st!=="판매중") al.push(`공식몰 상태가 <b style='display:inline'>${esc(hit.st)}</b>입니다. 단종이 임박한 모델은 가격이 오히려 오르는 경우가 있습니다.`);
  d.flags.forEach(f=>al.push(esc(f)));
  al.push("모델명으로는 <b style='display:inline'>최대기압 · 에너지효율등급 · 소비전력</b>을 알 수 없습니다. 이 세 가지는 코드 체계에 없으니 상세페이지에서 확인하세요.");
  H.push(`<div class="alert warn"><b>확인하고 넘어갈 것</b><ul>${al.map(a=>`<li>${a}</li>`).join("")}</ul></div>`);

  box.innerHTML=H.join("");
  box.scrollIntoView({behavior:"smooth",block:"start"});
}

/* ═══ 자동완성 ═══ */
const q=document.getElementById("q"), ac=document.getElementById("ac");
let acIdx=-1, acList=[];
function showAC(){
  const v=q.value.toUpperCase().replace(/\s/g,"");
  if(v.length<2){ac.style.display="none";return;}
  acList=DB.filter(r=>r.m.includes(v)).slice(0,12);
  if(!acList.length){ac.style.display="none";return;}
  acIdx=-1;
  ac.innerHTML=acList.map((r,i)=>`<div data-i="${i}">${r.m}<span>${r.cp}인 · ${r.sp?W(r.sp):"가격없음"}</span></div>`).join("");
  ac.style.display="block";
}
q.addEventListener("input",showAC);
q.addEventListener("keydown",e=>{
  if(ac.style.display==="block"&&acList.length){
    if(e.key==="ArrowDown"||e.key==="ArrowUp"){
      e.preventDefault(); acIdx=(acIdx+(e.key==="ArrowDown"?1:-1)+acList.length)%acList.length;
      [...ac.children].forEach((c,i)=>c.classList.toggle("on",i===acIdx));
      ac.children[acIdx].scrollIntoView({block:"nearest"}); return;
    }
    if(e.key==="Enter"&&acIdx>=0){e.preventDefault();go(acList[acIdx].m);return;}
    if(e.key==="Escape"){ac.style.display="none";return;}
  }
  if(e.key==="Enter") go(q.value);
});
ac.addEventListener("click",e=>{const t=e.target.closest("[data-i]");if(t)go(acList[+t.dataset.i].m);});
document.addEventListener("click",e=>{if(!e.target.closest(".console"))ac.style.display="none";});

function go(v){q.value=v;ac.style.display="none";render(v);}
document.getElementById("go").onclick=()=>go(q.value);
document.body.addEventListener("click",e=>{
  const ex=e.target.closest("[data-ex]"); if(ex){go(ex.dataset.ex);return;}
  const g=e.target.closest("[data-go]"); if(g){go(g.dataset.go);}
});

/* ═══ 브라우저 ═══ */
const CATS=[["ALL","전체"],["TP","트윈프레셔"],["IH","IH압력"],["PL","열판압력"],
 ["WM","보온(비압력)"],["LS","저당"],["AS","올스테인리스"],["SI","사일런스"]];
let cur="ALL";
const fbox=document.getElementById("filters");
fbox.innerHTML=CATS.map(c=>`<button data-c="${c[0]}" class="${c[0]==="ALL"?"on":""}">${c[1]}</button>`).join("");
fbox.addEventListener("click",e=>{const b=e.target.closest("[data-c]");if(!b)return;
  cur=b.dataset.c;[...fbox.children].forEach(x=>x.classList.toggle("on",x===b));drawBrowse();});
function drawBrowse(){
  const rows=DB.filter(r=>cur==="ALL"||r.ct.includes(cur))
    .sort((a,b)=>(a.sp||a.lp||9e9)-(b.sp||b.lp||9e9));
  document.getElementById("browse").innerHTML=
   `<thead><tr><th class="mono">모델</th><th>라인</th><th>용량</th><th>가열</th><th>내솥</th><th style="text-align:right">쿠쿠몰가</th></tr></thead><tbody>`+
   rows.map(r=>`<tr><td class="mono"><span class="lnk" data-go="${r.m}">${r.m}</span></td>
    <td>${esc(r.dz)}</td><td>${r.cp}인</td>
    <td>${r.ht.startsWith("IH")?"IH":r.ht.startsWith("열판")?"열판":"비압력"}${r.tp?" · 트윈":""}${r.ls?" · 저당":""}</td>
    <td>${esc(r.pc)}</td><td style="text-align:right">${r.sp?W(r.sp):`<span style="color:var(--muted)">${W(r.lp)} (정가)</span>`}</td></tr>`).join("")+
   `</tbody>`;
}
drawBrowse();
render("CRP-DHP0610FD");
</script>
</body>
</html>"""

open('/home/claude/out/cuckoo-decoder.html','w',encoding='utf-8').write(
    HTML.replace("__DB__", json.dumps(slim, ensure_ascii=False, separators=(',',':')))
)
print("생성 완료:", len(slim), "모델")
