"""아카이브 갱신: reports.json 맨 앞에 이번 호 추가 → ai-trend/index.html, ai-trend/latest/index.html 재생성 (지시서 8.3·9.10)

사용법
  python _system/scripts/update_archive.py --issue 2026-10-w2_20261014
  python _system/scripts/update_archive.py --issue 2026-10-w2_20261014_r2 --supersede 2026-10-w2_20261014   # 정정 재발행(3.3)

원칙
  - 과거 항목은 지우거나 덮어쓰지 않는다. 같은 issue_id 가 이미 있으면 그 항목만 최신 정보로 갱신한다.
  - 정정 재발행이면 이전 항목의 status 를 superseded 로 바꾸고, latest/ 는 새 폴더를 가리킨다.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import ROOT, SITE, archive_entry_for, make_env, tokens_css  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--supersede", help="정정 재발행 시 superseded 로 바꿀 이전 발행 ID")
    a = ap.parse_args()

    d = json.loads((ROOT / "reports" / a.issue / "data.json").read_text(encoding="utf-8"))
    for f in ("index.html", "report.pdf", "report.pptx", "data.json", "og.png"):
        if not (ROOT / "reports" / a.issue / f).exists():
            print(f"경고: reports/{a.issue}/{f} 가 아직 없음")

    path = ROOT / "reports.json"
    doc = {"site": SITE, "publisher": "Unfade", "reports": []}
    if path.exists():
        doc = json.loads(path.read_text(encoding="utf-8"))
    reports = [r for r in doc.get("reports", []) if r.get("issue_id") != a.issue]
    if a.supersede:
        for r in reports:
            if r.get("issue_id") == a.supersede:
                r["status"] = "superseded"
    reports.insert(0, archive_entry_for(d))
    reports.sort(key=lambda r: (r["published_at_kst"], r.get("issue_no", 0), r["issue_id"]), reverse=True)
    doc["reports"] = reports
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    latest = next(r for r in reports if r.get("status") == "published")
    env = make_env()
    (ROOT / "index.html").write_text(env.get_template("index.html.j2").render(site=SITE, latest=latest, reports=reports,
                                                                             tokens_css=tokens_css()), encoding="utf-8")
    (ROOT / "latest").mkdir(exist_ok=True)
    (ROOT / "latest" / "index.html").write_text(env.get_template("latest.html.j2").render(site=SITE, latest=latest), encoding="utf-8")
    print(json.dumps({"reports": len(reports), "latest": latest["issue_id"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
