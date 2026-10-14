# -*- coding: utf-8 -*-
"""
쿠쿠 밥솥 마스터 데이터 v3 빌드
입력: cuckoo-source-v3.json  (공식몰 크롤링 2026-08-25 + 다나와 등록월)
출력: cuckoo-products.json / cuckoo-products.csv / (별도 스크립트) cuckoo-decoder.html

v3 신규:
- reg(다나와 등록월) 기반 연식 감가
- 절대가격 기준선: ceil(절대상한) / fair(적정) / spc(특가) / epic(역대급)
- IoT 모듈 코드 'T' (표시창 앞) 해독
- NL/FF = 병행 변형 코드로 정정 (등록월 2025.04~2026.08, 거의 동시)
"""
import json, csv, re, glob, os
from collections import Counter

BASE_YM = (2026, 8)  # 수집 시점

# ── v3.4: 경험 감가 곡선 (build_weights.py 산출) — 없으면 기존 계단식 가정 사용 ──
DEP_BINS, DEP_OLD = None, 0.85
if os.path.exists("cuckoo-weights.json"):
    try:
        _wx = json.load(open("cuckoo-weights.json", encoding="utf-8"))
        if "dep" in _wx:
            DEP_BINS = [((b["ub"] or 10**9), b["f"]) for b in _wx["dep"]["bins"]]
            DEP_OLD = _wx["dep"]["old"]
            print("경험 감가 곡선 사용:", [(u if u < 10**9 else "inf", f) for u, f in DEP_BINS], "old", DEP_OLD)
    except Exception as e:
        print("가중치 파일 읽기 실패 — 기본 감가 사용:", e)

# ── v3.4: 상세 스펙 (쿠쿠몰 텍스트 40개 + 다나와 스템 보완) ──
DET = json.load(open("cuckoo-detail.json", encoding="utf-8")) if os.path.exists("cuckoo-detail.json") else {}
DNW = json.load(open("cuckoo-danawa-spec.json", encoding="utf-8")) if os.path.exists("cuckoo-danawa-spec.json") else {}

# ── v3.4: 가격 스냅샷 이력 ──
SNAPS = []
for _p in sorted(glob.glob("snapshots/price-*.json")):
    try:
        _s = json.load(open(_p, encoding="utf-8"))
        # 키 정규화: 몰 productCd 의 괄호 서픽스 '(C)' 등 제거 → 소스 모델명과 매칭
        SNAPS.append((_s["date"], {re.sub(r"\(.*?\)$", "", k.upper()): v for k, v in _s["prices"].items()}))
    except Exception:
        pass
if SNAPS:
    print("가격 스냅샷:", [d for d, _ in SNAPS])

DESIGN_IH = {
    "AH": "A형(구형)", "BH": "B형(구형)", "CH": "C형(10인용 주력)",
    "DH": "D형(6인용 주력)", "EH": "E형(3인용 전용)", "FH": "F형(중상급)",
    "JH": "J형(중급)", "KH": "K형(트윈프레셔)", "LH": "L형(마스터셰프)",
    "MH": "M형(쁘띠/소용량)", "NH": "N형(사일런스)", "OH": "O형(사일런스 오브제)",
    "PH": "P형(사일런스 프로)", "QH": "Q형(사일런스 큐브)",
    "BDH": "BD형(타철명장)", "BCH": "BC형(타철명장)",
}
DESIGN_IH_OLD = {
    "HQ": "HQ형(구형)", "HU": "HU형(구형)", "HV": "HV형(구형)",
    "HW": "HW형(구형)", "HM": "HM형(구형)",
}
SILENCE_LINES = {"NH", "OH", "PH", "QH"}
OLD_LINES = {"AH", "BH", "HQ", "HU", "HV", "HW", "HM"}
GROUP_PLATE = {
    "ST": (True,  "더 라이트 (열판 트윈프레셔)"),
    "UT": (True,  "사일런스 어반 (열판 트윈프레셔)"),
    "TT": (True,  "트윈프레셔 미니 (3인용)"),
    "RT": (True,  "열판 트윈프레셔"),
    "QK": (False, "Q형 열판압력"),
    "PK": (False, "P형 열판압력"),
    "RK": (False, "R형 열판압력"),
    "PW": (False, "P형 열판압력(변형)"),
    "P":  (False, "P형 열판압력"),
    "R":  (False, "R형 열판압력"),
    "T":  (False, "미니 열판압력 (3인용)"),
}
POT = [
    ("AS", "올스테인리스 무코팅(와이드앤플랫)", 5),
    ("AR", "올스테인리스 무코팅(라운드/커브드)", 5),
    ("XB", "일반 코팅(다이아 계열)", 1),
    ("R",  "투톤코팅 + 라운드(커브드)", 4),
    ("S",  "하단 투톤코팅(에코스텐)", 3),
    ("P",  "스테인리스 외피 코팅내솥", 2),
    ("B",  "일반 코팅(다이아쉴드/블랙)", 1),
    ("F",  "타철명장/플랫 계열(구형)", 1),
]
VARIANT = {"NL": "병행 변형(선행 리비전·할인 유통)", "FF": "병행 변형(후행 리비전·2026)"}
DISPLAY = {"F": "LCD(퍼지) 디스플레이", "S": "일반 숫자/램프 표시",
           "B": "버튼식/일반 표시", "M": "구형 소형 표시(추정)", "G": "미확정"}
COLOR = {
    "W": "화이트", "S": "실버", "B": "블랙", "D": "다크실버/다크그레이",
    "G": "그레이", "P": "핑크", "T": "테라코타", "R": "로즈/레드",
    "C": "캐비어블루", "I": "아이보리", "V": "바이올렛",
    "GW": "그레이스화이트", "GB": "그레이스블랙", "GI": "그레이스아이보리",
    "GG": "어반그레이", "MG": "메탈릭그린", "LB": "루미블랙/루미다크실버",
    "GPS": "그레이스핑크실버", "WS": "화이트스톤", "BS": "블랙실버",
    "BB": "블랙브라운", "WG": "화이트그레이", "GS": "그레이실버",
    "LS": "루미실버", "PS": "핑크실버", "PP": "핑크", "WM": "화이트무광(추정)",
    "BE": "베이지(추정)", "BD": "블랙다크(추정)", "DB": "다크블랙(추정)",
    "BGI": "블랙그레이아이보리(추정)", "SDB": "실버다크블랙(추정)",
    "BUG": "미확정", "EL": "미확정", "E": "미확정", "UG": "미확정", "FR": "미확정",
    "GSM": "미확정",
}
CAPACITY = {"01": 1, "02": 2, "03": 3, "04": 4, "06": 6, "08": 8, "10": 10, "35": 35}


def decode(model):
    r = {"model": model, "flags": [], "confidence": "high", "iot": False, "old_gen": False}
    m = model.replace(" ", "").upper()
    m = re.sub(r"\(.*?\)$", "", m)

    if m.startswith("CRP-"):
        r["pressure"] = "압력식"; core = m[4:]
    elif m.startswith("CR-"):
        r["pressure"] = "비압력(보온)"; core = m[3:]
    else:
        r["flags"].append("접두사 인식 실패"); r["confidence"] = "fail"; return r

    mnum = re.search(r"\d", core)
    if not mnum:
        r["flags"].append("숫자 블록 없음"); r["confidence"] = "fail"; return r
    letters, rest = core[:mnum.start()], core[mnum.start():]

    r["design_code"] = ""
    if r["pressure"].startswith("비압력"):
        r["design"] = "-"; r["heating"] = "비압력(열판 보온)"
        r["twin_pressure"] = False; r["low_sugar"] = False
        r["pot_code"] = "-"; r["pot"] = "논스틱 코팅(일반)"; r["pot_grade"] = 0
        r["variant"] = ""; r["silence"] = False
    else:
        design = heat = None
        if letters[:3] in DESIGN_IH:
            r["design_code"] = letters[:3]
            design, heat, letters = DESIGN_IH[letters[:3]], "IH", letters[3:]
        elif letters[:2] in DESIGN_IH:
            r["design_code"] = letters[:2]
            design, heat, letters = DESIGN_IH[letters[:2]], "IH", letters[2:]
        elif letters[:2] in DESIGN_IH_OLD:
            r["design_code"] = letters[:2]
            design, heat, letters = DESIGN_IH_OLD[letters[:2]], "IH", letters[2:]
            r["flags"].append("구형 명명체계(H가 앞)")
        else:
            for g in sorted(GROUP_PLATE, key=len, reverse=True):
                if letters.startswith(g):
                    tw, desc = GROUP_PLATE[g]
                    r["design_code"] = g
                    design, heat, letters = desc, "열판", letters[len(g):]
                    r["_plate_twin"] = tw
                    break
        if design is None:
            r["flags"].append(f"디자인 코드 미등록: {letters}")
            r["confidence"] = "low"; design, heat = f"미상({letters})", "미상"
            letters = ""
        r["design"], r["heating"] = design, heat
        r["silence"] = r["design_code"] in SILENCE_LINES
        r["old_gen"] = r["design_code"] in OLD_LINES

        var = ""
        for v in VARIANT:
            if v in letters:
                var = v; letters = letters.replace(v, "", 1)
        r["variant"] = var

        tw = r.pop("_plate_twin", False)
        ls = False
        if letters.startswith("T"):
            tw = True; letters = letters[1:]
        elif letters.startswith("L"):
            ls = True; tw = True; letters = letters[1:]
        r["twin_pressure"], r["low_sugar"] = tw, ls

        pot = None
        for code, name, grade in POT:
            if letters.startswith(code):
                pot = (code, name, grade); letters = letters[len(code):]
                break
        if pot:
            r["pot_code"], r["pot"], r["pot_grade"] = pot
        else:
            r["pot_code"], r["pot"], r["pot_grade"] = "-", "미표기(기본 코팅)", 0
        if letters:
            r["flags"].append(f"미해독 문자: {letters}"); r["confidence"] = "low"

    mnum2 = re.match(r"(\d+)", rest)
    digits, tail = mnum2.group(1), rest[mnum2.end():]
    cap = digits[:2]
    r["capacity"] = CAPACITY.get(cap, None)
    if r["capacity"] is None:
        r["flags"].append(f"용량 코드 미상: {cap}"); r["confidence"] = "low"
    r["dist_code"] = digits[2:]

    # IoT 모듈 코드: 표시창 앞의 T (예: NHTRNL0610TFGW)
    if len(tail) > 2 and tail[0] == "T" and tail[1] in DISPLAY and tail[2:] in COLOR:
        r["iot"] = True; tail = tail[1:]

    suffix = ""
    if len(tail) > 2 and tail.endswith("M") and tail[:-1] not in COLOR:
        suffix, tail = "M", tail[:-1]
    r["suffix"] = suffix
    if tail and len(tail) > 1 and tail[0] in DISPLAY and tail[1:] in COLOR:
        r["display_code"] = tail[0]; r["display"] = DISPLAY[tail[0]]
        r["color_code"] = tail[1:]; r["color"] = COLOR[tail[1:]]
    elif tail and tail in COLOR:
        r["display_code"] = "-"; r["display"] = "표시창 코드 생략"
        r["color_code"] = tail; r["color"] = COLOR[tail]
        r["flags"].append("표시창 코드 생략형")
    elif tail:
        r["display_code"] = tail[0]
        r["display"] = DISPLAY.get(tail[0], "미상")
        ccode = tail[1:]
        r["color_code"] = ccode
        r["color"] = COLOR.get(ccode, "미등록")
        if ccode and ccode not in COLOR:
            r["flags"].append(f"색상 코드 미등록: {ccode}")
    else:
        r["display_code"] = r["display"] = r["color_code"] = r["color"] = "-"
    if r["flags"] and r["confidence"] == "high":
        r["confidence"] = "medium"
    return r


def ym_to_months(reg):
    """'19.08' -> 수집시점까지 경과 개월"""
    if not reg:
        return None
    try:
        y, m = reg.split(".")
        y, m = 2000 + int(y), int(m)
        return (BASE_YM[0] - y) * 12 + (BASE_YM[1] - m)
    except Exception:
        return None


def age_factor(months, old_gen):
    if DEP_BINS:                       # v3.4: 경험 곡선 (헤도닉 연령구간 + 보수 가정 결합)
        f = 1.0
        if months is not None:
            for ub, ff in DEP_BINS:
                if months <= ub:
                    f = ff; break
        if old_gen:
            f *= DEP_OLD
        return f
    if months is None:
        f = 1.0
    elif months <= 24:
        f = 1.0
    elif months <= 48:
        f = 0.97
    elif months <= 72:
        f = 0.92
    elif months <= 96:
        f = 0.85
    else:
        f = 0.70
    if old_gen:
        f *= 0.85
    return f


HEAT_RANK = {"IH": 2, "열판": 1, "비압력(열판 보온)": 0, "미상": 0}


def build():
    src = json.load(open("cuckoo-source-v3.json", encoding="utf-8"))
    rows = []
    for s in src:
        d = decode(s["model"])
        d.update({
            "name": s["name"], "list_price": s["lp"], "sale_price": s["sp"],
            "review_count": s["rc"], "official_features": [x.strip() for x in re.split(r"[∙ㆍ·]", s["desc"]) if x.strip()],
            "categories": s["cats"], "status": s["status"],
            "reg": s["reg"], "reg_est": s.get("reg_est", False), "is_new": s.get("new", False),
        })
        # 공식 상품명 괄호 안에 색상명이 있으면 코드 사전보다 우선한다(예: FB = 로즈브라운, FG = 메탈릭 그린).
        mc = re.search(r"[,(]\s*([^,()]*?(?:브라운|그린|블루|레드|골드|베이지|네이비|민트|퍼플))\s*\)", s["name"])
        if mc and mc.group(1).strip() != d.get("color"):
            d["color"] = mc.group(1).strip()
        d["discount_rate"] = round((1 - s["sp"] / s["lp"]) * 100) if (s["lp"] and s["sp"]) else None
        d["age_months"] = ym_to_months(s["reg"])
        # 색상형제 스템: 문자+숫자 블록까지 (표시창/색상/서픽스 제외)
        mm = re.sub(r"\(.*?\)$", "", s["model"])
        mo = re.match(r"(CRP?-?[A-Z]*\d+)", mm)
        d["stem"] = mo.group(1) if mo else mm

        # v3.4: 상세 스펙 병합 (쿠쿠몰 텍스트 우선, 없으면 다나와 스템 스펙)
        det = DET.get(s["model"].upper(), {})
        dnw = DNW.get(d["stem"], {}) or {}
        d["power_w"] = det.get("power_w") or dnw.get("power_w")
        d["energy_grade"] = det.get("energy_grade") if det.get("energy_grade") else dnw.get("energy_grade")
        d["atm"] = dnw.get("atm")
        d["weight_kg"] = det.get("weight_kg")
        d["size"] = det.get("size") or dnw.get("size_mm")

        # v3.4: 가격 관측 이력 (스냅샷 누적)
        h = []
        for _date, _prices in SNAPS:
            e = _prices.get(re.sub(r"\(.*?\)$", "", s["model"].upper()))
            if e:
                ep = e.get("sp") or e.get("lp")
                if ep:
                    h.append([_date, ep])
        d["hist"] = h
        d["hist_min"] = min((x[1] for x in h), default=None)
        rows.append(d)

    # ── 절대가격 기준선 ──
    def eff_price(r):
        return r["sale_price"] or r["list_price"]

    for r in rows:
        own = eff_price(r)
        sib = [eff_price(x) for x in rows if x["stem"] == r["stem"] and eff_price(x)]
        sib_min = min(sib) if sib else None
        grp = [eff_price(x) for x in rows
               if x is not r and eff_price(x) and x["status"] == "판매중"
               and x["heating"] == r["heating"] and x["twin_pressure"] == r["twin_pressure"]
               and x["low_sugar"] == r["low_sugar"] and x["pot_grade"] == r["pot_grade"]
               and x["silence"] == r["silence"] and x["capacity"] == r["capacity"]]
        grp_min = min(grp) if grp else None
        # 지배 규칙: 같은 용량·저당에서 전 항목 이상 + 1개 이상 우위인 모델의 최저가
        better = []
        hr = HEAT_RANK.get(r["heating"], 0)
        for x in rows:
            if x is r or not eff_price(x) or x["status"] != "판매중":
                continue
            if x["capacity"] != r["capacity"] or x["low_sugar"] != r["low_sugar"]:
                continue
            xr = HEAT_RANK.get(x["heating"], 0)
            # 올스텐(5등급)은 코팅 내솥의 상위호환이 아니라 취향 선택 → 지배 비교에서 5등급은 동급으로만
            xpg = min(x["pot_grade"], 4) if r["pot_grade"] < 5 else x["pot_grade"]
            rpg = r["pot_grade"]
            if rpg == 5 and x["pot_grade"] < 5:
                continue  # 올스텐을 원하는 사람에게 코팅은 대체재가 아님
            ge = (xr >= hr and x["twin_pressure"] >= r["twin_pressure"]
                  and xpg >= rpg and x["silence"] >= r["silence"])
            strict = (xr > hr or x["twin_pressure"] > r["twin_pressure"]
                      or xpg > rpg or x["silence"] > r["silence"])
            if ge and strict:
                better.append(eff_price(x))
        better_min = min(better) if better else None

        cands = [c for c in [own, sib_min,
                             int(grp_min * 1.05) if grp_min else None,
                             int(better_min * 0.97) if better_min else None] if c]
        anchor = min(cands) if cands else None
        if anchor:
            f = age_factor(r["age_months"], r["old_gen"])
            ceil_ = int(round(anchor * f / 1000) * 1000)
            r["px_ceiling"] = ceil_                                   # 이 이상 절대 금지
            r["px_fair"] = int(round(ceil_ * 0.90 / 1000) * 1000)     # 적정 상단
            r["px_special"] = int(round(ceil_ * 0.80 / 1000) * 1000)  # 특가
            r["px_epic"] = int(round(ceil_ * 0.68 / 1000) * 1000)     # 역대급
            r["px_basis"] = {
                "own": own, "sibling_min": sib_min, "group_min": grp_min,
                "better_min": better_min, "age_factor": round(f, 2),
            }
        else:
            r["px_ceiling"] = r["px_fair"] = r["px_special"] = r["px_epic"] = None
            r["px_basis"] = None

    # ── 리포트 ──
    print(f"총 제품 수: {len(rows)}")
    print("신뢰도:", Counter(x["confidence"] for x in rows))
    bad = [(x["model"], x["flags"]) for x in rows if x["confidence"] in ("low", "fail")]
    for m, fl in bad:
        print("  경고:", m, fl)
    print("IoT 모델:", [x["model"] for x in rows if x["iot"]])
    noreg = [x["model"] for x in rows if not x["reg"]]
    print("등록월 없음:", noreg)
    print("상세 스펙 커버리지 — 기압:", sum(1 for x in rows if x.get("atm")),
          "· 소비전력:", sum(1 for x in rows if x.get("power_w")),
          "· 에너지등급:", sum(1 for x in rows if x.get("energy_grade")),
          "· 가격이력 2회+:", sum(1 for x in rows if len(x.get("hist", [])) >= 2))

    json.dump(rows, open("cuckoo-products.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    cols = ["model", "name", "pressure", "design", "heating", "twin_pressure", "low_sugar",
            "silence", "iot", "pot_code", "pot", "pot_grade", "variant", "capacity",
            "atm", "power_w", "energy_grade",
            "display", "color_code", "color", "suffix", "reg", "age_months",
            "list_price", "sale_price", "discount_rate",
            "px_epic", "px_special", "px_fair", "px_ceiling",
            "review_count", "categories", "status", "confidence"]
    with open("cuckoo-products.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for r in rows:
            w.writerow([("|".join(map(str, r[c])) if isinstance(r.get(c), list) else r.get(c, ""))
                        for c in cols])
    print("저장 완료: cuckoo-products.json / cuckoo-products.csv")
    return rows


if __name__ == "__main__":
    build()
