# -*- coding: utf-8 -*-
"""cuckoo-decoder-mobile.html 생성 (모바일 앱 스타일 UI).
선행: python build_v3.py (cuckoo-products.json) + python build_weights.py (cuckoo-weights.json)
디코더·기준선·판정 로직은 build_html_v3.py 와 동일. 프레젠테이션만 모바일 전용."""
import json, glob
_d = sorted(glob.glob("snapshots/price-*.json"))[-1][-11:-5]
ASOF = "20" + _d[:2] + "-" + _d[2:4] + "-" + _d[4:]

DB = json.load(open('cuckoo-products.json', encoding='utf-8'))
WX = json.load(open('cuckoo-weights.json', encoding='utf-8'))
slim = []
for r in DB:
    slim.append({
        "m": r["model"], "nm": r["name"], "hp": r["pressure"], "dz": r["design"],
        "dcx": r["design_code"], "ht": r["heating"], "tp": r["twin_pressure"],
        "ls": r["low_sugar"], "si": r["silence"], "io": r["iot"], "og": r["old_gen"],
        "pc": r["pot_code"], "pt": r["pot"], "pg": r["pot_grade"], "vr": r["variant"],
        "cp": r["capacity"], "dp": r["display"], "cl": r["color"], "sf": r["suffix"],
        "lp": r["list_price"], "sp": r["sale_price"], "dr": r["discount_rate"],
        "rc": r["review_count"], "ct": r["categories"], "st": r["status"],
        "cf": r["confidence"], "fl": r["flags"], "rg": r["reg"], "am": r["age_months"],
        "sm": r["stem"], "px": [r["px_epic"], r["px_special"], r["px_fair"], r["px_ceiling"]],
        "nw": r["is_new"],
        "aw": r.get("atm"), "pw": r.get("power_w"), "eg": r.get("energy_grade"),
        "ph": r.get("hist") or [],
    })

HTML = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0D2A25">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>쿠쿠 해독기 v3 모바일</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
/* ═══════════ UNFADE. 쿠쿠 해독기 — Mobile · Light/Dark ═══════════ */
:root{
  --bg:#E7EAEE; --bg-hi:#F4F6F8; --bg-lo:#DDE2E7;
  --card:#FFFFFF; --card-2:#F7F9FA; --steel:#EEF1F3; --steel-2:#E1E6EA;
  --line:rgba(18,28,38,.10); --line-2:rgba(18,28,38,.24);
  --ink:#14181B; --ink-2:#333C42; --muted:#68737C;
  --lcd:#0C2823; --lcd-2:#123529; --lcd-fg:#9FE9C9; --lcd-dim:#528C77;
  --seal:#A81E27; --brass:#A67F3C; --ok:#1E7A57; --epic:#14532D; --warm:#B06A2A;
  --fair-tx:#7A5A20; --warm-tx:#8A4E17;
  --ok-bg:#ECF6F0; --epic-bg:#E9F4EB; --fair-bg:#FAF5E7; --warm-bg:#FAF0E4; --seal-bg:#FBEDEE; --info-bg:#EDF5F1;
  --gold1:#C7A057; --gold2:#8C6B2F;
  --sh-1:0 1px 2px rgba(15,23,32,.06),0 1px 1px rgba(15,23,32,.04);
  --sh-2:0 1px 2px rgba(15,23,32,.05),0 14px 34px -18px rgba(15,23,32,.28);
  --sh-3:0 2px 8px rgba(15,23,32,.10),0 24px 48px -20px rgba(15,23,32,.38);
  --glass:rgba(255,255,255,.72);
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --nav-h:62px;
  --sat:env(safe-area-inset-top,0px); --sab:env(safe-area-inset-bottom,0px);
  --tr:.2s cubic-bezier(.4,0,.2,1);
}
[data-theme="dark"]{
  --bg:#0E1114; --bg-hi:#14181C; --bg-lo:#0A0D0F;
  --card:#171C21; --card-2:#1C2227; --steel:#20262C; --steel-2:#2B333A;
  --line:rgba(255,255,255,.085); --line-2:rgba(255,255,255,.22);
  --ink:#E8ECEF; --ink-2:#C7CED4; --muted:#8C97A1;
  --lcd:#0B2621; --lcd-2:#123A2F; --lcd-fg:#A6F0D1; --lcd-dim:#5B977F;
  --seal:#E3596B; --brass:#CDA55F; --ok:#4CC08E; --epic:#63C287; --warm:#DB8F4E;
  --fair-tx:#DDC183; --warm-tx:#E8A96E;
  --ok-bg:rgba(60,170,120,.13); --epic-bg:rgba(70,160,100,.14); --fair-bg:rgba(190,150,70,.13);
  --warm-bg:rgba(205,125,60,.13); --seal-bg:rgba(225,85,100,.13); --info-bg:rgba(70,150,125,.13);
  --gold1:#E7C57F; --gold2:#B08F4C;
  --sh-1:0 1px 2px rgba(0,0,0,.45);
  --sh-2:0 1px 3px rgba(0,0,0,.5),0 16px 36px -18px rgba(0,0,0,.65);
  --sh-3:0 2px 8px rgba(0,0,0,.55),0 28px 56px -22px rgba(0,0,0,.75);
  --glass:rgba(18,23,27,.72);
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:
    radial-gradient(1200px 500px at 85% -10%, var(--bg-hi) 0%, transparent 60%),
    radial-gradient(900px 420px at -10% 30%, var(--bg-lo) 0%, transparent 55%),
    repeating-linear-gradient(90deg, rgba(127,127,127,.028) 0 1px, transparent 1px 3px),
    var(--bg);
  color:var(--ink);
  font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Malgun Gothic",sans-serif;
  font-size:15px;line-height:1.58;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
  padding-bottom:calc(var(--nav-h) + var(--sab) + 14px);
  overscroll-behavior-y:contain;
  transition:background-color var(--tr), color var(--tr);
}
button,input,select{font-family:inherit;color:inherit}
::selection{background:var(--lcd);color:var(--lcd-fg)}
:focus-visible{outline:2px solid var(--brass);outline-offset:2px;border-radius:4px}
::-webkit-scrollbar{width:9px;height:9px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:99px;border:2px solid transparent;background-clip:content-box}
::-webkit-scrollbar-thumb:hover{background:var(--muted);border:2px solid transparent;background-clip:content-box}
b,strong{font-weight:700}
.mono,[class*="mono"]{font-variant-numeric:tabular-nums}

/* ── 상단 앱바 — frosted glass ── */
.appbar{
  position:sticky;top:0;z-index:50;
  display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:calc(10px + var(--sat)) 16px 10px;
  background:linear-gradient(160deg, var(--lcd-2) 0%, var(--lcd) 70%);
  color:var(--lcd-fg);
  box-shadow:0 1px 0 rgba(255,255,255,.08) inset, 0 6px 24px -8px rgba(4,18,15,.55);
}
.appbar::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;
  background:linear-gradient(90deg, transparent, var(--gold1), transparent);opacity:.55}
.appbar .ttl{min-width:0}
.brand{
  font-family:var(--mono);font-size:10px;font-weight:800;letter-spacing:.42em;
  background:linear-gradient(92deg, var(--gold1), #EFE0B8 45%, var(--gold2));
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
  text-transform:uppercase;white-space:nowrap;
}
.brand span{
  -webkit-text-fill-color:var(--lcd-dim);letter-spacing:.12em;font-weight:600;
  margin-left:8px;font-family:Pretendard,sans-serif;font-size:9.5px;
}
.appbar h1{margin:2px 0 0;font-size:16.5px;font-weight:800;letter-spacing:-.01em;white-space:nowrap;
  text-shadow:0 0 18px rgba(140,235,190,.25)}
.appbar h1 em{font-style:normal;color:#E9B7BB;font-family:var(--mono);font-size:11.5px;margin-left:6px;letter-spacing:.08em}
#themetog{
  flex:0 0 auto;width:38px;height:38px;border-radius:12px;cursor:pointer;font-size:17px;line-height:1;
  border:1px solid rgba(159,233,201,.28);background:rgba(255,255,255,.06);
  backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  transition:transform var(--tr), background var(--tr);
}
#themetog:active{transform:scale(.9) rotate(-12deg)}

/* ── 뷰 전환 ── */
.view{display:none;padding:15px 13px 26px;max-width:640px;margin:0 auto;animation:rise .34s cubic-bezier(.2,.8,.3,1) both}
.view.on{display:block}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}

/* ── 하단 탭바 — frosted, pill indicator ── */
.tabbar{
  position:fixed;left:0;right:0;bottom:0;z-index:60;
  display:flex;height:calc(var(--nav-h) + var(--sab));
  padding:5px 6px calc(5px + var(--sab));gap:2px;
  background:var(--glass);
  backdrop-filter:blur(16px) saturate(1.5);-webkit-backdrop-filter:blur(16px) saturate(1.5);
  border-top:1px solid var(--line);
  box-shadow:0 -8px 32px -12px rgba(10,20,30,.25);
}
.tabbar button{
  flex:1;border:0;background:none;cursor:pointer;position:relative;border-radius:12px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;
  font-size:9.5px;font-weight:700;color:var(--muted);padding:0;white-space:nowrap;
  transition:color var(--tr), background var(--tr), transform var(--tr);
}
.tabbar button .ico{font-size:17px;line-height:1;filter:grayscale(1);opacity:.5;transition:filter var(--tr),opacity var(--tr),transform var(--tr)}
.tabbar button.on{color:var(--ink);background:linear-gradient(180deg,var(--steel),transparent)}
.tabbar button.on .ico{filter:none;opacity:1;transform:translateY(-1px) scale(1.08)}
.tabbar button.on::after{content:"";position:absolute;top:2px;width:26px;height:3px;border-radius:99px;
  background:linear-gradient(90deg,var(--gold1),var(--gold2))}
.tabbar button:active{transform:scale(.94)}

/* ── 검색 콘솔 ── */
.console{background:linear-gradient(180deg,var(--card),var(--card-2));border:1px solid var(--line);
  border-radius:18px;padding:16px;position:relative;box-shadow:var(--sh-2),0 1px 0 rgba(255,255,255,.55) inset}
[data-theme="dark"] .console{box-shadow:var(--sh-2),0 1px 0 rgba(255,255,255,.05) inset}
.console label{display:block;font-size:10.5px;font-weight:800;letter-spacing:.14em;color:var(--muted);
  text-transform:uppercase;margin-bottom:9px}
#q,#price{display:block;width:100%;font-family:var(--mono);font-size:16px;font-weight:600;
  letter-spacing:.04em;padding:13px 15px;border:1.5px solid var(--line-2);background:var(--card);color:var(--ink);
  border-radius:12px;-webkit-appearance:none;transition:border-color var(--tr), box-shadow var(--tr)}
#q{text-transform:uppercase}
#price{margin-top:9px}
#q:focus,#price:focus{outline:none;border-color:var(--lcd-dim);box-shadow:0 0 0 4px rgba(30,122,87,.13)}
#q::placeholder,#price::placeholder{color:var(--muted);opacity:.55;font-weight:400;font-size:14px;letter-spacing:.01em}
.btn{width:100%;margin-top:11px;font-size:16px;font-weight:800;padding:14px;cursor:pointer;letter-spacing:.02em;
  border:0;border-radius:12px;color:#fff;
  background:linear-gradient(180deg,#232A2F,#101519);
  box-shadow:0 1px 0 rgba(255,255,255,.14) inset, 0 8px 20px -8px rgba(10,18,25,.6);
  transition:transform var(--tr), box-shadow var(--tr), filter var(--tr);
}
[data-theme="dark"] .btn{background:linear-gradient(180deg,#3A444C,#22292F);box-shadow:0 1px 0 rgba(255,255,255,.12) inset,0 8px 22px -8px rgba(0,0,0,.7)}
.btn:active{transform:translateY(1px) scale(.99);filter:brightness(1.15)}
#ac{position:absolute;left:16px;right:16px;z-index:40;background:var(--card);border:1px solid var(--line-2);
  border-radius:12px;max-height:264px;overflow:auto;display:none;box-shadow:var(--sh-3)}
#ac div{padding:11px 13px;font-family:var(--mono);font-size:13.5px;
  display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid var(--line)}
#ac div:last-child{border-bottom:0}
#ac div:active,#ac div.on{background:var(--lcd);color:var(--lcd-fg)}
#ac span{font-family:Pretendard,sans-serif;font-size:11px;opacity:.7;white-space:nowrap}

/* 예시·최근 기록 칩 */
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:11px}
.chips .tl{flex-basis:100%;font-size:10px;font-weight:800;letter-spacing:.12em;color:var(--muted);text-transform:uppercase}
.chip-btn{font-family:var(--mono);font-size:12px;font-weight:600;padding:7px 12px;cursor:pointer;
  border:1px solid var(--line-2);background:var(--card);color:var(--ink);border-radius:999px;
  transition:border-color var(--tr), background var(--tr), transform var(--tr);box-shadow:var(--sh-1)}
.chip-btn:active{border-color:var(--lcd-dim);background:var(--info-bg);transform:scale(.96)}
.chip-btn small{font-family:Pretendard,sans-serif;color:var(--muted);font-weight:400;margin-left:3px}

/* ── 판정 배너 ── */
.verdict{margin-top:15px;border:1px solid;border-left-width:6px;border-radius:14px;padding:15px 17px;
  box-shadow:var(--sh-2);animation:rise .4s cubic-bezier(.2,.8,.3,1) both}
.verdict .vp{font-family:var(--mono);font-size:25px;font-weight:800;line-height:1.15;letter-spacing:-.01em;font-variant-numeric:tabular-nums}
.verdict .vt{font-size:16px;font-weight:800;margin-top:3px}
.verdict .vd{font-size:13px;margin-top:7px;line-height:1.6}
.v-epic{border-color:var(--epic);background:linear-gradient(160deg,var(--epic-bg),var(--card));color:var(--epic)}
.v-deal{border-color:var(--ok);background:linear-gradient(160deg,var(--ok-bg),var(--card));color:var(--ok)}
.v-fair{border-color:var(--brass);background:linear-gradient(160deg,var(--fair-bg),var(--card));color:var(--fair-tx)}
.v-warm{border-color:var(--warm);background:linear-gradient(160deg,var(--warm-bg),var(--card));color:var(--warm-tx)}
.v-no{border-color:var(--seal);background:linear-gradient(160deg,var(--seal-bg),var(--card));color:var(--seal)}

/* ── 코드 해부 ── */
.anat{margin-top:15px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:15px;box-shadow:var(--sh-2)}
.anat h2{margin:0 0 2px;font-size:12px;font-weight:800;letter-spacing:.11em;text-transform:uppercase}
.anat .note{font-size:11.5px;color:var(--muted);margin-bottom:11px}
.strip{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:7px}
.seg{background:var(--card);border:1px solid var(--line-2);border-radius:10px;min-width:44px;flex:0 0 auto;
  box-shadow:var(--sh-1);animation:pop .34s cubic-bezier(.2,.9,.3,1.25) backwards}
.seg .ch{display:block;font-family:var(--mono);font-size:19px;font-weight:700;text-align:center;padding:8px 8px 3px}
.seg .lb{display:block;font-size:9px;font-weight:700;text-align:center;padding:0 5px 6px;color:var(--muted);white-space:nowrap}
.seg.key{border-color:var(--lcd-dim);background:linear-gradient(180deg,var(--info-bg),var(--card));box-shadow:0 0 0 1px rgba(30,122,87,.12),var(--sh-1)}
.seg.key .ch,.seg.key .lb{color:var(--ok)}
.seg.warn{border-color:var(--seal);background:linear-gradient(180deg,var(--seal-bg),var(--card))}
.seg.warn .ch,.seg.warn .lb{color:var(--seal)}
.seg.mute{opacity:.48}
@keyframes pop{from{opacity:0;transform:translateY(8px) scale(.94)}to{opacity:1;transform:none}}
.legend{margin-top:6px}
.legend div{display:grid;grid-template-columns:52px 1fr;gap:10px;font-size:13px;padding:8px 0;border-top:1px solid var(--line)}
.legend .k{font-family:var(--mono);font-weight:700;font-size:12.5px;word-break:break-all}
.legend .v strong{font-weight:700}
.legend .v em{font-style:normal;color:var(--muted);font-size:12px}

/* ── LCD — 유리 반사 + 글로우 ── */
.lcd{margin-top:15px;position:relative;overflow:hidden;border-radius:16px;
  background:
    repeating-linear-gradient(0deg, rgba(255,255,255,.016) 0 1px, transparent 1px 3px),
    linear-gradient(165deg, var(--lcd-2) 0%, var(--lcd) 65%);
  border:1px solid #05201A;padding:16px 17px;color:var(--lcd-fg);
  box-shadow:0 0 0 1px rgba(159,233,201,.14) inset, 0 1px 0 rgba(255,255,255,.1) inset, var(--sh-3), 0 0 44px -18px rgba(40,180,120,.35)}
.lcd::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:inherit;
  background:linear-gradient(115deg, rgba(255,255,255,.10) 0%, rgba(255,255,255,.03) 22%, transparent 40%)}
.lcd .tag{font-family:var(--mono);font-size:10px;letter-spacing:.2em;color:var(--lcd-dim);margin-bottom:5px}
.lcd .title{font-size:19.5px;font-weight:800;line-height:1.25;word-break:break-all;
  text-shadow:0 0 16px rgba(140,235,190,.4)}
.lcd .name{font-size:12px;color:var(--lcd-dim);margin-top:3px}
.lcd .line{margin-top:12px;display:flex;flex-wrap:wrap;gap:6px}
.fchip{border:1px solid var(--lcd-dim);padding:3.5px 10px;font-size:11.5px;font-weight:600;border-radius:999px;
  transition:background var(--tr)}
.fchip.on{background:var(--lcd-fg);color:var(--lcd);border-color:var(--lcd-fg);
  box-shadow:0 0 14px -2px rgba(159,233,201,.5)}
.fchip.off{opacity:.38;text-decoration:line-through}
.lcd .meta{margin-top:14px;padding-top:12px;border-top:1px dashed rgba(82,140,119,.55);
  display:grid;grid-template-columns:1fr 1fr;gap:11px}
.lcd .meta div span{display:block;font-size:10px;color:var(--lcd-dim);letter-spacing:.08em}
.lcd .meta div b{display:block;font-size:14px;font-weight:700;margin-top:2px;font-variant-numeric:tabular-nums}

.card{margin-top:15px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:15px;
  box-shadow:var(--sh-2)}
.card h3{margin:0 0 3px;font-size:12px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;
  display:flex;align-items:center;gap:8px}
.card h3::before{content:"";width:14px;height:3px;border-radius:99px;flex:0 0 auto;
  background:linear-gradient(90deg,var(--gold1),var(--gold2))}
.card .cap{font-size:11.5px;color:var(--muted);margin-bottom:12px;line-height:1.55}
.cap.lgnd{margin:2px 2px 10px;line-height:1.9}

/* ── 기준선 사다리 ── */
.ladder{display:flex;height:40px;border-radius:999px;overflow:hidden;margin:14px 0 6px;font-family:var(--mono);
  box-shadow:0 2px 8px -2px rgba(10,20,30,.35), 0 1px 0 rgba(255,255,255,.25) inset}
.ladder div{display:flex;justify-content:center;align-items:center;min-width:0;overflow:hidden;position:relative}
.ladder div+div{border-left:1px solid rgba(255,255,255,.28)}
.ladder div::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.18),transparent 55%)}
.ladder b{font-size:10px;font-weight:700;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.35);position:relative;z-index:1}
.ld-epic{background:#14532D} .ld-deal{background:#1E7A57} .ld-fair{background:#A67F3C}
.ld-warm{background:#B06A2A} .ld-no{background:#A81E27}
.ladlab{display:flex;justify-content:space-between;font-size:10.5px;color:var(--muted);font-family:var(--mono)}
.ladkey{display:flex;flex-wrap:wrap;gap:10px;font-size:11px;margin-top:8px;color:var(--muted)}
.ladkey i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:4px;vertical-align:-1px}
.prices{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);
  border-radius:12px;overflow:hidden;margin-top:14px}
.prices div{background:var(--card-2);padding:11px 13px}
.prices span{display:block;font-size:10.5px;color:var(--muted);letter-spacing:.02em}
.prices b{display:block;font-family:var(--mono);font-size:14.5px;font-weight:700;margin-top:3px;font-variant-numeric:tabular-nums}
.prices b.good{color:var(--ok)} .prices b.bad{color:var(--seal)}
.prices b.strike{text-decoration:line-through;color:var(--muted);font-size:13px}
.prices b.epic{color:var(--epic)}

/* ── 형제·동급 미니 리스트 ── */
.mrow{display:flex;justify-content:space-between;align-items:center;gap:10px;
  padding:11px 8px;margin:0 -8px;border-radius:10px;border-top:1px solid var(--line);cursor:pointer;
  transition:background var(--tr)}
.mrow:active{background:var(--steel)}
.mrow .l{min-width:0}
.mrow .mm{font-family:var(--mono);font-size:13.5px;font-weight:700;word-break:break-all}
.mrow .ms{font-size:11.5px;color:var(--muted);margin-top:1px}
.mrow .mp{font-family:var(--mono);font-size:14px;font-weight:700;white-space:nowrap;font-variant-numeric:tabular-nums}
.mrow.self{background:var(--info-bg)}
.mrow.self .mm::after{content:"지금 이 모델";font-family:Pretendard,sans-serif;font-size:9.5px;font-weight:700;
  color:var(--ok);border:1px solid var(--ok);border-radius:99px;padding:1px 7px;margin-left:6px;vertical-align:1px}
.mrow.cheap .mp{color:var(--ok)}

.alert{margin-top:15px;border:1px solid var(--seal);border-left-width:5px;border-radius:12px;
  background:linear-gradient(160deg,var(--seal-bg),var(--card));padding:13px 14px;font-size:13px;box-shadow:var(--sh-1)}
.alert.warn{border-color:var(--brass);background:linear-gradient(160deg,var(--fair-bg),var(--card))}
.alert.info{border-color:var(--lcd-dim);background:linear-gradient(160deg,var(--info-bg),var(--card))}
.alert b{display:block;margin-bottom:3px}
.alert ul{margin:6px 0 0;padding-left:17px}
.alert li{margin-bottom:5px}
.alert li:last-child{margin-bottom:0}

.empty{padding:32px 10px;text-align:center;color:var(--muted);font-size:13.5px}
.empty b{display:block;font-size:15px;color:var(--ink);margin-bottom:6px}

/* ── 리스트 탭 ── */
.fscroll{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:2px 0 9px;scrollbar-width:none}
.fscroll::-webkit-scrollbar{display:none}
.fscroll button{flex:0 0 auto;font-size:12.5px;font-weight:600;padding:8px 14px;cursor:pointer;
  border:1px solid var(--line-2);background:var(--card);color:var(--muted);border-radius:999px;
  box-shadow:var(--sh-1);transition:all var(--tr)}
.fscroll button.on{border-color:transparent;color:#fff;
  background:linear-gradient(180deg,#2A3238,#14191D);box-shadow:0 1px 0 rgba(255,255,255,.12) inset,var(--sh-1)}
[data-theme="dark"] .fscroll button.on{background:linear-gradient(180deg,#48545C,#2B343B)}
.listbar{display:flex;gap:8px;margin-bottom:8px}
#lq{flex:1;font-family:var(--mono);font-size:16px;padding:10px 13px;border:1.5px solid var(--line-2);
  background:var(--card);text-transform:uppercase;min-width:0;border-radius:11px;-webkit-appearance:none;
  transition:border-color var(--tr), box-shadow var(--tr)}
#lq:focus{outline:none;border-color:var(--lcd-dim);box-shadow:0 0 0 4px rgba(30,122,87,.13)}
#lq::placeholder{font-size:13px;text-transform:none;color:var(--muted);opacity:.6}
.listbar .cnt{align-self:center;font-size:12px;color:var(--muted);font-family:var(--mono);white-space:nowrap}
.efftog{font-size:12px;font-weight:700;padding:9px 12px;border:1px solid var(--line-2);background:var(--card);
  color:var(--muted);cursor:pointer;border-radius:11px;white-space:nowrap;transition:all var(--tr);box-shadow:var(--sh-1)}
.efftog.on{border-color:transparent;background:linear-gradient(180deg,#1B6B45,#124D31);color:#fff;
  box-shadow:0 1px 0 rgba(255,255,255,.15) inset,0 4px 14px -4px rgba(20,83,45,.5)}
.sortbar{display:flex;gap:8px;margin-bottom:10px}
.sortbar select{flex:1;font-size:14px;padding:10px 12px;border:1px solid var(--line-2);background:var(--card);
  color:var(--ink);min-width:0;border-radius:11px;-webkit-appearance:none;box-shadow:var(--sh-1)}
.sortbar button{font-size:14px;font-weight:700;padding:10px 14px;border:1px solid var(--line-2);background:var(--card);
  cursor:pointer;border-radius:11px;white-space:nowrap;box-shadow:var(--sh-1);transition:transform var(--tr)}
.sortbar button:active{transform:scale(.96)}
.pcard{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:13px 15px;margin-bottom:9px;
  cursor:pointer;box-shadow:var(--sh-1);transition:transform var(--tr), box-shadow var(--tr), background var(--tr)}
.pcard:active{transform:scale(.985);background:var(--card-2)}
.pc-top{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.pc-top .pm{font-family:var(--mono);font-size:14.5px;font-weight:700;word-break:break-all}
.pc-mid{font-size:12px;color:var(--muted);margin-top:3px;line-height:1.55}
.pc-row{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-top:9px;flex-wrap:wrap}
.pc-price{font-family:var(--mono);font-size:16px;font-weight:700;font-variant-numeric:tabular-nums}
.pc-price s{font-size:12px;color:var(--muted);font-weight:400;margin-right:6px}
.pc-price .d{font-size:12px;color:var(--seal);margin-left:4px}
.pc-px{font-family:var(--mono);font-size:11.5px;text-align:right;line-height:1.7}
.pc-px b.g{color:var(--ok)} .pc-px b.r{color:var(--seal)}
.badge{display:inline-block;font-size:10px;font-weight:700;padding:1.5px 7px;border-radius:99px;vertical-align:1px}
.b-so{background:var(--seal);color:#fff}
.b-new{background:var(--epic);color:#fff}
.b-dom{background:var(--muted);color:var(--card)}
#more{width:100%;margin-top:4px;font-size:14px;font-weight:700;padding:13px;cursor:pointer;
  border:1px dashed var(--line-2);background:transparent;color:var(--muted);border-radius:12px;
  transition:all var(--tr)}
#more:active{border-color:var(--ink);color:var(--ink);background:var(--card)}

/* ── 가이드 탭 ── */
.guide h2{font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;
  margin:0 0 6px;padding-bottom:7px;border-bottom:2px solid var(--ink);position:relative}
.guide h2::after{content:"";position:absolute;left:0;bottom:-2px;width:44px;height:2px;
  background:linear-gradient(90deg,var(--gold1),var(--gold2))}
.guide .card p{font-size:13.5px;margin:8px 0}
.guide .card p:first-of-type{margin-top:0}
.gcode{font-family:var(--mono);font-weight:700;background:var(--steel);padding:1px 6px;font-size:12.5px;border-radius:6px}
.gt{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:8px}
.gt th{text-align:left;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
  padding:6px;border-bottom:2px solid var(--ink);white-space:nowrap}
.gt td{padding:7px 6px;border-bottom:1px solid var(--line);vertical-align:top}
.gt td.k{font-family:var(--mono);font-weight:700;white-space:nowrap}
.tierdot{display:inline-block;width:11px;height:11px;border-radius:4px;margin-right:6px;vertical-align:-1px}

footer{margin:28px 6px 8px;font-size:11px;color:var(--muted);line-height:1.7}
.totop{position:fixed;right:14px;bottom:calc(var(--nav-h) + var(--sab) + 16px);z-index:55;
  width:46px;height:46px;border-radius:50%;border:1px solid var(--line-2);font-size:18px;font-weight:800;
  cursor:pointer;display:none;color:var(--ink);
  background:var(--glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  box-shadow:var(--sh-3);transition:transform var(--tr)}
.totop:active{transform:scale(.9)}
.totop.show{display:block;animation:rise .3s both}

/* ── 조건 빌더 ── */
.bfield{display:flex;gap:8px;align-items:flex-start;margin-bottom:8px}
.bfield .bl{flex:0 0 62px;font-size:11.5px;font-weight:700;color:var(--muted);padding-top:9px}
.bops{display:flex;flex-wrap:wrap;gap:5px;min-width:0}
.bops button{font-size:12.5px;font-weight:600;padding:8px 12px;cursor:pointer;
  border:1px solid var(--line-2);background:var(--card);color:var(--muted);border-radius:999px;
  transition:all var(--tr);box-shadow:var(--sh-1)}
.bops button.on{border-color:transparent;color:#fff;background:linear-gradient(180deg,#2A3238,#14191D);
  box-shadow:0 1px 0 rgba(255,255,255,.12) inset,var(--sh-1)}
[data-theme="dark"] .bops button.on{background:linear-gradient(180deg,#48545C,#2B343B)}
.best{margin:13px 0;border:1px solid var(--lcd-dim);border-left-width:5px;border-radius:12px;
  background:linear-gradient(160deg,var(--info-bg),var(--card));padding:12px 14px;font-size:13px}
.best b{font-family:var(--mono);font-size:16px;font-variant-numeric:tabular-nums}
.best .bparts{display:block;font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:4px;line-height:1.7}
.best .bnote{display:block;font-size:11px;color:var(--muted);margin-top:4px}
.bcnt{font-size:12px;color:var(--muted);font-family:var(--mono);margin:10px 0 4px}

/* ── 가중치 ── */
.wrow{display:grid;grid-template-columns:1fr 60px 96px;gap:8px;align-items:center;padding:9px 0;border-top:1px solid var(--line)}
.wrow .wl b{font-size:13px}
.wrow .wl span{display:block;font-size:10.5px;color:var(--muted)}
.wrow .wl em{display:block;font-style:normal;font-size:11px;color:var(--muted);margin-top:1px}
.wb{height:12px;background:var(--steel);position:relative;border-radius:99px;overflow:hidden;
  box-shadow:0 1px 2px rgba(10,20,30,.12) inset}
.wb i{position:absolute;left:0;top:0;bottom:0;border-radius:99px}
.wb i.pos{background:linear-gradient(90deg,#1E7A57,#37A578)} .wb i.neg{background:linear-gradient(90deg,#C2444F,#A81E27)}
.wv{font-family:var(--mono);font-size:12.5px;font-weight:700;text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.wv.pos{color:var(--ok)} .wv.neg{color:var(--seal)}
.wv .wsub{display:block;font-family:Pretendard,sans-serif;font-size:9.5px;font-weight:600;color:var(--muted);margin-top:2px}
.conf{display:inline-block;font-size:9px;font-weight:800;padding:1px 7px;border-radius:99px;border:1px solid;letter-spacing:.02em}
.conf.hi{color:var(--ok);border-color:var(--ok);background:var(--ok-bg)}
.conf.lo{color:var(--seal);border-color:var(--seal);background:var(--seal-bg)}
.wcap{margin-top:13px;padding:11px 13px;background:var(--steel);border-radius:11px;font-size:12px;line-height:1.75}
.depline{display:inline-block;margin:4px 0;font-family:var(--mono);font-size:11.5px}
.wnote{margin-top:10px;padding-top:9px;border-top:1px dashed var(--line-2);font-size:10.5px;color:var(--muted);line-height:1.6}

/* ── 코드 사전 ── */
#dictq{display:block;width:100%;font-size:16px;padding:11px 13px;border:1.5px solid var(--line-2);
  background:var(--card);border-radius:11px;-webkit-appearance:none;margin-bottom:4px;
  transition:border-color var(--tr), box-shadow var(--tr)}
#dictq:focus{outline:none;border-color:var(--lcd-dim);box-shadow:0 0 0 4px rgba(30,122,87,.13)}
#dictq::placeholder{font-size:13px;color:var(--muted);opacity:.6}
.dcat{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
  margin:18px 0 4px;padding-bottom:5px;border-bottom:2px solid var(--ink);position:relative}
.dcat::after{content:"";position:absolute;left:0;bottom:-2px;width:36px;height:2px;
  background:linear-gradient(90deg,var(--gold1),var(--gold2))}
.drow{display:flex;gap:10px;padding:11px 4px 11px 10px;border-bottom:1px solid var(--line);border-left:3px solid transparent;
  border-radius:2px 10px 10px 2px;transition:background var(--tr)}
.drow.t-good{border-left-color:var(--ok)}
.drow.t-mid{border-left-color:var(--brass)}
.drow.t-warn{border-left-color:var(--seal)}
.drow .dc{flex:0 0 54px;font-family:var(--mono);font-size:14px;font-weight:800;word-break:break-all;padding-top:1px}
.drow .dm{min-width:0;flex:1}
.drow .dn b{font-size:13.5px}
.dtag{display:inline-block;font-size:10px;font-weight:700;padding:1px 7px;margin-left:6px;vertical-align:1px;border:1px solid;border-radius:99px}
.dtag.t-good{color:var(--ok);border-color:var(--ok);background:var(--ok-bg)}
.dtag.t-mid{color:var(--fair-tx);border-color:var(--brass);background:var(--fair-bg)}
.dtag.t-warn{color:var(--seal);border-color:var(--seal);background:var(--seal-bg)}
.dtag.t-neutral{color:var(--muted);border-color:var(--line-2)}
.drow .dd{font-size:12.5px;color:var(--ink-2);margin-top:2px;line-height:1.55}
.drow .ds{font-size:11.5px;color:var(--muted);margin-top:3px;font-family:var(--mono)}
.drow .ds .lnk{color:var(--ink);border-bottom:1px solid var(--line-2);cursor:pointer}

/* ── 상황별 추천 ── */
.pdesc{font-size:13px;background:var(--steel);border-radius:11px;padding:11px 13px;margin:6px 0 12px;line-height:1.6}
.rtier{border:1px solid var(--line);background:var(--card-2);border-radius:13px;margin-bottom:11px;padding:12px 14px;
  box-shadow:var(--sh-1)}
.rt-lv{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.04em;color:#fff;border-radius:99px;
  background:linear-gradient(180deg,#154237,#0C2823);padding:2.5px 10px;box-shadow:0 1px 0 rgba(255,255,255,.15) inset}
.rt-lv.l2{background:linear-gradient(180deg,#26906A,#1E7A57)}
.rt-lv.l3{background:linear-gradient(180deg,#B98F4B,#96702F)}
.rt-why{font-size:12px;color:var(--muted);margin-left:7px}
.rt-now{font-size:12px;margin-top:7px;padding-top:8px;border-top:1px dashed var(--line-2);line-height:1.6;color:var(--ink-2)}
.tx-good{color:var(--ok)} .tx-bad{color:var(--seal)} .tx-mid{color:var(--ink-2)}
.vbadge{display:inline-block;font-size:10px;font-weight:800;padding:1px 7px;margin-left:6px;border:1px solid;border-radius:99px;vertical-align:1px}
.vbadge.v-epic{color:var(--epic);border-color:var(--epic);background:var(--epic-bg)}
.vbadge.v-deal{color:var(--ok);border-color:var(--ok);background:var(--ok-bg)}
.vbadge.v-fair{color:var(--fair-tx);border-color:var(--brass);background:var(--fair-bg)}
.vbadge.v-warm{color:var(--warm-tx);border-color:var(--warm);background:var(--warm-bg)}
.vbadge.v-no{color:var(--seal);border-color:var(--seal);background:var(--seal-bg)}

/* ── FAQ ── */
.faq{border:1px solid var(--line);background:var(--card-2);border-radius:13px;margin-bottom:9px;overflow:hidden;
  transition:box-shadow var(--tr)}
.faq[open]{box-shadow:var(--sh-2);background:var(--card)}
.faq summary{padding:13px 40px 13px 15px;font-weight:700;font-size:13.5px;cursor:pointer;list-style:none;position:relative;
  transition:color var(--tr)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:15px;top:50%;transform:translateY(-50%);
  font-size:19px;font-weight:400;color:var(--muted);transition:transform var(--tr)}
.faq[open] summary::after{content:"−";color:var(--ok)}
.faq .fa{padding:0 15px 14px;font-size:13px;line-height:1.68;color:var(--ink-2)}
.faq .fa p{margin:8px 0}
.faq .fa p:first-child{margin-top:0}
.mtx{width:100%;border-collapse:collapse;font-size:12px;margin:8px 0;border-radius:8px;overflow:hidden}
.mtx th,.mtx td{border:1px solid var(--line);padding:7px 9px;text-align:left}
.mtx th{background:var(--steel);font-size:11px}

/* ── 1:1 비교 ── */
#cmpa,#cmpb{display:block;width:100%;font-family:var(--mono);font-size:16px;font-weight:600;padding:12px 14px;
  border:1.5px solid var(--line-2);background:var(--card);text-transform:uppercase;border-radius:11px;
  -webkit-appearance:none;transition:border-color var(--tr), box-shadow var(--tr)}
#cmpa:focus,#cmpb:focus{outline:none;border-color:var(--lcd-dim);box-shadow:0 0 0 4px rgba(30,122,87,.13)}
#cmpa::placeholder,#cmpb::placeholder{font-size:13px;text-transform:none;font-weight:400;color:var(--muted);opacity:.6}
.cmpt{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:12px}
.cmpt th,.cmpt td{border:1px solid var(--line);padding:7px 9px;text-align:left}
.cmpt tr:first-child th{background:var(--steel);font-family:var(--mono);font-size:10.5px;word-break:break-all}
.cmpt tr th:first-child{background:var(--card-2);font-size:11px;color:var(--muted);white-space:nowrap}
.cmpt tr.diff td{background:var(--fair-bg)}
.cmpt td.win{color:var(--ok);font-weight:700}

/* ── 가격 이력 ── */
.phrow{display:flex;flex-wrap:wrap;gap:7px;align-items:center;font-family:var(--mono)}
.phpt{border:1px solid var(--line-2);background:var(--card);border-radius:10px;padding:7px 11px;font-size:11px;
  color:var(--muted);text-align:center;box-shadow:var(--sh-1)}
.phpt b{display:block;font-size:14px;color:var(--ink);margin-top:1px;font-variant-numeric:tabular-nums}
.phpt.lo{border-color:var(--ok);background:var(--ok-bg)} .phpt.lo b{color:var(--ok)}
.pharrow{color:var(--muted);font-size:13px}

@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}html{scroll-behavior:auto}}
@media(min-width:640px){.view{padding:20px 16px 32px}}
</style>
</head>
<body>

<header class="appbar">
  <div class="ttl">
    <div class="brand">UNFADE.<span>신혼집 가전 사기</span></div>
    <h1>쿠쿠 밥솥 해독기<em>v3</em></h1>
  </div>
  <button id="themetog" aria-label="다크모드 전환">🌙</button>
</header>

<!-- ═══ 탭 1: 판정 ═══ -->
<main id="view-check" class="view on">
  <div class="console">
    <label for="q">모델명 + (선택) 제시된 가격 — "이 특가, 진짜인가?"</label>
    <input id="q" placeholder="모델명 입력 · 예: CRP-DHP0610FD" autocomplete="off" spellcheck="false"
      autocapitalize="characters" autocorrect="off" enterkeyhint="search">
    <div id="ac"></div>
    <input id="price" placeholder="제시된 가격 (원 · 비워도 됨)" inputmode="numeric" autocomplete="off" enterkeyhint="go">
    <button class="btn" id="go">판정하기</button>
    <div class="chips" id="recent"></div>
    <div id="stale" style="margin-top:10px;font-size:12px;line-height:1.6;color:var(--muted)"></div>
    <div class="chips">
      <span class="tl">예시로 눌러보기</span>
      <button class="chip-btn" data-ex="CRP-DHP0610FD" data-exp="199000">DHP0610FD<small>@19.9만</small></button>
      <button class="chip-btn" data-ex="CRP-LHTR0610FWM" data-exp="239000">LHTR0610FWM<small>@23.9만</small></button>
      <button class="chip-btn" data-ex="CRP-HVB06BS" data-exp="250000">HVB06BS<small>@25만</small></button>
      <button class="chip-btn" data-ex="CRP-DHAS069FB" data-exp="">DHAS069FB<small>가격없이</small></button>
    </div>
  </div>
  <div id="result"></div>

  <div class="card">
    <h3>1:1 비교 — A냐 B냐</h3>
    <div class="cap">최종 후보 둘을 넣으면 스펙 차이를 짚고, <b>가격차가 스펙 가치로 정당한지</b>를 항목별 가중치로 해부합니다.
      지배 관계(한쪽이 스펙·가격 모두 앞서는 경우)도 자동 판정합니다.</div>
    <input id="cmpa" list="mlist" placeholder="모델 A — 입력하면 자동완성 (예: CRP-DHP0610FD)" autocomplete="off" autocapitalize="characters" autocorrect="off">
    <input id="cmpb" list="mlist" placeholder="모델 B (예: CRP-ST0615FW)" autocomplete="off" autocapitalize="characters" autocorrect="off" style="margin-top:8px">
    <button class="btn" id="cmpgo">비교하기</button>
    <datalist id="mlist"></datalist>
    <div id="cmpout"></div>
  </div>
</main>

<!-- ═══ 탭: 상황별 추천 ═══ -->
<main id="view-reco" class="view">
  <div class="card" style="margin-top:0">
    <h3>상황별 추천 — 뭘 사야 할지 모르겠다면</h3>
    <div class="cap">우리 집 상황을 고르면, 판매중 모델 중에서 <b>이거면 충분 / 균형 추천 / 제대로 갖추기</b> 3단계로
      추천합니다. 왜 이 스펙인지(사유)와 왜 지금 이 모델인지(현재가가 자체 기준선 대비 어느 구간인지)를 함께 보여줍니다.</div>
    <div class="fscroll" id="pers"></div>
    <div id="reco"></div>
  </div>
</main>

<!-- ═══ 탭 2: 전체 리스트 ═══ -->
<main id="view-list" class="view">
  <div class="fscroll" id="filters"></div>
  <div class="fscroll" id="capfilters"></div>
  <div class="listbar">
    <input id="lq" placeholder="모델명·제품명 검색 (예: DHAS)" autocomplete="off" autocapitalize="characters" autocorrect="off">
    <button id="effonly" class="efftog" title="같은 돈에 더 나은 대안이 없는 판매중 모델만">알짜만</button>
    <span class="cnt" id="lcnt"></span>
  </div>
  <div class="cap lgnd">배지: <b class="badge b-dom">대안있음</b> = 같은 돈에 스펙이 같거나 더 좋은 모델 존재(눌러서 판정 화면에서 확인) ·
    <b class="badge b-new">NEW</b> 신상 · <b class="badge b-so">품절</b> 단종·품절. "알짜만" = 대안 없는 진짜 선택지 55개만 보기.</div>
  <div class="sortbar">
    <select id="sortsel" aria-label="정렬 기준">
      <option value="sp">몰가 순</option>
      <option value="vfm">시세보다 싼 순</option>
      <option value="rv">인기 순(월 리뷰)</option>
      <option value="rg">출시 순</option>
      <option value="px3">절대상한 순</option>
      <option value="px1">특가컷 순</option>
      <option value="dr">할인율 순</option>
      <option value="rc">리뷰수 순</option>
      <option value="cp">용량 순</option>
      <option value="m">모델명 순</option>
      <option value="dz">라인 순</option>
    </select>
    <button id="sortdir">▲ 오름</button>
  </div>
  <div id="cards"></div>
  <button id="more">더 보기</button>
</main>

<!-- ═══ 탭: 조건 검색 ═══ -->
<main id="view-build" class="view">
  <div class="card" style="margin-top:0">
    <h3>조건으로 찾기 — 이 조합, 실제로 있나?</h3>
    <div class="cap">원하는 조건을 고르면 공식몰 213개에서 실존 모델을 찾고, 아래 "항목별 가중치"로 그 조합의 예상가도 계산합니다. 모델을 누르면 판정으로 이동합니다.</div>
    <div id="bld"></div>
    <div id="bres"></div>
  </div>
  <div class="card">
    <h3>항목별 가중치 — 이 기능에 얼마가 붙나</h3>
    <div id="wx"></div>
  </div>
</main>

<!-- ═══ 탭: 코드 사전 ═══ -->
<main id="view-dict" class="view">
  <div class="card" style="margin-top:0">
    <h3>코드 사전 — 모델명에 올 수 있는 모든 코드</h3>
    <div class="cap">모델명 각 자리에 올 수 있는 코드 전부입니다. 코드·이름·설명 무엇으로든 검색되고,
      왼쪽 색 = <span style="color:var(--ok);font-weight:700">좋음</span> /
      <span style="color:#7A5A20;font-weight:700">중간·취향</span> /
      <span style="color:var(--seal);font-weight:700">주의</span>.
      대표 모델을 누르면 판정으로 이동합니다. <span id="dictcnt" style="font-family:var(--mono)"></span></div>
    <input id="dictq" placeholder="코드·기능 검색 (예: TT, 트윈, 올스텐, 저당)" autocomplete="off" autocorrect="off">
    <div id="dict"></div>
  </div>
</main>

<!-- ═══ 탭 3: 가이드 ═══ -->
<main id="view-guide" class="view guide">

  <div class="card">
    <h2>이 도구는 무엇인가</h2>
    <p>쿠쿠 공식몰 <b>213개 전 모델</b>의 모델명 규칙을 역공학해서, 홈쇼핑·오픈마켓의
    "특가"가 <b>진짜 특가인지</b>를 스펙 기준으로 판정합니다. 인터넷 연결 없이 동작하는
    오프라인 도구이며, 데이터는 __ASOF__ 수집본입니다.</p>
    <p>판정 탭에서 모델명을 넣으면 코드를 해부해 스펙을 보여주고, 가격까지 넣으면
    그 가격이 5단계 중 어디인지 판정합니다. 뭘 사야 할지부터 막막하면 <b>추천 탭</b>에서 시작하세요.</p>
  </div>

  <div class="card">
    <h2>자주 묻는 것 — 쉬운 답</h2>
    <div id="faq"></div>
  </div>

  <div class="card">
    <h2>모델명 읽는 법</h2>
    <p>예: <span class="gcode">CRP-DHP0610FD</span></p>
    <table class="gt"><thead><tr><th>자리</th><th>의미</th></tr></thead><tbody>
      <tr><td class="k">CRP / CR</td><td>압력식 / 비압력(보온) 구분</td></tr>
      <tr><td class="k">DH</td><td>디자인 라인 + 가열방식. H로 끝나면 IH, ST·QK 등은 열판</td></tr>
      <tr><td class="k">T / L</td><td>라인 뒤 T = 트윈프레셔, L = 저당취사(트윈 포함)</td></tr>
      <tr><td class="k">AS·XB·R…</td><td>내솥 코드. AS/AR = 올스테인리스 무코팅(5등급)</td></tr>
      <tr><td class="k">06</td><td>인용 수(용량). 뒤에 붙는 숫자는 유통 채널 구분 — 무시</td></tr>
      <tr><td class="k">T(뒤쪽)</td><td>표시창 코드 앞의 T = IoT(WiFi 앱연동) 모듈</td></tr>
      <tr><td class="k">F / S / B</td><td>표시창: LCD(퍼지) / 숫자·램프 / 버튼식</td></tr>
      <tr><td class="k">D·W·B…</td><td>색상. 성능과 무관 — 색상만 다르면 싼 쪽 구매</td></tr>
    </tbody></table>
    <p style="color:var(--muted);font-size:12px">NL/FF는 병행 변형 코드(세대 아님)입니다. 성능 차이가 확인되지 않았으니
    같은 스펙이면 무조건 싼 쪽을 사면 됩니다.</p>
  </div>

  <div class="card">
    <h2>가격 판정 5단계</h2>
    <p>모델마다 같은 스펙 최저가 · 색상 형제 최저가 · 상위스펙 대체재 가격 · 연식 감가를
    조합해 <b>절대상한</b>("이 이상 주면 손해")을 만들고, 그 아래를 4단계로 자릅니다.</p>
    <table class="gt"><thead><tr><th>판정</th><th>기준</th><th>행동</th></tr></thead><tbody>
      <tr><td class="k"><i class="tierdot" style="background:var(--epic)"></i>목표가</td><td>상한의 68% 이하</td><td>사도 좋음</td></tr>
      <tr><td class="k"><i class="tierdot" style="background:var(--ok)"></i>특가</td><td>상한의 80% 이하</td><td>필요한 스펙이면 좋은 딜</td></tr>
      <tr><td class="k"><i class="tierdot" style="background:var(--brass)"></i>적정</td><td>상한의 90% 이하</td><td>급하면 구매, 아니면 대기</td></tr>
      <tr><td class="k"><i class="tierdot" style="background:var(--warm)"></i>보류</td><td>상한 이내</td><td>흔한 가격. "특가" 문구에 속지 말 것</td></tr>
      <tr><td class="k"><i class="tierdot" style="background:var(--seal)"></i>비쌈</td><td>상한 초과</td><td>기다리기</td></tr>
    </tbody></table>
    <p style="color:var(--muted);font-size:12px">공식몰 미등록 신모델도 동급 스펙 기준으로 추정 판정합니다(추정치 표기).</p>
  </div>

  <div class="card">
    <h2>스펙 우선순위 (돈 값 하는 순서)</h2>
    <table class="gt"><tbody>
      <tr><td class="k">1. 가열</td><td><b>IH</b>(전체 유도가열, 2기압↑) &gt; 열판(바닥만, IH보다 저압) &gt; 비압력</td></tr>
      <tr><td class="k">2. 트윈프레셔</td><td>고압/무압 선택. 볶음밥·냉동밥에 유리</td></tr>
      <tr><td class="k">3. 내솥</td><td>올스테인리스(무코팅)는 코팅 걱정이 없는 대신 눌어붙어 세척 번거로움 — 취향 문제</td></tr>
      <tr><td class="k">4. 사일런스</td><td>NH/OH/PH/QH 라인. 단, "사일런스 어반(UT)"은 이름만 사일런스인 열판식 — 주의</td></tr>
      <tr><td class="k">5. IoT</td><td>WiFi 앱연동. 앱 지원이 끊기면 일반 밥솥 — 웃돈 크게 주지 말 것</td></tr>
    </tbody></table>
    <p style="color:var(--muted);font-size:12px">각 항목에 시장이 실제로 얼마를 얹는지(원 단위)는
    <b>조건검색 탭 하단 "항목별 가중치"</b>에, 코드 하나하나의 상세 설명·실측 통계는 <b>코드사전 탭</b>에 있습니다.</p>
  </div>

  <div class="card">
    <h2>흔한 함정</h2>
    <p>· <b>정가 대비 할인율</b>은 의미가 없습니다. 쿠쿠 정가는 애초에 높게 잡혀 있어
    "50% 할인"도 절대상한을 넘는 경우가 있습니다. 할인율보다 이 도구의 기준선과 비교해 보세요.</p>
    <p>· <b>구형 명명</b>(H가 앞에 오는 HV·HW 등, AH/BH 라인)은 단종 수순입니다.
    신형 동급보다 확실히 싸지 않다면 신형을 먼저 보세요.</p>
    <p>· <b>출시 6년 이상</b> 지난 모델에 신품 프리미엄을 주지 마세요. 기준선에 연식
    감가가 이미 반영되어 있습니다.</p>
    <p>· <b>모델명으로 알 수 없는 것</b>: 최대기압 · 에너지효율등급 · 소비전력. 다만 이 도구는
    다나와·공식몰 크롤로 대부분 모델의 실측값을 확보해 판정 화면에 표시합니다 (없는 모델은 상세페이지 확인).</p>
  </div>

  <footer>
    데이터: 쿠쿠 공식몰(cuckoo.co.kr) __ASOF__ 수집(대용량밥솥 분류는 제외, 다른 분류에 함께 오른 모델은 포함) · 출시(등록월)는 다나와 등록월 기준.<br>
    절대가격 기준선은 이 도구의 자체 산출값입니다. 구매 손실을 보장하지 않으며, 최종 판단 전 현재 가격을 직접 확인하세요.<span id="pclink"></span>
    <span id="hitbox" style="display:block;margin-top:8px;min-height:14px;color:transparent;user-select:all;-webkit-user-select:all;font-family:var(--mono);font-size:10px" aria-hidden="true"></span>
  </footer>
</main>

<button class="totop" id="totop" aria-label="맨 위로">↑</button>

<nav class="tabbar">
  <button class="on" data-v="check"><span class="ico">🔍</span>판정</button>
  <button data-v="reco"><span class="ico">⭐</span>추천</button>
  <button data-v="build"><span class="ico">⚙️</span>조건</button>
  <button data-v="list"><span class="ico">📋</span>리스트</button>
  <button data-v="dict"><span class="ico">🔤</span>사전</button>
  <button data-v="guide"><span class="ico">📖</span>가이드</button>
</nav>

<script>
const DB = __DB__;

/* ═══ 코드 테이블 (v3와 동일) ═══ */
const DESIGN={AH:["A형","구형 라인"],BH:["B형","구형 라인"],CH:["C형","10인용 주력"],
 DH:["D형","6인용 주력"],EH:["E형","3인용 전용"],FH:["F형","중상급"],JH:["J형","중급"],
 KH:["K형","트윈프레셔 중상급"],LH:["L형","마스터셰프"],MH:["M형","쁘띠/소용량"],
 NH:["N형","사일런스"],OH:["O형","사일런스 오브제"],PH:["P형","사일런스 프로"],
 QH:["Q형","사일런스 큐브"],BDH:["BD형","타철명장"],BCH:["BC형","타철명장"]};
const DESIGN_OLD={HQ:["HQ형","구형"],HU:["HU형","구형"],HV:["HV형","구형"],HW:["HW형","구형"],HM:["HM형","구형"]};
const SIL={NH:1,OH:1,PH:1,QH:1};
const OLDG={AH:1,BH:1,HQ:1,HU:1,HV:1,HW:1,HM:1};
const PLATE={ST:[1,"더 라이트"],UT:[1,"사일런스 어반"],TT:[1,"트윈프레셔 미니"],RT:[1,"열판 트윈프레셔"],
 QK:[0,"Q형 열판압력"],PK:[0,"P형 열판압력"],RK:[0,"R형 열판압력"],PW:[0,"P형 열판압력(변형)"],
 P:[0,"P형 열판압력"],R:[0,"R형 열판압력"],T:[0,"미니 열판압력"]};
const POT=[["AS","올스테인리스 무코팅 (와이드앤플랫)",5],["AR","올스테인리스 무코팅 (라운드)",5],
 ["XB","일반 코팅 (다이아 계열)",1],["R","투톤코팅 + 라운드(커브드)",4],["S","하단 투톤코팅 (에코스텐)",3],
 ["P","스테인리스 외피 코팅내솥",2],["B","일반 코팅 (다이아쉴드/블랙)",1],["F","타철명장/플랫 (구형)",1]];
const VAR={NL:"병행 변형 — 선행 리비전, 할인 유통 중심",FF:"병행 변형 — 후행 리비전(2026), 할인 거의 없음"};
const DISP={F:"LCD(퍼지) 디스플레이",S:"일반 숫자·램프 표시",B:"버튼식·일반 표시",M:"구형 소형 표시"};
const COLOR={W:"화이트",S:"실버",B:"블랙",D:"다크실버",G:"그레이",I:"아이보리",P:"핑크",
 T:"테라코타",R:"로즈/레드",C:"캐비어블루",V:"바이올렛",GW:"그레이스화이트",GB:"그레이스블랙",
 GI:"그레이스아이보리",GG:"어반그레이",MG:"메탈릭그린",LB:"루미블랙/루미다크실버",GPS:"그레이스핑크실버",
 WS:"화이트스톤",BS:"블랙실버",BB:"블랙브라운",WG:"화이트그레이",GS:"그레이실버",LS:"루미실버",
 PS:"핑크실버",BE:"베이지(추정)",BD:"다크블랙(추정)",PP:"핑크",WM:"화이트무광(추정)",
 DB:"다크블랙(추정)",SDB:"실버다크블랙(추정)",BGI:"블랙그레이아이보리(추정)",
 UG:"미확정",E:"미확정",EL:"미확정",FR:"미확정",BUG:"미확정"};
const CAP={"01":1,"02":2,"03":3,"04":4,"06":6,"08":8,"10":10,"35":35};
const HEATR={"IH":2,"열판":1};

/* ═══ 디코더 (v3와 동일) ═══ */
function decode(raw){
  let m=(raw||"").toUpperCase().replace(/\s/g,"").replace(/\(.*?\)$/,"");
  if(m && !m.includes("-")){ const g=m.match(/^(CRP|CR)(.+)$/); if(g) m=g[1]+"-"+g[2]; }
  const R={input:raw,model:m,seg:[],flags:[],ok:true,iot:false,oldGen:false,silence:false,dcx:""};
  let core;
  if(m.startsWith("CRP-")){R.pressure="전기압력밥솥";core=m.slice(4);R.seg.push(["CRP","압력식",1]);}
  else if(m.startsWith("CR-")){R.pressure="전기보온밥솥 (비압력)";core=m.slice(3);R.seg.push(["CR","비압력",1]);}
  else{R.ok=false;R.err="CRP- 또는 CR- 로 시작하는 쿠쿠 밥솥 모델명이 아닙니다.";return R;}

  const di=core.search(/\d/);
  if(di<0){R.ok=false;R.err="용량 숫자를 찾을 수 없습니다. 모델명이 잘렸는지 확인하세요.";return R;}
  let L=core.slice(0,di), rest=core.slice(di);

  if(R.pressure.includes("비압력")){
    R.design="-";R.designNote="보온 전용";R.heating="비압력";
    R.twin=false;R.low=false;R.potCode="-";R.pot="논스틱 코팅 (기본)";R.potGrade=0;R.variant="";
  }else{
    let d=null;
    if(DESIGN[L.slice(0,3)]){R.dcx=L.slice(0,3);d=DESIGN[R.dcx];R.seg.push([R.dcx,"디자인+IH",2]);L=L.slice(3);R.heating="IH";}
    else if(DESIGN[L.slice(0,2)]){R.dcx=L.slice(0,2);d=DESIGN[R.dcx];R.seg.push([R.dcx,"디자인+IH",2]);L=L.slice(2);R.heating="IH";}
    else if(DESIGN_OLD[L.slice(0,2)]){R.dcx=L.slice(0,2);d=DESIGN_OLD[R.dcx];R.seg.push([R.dcx,"디자인(구형)",2]);L=L.slice(2);R.heating="IH";
      R.flags.push("구형 명명체계(H가 앞) 모델입니다. 단종 수순이므로 신품 프리미엄을 주지 마세요.");}
    else{
      const ks=Object.keys(PLATE).sort((a,b)=>b.length-a.length);
      for(const k of ks) if(L.startsWith(k)){R.dcx=k;d=[k+"형",PLATE[k][1]];R.seg.push([k,"디자인(열판)",2]);L=L.slice(k.length);R.heating="열판";R._pt=!!PLATE[k][0];break;}
    }
    if(!d){R.ok=false;R.err="디자인 코드를 인식하지 못했습니다: "+L+" — 신규 코드이거나 오타일 수 있습니다.";return R;}
    R.design=d[0];R.designNote=d[1];
    R.silence=!!SIL[R.dcx]; R.oldGen=!!OLDG[R.dcx];

    R.variant="";
    for(const v in VAR) if(L.includes(v)){R.variant=v;R.seg.push([v,"병행 변형",4]);L=L.replace(v,"");}

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
  R.stem=m.replace(/\(.*?\)$/,"").match(/^(CRP?-?[A-Z]*\d+)/)[1];

  if(tail.length>2 && tail[0]==="T" && DISP[tail[1]] && COLOR[tail.slice(2)]){
    R.iot=true; R.seg.push(["T","IoT(WiFi)",1]); tail=tail.slice(1);
  }
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
const Wk=n=>n==null?"—":(n/10000).toFixed(n%10000?1:0)+"만";
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const eff=r=>r.sp||r.lp;
const heatShort=h=>h.startsWith("IH")?"IH":(h.includes("비압력")?"비압력":"열판");

/* 미등록 모델용 기준선 산출 (build_v3.py와 동일 로직) */
function calcTiers(d){
  const hr=HEATR[heatShort(d.heating)]||0;
  const sib=DB.filter(r=>r.sm===d.stem&&eff(r)).map(eff);
  const grp=DB.filter(r=>eff(r)&&r.st==="판매중"&&heatShort(r.ht)===heatShort(d.heating)
    &&r.tp===d.twin&&r.ls===d.low&&r.pg===d.potGrade&&r.si===d.silence&&r.cp===d.capacity).map(eff);
  const better=DB.filter(r=>{
    if(!eff(r)||r.st!=="판매중"||r.cp!==d.capacity||r.ls!==d.low)return false;
    if(d.potGrade===5&&r.pg<5)return false;
    const xr=HEATR[heatShort(r.ht)]||0;
    const xpg=(d.potGrade<5)?Math.min(r.pg,4):r.pg;
    const ge=xr>=hr&&(r.tp?1:0)>=(d.twin?1:0)&&xpg>=d.potGrade&&(r.si?1:0)>=(d.silence?1:0);
    const st=xr>hr||(r.tp?1:0)>(d.twin?1:0)||xpg>d.potGrade||(r.si?1:0)>(d.silence?1:0);
    return ge&&st;
  }).map(eff);
  const c=[];
  if(sib.length)c.push(Math.min(...sib));
  if(grp.length)c.push(Math.round(Math.min(...grp)*1.05));
  if(better.length)c.push(Math.round(Math.min(...better)*0.97));
  if(!c.length)return null;
  let f=1.0;
  if(d.oldGen)f*=0.85*0.85;      // 연식 미상 + 구형 라인
  const ceil=Math.round(Math.min(...c)*f/1000)*1000;
  return {px:[Math.round(ceil*0.68/1000)*1000,Math.round(ceil*0.8/1000)*1000,
              Math.round(ceil*0.9/1000)*1000,ceil],est:true};
}

function verdictOf(price,px){
  const [epic,spc,fair,ceil]=px;
  if(price<=epic)return{cls:"v-epic",t:"목표가 이하",d:"이 도구가 정한 가장 낮은 기준선(상한의 68%) 이하입니다. 보기 드문 가격이니 미개봉 정품·국내 정발인지 확인하고 사도 좋습니다."};
  if(price<=spc)return{cls:"v-deal",t:"진짜 특가",d:"절대상한 대비 20% 이상 저렴합니다. 필요하던 스펙이 맞다면 좋은 딜입니다."};
  if(price<=fair)return{cls:"v-fair",t:"적정가",d:"손해는 아니지만 특가도 아닙니다. 급하면 사도 되고, 급하지 않으면 특가 시즌(설·추석·블프)을 기다릴 만합니다."};
  if(price<=ceil)return{cls:"v-warm",t:"보류 — 흔한 가격",d:"절대상한 이내지만 흔히 볼 수 있는 가격입니다. '특가'라는 문구에 속지 마세요."};
  return{cls:"v-no",t:"비싼 편 — 기다리기 권장",d:"이 모델의 절대상한("+W(ceil)+")을 넘습니다. 같은 돈이면 더 나은 스펙을 살 수 있거나, 기다리면 이 가격 아래로 내려오는 경우가 많습니다."};
}

/* ═══ 탭 전환 ═══ */
const views={check:document.getElementById("view-check"),reco:document.getElementById("view-reco"),
  build:document.getElementById("view-build"),list:document.getElementById("view-list"),
  dict:document.getElementById("view-dict"),guide:document.getElementById("view-guide")};
const tabbar=document.querySelector(".tabbar");
function switchView(v){
  for(const k in views)views[k].classList.toggle("on",k===v);
  [...tabbar.children].forEach(b=>b.classList.toggle("on",b.dataset.v===v));
  window.scrollTo({top:0,behavior:"auto"});
}
tabbar.addEventListener("click",e=>{const b=e.target.closest("[data-v]");if(b)switchView(b.dataset.v);});

/* ═══ 최근 판정 기록 ═══ */
const LSK="cuckoo_recent_v3";
function loadRecent(){try{return JSON.parse(localStorage.getItem(LSK))||[]}catch(e){return[]}}
function saveRecent(m,p){
  try{
    let rec=loadRecent().filter(x=>x.m!==m);
    rec.unshift({m,p:p||""});
    localStorage.setItem(LSK,JSON.stringify(rec.slice(0,6)));
  }catch(e){}
  drawRecent();
}
function drawRecent(){
  const rec=loadRecent(), box=document.getElementById("recent");
  if(!rec.length){box.innerHTML="";return;}
  box.innerHTML=`<span class="tl">최근 판정</span>`+rec.map(x=>
    `<button class="chip-btn" data-ex="${esc(x.m)}" data-exp="${esc(x.p)}">${esc(x.m.replace(/^CRP?-/,""))}${x.p?`<small>@${Wk(+x.p)}</small>`:""}</button>`).join("");
}

/* ═══ 결과 렌더 ═══ */
function render(raw,priceRaw,quiet){
  const box=document.getElementById("result");
  const d=decode(raw);
  const price=priceRaw?parseInt(String(priceRaw).replace(/[^0-9]/g,"")):null;
  if(!d.ok){
    box.innerHTML=`<div class="card"><div class="empty"><b>해독할 수 없습니다</b>${esc(d.err)}<br><br>
      모델명은 밥솥 앞면 또는 바닥 라벨에 있습니다. 예: CRP-DHP0610FD</div></div>`;
    if(!quiet)box.scrollIntoView({behavior:"smooth",block:"start"});return;
  }
  saveRecent(d.model,price?String(price):"");
  const hit=DB.find(r=>r.m===d.model);
  let px=hit&&hit.px[3]?hit.px:null, est=false;
  if(!px){const t=calcTiers(d);if(t){px=t.px;est=true;}}
  const H=[];

  /* 가격 판정 배너 */
  if(price&&px){
    const v=verdictOf(price,px);
    H.push(`<div class="verdict ${v.cls}"><div class="vp">${W(price)}</div><div class="vt">${v.t}</div>
      <div class="vd">${v.d}${est?" (미등록/신규 모델 — 동급 스펙 기준 추정치입니다.)":""}</div></div>`);
  }else if(price&&!px){
    H.push(`<div class="verdict v-warm"><div class="vp">${W(price)}</div><div class="vt">판정 불가</div>
      <div class="vd">동급 비교 대상이 없어 기준선을 만들 수 없습니다.</div></div>`);
  }

  /* 코드 해부 */
  const cls=["mute","","key","warn","warn"];
  H.push(`<div class="anat"><h2>코드 해부</h2>
    <div class="note">초록 = 성능을 결정하는 자리 · 회색 = 무시해도 되는 자리 · 옆으로 스크롤</div>
    <div class="strip">${d.seg.map((s,i)=>
      `<div class="seg ${cls[s[2]]}" style="animation-delay:${i*45}ms">
        <span class="ch">${esc(s[0])}</span><span class="lb">${esc(s[1])}</span></div>`).join("")}</div>`);

  const rows=[["CRP/CR",d.pressure,""],
    [d.design,`<strong>${esc(d.designNote)}</strong>`,""],
    ["가열",`<strong>${esc(d.heating)}</strong>`, d.heating==="IH"?"내솥 전체를 유도가열. 2기압 이상 가능":d.heating==="열판"?"바닥만 가열. IH보다 압력이 낮은 편(모델별 표기 확인)":"압력 없음. 취사가 느림"],
    ["압력선택",d.twin?"<strong>트윈프레셔 있음</strong>":"없음",d.twin?"고압/무압 선택. 볶음밥·냉동밥에 유리":"압력 고정"],
    ["저당",d.low?"<strong>저당취사 있음</strong>":"없음",d.low?"트레이로 밥물 배출. 찰기는 줄어듦":""],
    [d.potCode,`<strong>${esc(d.pot)}</strong>`,d.potGrade?`내솥 등급 ${d.potGrade}/5`:""],
    ["용량",d.capacity?`<strong>${d.capacity}인용</strong>`:"미상",""],
    ["표시창",esc(d.disp),""],["색상",esc(hit&&hit.cl&&hit.cl!==d.color?hit.cl:d.color),"성능과 무관"]];
  if(d.iot) rows.splice(7,0,["T","<strong>IoT 모듈 (WiFi 앱연동)</strong>","표시창 코드 앞의 T"]);
  if(d.variant) rows.splice(5,0,[d.variant,`<strong>${VAR[d.variant]}</strong>`,"성능 차이 확인 안 됨 — 싼 쪽을 사면 됨"]);
  if(d.suffix) rows.push(["M","서픽스","가격·스펙 동일 확인. 외관 변형 추정"]);
  H.push(`<div class="legend">${rows.map(r=>
    `<div><span class="k">${esc(r[0])}</span><span class="v">${r[1]}${r[2]?` <em>— ${esc(r[2])}</em>`:""}</span></div>`).join("")}</div></div>`);

  /* LCD */
  const chips=[["IH 가열",d.heating==="IH"],["트윈프레셔",d.twin],["저당취사",d.low],
    ["올스테인리스",d.potCode==="AS"||d.potCode==="AR"],["사일런스",d.silence],["IoT",d.iot]];
  H.push(`<div class="lcd"><div class="tag">${hit?"공식몰 등록 모델":"미등록 — 코드 규칙으로 해독"}</div>
    <div class="title">${esc(d.model)}</div>
    ${hit?`<div class="name">${esc(hit.nm)}</div>`:""}
    <div class="line">${chips.map(c=>`<span class="fchip ${c[1]?"on":"off"}">${c[0]}</span>`).join("")}</div>
    <div class="meta">
      <div><span>용량</span><b>${d.capacity?d.capacity+"인용":"미상"}</b></div>
      <div><span>라인</span><b>${esc(d.designNote)}</b></div>
      <div><span>출시(등록)</span><b>${hit&&hit.rg?"20"+esc(hit.rg)+(hit.am>=12?" ("+Math.floor(hit.am/12)+"년 경과)":""):"미상"}</b></div>
      <div><span>상태</span><b>${hit?esc(hit.st)+(hit.nw?" · 신상":""):"미등록"}</b></div>
      ${hit&&hit.rc?`<div><span>인기 (월평균 리뷰)</span><b>${rvFmt(hit)} · 총 ${hit.rc.toLocaleString("ko-KR")}</b></div>`:""}
      ${hit&&hit.aw?`<div><span>최대 압력 (실측)</span><b>${hit.aw}기압${hit.tp?" · 무압 선택":""}</b></div>`:""}
      ${hit&&(hit.pw||hit.eg)?`<div><span>소비전력 · 효율 (실측)</span><b>${hit.pw?hit.pw.toLocaleString("ko-KR")+"W":"—"}${hit.eg?" · "+hit.eg+"등급":""}</b></div>`:""}
    </div></div>`);

  /* 지배 경고 — 같은 돈에 더 나은 대안 */
  if(hit&&hit.st==="판매중"){
    const doms=domCalc().get(hit.m);
    if(doms&&doms.length){
      H.push(`<div class="alert"><b>더 싸고 같거나 나은 모델이 있습니다 — 특별한 이유가 없다면 대안부터 보세요</b>
        가열·트윈·저당·사일런스·내솥·용량이 같거나 우위인데 가격은 같거나 쌉니다(색상형제 제외). 누르면 판정으로 이동.
        ${doms.slice(0,3).map(x=>`<div class="mrow" data-go="${x.m}"><div class="l"><div class="mm">${x.m}</div>
        <div class="ms">${esc(x.dz).replace(/\(.*\)/,"")} · ${heatShort(x.ht)}${x.tp?"·트윈":""}${x.si?"·사일런스":""} · 내솥 ${esc(x.pc)} · ${x.rg?"20"+x.rg:"—"}</div></div>
        <div class="mp">${W(eff(x))}${eff(x)<eff(hit)?` <span style="color:var(--ok);font-size:11px">${W(eff(x)-eff(hit))}</span>`:""}</div></div>`).join("")}</div>`);
    }
  }

  /* 후속작 리스크 — 라인 리프레시 주기 (다나와 등록월 기반 자체 추정) */
  if(hit&&d.dcx&&WX.lines&&WX.lines[d.dcx]){
    const L=WX.lines[d.dcx];
    if(L.med&&L.waves>=4){   /* 간격 3개 이상일 때만 주기를 추정한다 */
      const toN=s=>{const p=s.split(".").map(Number);return (2000+p[0])*12+p[1];};
      const now=new Date(),nowN=now.getFullYear()*12+now.getMonth()+1,fut=toN(L.next)>nowN,stale=nowN-toN(L.next)>12;
      H.push(`<div class="alert info"><b>후속작 리스크 — 이 라인의 신모델 주기</b>
        ${esc(d.designNote)} 라인의 신모델 웨이브 ${L.waves}회, 간격 중앙값 <b>${L.med}개월</b>(IQR ${L.q1}~${L.q3}개월).
        마지막 웨이브 20${L.last} → 다음 웨이브 추정 <b>20${L.next}</b> (20${L.next_lo}~20${L.next_hi}).
        ${fut?"아직 주기 안입니다 — 당분간 구형화 위험은 낮은 편.":stale?"추정 시점이 1년 넘게 지났습니다 — 라인이 정리됐거나 주기가 바뀐 것으로 보여 이 추정은 참고하지 마세요.":"주기상 후속 시점이 이미 지났습니다 — <b>리프레시 임박 또는 라인 정리 신호</b>. 제값 주고 사기엔 타이밍 위험이 있으니, 신형 발표 직후의 구형 할인을 노리는 편이 유리합니다."}
        <span style="display:block;font-size:11px;color:var(--muted);margin-top:4px">다나와 등록월(색상 추가 제외, 스템 최초 등장 기준) 자체 추정 — 제조사 공식 로드맵이 아닙니다.</span></div>`);
    }
  }

  /* 가격 관측 이력 (스냅샷 누적 — 서버 없이 로컬 파일) */
  if(hit&&hit.ph&&hit.ph.length>=2){
    const ph=hit.ph;
    const lo=Math.min(...ph.map(x=>x[1])), hi2=Math.max(...ph.map(x=>x[1]));
    const fmtD=x=>`${x.slice(0,2)}.${x.slice(2,4)}.${x.slice(4)}`;
    H.push(`<div class="card"><h3>가격 관측 이력</h3>
      <div class="cap">크롤 시점마다 공식몰가를 기록한 자체 이력입니다. 관측이 쌓일수록 "역대 최저"의 근거가 실측이 됩니다.</div>
      <div class="phrow">${ph.map(x=>`<span class="phpt${x[1]===lo&&lo!==hi2?" lo":""}">${fmtD(x[0])}<b>${Wk(x[1])}</b></span>`).join(`<span class="pharrow">→</span>`)}</div>
      <div class="cap" style="margin:8px 0 0">${lo===hi2?`관측 ${ph.length}회 — 변동 없음`:`관측 ${ph.length}회 — 최저 ${W(lo)} · 최고 ${W(hi2)}`}</div>
    </div>`);
  }

  /* 절대가격 기준선 */
  if(px){
    const [epic,spc,fair,ceil]=px;
    const off=hit?eff(hit):null;
    const hi=Math.max(ceil*1.25,off||0);
    const pw=v=>Math.max(4,(v/hi)*100);
    H.push(`<div class="card"><h3>절대가격 기준선</h3>
      <div class="cap">${est?"미등록/신규 모델 — 동급 스펙으로 추정한 기준입니다.":"동급 최저가 · 색상 형제 · 상위스펙 대체재 · 연식을 반영한 이 모델 전용 기준입니다."}
      오픈마켓 실시간가와 무관하게, 스펙만으로 "이 가격이면 사라/사지 마라"를 판단합니다.</div>
      <div class="ladder">
        <div class="ld-epic" style="width:${pw(epic)}%"><b>≤${Wk(epic)}</b></div>
        <div class="ld-deal" style="width:${pw(spc)-pw(epic)}%"><b>≤${Wk(spc)}</b></div>
        <div class="ld-fair" style="width:${pw(fair)-pw(spc)}%"><b>≤${Wk(fair)}</b></div>
        <div class="ld-warm" style="width:${pw(ceil)-pw(fair)}%"><b>≤${Wk(ceil)}</b></div>
        <div class="ld-no" style="flex:1"><b>&gt;${Wk(ceil)}</b></div>
      </div>
      <div class="ladlab"><span>0원</span><span>${W(Math.round(hi))}</span></div>
      <div class="ladkey">
        <span><i style="background:var(--epic)"></i>목표가</span>
        <span><i style="background:var(--ok)"></i>특가</span>
        <span><i style="background:var(--brass)"></i>적정</span>
        <span><i style="background:var(--warm)"></i>보류</span>
        <span><i style="background:var(--seal)"></i>비쌈</span>
      </div>
      <div class="prices">
        ${hit&&hit.lp?`<div><span>쿠쿠 정가</span><b class="strike">${W(hit.lp)}</b></div>`:""}
        ${off?`<div><span>쿠쿠몰 판매가${hit.dr?" ("+hit.dr+"%↓)":""}</span><b class="${off>ceil?"bad":""}">${W(off)}${off>ceil?" ⚠":""}</b></div>`:""}
        <div><span>목표가</span><b class="epic">${W(epic)} 이하</b></div>
        <div><span>특가 인정선</span><b class="good">${W(spc)} 이하</b></div>
        <div><span>절대상한 (넘으면 비쌈)</span><b class="bad">${W(ceil)}</b></div>
        ${hit&&mvOf(hit)?`<div><span>이 스펙이면 보통 이 가격 (시세 추정)</span><b>${W(mvOf(hit))}</b></div>
        <div><span>지금 쿠쿠몰가는</span><b class="${vfmText(hit).cls}">${vfmText(hit).t}</b></div>`:""}
      </div>
      ${off&&off>ceil?`<div class="alert"><b>공식몰 가격부터가 절대상한 초과입니다</b>
        지금 쿠쿠몰 가격(${W(off)})은 이 도구의 상한보다 높습니다. 공식몰 정가는 대부분 상한을 넘으니, 행사가가 ${W(ceil)} 이하로 내려올 때를 기다리거나 동급 대안을 보세요.</div>`:""}
    </div>`);
  }

  /* 색상 형제 */
  if(hit){
    const sib=DB.filter(r=>r.m!==hit.m&&r.sm===hit.sm);
    if(sib.length){
      const all=[hit,...sib].filter(r=>eff(r)).sort((a,b)=>eff(a)-eff(b));
      if(all.length>1&&eff(all[all.length-1])-eff(all[0])>0){
        H.push(`<div class="card"><h3>색상만 다른 같은 제품</h3>
          <div class="cap">성능은 동일합니다. 색상 선택만으로 ${W(eff(all[all.length-1])-eff(all[0]))} 차이가 납니다. 눌러서 판정으로 이동.</div>
          ${all.map(r=>`<div class="mrow ${r.m===hit.m?"self":""} ${eff(r)===eff(all[0])?"cheap":""}" data-go="${r.m}">
            <div class="l"><div class="mm">${r.m}</div><div class="ms">${esc(r.cl)} · ${r.rg?"20"+r.rg:"출시미상"}</div></div>
            <div class="mp">${W(eff(r))}</div></div>`).join("")}
          </div>`);
      }
    }
  }

  /* 동급 대안 */
  {
    const peers=DB.filter(r=>eff(r)&&heatShort(r.ht)===heatShort(d.heating)&&r.tp===d.twin&&r.ls===d.low
      &&r.pg===d.potGrade&&r.cp===d.capacity&&r.m!==d.model);
    if(peers.length){
      const sorted=peers.sort((a,b)=>eff(a)-eff(b)).slice(0,8);
      H.push(`<div class="card"><h3>같은 스펙 다른 모델</h3>
        <div class="cap">가열방식·압력선택·저당·내솥등급·용량이 같습니다. 더 싼 게 있으면 그쪽을 먼저 보세요. 눌러서 판정으로 이동.</div>
        ${sorted.map(r=>`<div class="mrow ${eff(r)===eff(sorted[0])?"cheap":""}" data-go="${r.m}">
          <div class="l"><div class="mm">${r.m}</div><div class="ms">${esc(r.dz).replace(/\(.*\)/,"")} · ${esc(r.cl)} · ${r.rg?"20"+r.rg:"출시미상"}</div></div>
          <div class="mp">${W(eff(r))}</div></div>`).join("")}
        </div>`);
    }
  }

  /* 경고 */
  const al=[];
  if(hit&&hit.am!=null&&hit.am>=72) al.push(`출시(등록) <b style='display:inline'>${Math.floor(hit.am/12)}년이 지난 모델</b>입니다. 신품 프리미엄을 줄 이유가 없습니다 — 기준선에 연식 감가가 이미 반영되어 있습니다.`);
  if(d.oldGen) al.push("<b style='display:inline'>구형 라인</b>입니다. 부품 수급·에너지효율에서 불리하고, 신형 동급보다 확실히 싸지 않다면 신형을 먼저 보세요.");
  if(d.variant==="NL") al.push("NL 변형입니다. FF 짝과 성능 차이가 확인되지 않았고 NL 쪽에 할인이 잘 붙습니다. <b style='display:inline'>같은 스펙이면 무조건 싼 쪽</b>을 사세요.");
  if(d.variant==="FF") al.push("FF 변형(2026 후행 리비전)입니다. 출시 초기라 할인이 거의 없습니다. NL 짝의 실구매가를 반드시 비교하세요.");
  if(d.heating==="열판"&&d.twin) al.push("트윈프레셔가 있지만 <b style='display:inline'>IH가 아닌 열판식</b>입니다. 이름과 기능만 보고 상급으로 오해하기 쉬운 지점입니다.");
  if(d.dcx==="UT") al.push("사일런스 '어반'은 이름만 사일런스인 <b style='display:inline'>열판식</b>입니다. IH 사일런스(NH/OH/PH/QH)와 완전히 다른 제품군입니다.");
  if(d.potCode==="AS"||d.potCode==="AR") al.push("올스테인리스 무코팅은 코팅 걱정이 없는 대신 <b style='display:inline'>밥알이 눌어붙어 세척이 번거롭습니다.</b>");
  if(d.low) al.push("저당 취사는 당질 30~40% 저감이지만 찰기·단맛도 줄어듭니다. 혈당 관리는 의사·영양사 상담과 병행하세요.");
  if(d.iot) al.push("IoT 앱연동 모델입니다. 앱 지원이 끊기면 일반 밥솥이 됩니다. IoT 기능에 웃돈을 크게 주지 마세요.");
  if(hit&&hit.st!=="판매중") al.push(`공식몰 상태가 <b style='display:inline'>${esc(hit.st)}</b>입니다. 단종 임박 모델은 가격이 오히려 오르는 경우가 있습니다 — 재고 프리미엄을 주지 마세요.`);
  d.flags.forEach(f=>al.push(esc(f)));
  if(hit&&(hit.aw||hit.pw))al.push("최대 압력·소비전력·에너지등급은 다나와/공식몰 텍스트에서 확보한 <b style='display:inline'>실측값</b>입니다. 구매 전 상세페이지에서 한 번 더 확인하세요.");
  else al.push("이 모델은 <b style='display:inline'>최대기압 · 에너지효율등급 · 소비전력</b> 실측을 확보하지 못했습니다. 상세페이지에서 확인하세요.");
  H.push(`<div class="alert warn"><b>확인하고 넘어갈 것</b><ul>${al.map(a=>`<li>${a}</li>`).join("")}</ul></div>`);

  box.innerHTML=H.join("");
  if(!quiet)box.scrollIntoView({behavior:"smooth",block:"start"});
}

/* ═══ 자동완성 ═══ */
const q=document.getElementById("q"), priceEl=document.getElementById("price"), ac=document.getElementById("ac");
let acIdx=-1, acList=[];
function showAC(){
  const v=q.value.toUpperCase().replace(/\s/g,"");
  if(v.length<2){ac.style.display="none";return;}
  acList=DB.filter(r=>r.m.includes(v)).slice(0,10);
  if(!acList.length){ac.style.display="none";return;}
  acIdx=-1;
  ac.innerHTML=acList.map((r,i)=>`<div data-i="${i}">${r.m}<span>${r.cp}인 · ${eff(r)?W(eff(r)):"가격없음"}</span></div>`).join("");
  ac.style.top=(q.offsetTop+q.offsetHeight-2)+"px";
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
    if(e.key==="Enter"&&acIdx>=0){e.preventDefault();q.value=acList[acIdx].m;ac.style.display="none";return;}
    if(e.key==="Escape"){ac.style.display="none";return;}
  }
  if(e.key==="Enter"){q.blur();go(q.value);}
});
priceEl.addEventListener("keydown",e=>{if(e.key==="Enter"){priceEl.blur();go(q.value);}});
priceEl.addEventListener("input",()=>{
  const raw=priceEl.value.replace(/[^0-9]/g,"");
  priceEl.value=raw?parseInt(raw).toLocaleString("ko-KR"):"";
});
ac.addEventListener("click",e=>{const t=e.target.closest("[data-i]");if(t){q.value=acList[+t.dataset.i].m;ac.style.display="none";priceEl.focus();}});
document.addEventListener("click",e=>{if(!e.target.closest(".console"))ac.style.display="none";});

function go(v){
  q.value=(v||"").toUpperCase();ac.style.display="none";
  switchView("check");
  render(v,priceEl.value);
}
document.getElementById("go").addEventListener("click",()=>{q.blur();priceEl.blur();go(q.value);});
document.body.addEventListener("click",e=>{
  const ex=e.target.closest("[data-ex]");
  if(ex){priceEl.value=ex.dataset.exp?parseInt(ex.dataset.exp).toLocaleString("ko-KR"):"";go(ex.dataset.ex);return;}
  const g=e.target.closest("[data-go]"); if(g){priceEl.value="";go(g.dataset.go);}
});

/* ═══ 리스트 탭 ═══ */
const CATS=[["ALL","전체"],["TP","트윈프레셔"],["IH","IH압력"],["PL","열판압력"],
 ["WM","보온(비압력)"],["LS","저당"],["AS","올스테인리스"],["SI","사일런스"]];
const CAPS=[["ALL","전체 용량"],["3","1~3인"],["6","4~6인"],["10","8인 이상"]];
let cur="ALL", curCap="ALL", sortKey="sp", sortAsc=true, lquery="", shown=40;
const PAGE=40;
const fbox=document.getElementById("filters"), cbox=document.getElementById("capfilters");
fbox.innerHTML=CATS.map(c=>`<button data-c="${c[0]}" class="${c[0]==="ALL"?"on":""}">${c[1]}</button>`).join("");
cbox.innerHTML=CAPS.map(c=>`<button data-p="${c[0]}" class="${c[0]==="ALL"?"on":""}">${c[1]}</button>`).join("");
fbox.addEventListener("click",e=>{const b=e.target.closest("[data-c]");if(!b)return;
  cur=b.dataset.c;[...fbox.children].forEach(x=>x.classList.toggle("on",x===b));shown=PAGE;drawBrowse();});
cbox.addEventListener("click",e=>{const b=e.target.closest("[data-p]");if(!b)return;
  curCap=b.dataset.p;[...cbox.children].forEach(x=>x.classList.toggle("on",x===b));shown=PAGE;drawBrowse();});
document.getElementById("lq").addEventListener("input",e=>{lquery=e.target.value.toUpperCase().replace(/\s/g,"");shown=PAGE;drawBrowse();});

function sortVal(r,k){
  if(k==="rg")return r.rg?parseFloat(r.rg.replace(".","")):0;
  if(k==="px1")return r.px[1]||0;
  if(k==="px3")return r.px[3]||0;
  if(k==="sp")return eff(r)||9e9;
  if(k==="vfm")return vfmOf(r)||0;
  if(k==="rv")return rvOf(r);
  const v=r[k]; return v==null?(typeof v==="number"?0:""):v;
}
function drawBrowse(){
  let rows=DB.filter(r=>cur==="ALL"||r.ct.includes(cur));
  if(effOnly)rows=rows.filter(r=>r.st==="판매중"&&!domCalc().has(r.m));
  if(curCap!=="ALL"){
    rows=rows.filter(r=>curCap==="3"?r.cp<=3:curCap==="6"?(r.cp>=4&&r.cp<=6):r.cp>=8);
  }
  if(lquery)rows=rows.filter(r=>r.m.includes(lquery)||r.nm.toUpperCase().includes(lquery));
  rows=rows.slice().sort((a,b)=>{
    const x=sortVal(a,sortKey),y=sortVal(b,sortKey);
    const c=(typeof x==="string")?x.localeCompare(y):x-y;
    return sortAsc?c:-c;
  });
  document.getElementById("lcnt").textContent=rows.length+"개";
  const vis=rows.slice(0,shown);
  document.getElementById("cards").innerHTML=vis.map(r=>{
    const badge=(r.st!=="판매중"?`<span class="badge b-so">${r.st}</span>`:"")+(r.nw?`<span class="badge b-new">NEW</span>`:"")
      +(domCalc().has(r.m)?`<span class="badge b-dom" title="같은 돈에 스펙이 같거나 더 좋은 모델이 있음">대안있음</span>`:"");
    return `<div class="pcard" data-go="${r.m}">
      <div class="pc-top"><span class="pm">${r.m}</span>${badge}</div>
      <div class="pc-mid">${esc(r.dz).replace(/\(.*\)/,"")} · ${r.cp}인 · ${heatShort(r.ht)}${r.tp?"·트윈":""}${r.ls?"·저당":""}${r.si?"·사일런스":""}${r.io?"·IoT":""} · 내솥 ${esc(r.pc)} · ${r.rg?"20"+r.rg:"출시미상"}${rvOf(r)?` · 리뷰 ${rvFmt(r)}`:""}</div>
      <div class="pc-row">
        <span class="pc-price">${r.lp&&r.sp?`<s>${Wk(r.lp)}</s>`:""}${eff(r)?Wk(eff(r)):"—"}${r.sp?"":" <span style='font-size:11px;color:var(--muted)'>(정가)</span>"}${r.dr?`<span class="d">${r.dr}%↓</span>`:""}</span>
        <span class="pc-px">특가 <b class="g">${r.px[1]?Wk(r.px[1]):"—"}</b> · 상한 <b class="r">${r.px[3]?Wk(r.px[3]):"—"}</b>${vfmPct(r)!=null?` · <b class="${vfmPct(r)>=VFM_T?"g":vfmPct(r)<=-VFM_T?"r":""}">${vfmPct(r)>=VFM_T?vfmPct(r)+"% 저렴":vfmPct(r)<=-VFM_T?(-vfmPct(r))+"% 비쌈":"시세수준"}</b>`:""}</span>
      </div></div>`;
  }).join("")||`<div class="empty"><b>결과 없음</b>필터나 검색어를 바꿔보세요.</div>`;
  const more=document.getElementById("more");
  more.style.display=rows.length>shown?"block":"none";
  more.textContent=`더 보기 (${rows.length-shown}개 남음)`;

  const sel=document.getElementById("sortsel");
  if(sel.value!==sortKey&&[...sel.options].some(o=>o.value===sortKey))sel.value=sortKey;
  document.getElementById("sortdir").textContent=sortAsc?"▲ 오름":"▼ 내림";
}
document.getElementById("more").addEventListener("click",()=>{shown+=PAGE;drawBrowse();});
document.getElementById("sortsel").addEventListener("change",e=>{
  sortKey=e.target.value;
  sortAsc=(sortKey!=="dr"&&sortKey!=="rc"&&sortKey!=="rg"&&sortKey!=="vfm"&&sortKey!=="rv"); // 할인·리뷰·출시·가성비·인기는 내림차순이 자연스러움
  shown=PAGE;drawBrowse();
});
document.getElementById("sortdir").addEventListener("click",()=>{sortAsc=!sortAsc;drawBrowse();});

/* ═══ 맨 위로 ═══ */
const totop=document.getElementById("totop");
window.addEventListener("scroll",()=>{totop.classList.toggle("show",window.scrollY>600)},{passive:true});
totop.addEventListener("click",()=>window.scrollTo({top:0,behavior:"smooth"}));

/* ═══ v3.1 확장: 항목별 가중치 · 코드 사전 · 조건 빌더 ═══ */
const WX=__WX__;
const sgn=n=>(n<0?"−":"+")+Math.abs(n).toLocaleString("ko-KR")+"원";

/* ── 가중치 ── */
const FEATW=[
 ["ih","IH 가열","열판 대비","전체 유도가열·2기압 이상. 밥맛 체감이 가장 큰 자리 — 우선순위 1"],
 ["twin","트윈프레셔","없음 대비","고압/무압 선택 — 우선순위 2"],
 ["low","저당취사","트윈만 있는 모델 대비","저당 트레이 추가분"],
 ["silence","사일런스","일반 라인 대비","증기 배출음 저감 (NH/OH/PH/QH)"],
 ["capL","8~10인 용량","4~6인 대비","대가족 프리미엄 — \"10인이면 얼마 더 주는 게 정상인가\"의 실제 값"],
 ["capS","1~3인 용량","4~6인 대비","소용량은 오히려 쌉니다"],
 ["flag","플래그십 라인 (마스터셰프·타철명장)","일반 라인 대비","LH·BDH·BCH 브랜드 프리미엄 — 기능 가치와 분리해 측정"],
 ["pot34","투톤·에코스텐 내솥","기본 코팅 대비","실판매가엔 웃돈이 없음 — 라인 구성 차이"],
 ["pot2","스텐외피 코팅 내솥","기본 코팅 대비",""],
 ["pot5","올스테인리스 내솥","기본 코팅 대비","추정값은 마이너스지만 통계적으로 확실하지 않음 — 웃돈이 확인되지 않음(상위호환이 아니라 취향 선택으로 봄)"],
 ["iot","IoT (WiFi)","없음 대비","표본 2개(같은 계열)뿐 — 웃돈을 추정할 수 없음. IoT에 웃돈을 크게 주지 마세요"],
 ["old","구형 명명·라인","신형 대비","구형은 이만큼 싸야 정상"],
 ["age","연차 1년당","등록 직후 대비","1년 지날 때마다 이만큼 감가"]];
function drawWeights(){
  const box=document.getElementById("wx");if(!box)return;
  const mx=Math.max(...FEATW.map(f=>Math.abs(WX.w[f[0]])));
  let h=`<div class="cap">시장이 각 기능에 <b>실제로 얼마를 얹는지</b>, 실판매가 ${WX.n}개를 통계 분석해 구한 값입니다.
    기준 모델(열판·4~6인·기본코팅·일반 라인·기능 없음·신형) ${WX.w.base.toLocaleString("ko-KR")}원 위에 아래 금액이 붙거나 빠집니다.
    <span class="conf hi">믿을 만함</span> = 데이터가 일관되게 보여주는 웃돈 ·
    <span class="conf lo">불확실</span> = 표본이 적거나 흔들려서 참고만 할 것.</div>`;
  h+=FEATW.map(f=>{const v=WX.w[f[0]],n=WX.cnt[f[0]],ci=WX.ci&&WX.ci[f[0]],pp=WX.wp?WX.wp[f[0]]:null;
    const na=WX.ci&&f[0] in WX.ci&&!ci, unc=na||(ci&&ci[0]<=0&&ci[1]>=0);
    return `<div class="wrow"><div class="wl"><b>${f[1]}</b><span>${f[2]}${n?` · 표본 ${n}개`:""}</span>${f[3]?`<em>${f[3]}</em>`:""}</div>
      <div class="wb">${na?"":`<i class="${v>=0?"pos":"neg"}" style="width:${Math.max(3,Math.abs(v)/mx*100)}%"></i>`}</div>
      <div class="wv ${na?"":v>=0?"pos":"neg"}">${na?"—":sgn(v)}<span class="wsub"><span class="conf ${unc?"lo":"hi"}">${na?"추정 불가":unc?"불확실":"믿을 만함"}</span>${pp!=null&&!na?` ${(pp>=0?"+":"−")+Math.abs(pp)}%`:""}</span></div></div>`;}).join("");
  h+=`<div class="wcap"><b>용량별 실측 중앙값 (IH 압력만)</b> — ${Object.entries(WX.cap).map(([c,v])=>`${c}인 ${Wk(v.med)} (${v.n}개)`).join(" · ")}</div>`;
  const cps=Object.entries(WX.colorp).filter(([c,v])=>v.n>=3&&v.avg>0&&!/미확정|미등록|^-$/.test(c)).slice(0,8);
  if(cps.length)h+=`<div class="wcap"><b>색상 프리미엄</b> — 같은 제품의 색상형제 중 최저가 색 대비 평균 웃돈.
    성능 차이는 전혀 없으니, 색만 양보하면 이만큼 아낍니다.<br>
    ${cps.map(([c,v])=>`${c} +${Wk(v.avg)}(${v.n})`).join(" · ")}</div>`;
  if(WX.dep){
    const db=WX.dep.bins,pc=x=>Math.round(x*100)+"%";
    h+=`<div class="wcap"><b>오래된 모델엔 얼마까지? — 연식 잔존율</b><br>
    같은 스펙이라도 출시 후 시간이 지난 모델은 그만큼 싸게 사야 정상입니다. 실판매가 회귀로 추정하되, 표본이 적은 6년 이상 구간은 보수적으로 정한 가정값입니다:<br>
    <span class="depline">출시 2년 이내 <b>${pc(db[0].f)}</b> → 2~4년 <b>${pc(db[1].f)}</b> → 4~6년 <b>${pc(db[2].f)}</b> → 6~8년 <b>${pc(db[3].f)}</b> → 8년 이상 <b>${pc(db[4].f)}</b></span>
    구형 명명 라인(H앞·AH·BH)은 여기에 추가로 <b>×${pc(WX.dep.old)}</b>.<br>
    예: 기준가 30만원짜리가 5년차면 <b>27만원이 상한</b>이라는 뜻. 이 계산은 각 모델의 <b>절대가격 기준선에 이미 자동 반영</b>되어
    있으므로 직접 계산할 필요는 없습니다. (신품 구매 상한 기준 — 중고 시세가 아님)</div>`;
  }
  h+=`<div class="wnote">방법: 헤도닉 회귀 v2 — 선형(원)+로그(%) 병행, 플래그십 분리, 부트스트랩 500회(색상만 다른 형제 모델은 한 묶음으로 재표본) 95% 신뢰구간으로 믿을 만함/불확실 판정, 표본이 너무 적은 항목은 추정 불가,
    감가는 연령구간 회귀+단조화+보수가정 결합. 설명력 R² ${WX.r2}(선형, 변수 수 보정 ${WX.r2adj}, 계열 단위 5겹 교차검증 약 ${WX.r2cv}(${WX.r2cv_rng[0]}~${WX.r2cv_rng[1]}))·${WX.r2log}(로그), 표본 ${WX.n}개·${WX.n_stems}계열. 상세: cuckoo-master.md §7.7·§7.10</div>`;
  box.innerHTML=h;
}

/* ── 코드 사전 ── */
function dstat(f){
  const rs=DB.filter(f);if(!rs.length)return null;
  const ps=rs.map(eff).filter(Boolean);
  const ex=rs.slice().sort((a,b)=>b.rc-a.rc)[0];
  return {n:rs.length,lo:ps.length?Math.min(...ps):null,hi:ps.length?Math.max(...ps):null,ex};
}
function buildDict(){
  const E=[];
  const P=(cat,c,nm,d,tier,tag,f)=>E.push({cat,c,nm,d,tier,tag,st:f?dstat(f):null});
  P("접두 — 제품 구분","CRP","전기압력밥솥","압력 취사. 쿠쿠 밥솥의 표준 — 이게 아니면 압력 취사가 아닙니다.","good","압력",r=>r.m.startsWith("CRP-"));
  P("접두 — 제품 구분","CR","전기보온밥솥 (비압력)","압력 없이 취사·보온. 취사가 느리고 밥맛에서 불리 — 보온·업소 용도가 아니면 비추천.","warn","비압력",r=>r.m.startsWith("CR-"));
  const LINED={CH:"10인용 주력. DH 구성의 대가족 버전.",DH:"6인용 볼륨존 주력. 모델 수·할인 변동이 가장 많아 특가가 자주 뜨는 라인.",
   EH:"3인용 전용 소형.",FH:"중상급. 트윈프레셔 조합이 많음.",JH:"중급 허리 라인. 2026년 JHF 신라인 포함 — 신모델이 계속 나옵니다.",
   KH:"트윈프레셔 중상급.",LH:"마스터셰프 — 플래그십. 저당(LHTR) 조합 다수, 가격대 최상단.",MH:"쁘띠 — 1~3인 소용량 라인.",
   NH:"사일런스 기본형. 증기 배출음 저감.",OH:"사일런스 오브제 — 디자인 파생.",PH:"사일런스 프로 — 상급.",QH:"사일런스 큐브 — 최신 파생.",
   BDH:"타철명장 — 무쇠(타철) 내솥 프리미엄.",BCH:"타철명장 파생.",
   AH:"구형 라인 — 단종 수순. 신품이라고 웃돈을 주지 마세요.",BH:"구형 라인 — 단종 수순. 신품이라고 웃돈을 주지 마세요."};
  for(const k in DESIGN){
    const old=!!OLDG[k],sil=!!SIL[k];
    P("디자인 라인 — IH 압력",k,DESIGN[k][1],
      (LINED[k]||"")+` IH 가열(${sgn(WX.w.ih)})`+(sil?` · 사일런스(${sgn(WX.w.silence)})`:"")+(old?` · 구형(${sgn(WX.w.old)})`:""),
      old?"warn":"good",old?"IH·구형":(sil?"IH·사일런스":"IH"),r=>r.dcx===k);
  }
  for(const k in DESIGN_OLD)
    P("디자인 라인 — 구형 명명",k,DESIGN_OLD[k][0],
      "구형 명명체계 — H가 라인명 앞에 옵니다. 단종 수순이라 기준선에 연식 감가가 추가 적용(×0.85)됩니다. 신형 동급보다 확실히 싸지 않으면 패스.",
      "warn","IH·구형",r=>r.dcx===k);
  const PLATED={ST:"더 라이트 — 열판인데 트윈프레셔를 얹은 보급 주력. 가성비 구간의 중심.",
   UT:"사일런스 '어반' — 이름만 사일런스인 열판식. IH 사일런스(NH/OH/PH/QH)와 완전 별개, 혼동 주의.",
   TT:"트윈프레셔 미니 — 열판 소형.",RT:"열판 트윈프레셔.",QK:"Q형 열판압력 보급형.",PK:"P형 열판압력 보급형.",
   RK:"R형 열판압력 보급형.",PW:"P형 열판압력 변형.",P:"P형 열판압력 — 한 글자 코드.",R:"R형 열판압력 — 한 글자 코드.",T:"미니 열판압력 — 한 글자 코드."};
  for(const k in PLATE)
    P("디자인 라인 — 열판 압력",k,PLATE[k][1],(PLATED[k]||"")+" 바닥만 가열, IH보다 압력이 낮은 편 — IH보다 싼 대신 밥맛에서 불리.",
      PLATE[k][0]?"mid":"neutral",PLATE[k][0]?"열판·트윈":"열판",r=>r.dcx===k);
  P("기능 코드","T","트윈프레셔 (라인 바로 뒤)",`고압↔무압 전환 선택. 볶음밥·냉동밥·쾌속취사에 유리. 실판매가 웃돈 ${sgn(WX.w.twin)}.`,"good",sgn(WX.w.twin),r=>r.tp);
  P("기능 코드","L","저당취사 (라인 바로 뒤)",`저당 트레이로 밥물 배출 — 당질 30~40% 저감, 대신 찰기·단맛도 감소. 트윈프레셔 포함. 트윈 대비 추가 웃돈 ${sgn(WX.w.low)}.`,"good",sgn(WX.w.low),r=>r.ls);
  P("기능 코드","T","IoT·WiFi (표시창 코드 앞)",`앱 연동(원격취사·예약). 표본 2개(같은 계열)뿐이라 실판매가로 웃돈을 추정할 수 없습니다. 앱 지원이 끊기면 일반 밥솥 — 웃돈을 주지 마세요.`,"warn","추정 불가",r=>r.io);
  P("기능 코드","M","서픽스 (맨 끝)","가격·스펙 동일 확인. 외관 변형 추정 — 무시해도 됩니다.","neutral","",r=>!!r.sf);
  P("병행 변형","NL","선행 리비전","FF와 병행 판매되는 변형 코드(세대 아님 — 등록월 거의 동시). 할인 유통 중심이라 실구매가가 싼 경우가 많습니다. 같은 스펙이면 싼 쪽.","mid","싼 쪽 구매",r=>r.vr==="NL");
  P("병행 변형","FF","후행 리비전 (2026)","NL 짝과 성능 차이 확인 안 됨. 출시 초기라 할인이 거의 없습니다 — NL 실구매가와 반드시 비교.","mid","비교 필수",r=>r.vr==="FF");
  const POTD={AS:"와이드앤플랫 올스테인리스(올스텐) 무코팅. 코팅 박리 걱정이 없는 대신 눌어붙어 세척이 번거로움.",
   AR:"라운드형 올스테인리스(올스텐) 무코팅. AS와 같은 성격.",XB:"다이아 계열 일반 코팅. 기본기.",
   R:"투톤코팅 + 라운드(커브드).",S:"에코스텐 — 하단 투톤코팅.",P:"스테인리스 외피 + 코팅 내솥.",
   B:"다이아쉴드/블랙 일반 코팅.",F:"타철명장/플랫 (구형)."};
  for(const [c,nm,g] of POT){
    let d=(POTD[c]||"")+` 내솥 등급 ${g}/5.`;
    if(g===5)d+=` 실판매가는 코팅보다 높지 않음(추정 ${sgn(WX.w.pot5)}, 불확실) — 상위호환이 아니라 취향 선택.`;
    P("내솥 코드",c,nm,d,g===5?"mid":(g>=3?"good":"neutral"),`등급 ${g}/5`,r=>r.pc===c);
  }
  for(const cc in CAP){
    const v=CAP[cc],cm=WX.cap[String(v)];
    let d=`${v}인용. 용량 숫자 뒤에 더 붙는 숫자(예: 0610의 10)는 유통 채널 구분 — 스펙과 무관, 무시.`;
    if(cm)d+=` IH 압력 실측 중앙값 ${Wk(cm.med)}(${cm.n}개).`;
    if(v<=3)d+=` 4~6인 대비 회귀 ${sgn(WX.w.capS)}.`;
    if(v>=8&&v<20)d+=` 4~6인 대비 회귀 ${sgn(WX.w.capL)}.`;
    P("용량 코드",cc,`${v}인용`,d,"neutral",cm?`중앙값 ${Wk(cm.med)}`:"",r=>r.cp===v);
  }
  const DISPM={F:"LCD",S:"숫자",B:"버튼",M:"구형 소형"};
  const DISPD={F:"LCD(퍼지) 디스플레이 — 현행 주력. 대부분의 모델이 F.",S:"일반 숫자·램프 표시.",
   B:"버튼식·일반 표시 — 보급형.",M:"구형 소형 표시 — 구형 보온밥솥 계열."};
  for(const k in DISP)P("표시창 코드",k,DISP[k],DISPD[k]||"","neutral","",r=>r.dp.includes(DISPM[k]));
  const cmap={};
  for(const code in COLOR){const nm=COLOR[code];(cmap[nm]=cmap[nm]||[]).push(code);}
  for(const nm in cmap){
    const pr=WX.colorp[nm];
    let d=nm.includes("미확정")?"실물 색상이 확인되지 않은 코드. 성능과 무관.":"성능과 무관 — 같은 제품이면 싼 색을 사면 됩니다.";
    if(pr&&pr.avg>0)d+=` 색상형제 대비 평균 ${Wk(pr.avg)} 비싸게 팔리는 인기색(표본 ${pr.n}개).`;
    else if(pr)d+=" 색상형제 중 최저가 축에 속하는 색.";
    P("색상 코드",cmap[nm].join("·"),nm,d,"neutral",pr&&pr.avg>0?`+${Wk(pr.avg)}`:"",r=>r.cl===nm);
  }
  return E;
}
let dictQ="";
function drawDict(){
  const box=document.getElementById("dict");if(!box)return;
  const q=dictQ.trim().toUpperCase();
  const cats=[...new Set(DICTE.map(e=>e.cat))];
  let h="",total=0;
  for(const c of cats){
    const es=DICTE.filter(e=>e.cat===c&&(!q||e.c.toUpperCase().includes(q)||e.nm.toUpperCase().includes(q)||e.d.toUpperCase().includes(q)||c.toUpperCase().includes(q)));
    if(!es.length)continue; total+=es.length;
    h+=`<div class="dcat">${c}</div>`+es.map(e=>{
      const s=e.st;
      return `<div class="drow t-${e.tier}"><div class="dc">${e.c}</div><div class="dm">
        <div class="dn"><b>${e.nm}</b>${e.tag?`<span class="dtag t-${e.tier}">${e.tag}</span>`:""}</div>
        <div class="dd">${e.d}</div>
        ${s?`<div class="ds">공식몰 ${s.n}개${s.lo?` · ${Wk(s.lo)}~${Wk(s.hi)}`:""}${s.ex?` · 대표 <span class="lnk" data-go="${s.ex.m}">${s.ex.m}</span>`:""}</div>`:`<div class="ds">현재 공식몰 등록 0개 (규칙상 존재하는 코드)</div>`}
        </div></div>`;}).join("");
  }
  const cnt=document.getElementById("dictcnt");if(cnt)cnt.textContent=total+"개 코드";
  box.innerHTML=h||`<div class="empty"><b>검색 결과 없음</b>다른 코드나 단어로 검색해보세요.</div>`;
}

/* ── 조건 빌더 ── */
const BFIELDS=[
 ["heat","가열",[["any","무관"],["IH","IH"],["열판","열판"],["비압력","비압력(보온)"]]],
 ["twin","트윈프레셔",[["any","무관"],["y","있음"],["n","없음"]]],
 ["low","저당",[["any","무관"],["y","있음"],["n","없음"]]],
 ["sil","사일런스",[["any","무관"],["y","있음"],["n","없음"]]],
 ["iot","IoT",[["any","무관"],["y","있음"],["n","없음"]]],
 ["pot","내솥",[["any","무관"],["5","올스텐"],["34","투톤·에코스텐"],["2","스텐외피"],["1","기본코팅"]]],
 ["cap","용량",[["any","무관"],["S","1~3인"],["M","4~6인"],["L","8인 이상"]]],
 ["sale","판매상태",[["y","판매중만"],["any","품절 포함"]]]];
let BS={heat:"any",twin:"any",low:"any",sil:"any",iot:"any",pot:"any",cap:"any",sale:"y"};
function bMatch(r){
  if(BS.sale==="y"&&r.st!=="판매중")return false;
  if(BS.heat!=="any"&&heatShort(r.ht)!==BS.heat)return false;
  if(BS.twin!=="any"&&r.tp!==(BS.twin==="y"))return false;
  if(BS.low!=="any"&&r.ls!==(BS.low==="y"))return false;
  if(BS.sil!=="any"&&r.si!==(BS.sil==="y"))return false;
  if(BS.iot!=="any"&&r.io!==(BS.iot==="y"))return false;
  if(BS.pot!=="any"){
    const g=r.pg;
    if(BS.pot==="5"&&g!==5)return false;
    if(BS.pot==="34"&&!(g===3||g===4))return false;
    if(BS.pot==="2"&&g!==2)return false;
    if(BS.pot==="1"&&g>1)return false;
  }
  if(BS.cap!=="any"){
    const c=r.cp||0;
    if(BS.cap==="S"&&c>3)return false;
    if(BS.cap==="M"&&(c<4||c>6))return false;
    if(BS.cap==="L"&&c<8)return false;
  }
  return true;
}
function bEstimate(){
  if(BS.heat==="비압력")return null;
  let v=WX.w.base;const parts=[["기본",WX.w.base]];
  const add=(cond,key,label)=>{if(cond){v+=WX.w[key];parts.push([label,WX.w[key]]);}};
  add(BS.heat==="IH","ih","IH");
  add(BS.twin==="y"||BS.low==="y","twin","트윈");
  add(BS.low==="y","low","저당");
  add(BS.sil==="y","silence","사일런스");
  add(BS.iot==="y","iot","IoT");
  add(BS.pot==="5","pot5","올스텐");
  add(BS.pot==="34","pot34","투톤·에코스텐");
  add(BS.pot==="2","pot2","스텐외피");
  add(BS.cap==="S","capS","1~3인");
  add(BS.cap==="L","capL","8인 이상");
  return {v:Math.round(v/1000)*1000,parts};
}
function drawBuilder(){
  const box=document.getElementById("bld");if(!box)return;
  box.innerHTML=BFIELDS.map(f=>`<div class="bfield"><span class="bl">${f[1]}</span><div class="bops">
    ${f[2].map(o=>`<button data-bf="${f[0]}" data-bv="${o[0]}" class="${BS[f[0]]===o[0]?"on":""}">${o[1]}</button>`).join("")}
  </div></div>`).join("");
  const res=document.getElementById("bres");if(!res)return;
  const rows=DB.filter(bMatch).sort((a,b)=>(eff(a)||9e9)-(eff(b)||9e9));
  const est=bEstimate();
  const selCnt=Object.keys(BS).filter(k=>k!=="sale"&&BS[k]!=="any").length;
  let h="";
  if(est&&selCnt){
    const ps=est.parts.map((p,i)=>i===0?`기본 ${p[1].toLocaleString("ko-KR")}`:`${p[0]} ${p[1]<0?"−":"+"}${Math.abs(p[1]).toLocaleString("ko-KR")}`).join(" · ");
    h+=`<div class="best">이 조합의 회귀 예상가 <b>${W(est.v)}</b>
      <span class="bparts">${ps}</span>
      <span class="bnote">신형·연차 0 기준. 선택 안 한 항목은 기본값(열판·4~6인·기본코팅·기능 없음)으로 가정한 추정치이며,
      실제 판단은 개별 모델의 절대가격 기준선을 따르세요.</span></div>`;
  }
  if(!rows.length){
    const sugg=[];
    for(const f of BFIELDS){
      if(f[0]==="sale"||BS[f[0]]==="any")continue;
      const save=BS[f[0]];BS[f[0]]="any";
      const n=DB.filter(bMatch).length;BS[f[0]]=save;
      if(n)sugg.push(`'${f[1]}' 조건을 빼면 ${n}개`);
    }
    h+=`<div class="empty"><b>이 조합의 제품이 공식몰에 없습니다</b>${sugg.length?sugg.join(" · "):"조건을 하나씩 풀어보세요."}</div>`;
  }else{
    h+=`<div class="bcnt">${rows.length}개 일치 — 싼 순 ${Math.min(rows.length,15)}개 표시</div>`;
    h+=rows.slice(0,15).map(r=>`<div class="mrow ${eff(r)===eff(rows[0])?"cheap":""}" data-go="${r.m}">
      <div class="l"><div class="mm">${r.m}${r.st!=="판매중"?` <span class="badge b-so">${r.st}</span>`:""}${r.nw?` <span class="badge b-new">NEW</span>`:""}</div>
      <div class="ms">${esc(r.dz).replace(/\(.*\)/,"")} · ${r.cp}인 · ${heatShort(r.ht)}${r.tp?"·트윈":""}${r.ls?"·저당":""}${r.si?"·사일런스":""}${r.io?"·IoT":""} · 내솥 ${esc(r.pc)} · ${r.rg?"20"+r.rg:"—"}</div></div>
      <div class="mp">${eff(r)?W(eff(r)):"—"}</div></div>`).join("");
  }
  res.innerHTML=h;
}
const _bld=document.getElementById("bld");
if(_bld)_bld.addEventListener("click",e=>{const b=e.target.closest("[data-bf]");if(!b)return;BS[b.dataset.bf]=b.dataset.bv;drawBuilder();});
const _dq=document.getElementById("dictq");
if(_dq)_dq.addEventListener("input",e=>{dictQ=e.target.value;drawDict();});
const DICTE=buildDict();

/* ═══ v3.2: 가성비 지수 · 상황별 추천 · 쉬운 FAQ ═══ */
function mvOf(r){
  if(!eff(r)||heatShort(r.ht)==="비압력")return null;
  let v=WX.w.base;
  if(heatShort(r.ht)==="IH")v+=WX.w.ih;
  if(r.tp)v+=WX.w.twin;
  if(r.ls)v+=WX.w.low;
  if(r.si)v+=WX.w.silence;
  if(r.io)v+=WX.w.iot;
  if(r.pg===5)v+=WX.w.pot5;else if(r.pg>=3)v+=WX.w.pot34;else if(r.pg===2)v+=WX.w.pot2;
  if(r.cp&&r.cp<=3)v+=WX.w.capS;else if(r.cp>=8)v+=WX.w.capL;
  if(r.dcx==="LH"||r.dcx==="BDH"||r.dcx==="BCH")v+=WX.w.flag;
  if(r.og)v+=WX.w.old;
  if(r.am)v+=WX.w.age*(r.am/12);
  return Math.max(Math.round(v/1000)*1000,50000);
}
const rvOf=r=>r.rc?(r.am&&r.am>=1?r.rc/r.am:r.rc):0;   // 월평균 리뷰 = 스테디셀러 지수
const rvFmt=r=>{const v=rvOf(r);return v?(v>=1?Math.round(v):v.toFixed(1))+"/월":"—";};
const vfmOf=r=>{const m=mvOf(r);return m&&eff(r)?m/eff(r):null;};
const vfmPct=r=>{const v=vfmOf(r);return v?Math.round((v-1)*100):null;};
/* 시세 추정의 보통 오차가 약 20%라 그보다 작은 차이는 '시세 수준'으로 본다 */
const VFM_T=20;
function vfmText(r){const p=vfmPct(r);if(p==null)return null;
  if(p>=VFM_T)return{t:"시세 대비 "+p+"% 저렴",cls:"good"};
  if(p<=-VFM_T)return{t:"시세 대비 "+(-p)+"% 비쌈",cls:"bad"};
  return{t:"시세 수준 (추정 오차 안)",cls:""};}
const VSHORT={"v-epic":"목표가","v-deal":"특가","v-fair":"적정","v-warm":"보류","v-no":"비쌈"};

/* ── 상황별 추천 ── */
const PERS=[
 {k:"solo",ic:"🍚",t:"1인 가구",
  d:"한 번에 1~2공기면 3인용이 맞습니다. 크게 지어 냉동해 두는 스타일이라면 6인+트윈프레셔(냉동밥)도 대안이니, 신혼·2인 추천도 함께 보세요.",
  tiers:[
   ["이거면 충분","1~3인용 압력밥솥 중 지금 가장 값어치 있는 것 — 혼자 먹는 밥은 이걸로 부족하지 않습니다.",r=>r.cp<=3&&heatShort(r.ht)!=="비압력"],
   ["균형 추천","소형인데 IH — 혼자 살아도 밥맛은 포기하지 않는 선택.",r=>r.cp<=3&&heatShort(r.ht)==="IH"],
   ["제대로 갖추기","소형 IH + 트윈프레셔 — 냉동밥·쾌속·요리까지, 1인 가구 상한선.",r=>r.cp<=3&&heatShort(r.ht)==="IH"&&r.tp]]},
 {k:"couple",ic:"👫",t:"신혼·2인",
  d:"2인이어도 6인용이 표준입니다. 잡곡·현미는 물을 더 먹고, 손님과 냉동밥까지 생각하면 3인용은 금방 좁아집니다.",
  tiers:[
   ["이거면 충분","6인 열판+트윈프레셔(더 라이트 계열) — 가장 싸게 '압력밥솥다운 밥'.",r=>r.cp>=4&&r.cp<=6&&heatShort(r.ht)==="열판"&&r.tp],
   ["균형 추천","6인 IH — 밥맛 체감이 가장 큰 업그레이드에 돈을 쓰는 선택.",r=>r.cp>=4&&r.cp<=6&&heatShort(r.ht)==="IH"],
   ["제대로 갖추기","6인 IH+트윈프레셔 — 무압 요리·냉동밥까지, 신혼 활용도 최상.",r=>r.cp>=4&&r.cp<=6&&heatShort(r.ht)==="IH"&&r.tp]]},
 {k:"fam4",ic:"👨‍👩‍👧",t:"3~4인 가족",
  d:"6인용이 기본, 아이들이 크면 10인용. 매일 쓰는 물건이라 IH 값(밥맛)은 하는 집이 많습니다.",
  tiers:[
   ["이거면 충분","6인 열판 트윈 — 예산 최소로 4인 식탁.",r=>r.cp>=4&&r.cp<=6&&heatShort(r.ht)==="열판"&&r.tp],
   ["균형 추천","6인 IH 트윈 — 가족 식탁의 표준 조합.",r=>r.cp>=4&&r.cp<=6&&heatShort(r.ht)==="IH"&&r.tp],
   ["제대로 갖추기","10인 IH 트윈 — 손님·잡곡·찜까지 여유 있게.",r=>r.cp>=8&&heatShort(r.ht)==="IH"&&r.tp]]},
 {k:"big",ic:"👨‍👩‍👧‍👦",t:"대가족 5인+",
  d:"8~10인용. 한 번에 많이 짓고 보온 시간이 길어지므로 보온 품질까지 좋은 IH의 가치가 더 커집니다.",
  tiers:[
   ["이거면 충분","8인 이상 압력밥솥 중 최고 값어치.",r=>r.cp>=8&&heatShort(r.ht)!=="비압력"],
   ["균형 추천","10인 IH.",r=>r.cp>=8&&heatShort(r.ht)==="IH"],
   ["제대로 갖추기","10인 IH+트윈.",r=>r.cp>=8&&heatShort(r.ht)==="IH"&&r.tp]]},
 {k:"sugar",ic:"🩺",t:"혈당 관리",
  d:"저당취사(L 코드)는 트레이로 밥물을 빼 당질 30~40%를 줄입니다. 찰기·단맛도 함께 줄어드니 '맛은 조금 양보'가 전제이고, 혈당 관리는 의사 상담과 병행하세요.",
  tiers:[
   ["이거면 충분","저당취사 되는 것 중 지금 최고 값어치.",r=>r.ls],
   ["균형 추천","저당 + 4~6인 IH.",r=>r.ls&&r.cp>=4&&r.cp<=6&&heatShort(r.ht)==="IH"],
   ["제대로 갖추기","마스터셰프 저당(LHTR) — 저당에 요리 활용까지.",r=>r.ls&&r.dcx==="LH"]]},
 {k:"quiet",ic:"🤫",t:"소음 민감",
  d:"증기 배출음이 스트레스라면 사일런스(NH/OH/PH/QH). 원룸·오픈키친·아기 있는 집에서 체감이 큽니다. '사일런스 어반(UT)'은 이름만 같은 열판식이라 제외했습니다.",
  tiers:[
   ["이거면 충분","IH 사일런스 중 최고 값어치.",r=>r.si],
   ["균형 추천","사일런스 + 트윈프레셔.",r=>r.si&&r.tp],
   ["제대로 갖추기","사일런스 오브제/프로/큐브 상급.",r=>r.si&&r.tp&&(r.dcx==="OH"||r.dcx==="PH"||r.dcx==="QH")]]},
 {k:"cook",ic:"🍲",t:"요리·이유식",
  d:"트윈프레셔의 무압 모드가 요리용입니다(만능찜·조림·냄비밥 식감). 마스터셰프(LH)는 오픈쿠킹(취사 중 뚜껑 열고 재료 추가)에 이유식·건강죽·누룽지 등 요리모드가 가장 많습니다.",
  tiers:[
   ["이거면 충분","트윈프레셔(무압 요리 가능) 중 최고 값어치.",r=>r.tp&&heatShort(r.ht)!=="비압력"],
   ["균형 추천","IH + 트윈 — 요리와 밥맛 둘 다.",r=>r.tp&&heatShort(r.ht)==="IH"],
   ["제대로 갖추기","마스터셰프(LH) — 오픈쿠킹 + 요리모드 최다.",r=>r.dcx==="LH"]]},
 {k:"budget",ic:"💸",t:"최소 예산",
  d:"어쨌든 압력밥솥이 필요할 뿐이라면. 단, 구형 재고(오히려 비싼 경우가 있음)는 걸렀습니다.",
  tiers:[
   ["이거면 충분","판매중 압력밥솥 중 최저가(구형 제외).",r=>heatShort(r.ht)!=="비압력"&&!r.og,"cheap"],
   ["균형 추천","최저가권에서 트윈프레셔까지 챙기기.",r=>heatShort(r.ht)!=="비압력"&&!r.og&&r.tp,"cheap"],
   ["제대로 갖추기","시세 대비 가장 싸게 팔리는 IH — 같은 돈으로 가장 많은 스펙.",r=>heatShort(r.ht)==="IH"&&!r.og,"vfm"]]},
];
let curPers="solo";
function pick(filter,exclude,mode){
  const all=DB.filter(r=>r.st==="판매중"&&eff(r)&&r.px&&r.px[3]&&filter(r)&&!exclude.has(r.m));
  const und=all.filter(r=>!domCalc().has(r.m));   // 지배당한 모델은 추천에서 제외
  const c=und.length?und:all;
  if(!c.length)return null;
  c.sort((a,b)=>mode==="cheap"?(eff(a)-eff(b))
    :mode==="vfm"?((vfmOf(b)||0)-(vfmOf(a)||0))
    :((eff(a)/a.px[3])-(eff(b)/b.px[3])||eff(a)-eff(b)));
  return c[0];
}
function nowReason(r){
  const v=verdictOf(eff(r),r.px);
  const pct=Math.round(eff(r)/r.px[3]*100);
  const map={"v-epic":"목표가 이하 — 사도 좋은 시점","v-deal":"특가 구간 — 지금 사도 되는 시점",
    "v-fair":"적정가 구간 — 손해는 아닌 시점","v-warm":"평소 가격 — 급하지 않으면 특가 시즌을 기다릴 만함",
    "v-no":"기준선 초과 — 후보 중 최선일 뿐, 지금 가격엔 사지 말 것"};
  return `지금 쿠쿠몰가 ${W(eff(r))}${r.dr?` (정가 대비 ${r.dr}%↓)`:""}는 이 모델 절대상한의 ${pct}% — ${map[v.cls]}`;
}
function drawReco(){
  const pbox=document.getElementById("pers");if(!pbox)return;
  pbox.innerHTML=PERS.map(p=>`<button data-pk="${p.k}" class="${p.k===curPers?"on":""}">${p.ic} ${p.t}</button>`).join("");
  const p=PERS.find(x=>x.k===curPers), box=document.getElementById("reco");
  const ex=new Set(), lvCls=["","l2","l3"];
  let h=`<div class="pdesc">${p.d}</div>`;
  p.tiers.forEach((t,i)=>{
    const r=pick(t[2],ex,t[3]);
    h+=`<div class="rtier"><div><span class="rt-lv ${lvCls[i]}">${t[0]}</span><span class="rt-why">${t[1]}</span></div>`;
    if(!r){h+=`<div class="rt-now">이 조건에 맞는 판매중 모델이 지금 없습니다.</div></div>`;return;}
    ex.add(r.m);
    const v=verdictOf(eff(r),r.px);
    h+=`<div class="mrow" data-go="${r.m}">
      <div class="l"><div class="mm">${r.m}<span class="vbadge ${v.cls}">${VSHORT[v.cls]}</span>${r.nw?` <span class="badge b-new">NEW</span>`:""}</div>
      <div class="ms">${esc(r.dz).replace(/\(.*\)/,"")} · ${r.cp}인 · ${heatShort(r.ht)}${r.tp?"·트윈":""}${r.ls?"·저당":""}${r.si?"·사일런스":""}${r.io?"·IoT":""} · 내솥 ${esc(r.pc)} · ${r.rg?"20"+r.rg:"—"}</div></div>
      <div class="mp">${W(eff(r))}</div></div>
      <div class="rt-now">${nowReason(r)}${vfmText(r)?` · <b class="tx-${vfmText(r).cls||"mid"}">${vfmText(r).t}</b>`:""}</div></div>`;
  });
  h+=`<div class="cap" style="margin-top:10px">선정 방식: 판매중 + 각 단계 조건 충족 모델 중 "현재가 ÷ 자체 절대상한"이 가장 유리한 것(최소 예산은 최저가순).
    모델을 누르면 판정 화면에서 근거 전체(기준선·형제·동급 대안)를 볼 수 있습니다.</div>`;
  box.innerHTML=h;
}
const _pers=document.getElementById("pers");
if(_pers)_pers.addEventListener("click",e=>{const b=e.target.closest("[data-pk]");if(!b)return;curPers=b.dataset.pk;drawReco();});

/* ── 쉬운 FAQ ── */
function drawFaq(){
  const box=document.getElementById("faq");if(!box)return;
  const cell=f=>{const rs=DB.filter(r=>r.st==="판매중"&&eff(r)&&f(r));if(!rs.length)return "0개";const ps=rs.map(eff);return `${rs.length}개 · ${Wk(Math.min(...ps))}~${Wk(Math.max(...ps))}`;};
  box.innerHTML=`
  <details class="faq" open><summary>IH가 뭔가요? 트윈프레셔에만 있는 건가요?</summary><div class="fa">
    <p><b>완전히 별개인 두 기능입니다.</b> IH는 <b>가열 방식</b> — 코일로 내솥 전체를 통째로 가열합니다(열판은 바닥만 가열, 압력도 IH보다 낮은 편).
    트윈프레셔는 <b>압력 방식</b> — 고압(약 2기압)과 무압을 스위치로 고릅니다. 그래서 네 조합이 모두 실제로 존재합니다:</p>
    <table class="mtx"><tr><th></th><th>트윈프레셔 있음</th><th>트윈프레셔 없음</th></tr>
    <tr><th>IH</th><td>${cell(r=>heatShort(r.ht)==="IH"&&r.tp)}</td><td>${cell(r=>heatShort(r.ht)==="IH"&&!r.tp)}</td></tr>
    <tr><th>열판</th><td>${cell(r=>heatShort(r.ht)==="열판"&&r.tp)}</td><td>${cell(r=>heatShort(r.ht)==="열판"&&!r.tp)}</td></tr></table>
    <p>돈을 한 곳에만 쓸 수 있다면 <b>IH가 먼저</b>입니다 — 밥맛 체감이 가장 크고, 시장도 IH에 ${sgn(WX.w.ih)},
    트윈프레셔에 ${sgn(WX.w.twin)}을 매깁니다.</p></div></details>
  <details class="faq"><summary>트윈프레셔는 정확히 뭐고, 돈값 하나요?</summary><div class="fa">
    <p>취사 압력을 <b>고압(약 2기압)</b>과 <b>무압</b> 중에서 고르는 기능입니다. 고압이면 촉촉하고 찰진 압력밥,
    무압이면 고슬고슬한 냄비밥 식감 — 그리고 이 무압 모드가 찜·조림·이유식 같은 <b>요리 기능의 기반</b>입니다.</p>
    <p>실판매가 기준 시장 웃돈은 <b>${sgn(WX.w.twin)}</b>. 냉동밥을 자주 만든다 / 볶음밥·고슬밥을 좋아한다 /
    찜·조림·이유식에 쓸 생각이다 — 하나라도 해당하면 그 값을 합니다. 반대로 <b>흰밥을 고압으로만</b> 먹는 집이라면
    없어도 아쉽지 않습니다.</p></div></details>
  <details class="faq"><summary>내솥은 뭐가 좋은가요? 올스텐 vs 투톤 vs 스텐외피 vs 코팅</summary><div class="fa">
    <p><b>정답이 없는 취향 문제</b>라, 두 질문이면 정리됩니다.</p>
    <p>① 코팅 벗겨짐이 스트레스고 몇 년마다 내솥 교체비(3~10만원)가 싫다 → <b>올스테인리스(AS/AR)</b>.
    무코팅이라 반영구인 대신 밥알이 눌어붙어 설거지가 번거롭습니다.</p>
    <p>② 설거지 편한 게 최고다 → <b>코팅 내솥</b>(XB/B 기본, S 에코스텐, P 스텐외피, R 투톤). 등급이 높을수록
    구성이 좋지만 결국 소모품 — 수년 뒤 내솥만 사서 교체하면 됩니다. 투톤·에코스텐·스텐외피는 코팅 계열 안의 변형일 뿐,
    사용감 차이는 크지 않습니다.</p>
    <p>실판매가 근거: 올스텐이라고 더 비싸게 팔리지 않습니다(추정 <b>${sgn(WX.w.pot5)}</b>, 통계적으로는 불확실) — 상위호환이 아니라 '취향 옵션'으로 보는 편이 맞습니다.</p></div></details>
  <details class="faq"><summary>밥맛을 점수로 매길 수 있나요?</summary><div class="fa">
    <p><b>솔직한 답: 공인된 밥맛 점수는 없습니다.</b> 블라인드 테스트도 쌀·물·보온 시간에 따라 결과가 흔들려
    재현성이 낮습니다. 물리적으로 밥맛을 좌우하는 변수는 스펙에서 세 가지가 잡힙니다 — ① 가열 균일도(IH &gt; 열판)
    ② 압력(고압일수록 찰짐, 쿠쿠 고압 약 2기압) ③ 보온 품질. 여기까지가 "스펙으로 말할 수 있는 맛"이고 그 너머는 취향입니다.</p>
    <p>그래서 이 도구는 맛 점수를 지어내는 대신, <b>시장이 각 기능에 매긴 값(항목별 가중치)</b>과
    <b>"시세 대비 n% 저렴/비쌈"</b> 표시로 수치화합니다 — 주관 없이 실판매가 데이터로만 계산한 숫자입니다.</p></div></details>
  <details class="faq"><summary>밥솥으로 요리도 되나요? 마스터셰프가 뭔가요?</summary><div class="fa">
    <p>트윈프레셔 모델이면 무압 모드로 <b>만능찜·조림·이유식</b>이 됩니다. 그중 <b>마스터셰프 = LH 라인</b>입니다
    (코드에서 빠진 게 아니라 LH가 바로 그것). 요리 특화 플래그십으로 취사모드 11가지, 이유식·건강죽·누룽지·간편식 메뉴,
    고압&무압찜, 그리고 <b>오픈쿠킹</b>(취사 중 뚜껑을 열어 재료 추가 — 나물밥에 유용)까지 지원합니다.
    "요리 전용"이 아니라 <b>"요리까지 잘하는 밥솥"</b>입니다. 추천 탭의 '요리·이유식'에서 현시점 추천을 볼 수 있습니다.</p></div></details>
  <details class="faq"><summary>돈값 못하는 기능은 뭔가요?</summary><div class="fa">
    <p>실판매가 데이터 기준으로: ① <b>IoT(WiFi)</b> — 표본이 2개뿐이라 시장 웃돈을 추정할 수 없고, 앱 지원이 끊기면
    일반 밥솥이 됩니다. ② <b>인기 색상 웃돈</b> — 성능이 동일한데 색만으로 수만~수십만원 차이. ③ <b>구형 재고 프리미엄</b> —
    단종 임박 모델이 오히려 비싸지는 현상. ④ <b>"정가 대비 50% 할인"</b> — 정가 자체가 높게 잡혀 있어 할인율은
    판단 근거가 못 됩니다. 할인율보다 이 도구의 절대가격 기준선과 비교해 보세요.</p></div></details>
  <details class="faq"><summary>"시세 대비 n% 저렴"은 뭘 뜻하나요?</summary><div class="fa">
    <p>이 도구가 공식몰 실판매가로 계산한 <b>"이 스펙이면 보통 이 가격"(시세 추정)</b>과, 실제 쿠쿠몰가를 비교한 표시입니다.</p>
    <table class="mtx"><tr><th>표시</th><th>뜻</th></tr>
    <tr><td style="color:var(--ok);font-weight:700">시세 대비 20% 저렴</td><td>같은 스펙의 시세보다 20% 싸게 파는 중 — <b>좋음</b></td></tr>
    <tr><td>시세 수준</td><td>차이가 20% 안 — 시세 추정의 보통 오차(약 20%) 안이라 손해도 이득도 단정하기 어려움</td></tr>
    <tr><td style="color:var(--seal);font-weight:700">시세 대비 20% 비쌈</td><td>스펙값보다 20% 비싸게 파는 중 — <b>주의</b></td></tr></table>
    <p>판정 화면·리스트·추천에 <span style="color:var(--ok);font-weight:700">초록(저렴)</span> /
    <span style="color:var(--seal);font-weight:700">빨강(비쌈)</span> 색으로 표시됩니다.
    다만 최종 구매 판단은 이 표시가 아니라 모델별 <b>절대가격 기준선</b>(목표가/특가/적정/상한)이 우선입니다.</p></div></details>`;
}

/* ═══ v3.3: 지배 분석 · 1:1 비교 · 효율 필터 ═══ */
let DOMM=null, effOnly=false;
function dominates(a,b){          // a가 b를 지배하는가 (동일 용량·저당 그룹, 내솥 5등급=취향 규칙 적용)
  if(!eff(a)||!eff(b))return false;
  if(a.cp!==b.cp||a.ls!==b.ls)return false;
  if(b.pg===5&&a.pg<5)return false;
  const hr=r=>HEATR[heatShort(r.ht)]||0;
  const apg=(b.pg<5)?Math.min(a.pg,4):a.pg;
  const ge=hr(a)>=hr(b)&&(a.tp?1:0)>=(b.tp?1:0)&&apg>=b.pg&&(a.si?1:0)>=(b.si?1:0)&&eff(a)<=eff(b);
  const st=hr(a)>hr(b)||(a.tp?1:0)>(b.tp?1:0)||apg>b.pg||(a.si?1:0)>(b.si?1:0)||eff(a)<eff(b);
  return ge&&st;
}
function domCalc(){
  if(DOMM)return DOMM;
  DOMM=new Map();
  const alive=DB.filter(r=>r.st==="판매중"&&eff(r));
  for(const b of alive){
    const ds=alive.filter(a=>a!==b&&a.sm!==b.sm&&dominates(a,b));
    if(ds.length)DOMM.set(b.m,ds.sort((x,y)=>eff(x)-eff(y)));
  }
  return DOMM;
}
const _eff=document.getElementById("effonly");
if(_eff)_eff.addEventListener("click",()=>{effOnly=!effOnly;_eff.classList.toggle("on",effOnly);
  if(typeof shown!=="undefined")shown=PAGE;drawBrowse();});

/* ── 1:1 비교 ── */
function normM(v){let m=(v||"").toUpperCase().replace(/\s/g,"");
  if(m&&!m.includes("-")){const g=m.match(/^(CRP|CR)(.+)$/);if(g)m=g[1]+"-"+g[2];}return m;}
function drawCmp(){
  const out=document.getElementById("cmpout");if(!out)return;
  const a=DB.find(r=>r.m===normM(document.getElementById("cmpa").value));
  const b=DB.find(r=>r.m===normM(document.getElementById("cmpb").value));
  if(!a||!b){out.innerHTML=`<div class="empty"><b>두 모델을 모두 선택하세요</b>공식몰 등록 모델만 비교됩니다 — 입력하면 자동완성 목록이 뜹니다.</div>`;return;}
  if(a.m===b.m){out.innerHTML=`<div class="empty"><b>같은 모델입니다</b>서로 다른 두 모델을 넣어주세요.</div>`;return;}
  const Y="있음",N="없음";
  const rows=[
   ["가열",heatShort(a.ht),heatShort(b.ht),{"IH":2,"열판":1,"비압력":0}],
   ["트윈프레셔",a.tp?Y:N,b.tp?Y:N,{"있음":1,"없음":0}],
   ["저당취사",a.ls?Y:N,b.ls?Y:N,null],
   ["사일런스",a.si?Y:N,b.si?Y:N,{"있음":1,"없음":0}],
   ["IoT",a.io?Y:N,b.io?Y:N,null],
   ["최대 압력(실측)",a.aw?a.aw+"기압":"—",b.aw?b.aw+"기압":"—",null],
   ["소비전력(실측)",a.pw?a.pw.toLocaleString("ko-KR")+"W":"—",b.pw?b.pw.toLocaleString("ko-KR")+"W":"—",null],
   ["에너지효율(실측)",a.eg?a.eg+"등급":"—",b.eg?b.eg+"등급":"—",null],
   ["내솥 (취향)",`${esc(a.pc)} · ${a.pg}/5`,`${esc(b.pc)} · ${b.pg}/5`,null],
   ["용량",a.cp+"인",b.cp+"인",null],
   ["출시",a.rg?"20"+a.rg:"—",b.rg?"20"+b.rg:"—",null],
   ["상태",a.st,b.st,null],
   ["색상",esc(a.cl),esc(b.cl),null],
   ["쿠쿠몰가",W(eff(a)),W(eff(b)),null],
   ["특가 인정선",a.px[1]?W(a.px[1]):"—",b.px[1]?W(b.px[1]):"—",null],
   ["시세 대비",vfmText(a)?vfmText(a).t:"—",vfmText(b)?vfmText(b).t:"—",null],
   ["인기(월 리뷰)",rvFmt(a),rvFmt(b),null]];
  let h=`<table class="cmpt"><tr><th></th><th>${a.m}</th><th>${b.m}</th></tr>`;
  for(const rr of rows){
    const same=rr[1]===rr[2];
    let wa="",wb="";
    if(rr[3]&&!same){const s=rr[3];if((s[rr[1]]||0)>(s[rr[2]]||0))wa="win";else if((s[rr[2]]||0)>(s[rr[1]]||0))wb="win";}
    h+=`<tr class="${same?"":"diff"}"><th>${rr[0]}</th><td class="${wa}">${rr[1]}</td><td class="${wb}">${rr[2]}</td></tr>`;
  }
  h+=`</table>`;
  let concl="";
  const effA=eff(a),effB=eff(b);
  if(a.sm===b.sm){
    concl=effA===effB?"색상만 다른 같은 제품이고 가격도 같습니다 — 마음에 드는 색을 고르면 됩니다."
      :`색상만 다른 <b>같은 제품</b>입니다. 색상 취향이 아주 강하지 않다면 <b>싼 쪽(${effA<effB?a.m:b.m})</b>이 정답 —
        차액 ${W(Math.abs(effA-effB))}은 순수하게 색값입니다.`;
  }else if(dominates(a,b))concl=`<b>${a.m}가 ${b.m}를 지배합니다</b> — 스펙이 같거나 우위인데 가격도 같거나 쌉니다. 특별한 이유가 없다면 ${a.m} 쪽이 낫습니다.`;
  else if(dominates(b,a))concl=`<b>${b.m}가 ${a.m}를 지배합니다</b> — 스펙이 같거나 우위인데 가격도 같거나 쌉니다. 특별한 이유가 없다면 ${b.m} 쪽이 낫습니다.`;
  else if(effA&&effB&&mvOf(a)&&mvOf(b)){
    const hiM=effA>=effB?a:b, loM=effA>=effB?b:a;
    const gap=eff(hiM)-eff(loM), just=mvOf(hiM)-mvOf(loM), bub=gap-just;
    concl=`<b>${hiM.m}</b>가 ${W(gap)} 더 비쌉니다. 두 모델의 스펙·연식 차이가 갖는 시장가치는 <b>${W(Math.max(just,0))}</b>`;
    if(just<=0)concl+=` — 스펙 가치로는 오히려 ${loM.m} 쪽이 같거나 높습니다. 가격차 전액이 색상·유통·거품입니다. <b>${loM.m} 추천.</b>`;
    else if(bub>10000)concl+=` — 나머지 <b>${W(bub)}는 스펙으로 정당화되지 않는 차이</b>(색상·유통·거품)입니다. 그 차액이 아깝다면 ${loM.m}.`;
    else if(bub<-10000)concl+=` — 가격차가 스펙 가치보다 ${W(-bub)} 작습니다. <b>${hiM.m}가 실속</b>(좋은 스펙을 상대적으로 싸게 사는 셈)입니다.`;
    else concl+=` — 가격차가 스펙 가치와 거의 일치합니다. 예산과 취향으로 고르면 됩니다.`;
  }else concl="가격 정보가 없는 모델이 있어 가격차 해부는 생략합니다.";
  h+=`<div class="best" style="margin-top:12px">${concl}
    <span class="bnote">스펙 가치는 실판매가 회귀 가중치 기준 추정이며, 내솥(취향)·IoT·색상은 가치 계산에서 우위로 치지 않습니다.</span></div>`;
  out.innerHTML=h;
}
const _cmpBtn=document.getElementById("cmpgo");
if(_cmpBtn){
  document.getElementById("mlist").innerHTML=DB.map(r=>`<option value="${r.m}">`).join("");
  _cmpBtn.addEventListener("click",drawCmp);
  document.getElementById("cmpb").addEventListener("keydown",e=>{if(e.key==="Enter")drawCmp();});
}

/* ═══ 테마 (라이트/다크 — 시스템 감지 + 토글, localStorage 기억) ═══ */
const _tt=document.getElementById("themetog");
function applyTheme(t){document.documentElement.dataset.theme=t;
  if(_tt)_tt.textContent=t==="dark"?"☀️":"🌙";
  const mc=document.querySelector('meta[name="theme-color"]');
  if(mc)mc.content=t==="dark"?"#0E1114":"#0C2823";}
let _th="";try{_th=localStorage.getItem("cuckoo_theme")||""}catch(e){}
if(!_th)_th=(window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches)?"dark":"light";
applyTheme(_th);
if(_tt)_tt.addEventListener("click",()=>{_th=_th==="dark"?"light":"dark";
  try{localStorage.setItem("cuckoo_theme",_th)}catch(e){}applyTheme(_th);});

/* 웹 서빙일 때만: PC 링크(?pc = 자동이동 우회) + 방문자 집계(GoatCounter) + 드래그하면 보이는 숨김 카운터 */
if(location.protocol==="http:"||location.protocol==="https:"){
  const _pl=document.getElementById("pclink");
  if(_pl)_pl.innerHTML='<br><a href="../?pc" style="color:inherit;font-weight:700">🖥️ PC 버전 보기</a>';
  const _gc=document.createElement("script");
  _gc.setAttribute("data-goatcounter","https://unfade.goatcounter.com/count");
  _gc.async=true;_gc.src="https://gc.zgo.at/count.js";
  document.head.appendChild(_gc);
  (async()=>{
    const el=document.getElementById("hitbox");if(!el)return;
    const cnt=async(p,qs)=>{try{
      const r=await fetch("https://unfade.goatcounter.com/counter/"+p+".json"+(qs||""));
      if(!r.ok)return "-";
      return String((await r.json()).count||"-").replace(/[\s  ]/g,",");
    }catch(e){return "-"}};
    const d=new Date();
    const today=d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
    const [tot,tod,pg]=await Promise.all([
      cnt("TOTAL"), cnt("TOTAL","?start="+today), cnt(location.pathname)]);
    el.textContent="UNFADE STATS · TODAY(전체) "+tod+" · 이 페이지 누적 "+pg+" · 사이트 전체 누적 "+tot;
  })();
}

drawBrowse();
drawRecent();
drawWeights();
drawDict();
drawBuilder();
drawReco();
drawFaq();
(function(){const el=document.getElementById("stale");if(!el)return;const d0=new Date("__ASOF__T00:00:00"),n=new Date(),t0=new Date(n.getFullYear(),n.getMonth(),n.getDate()),days=Math.max(0,Math.round((t0-d0)/864e5));
  el.innerHTML=`가격 기준일 <b>__ASOF__</b>${days?` · <b>${days}일 지났습니다</b> — 쿠쿠몰 가격이 바뀌었을 수 있으니 오늘 본 가격을 함께 넣어 판정하세요`:""}`;})();
render("CRP-DHP0610FD","",true);
</script>
</body>
</html>"""

open('cuckoo-decoder-mobile.html', 'w', encoding='utf-8').write(
    HTML.replace("__DB__", json.dumps(slim, ensure_ascii=False, separators=(',', ':')))
        .replace("__WX__", json.dumps(WX, ensure_ascii=False, separators=(',', ':')))
        .replace("__NMODELS__", str(len(slim))).replace("__ASOF__", ASOF)
)
print("생성 완료:", len(slim), "모델")
