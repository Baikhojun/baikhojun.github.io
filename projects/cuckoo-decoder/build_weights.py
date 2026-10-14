# -*- coding: utf-8 -*-
"""cuckoo-weights.json 생성 v2 — 212개 실판매가 기반 항목별 가중치(헤도닉 회귀) 산출.
선행: python build_v3.py (cuckoo-products.json 필요)
v2 변경: ① 플래그십(LH·BDH·BCH) 더미 추가 — IH 계수에서 브랜드 프리미엄 분리
        ② 로그 가격 회귀 병행 — %프리미엄 산출
        ③ 부트스트랩(500회) 95% 신뢰구간 — 소표본 계수(IoT 등)의 불확실성 정직 표기
산출물은 build_html_v3.py / build_html_mobile.py 가 __WX__ 로 임베드한다."""
import json, math, random, statistics

DB = json.load(open('cuckoo-products.json', encoding='utf-8'))
eff = lambda r: r["sale_price"] or r["list_price"]
heat3 = lambda h: "IH" if h.startswith("IH") else ("비압력" if "비압력" in h else "열판")
FLAG = ("LH", "BDH", "BCH")   # 플래그십 라인 (마스터셰프·타철명장)

rows = [r for r in DB if eff(r) and heat3(r["heating"]) != "비압력"]

def feats(r):
    cp = r["capacity"] or 6
    return [
        1.0,
        1.0 if heat3(r["heating"]) == "IH" else 0.0,   # ih
        1.0 if r["twin_pressure"] else 0.0,            # twin
        1.0 if r["low_sugar"] else 0.0,                # low
        1.0 if r["silence"] else 0.0,                  # silence
        1.0 if r["iot"] else 0.0,                      # iot
        1.0 if r["pot_grade"] == 5 else 0.0,           # 올스테인리스
        1.0 if r["pot_grade"] in (3, 4) else 0.0,      # 투톤/에코스텐
        1.0 if r["pot_grade"] == 2 else 0.0,           # 스텐외피 코팅
        1.0 if cp <= 3 else 0.0,                       # 소용량
        1.0 if cp >= 8 else 0.0,                       # 대인용
        1.0 if r["design_code"] in FLAG else 0.0,      # 플래그십
        1.0 if r["old_gen"] else 0.0,                  # 구형
        (r["age_months"] or 0) / 12.0,                 # 연차
    ]

NAMES = ["base","ih","twin","low","silence","iot","pot5","pot34","pot2","capS","capL","flag","old","age"]
k = len(NAMES)

def ols(X, Y):
    A = [[sum(X[i][a]*X[i][b] for i in range(len(X))) for b in range(k)] for a in range(k)]
    B = [sum(X[i][a]*Y[i] for i in range(len(X))) for a in range(k)]
    M = [A[i][:] + [B[i]] for i in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda r_: abs(M[r_][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-9: continue
        for r_ in range(k):
            if r_ != c and M[r_][c]:
                f = M[r_][c] / M[c][c]
                for j in range(c, k+1): M[r_][j] -= f * M[c][j]
    return [M[i][k] / M[i][i] if abs(M[i][i]) > 1e-9 else 0.0 for i in range(k)]

def r2of(X, Y, coef):
    pred = [sum(c*x for c, x in zip(coef, X[i])) for i in range(len(X))]
    ybar = sum(Y)/len(Y)
    ssr = sum((Y[i]-pred[i])**2 for i in range(len(Y)))
    sst = sum((y-ybar)**2 for y in Y)
    return 1 - ssr/sst

X  = [feats(r) for r in rows]
Y  = [float(eff(r)) for r in rows]
Yl = [math.log(float(eff(r))) for r in rows]

coef  = ols(X, Y)
coefl = ols(X, Yl)
r2, r2l = r2of(X, Y, coef), r2of(X, Yl, coefl)

# ── 부트스트랩 95% CI (선형, 원 단위) ──
random.seed(20260825)
B = 500
boots = {n: [] for n in NAMES}
idx = list(range(len(X)))
for _ in range(B):
    s = [random.choice(idx) for _ in idx]
    cb = ols([X[i] for i in s], [Y[i] for i in s])
    for j, n in enumerate(NAMES): boots[n].append(cb[j])
def pctile(v, p):
    v = sorted(v); i = (len(v)-1)*p
    lo = int(i); return v[lo] + (v[min(lo+1, len(v)-1)]-v[lo])*(i-lo)
CI = {n: [round(pctile(boots[n], .025)/1000)*1000, round(pctile(boots[n], .975)/1000)*1000] for n in NAMES}

W  = {NAMES[i]: round(coef[i]/1000)*1000 for i in range(k)}
W["age"] = round(coef[NAMES.index("age")]/100)*100
WP = {NAMES[i]: round((math.exp(coefl[i])-1)*100) for i in range(k) if NAMES[i] != "base"}

CNT = {NAMES[j]: sum(1 for i in range(len(X)) if X[i][j] >= 1) for j in range(1, k-1)}
CNT["age"] = len(rows)

# ══ 감가 곡선 (v3.4): 연령구간 더미 헤도닉 — 계단 가정을 데이터로 교체 ══
# 방법: 로그가격 ~ 스펙(기존) + 연령구간 더미(0-2y 기준). exp(계수)=잔존율.
#       부트스트랩 300회 CI + PAV 단조화(나이 들수록 잔존율 비증가) + 1.0 상한 클립.
# 대조: 지수 감가(로그모델 연속 age 계수) 병기.
AGE_BINS = [(24, "0-2y"), (48, "2-4y"), (72, "4-6y"), (96, "6-8y"), (10**9, "8y+")]

def age_bin_idx(months):
    m = months or 0
    for i, (ub, _) in enumerate(AGE_BINS):
        if m <= ub: return i
    return len(AGE_BINS) - 1

def feats_dep(r):
    f = feats(r)[:-1]                      # 연속 age 제외
    b = age_bin_idx(r["age_months"])
    return f + [1.0 if b == i else 0.0 for i in range(1, len(AGE_BINS))]  # 0-2y = base

NAMES_DEP = NAMES[:-1] + [lb for _, lb in AGE_BINS[1:]]
kd = len(NAMES_DEP)

def ols_g(X_, Y_, kk):
    A = [[sum(X_[i][a]*X_[i][b] for i in range(len(X_))) for b in range(kk)] for a in range(kk)]
    B = [sum(X_[i][a]*Y_[i] for i in range(len(X_))) for a in range(kk)]
    M = [A[i][:] + [B[i]] for i in range(kk)]
    for c in range(kk):
        p = max(range(c, kk), key=lambda r_: abs(M[r_][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-9: continue
        for r_ in range(kk):
            if r_ != c and M[r_][c]:
                f = M[r_][c] / M[c][c]
                for j in range(c, kk+1): M[r_][j] -= f * M[c][j]
    return [M[i][kk] / M[i][i] if abs(M[i][i]) > 1e-9 else 0.0 for i in range(kk)]

Xd = [feats_dep(r) for r in rows]
cd_ = ols_g(Xd, Yl, kd)

def pav_dec(v):
    """비증가 단조화 (pooled adjacent violators)"""
    out = []
    for x in v:
        out.append([x, 1.0])
        while len(out) >= 2 and out[-2][0] < out[-1][0]:
            a, b = out.pop(), out.pop()
            out.append([(a[0]*a[1]+b[0]*b[1])/(a[1]+b[1]), a[1]+b[1]])
    res = []
    for val, wt in out: res += [val]*int(wt)
    return res

random.seed(20260826)
bootd = {lb: [] for _, lb in AGE_BINS[1:]}
for _ in range(300):
    s = [random.choice(idx) for _ in idx]
    cb = ols_g([Xd[i] for i in s], [Yl[i] for i in s], kd)
    for j, lb in enumerate([lb for _, lb in AGE_BINS[1:]]):
        bootd[lb].append(cb[len(NAMES)-1+j])

raw_f = [1.0] + [math.exp(cd_[len(NAMES)-1+j]) for j in range(len(AGE_BINS)-1)]
mono_f = [min(1.0, round(x, 3)) for x in pav_dec(raw_f)]
# 결합 규칙: 표본이 얇은 노후 구간에서 경험값이 기존 보수 가정보다 관대하면 보수 가정을 유지
#           final = 단조화( min(경험 단조값, 기존 가정) ), 기존 가정 = 1.0/0.97/0.92/0.85/0.70
PRIOR_F = [1.0, 0.97, 0.92, 0.85, 0.70]
use_f = [round(x, 3) for x in pav_dec([min(m, p) for m, p in zip(mono_f, PRIOR_F)])]
old_emp = round(math.exp(coefl[NAMES.index("old")]), 3)
DEP = {"bins": [], "old": min(old_emp, 0.85), "old_emp": old_emp,
       "exp_year": round(math.exp(coefl[NAMES.index("age")]), 4),
       "note": "연령구간 헤도닉(로그)→PAV 단조화→min(경험,보수가정) 재단조. old=구형 라인 추가 잔존율(경험·가정 중 낮은 쪽), exp_year=지수모델 연간 잔존율"}
for i, (ub, lb) in enumerate(AGE_BINS):
    ent = {"ub": ub if ub < 10**9 else None, "label": lb, "f": use_f[i],
           "emp": mono_f[i], "raw": round(raw_f[i], 3), "prior": PRIOR_F[i]}
    if i > 0:
        ci_lo = math.exp(pctile(bootd[lb], .025)); ci_hi = math.exp(pctile(bootd[lb], .975))
        ent["ci"] = [round(ci_lo, 2), round(ci_hi, 2)]
    DEP["bins"].append(ent)

# ══ 라인 리프레시 주기 (v3.4): 후속작 리스크 ══
# 라인(dcx)별 고유 등록월(웨이브) 간격의 중앙값·IQR → 다음 웨이브 추정
def ym_num(reg):
    y, m = reg.split("."); return (2000+int(y))*12 + int(m)
def num_ym(n):
    return f"{n//12-2000:02d}.{(n%12) or 12:02d}" if (n % 12) else f"{n//12-2001:02d}.12"

# 웨이브 = 스템(색상형제 그룹)의 최초 등록월 — 색상 추가로 인한 잡음 제거
stem_first = {}
for r in DB:
    if r.get("design_code") and r.get("reg"):
        sm = r["stem"]
        if sm not in stem_first or ym_num(r["reg"]) < ym_num(stem_first[sm][1]):
            stem_first[sm] = (r["design_code"], r["reg"])
line_regs = {}
for dcx, reg in stem_first.values():
    line_regs.setdefault(dcx, set()).add(reg)
LINES = {}
for dcx, regs in line_regs.items():
    ns = sorted(ym_num(x) for x in regs)
    gaps = [b-a for a, b in zip(ns, ns[1:]) if b-a > 0]
    ent = {"waves": len(ns), "last": num_ym(ns[-1])}
    if len(gaps) >= 2:
        gs = sorted(gaps)
        med = gs[len(gs)//2] if len(gs) % 2 else (gs[len(gs)//2-1]+gs[len(gs)//2])/2
        q1 = gs[max(0, int(len(gs)*0.25))]; q3 = gs[min(len(gs)-1, int(len(gs)*0.75))]
        ent.update({"med": round(med), "q1": q1, "q3": q3,
                    "next": num_ym(int(ns[-1]+med)),
                    "next_lo": num_ym(ns[-1]+q1), "next_hi": num_ym(ns[-1]+q3)})
    LINES[dcx] = ent

# ── 용량별 실측 중앙값 (IH 압력) ──
capmed = {}
for r in rows:
    if heat3(r["heating"]) != "IH": continue
    cp = r["capacity"]
    if cp: capmed.setdefault(cp, []).append(eff(r))
CAPS = {str(cp): {"n": len(v), "med": round(statistics.median(v)/1000)*1000}
        for cp, v in sorted(capmed.items())}

# ── 색상 프리미엄 ──
stems = {}
for r in DB:
    if eff(r): stems.setdefault(r["stem"], []).append(r)
cprem = {}
for sm, grp in stems.items():
    if len(grp) < 2: continue
    lo = min(eff(r) for r in grp)
    for r in grp:
        cprem.setdefault(r["color"], []).append(eff(r) - lo)
COLORP = {c: {"n": len(v), "avg": round(sum(v)/len(v)/100)*100}
          for c, v in cprem.items() if len(v) >= 2}
COLORP = dict(sorted(COLORP.items(), key=lambda x: -x[1]["avg"]))

OUT = {"n": len(rows), "r2": round(r2, 3), "r2log": round(r2l, 3),
       "w": W, "wp": WP, "ci": CI, "cnt": CNT, "cap": CAPS, "colorp": COLORP,
       "dep": DEP, "lines": LINES,
       "note": "2026-08-25 쿠쿠몰 실판매가 헤도닉 회귀 v2(비압력 제외, 플래그십 분리, 부트스트랩 500회). "
               "base=열판·4~6인·기본코팅·일반 라인·부가기능 없음·신형·연차0"}
json.dump(OUT, open('cuckoo-weights.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print("표본", len(rows), "R²(선형)", round(r2, 3), "R²(로그)", round(r2l, 3))
for n in NAMES:
    ci = CI[n]
    print(f"  {n:8s} {W[n]:>10,}  CI[{ci[0]:>9,} ~ {ci[1]:>9,}]  로그 {WP.get(n,0):>4}%")
print("용량 중앙값:", {c: v['med'] for c, v in CAPS.items()})
print("감가 곡선:", [(e["label"], e["f"], e.get("ci")) for e in DEP["bins"]],
      "old", DEP["old"], "지수/년", DEP["exp_year"])
print("라인 주기(예측 가능):", {k: f"{v['med']}개월→{v['next']}" for k, v in LINES.items() if "next" in v})
