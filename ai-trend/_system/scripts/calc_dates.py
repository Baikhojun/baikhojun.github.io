"""기준일·주차·비교 기간·발행 ID 계산 (지시서 2.2)

사용법
  python _system/scripts/calc_dates.py                 # 오늘(KST) 기준, JSON 출력
  python _system/scripts/calc_dates.py --date 2026-10-14
  python _system/scripts/calc_dates.py --selftest      # 지시서 예시 3건 검증

규칙
  - 기준일 = 실행 당일 KST (한국은 서머타임이 없어 UTC+9 고정)
  - 주차 = 기준일이 속한 주(월~일)의 월요일이 속한 연·월, 그 달의 첫 월요일이 있는 주 = 1주차
  - 발행 ID = YYYY-MM-wN_YYYYMMDD, 같은 날 재발행이면 _r2, _r3 …
  - 직전 발행본 = reports.json 에서 status 가 published 인 가장 최근 항목
  - 비교 기간 = 직전 기준일 다음 날 ~ 이번 기준일 (최초 발행 = 최근 30일)
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
WEEKDAYS_KO = ["월", "화", "수", "목", "금", "토", "일"]
SITE = "https://unfade.is-a.dev/ai-trend/"
AI_TREND_DIR = Path(__file__).resolve().parents[2]


def today_kst() -> date:
    return datetime.now(KST).date()


def week_info(d: date) -> dict:
    monday = d - timedelta(days=d.weekday())
    week_no = (monday.day - 1) // 7 + 1
    return {
        "monday": monday.isoformat(),
        "year": monday.year,
        "month": monday.month,
        "week_no": week_no,
        "week_label": f"{monday.year}년 {monday.month:02d}월 {week_no}주차",
        "download_prefix": f"AI_트렌드_{monday.year}년_{monday.month:02d}월_{week_no}주차",
        "base_id": f"{monday.year}-{monday.month:02d}-w{week_no}_{d:%Y%m%d}",
    }


def previous_report(reports_path: Path, base: date, exclude: str | None = None):
    """기준일 이전(당일 포함)의 가장 최근 발행본. exclude = 지금 계산 중인 발행 ID(자기 자신을 직전 발행본으로 잡지 않게)."""
    if not reports_path.exists():
        return None
    data = json.loads(reports_path.read_text(encoding="utf-8"))
    published = [
        r for r in data.get("reports", [])
        if r.get("status") == "published" and r.get("published_at_kst")
        and date.fromisoformat(r["published_at_kst"]) <= base
        and r.get("issue_id") != exclude
    ]
    if not published:
        return None
    return max(published, key=lambda r: (r["published_at_kst"], r.get("issue_no", 0)))


def calc(base: date, reports_path: Path, reports_dir: Path, same_day_new: bool = True) -> dict:
    w = week_info(base)

    # 같은 날 재발행: 폴더가 이미 있으면 _r2, _r3 …
    issue_id = w["base_id"]
    if same_day_new and (reports_dir / issue_id).exists():
        n = 2
        while (reports_dir / f"{w['base_id']}_r{n}").exists():
            n += 1
        issue_id = f"{w['base_id']}_r{n}"

    # 이미 reports.json 에 올라간 호를 다시 만들 때(--existing) 그 호 자신은 직전 발행본이 아니다
    prev = previous_report(reports_path, base, exclude=issue_id)

    if prev:
        prev_date = date.fromisoformat(prev["published_at_kst"])
        if prev_date == base:
            # 같은 날 정정 발행: 직전 발행본과 같은 비교 기간을 이어받는다
            period_start = date.fromisoformat(prev["period"].split("~")[0])
        else:
            period_start = prev_date + timedelta(days=1)
        issue_no = int(prev.get("issue_no", 0)) + 1
        baseline = False
    else:
        period_start = base - timedelta(days=29)  # 기준일 포함 30일
        issue_no = 1
        baseline = True

    return {
        "report_date_kst": base.isoformat(),
        "weekday_ko": WEEKDAYS_KO[base.weekday()],
        "report_date_label": f"{base.isoformat()} ({WEEKDAYS_KO[base.weekday()]})",
        "week_label": w["week_label"],
        "week_monday": w["monday"],
        "issue_id": issue_id,
        "download_prefix": w["download_prefix"],
        "issue_no": issue_no,
        "is_baseline": baseline,
        "period_start": period_start.isoformat(),
        "period_end": base.isoformat(),
        "period": f"{period_start.isoformat()}~{base.isoformat()}",
        "period_days": (base - period_start).days + 1,
        "previous_report": {
            "issue_id": prev["issue_id"] if prev else None,
            "report_date_kst": prev["published_at_kst"] if prev else None,
            "data_path": (prev.get("data_url") if prev else None),
        },
        "canonical_url": f"{SITE}reports/{issue_id}/",
    }


def selftest() -> int:
    cases = [
        ("2026-10-14", "2026년 10월 2주차", "2026-10-w2_20261014"),
        ("2026-10-02", "2026년 09월 4주차", "2026-09-w4_20261002"),
        ("2027-01-01", "2026년 12월 4주차", "2026-12-w4_20270101"),
    ]
    ok = True
    for d, label, iid in cases:
        w = week_info(date.fromisoformat(d))
        good = w["week_label"] == label and w["base_id"] == iid
        ok &= good
        print(f"{'OK ' if good else 'NG '} {d} -> {w['week_label']} / {w['base_id']}")
    # 최초 발행 비교 기간 = 30일
    r = calc(date(2026, 10, 14), Path("__none__.json"), Path("__none__"))
    good = r["period"] == "2026-09-15~2026-10-14" and r["period_days"] == 30
    ok &= good
    print(f"{'OK ' if good else 'NG '} 최초 발행 비교 기간 -> {r['period']} ({r['period_days']}일)")
    # 이미 reports.json 에 올라간 호를 다시 계산해도 자기 자신을 직전 발행본으로 잡지 않는다
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rp = Path(td) / "reports.json"
        rp.write_text(json.dumps({"reports": [{"issue_no": 1, "issue_id": "2026-10-w2_20261014", "status": "published",
                                               "published_at_kst": "2026-10-14", "period": "2026-09-15~2026-10-14"}]}),
                      encoding="utf-8")
        r = calc(date(2026, 10, 14), rp, Path(td), same_day_new=False)
        good = r["issue_no"] == 1 and r["is_baseline"] and r["previous_report"]["issue_id"] is None
        ok &= good
        print(f"{'OK ' if good else 'NG '} 같은 호 다시 계산 -> 제{r['issue_no']}호, 기준선 {r['is_baseline']}, 직전 {r['previous_report']['issue_id']}")
        r = calc(date(2026, 10, 21), rp, Path(td))
        good = r["issue_no"] == 2 and not r["is_baseline"] and r["period"] == "2026-10-15~2026-10-21"
        ok &= good
        print(f"{'OK ' if good else 'NG '} 다음 호 -> 제{r['issue_no']}호, 비교 기간 {r['period']}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="기준일 YYYY-MM-DD (기본값: 오늘 KST)")
    ap.add_argument("--reports", default=str(AI_TREND_DIR / "reports.json"))
    ap.add_argument("--reports-dir", default=str(AI_TREND_DIR / "reports"))
    ap.add_argument("--existing", action="store_true",
                    help="이미 만든 발행 폴더를 다시 계산할 때(_rN 접미사를 붙이지 않음)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    base = date.fromisoformat(a.date) if a.date else today_kst()
    out = calc(base, Path(a.reports), Path(a.reports_dir), same_day_new=not a.existing)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
