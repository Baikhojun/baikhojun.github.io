"""직전 발행본 data.json 과 이번 data.json 비교 (지시서 9장)

사용법
  python _system/scripts/diff.py --issue 2026-10-w2_20261014            # reports.json 의 직전 published 호와 비교
  python _system/scripts/diff.py --issue <이번 ID> --prev <직전 ID>        # 직접 지정
  python _system/scripts/diff.py --issue <이번 ID> --write                # 결과를 _local/diff_<ID>.json 에 저장

판정 (9.1)
  - 이번에만 있는 항목 id            → 신규 후보 (status 가 new/changed/ended/corrected 인지 확인)
  - 양쪽에 있고 사실·가격·태그가 다름 → 변경 후보 (가격 변동은 크기와 무관하게 전부)
  - 직전에 있던 watch 항목            → '직전 추적 항목 결과' 점검 목록
  - 직전에만 있는 항목               → 유지/종료 확인 목록 (조용히 지우지 말 것)
  - 리더보드: 같은 지표·같은 버전에서 순위 2계단 이상 또는 Arena ±10점 이상, 종합 지수 ±2점 이상 변동
  - 지표 버전이 바뀌면 '산식 변경으로 직접 비교 불가'
  - 요금: 같은 서비스·요금제의 가격이 다르면 전부 '가격' 변화
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(issue_id):
    p = ROOT / "reports" / issue_id / "data.json"
    return json.loads(p.read_text(encoding="utf-8"))


def prev_issue_id(cur):
    p = ROOT / "reports.json"
    if not p.exists():
        return None
    reports = json.loads(p.read_text(encoding="utf-8")).get("reports", [])
    older = [r for r in reports if r.get("status") == "published" and r["issue_id"] != cur["issue_id"]
             and r["published_at_kst"] <= cur["report_date_kst"]]
    if not older:
        return None
    return max(older, key=lambda r: (r["published_at_kst"], r.get("issue_no", 0)))["issue_id"]


def item_key_fields(it):
    return {k: it.get(k) for k in ("title_ko", "summary_ko", "tag", "status", "facts", "maturity")}


def compare(prev, cur):
    out = {"previous": prev["issue_id"] if prev else None, "current": cur["issue_id"], "baseline": prev is None}
    if prev is None:
        out["note"] = "직전 발행본이 없어 신규 기준선으로 처리한다. 상태(new/changed/ended)는 비교 기간 조사로 판정한 값이다."
        out["counts"] = {}
        for it in cur.get("items", []):
            out["counts"][it.get("status", "unchanged")] = out["counts"].get(it.get("status", "unchanged"), 0) + 1
        return out
    pi = {it["id"]: it for it in prev.get("items", [])}
    ci = {it["id"]: it for it in cur.get("items", [])}
    out["only_current"] = sorted(set(ci) - set(pi))
    out["only_previous"] = sorted(set(pi) - set(ci))
    out["changed_fields"] = {}
    for k in sorted(set(pi) & set(ci)):
        a, b = item_key_fields(pi[k]), item_key_fields(ci[k])
        diff = [f for f in a if a[f] != b[f]]
        if diff:
            out["changed_fields"][k] = diff
    out["previous_watch"] = [{"id": it["id"], "title": it.get("title_ko"), "watch_type": it.get("watch_type"),
                              "signal": it.get("signal")} for it in prev.get("items", []) if it.get("section") == "watch"]
    # 리더보드
    lb_out = []
    plb = {lb["id"]: lb for lb in prev.get("metrics", {}).get("leaderboards", [])}
    for lb in cur.get("metrics", {}).get("leaderboards", []):
        old = plb.get(lb["id"])
        if not old:
            lb_out.append({"id": lb["id"], "result": "신규 지표"})
            continue
        if old.get("version") != lb.get("version"):
            lb_out.append({"id": lb["id"], "result": "산식 변경으로 직접 비교 불가", "from": old.get("version"), "to": lb.get("version")})
            continue
        prev_rank = {r["model"]: r for r in old.get("rows", [])}
        moves = []
        for r in lb.get("rows", []):
            o = prev_rank.get(r["model"])
            if not o:
                moves.append({"model": r["model"], "change": "신규 진입", "rank": r["rank"]})
                continue
            d_rank = o["rank"] - r["rank"]
            d_score = (r.get("score") or 0) - (o.get("score") or 0)
            thr = 10 if lb["id"].startswith("arena") else 2
            if abs(d_rank) >= 2 or abs(d_score) >= thr:
                moves.append({"model": r["model"], "rank": f'{o["rank"]}→{r["rank"]}', "score": f'{o.get("score")}→{r.get("score")}'})
        lb_out.append({"id": lb["id"], "result": "비교", "moves": moves})
    out["leaderboards"] = lb_out
    # 요금
    def pk(p):
        return (p.get("service"), p.get("plan"))
    pp = {pk(p): p for p in prev.get("metrics", {}).get("prices", [])}
    price_changes = []
    for p in cur.get("metrics", {}).get("prices", []):
        o = pp.get(pk(p))
        if o and (o.get("price"), o.get("price_label")) != (p.get("price"), p.get("price_label")):
            price_changes.append({"service": p["service"], "plan": p["plan"], "from": o.get("price_label") or o.get("price"),
                                  "to": p.get("price_label") or p.get("price")})
        elif not o:
            price_changes.append({"service": p["service"], "plan": p["plan"], "from": None, "to": p.get("price_label") or p.get("price")})
    out["prices"] = price_changes
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--prev")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    cur = load(a.issue)
    pid = a.prev or prev_issue_id(cur)
    prev = load(pid) if pid else None
    res = compare(prev, cur)
    txt = json.dumps(res, ensure_ascii=False, indent=2)
    if a.write:
        out = ROOT / "_local" / f"diff_{a.issue}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(txt, encoding="utf-8")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
