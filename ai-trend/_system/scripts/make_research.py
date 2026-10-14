"""data.json → research.md (감사용 조사근거 기록, 지시서 1.3-4·5.1-9·10장)

사용법
  python _system/scripts/make_research.py --issue 2026-10-w2_20261014 [--queries 쿼리.md] [--qa 검수결과.json]

내용
  1 조사 개요(일시·검색 횟수·출처 수·재확인 목록) 2 실행 변수 3 사실 기록(항목별 사실·출처·게시일·확인일·등급·근거 충족)
  4 수치·계산식(환율 환산, 요금, 리더보드 버전) 5 미확인·충돌 6 조사 한계 7 검색 쿼리 8 이미지 사용 근거 9 품질 검수 결과
"""
import argparse
import json
import sys
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import ROOT, all_sources, counts_by_status, fmt_score  # noqa: E402


def won(usd, rate):
    v = (Decimal(str(usd)) * Decimal(str(rate)) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100
    return f"{int(v):,}원"


def grade_ok(sources):
    a = sum(1 for s in sources if s.get("grade") == "A")
    b = sum(1 for s in sources if s.get("grade") == "B")
    if a >= 1:
        return "충족(A)"
    if b >= 2:
        return "충족(B 2곳)"
    return "단일 B·C — '보도'로 표시"


def src_line(s):
    pub = s.get("published_at") or "게시일 미표기"
    return f"  - [{s.get('grade', '?')}] {s.get('publisher', '')} — {s.get('title', '')} · 게시 {pub} · 확인 {s.get('checked_at', '')} · <{s['url']}>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True)
    ap.add_argument("--queries", help="검색 쿼리 목록(마크다운) 파일")
    ap.add_argument("--qa", help="품질 검수 결과 JSON 파일")
    a = ap.parse_args()
    d = json.loads((ROOT / "reports" / a.issue / "data.json").read_text(encoding="utf-8"))
    srcs = all_sources(d)
    gc = {"A": 0, "B": 0, "C": 0}
    for s in srcs:
        gc[s.get("grade", "C")] = gc.get(s.get("grade", "C"), 0) + 1
    st = counts_by_status(d["items"])
    log = d.get("search_log", {})
    L = []
    w = L.append
    w(f"# AI 트렌드 브리핑 제{d['issue_no']}호 조사근거 — {d['week_label']}")
    w("")
    w(f"> 발행 ID `{d['issue_id']}` · 기준일 {d['report_date_kst']}({d.get('weekday_ko', '')}) KST · 비교 기간 {d['period'].replace('~', ' ~ ')} · "
      f"{'신규 기준선(직전 발행본 없음)' if d['is_baseline'] else '직전 발행일 ' + str(d['previous_report']['report_date_kst'])}")
    w("> 발행처 Unfade. 조사·작성 도구: Anthropic의 AI(Claude). 이해상충 가능성이 있어 Anthropic 관련 항목에도 같은 출처 기준을 적용했다.")
    w("> 이 문서는 사실 단위 기록이다. 기사·게시글 문장을 옮기지 않고 의역했으며, 커뮤니티 이용자 아이디는 싣지 않았다.")
    w("")
    w("## 1. 조사 개요")
    w("")
    started = log.get("started_kst")
    w(f"- 조사 일시: {started + ' KST 착수(실행 변수 계산 시각)' if started else d['report_date_kst'] + ' KST'}"
      f"{', 같은 날 완료' if started and started.startswith(d['report_date_kst']) else ''}"
      f"{' — ' + log['method'] if log.get('method') else ''}")
    w(f"- 웹 검색: **{d['search_count']}회**(실행 기준) · 원문 열람: **{d['methodology'].get('fetch_count', '—')}회**")
    if log.get("by_area"):
        w("")
        w("| 분야 | 검색 횟수 |")
        w("|---|---|")
        for k, v in log["by_area"].items():
            w(f"| {k} | {v} |")
        w("")
        if log.get("note"):
            w(f"- 비고: {log['note']}")
    w(f"- 출처: **{len(srcs)}개** — A {gc['A']} · B {gc['B']} · C {gc['C']} (URL 기준 중복 제거)")
    w(f"- 항목: 핵심 변화 {sum(1 for i in d['items'] if i['section'] == 'core')}건 · 토목 특집 {sum(1 for i in d['items'] if i['section'] == 'civil')}건 · "
      f"추적 {sum(1 for i in d['items'] if i['section'] == 'watch')}건 / 상태 신규 {st.get('new', 0)} · 변경 {st.get('changed', 0)} · "
      f"종료 {st.get('ended', 0)} · 정정 {st.get('corrected', 0)} · 추적 {st.get('watch', 0)}")
    if d.get("reverified"):
        w("- 편집 단계에서 원문을 직접 다시 연 핵심 사실:")
        for r in d["reverified"]:
            w(f"  - {r}")
    w("")
    w("## 2. 실행 변수 (calc_dates.py 계산)")
    w("")
    w("| 변수 | 값 |")
    w("|---|---|")
    for k, v in (("기준일", f"{d['report_date_kst']} ({d.get('weekday_ko', '')})"), ("주차 라벨", d["week_label"]), ("발행 ID", d["issue_id"]),
                 ("내려받기 파일명 접두", d["download_prefix"]), ("발행 번호", f"제{d['issue_no']}호"),
                 ("비교 기간", d["period"]), ("직전 발행본", d["previous_report"]["issue_id"] or "없음 — 신규 기준선(최근 30일)"),
                 ("발행본 주소", d["canonical_url"])):
        w(f"| {k} | {v} |")
    w("")
    base = date.fromisoformat(d["report_date_kst"])
    monday = base - timedelta(days=base.weekday())
    first = monday.replace(day=1)
    first_monday = first + timedelta(days=(7 - first.weekday()) % 7)
    w(f"주차 규칙: 기준일이 속한 주(월~일)의 월요일({monday.isoformat()})이 속한 달의 첫 월요일({first_monday:%m-%d})이 있는 주를 "
      f"1주차로 센다 → {d['week_label'].split(' ', 1)[1] if ' ' in d['week_label'] else d['week_label']}.")
    w("")
    w("## 3. 사실 기록")
    w("")
    for sec, title in (("core", "3-1. 핵심 변화"), ("civil", "3-2. 토목설계·건설 특집"), ("watch", "3-3. 다음 호까지 추적할 항목")):
        w(f"### {title}")
        w("")
        for it in [i for i in d["items"] if i["section"] == sec]:
            extra = []
            if it.get("maturity") and it["maturity"] != "해당 없음":
                extra.append(f"성숙도 {it['maturity']}")
            if it.get("watch_type"):
                extra.append(f"구분 {it['watch_type']}")
            if it.get("country"):
                extra.append(f"{it['country']} · {it.get('org', '')}")
            w(f"**[{it['id']}]** {it['title_ko']}  ")
            w(f"태그 {it['tag']} · 상태 {it['status']} · 중요도 {it['importance']} · 날짜 {it.get('date')} (최초 발표 {it.get('first_announced_at')}) · "
              f"지역 {it.get('region', '')}{' · ' + ' · '.join(extra) if extra else ''}  ")
            w(f"근거 충족: {grade_ok(it['sources'])}")
            w("")
            w(f"- 사실: {it['summary_ko']}")
            for f in it.get("facts", []):
                w(f"- {f}")
            if it.get("effect"):
                w(f"- 효과: {it['effect']}")
            w("- 출처:")
            for s in it["sources"]:
                w(src_line(s))
            w("")
    w("## 4. 수치·계산식")
    w("")
    fx = d["basis"]["fx"]
    w(f"- 환율: 1달러 = {fx['usd_krw']:,}원 — {fx['source']}({fx['date']}) <{fx['url']}>."
      + (f" 교차 확인: {fx['cross_check']}." if fx.get("cross_check") else ""))
    w(f"- 원화 환산식: `원화 = 달러 정가 × {fx['usd_krw']:,}`, 100원 단위 반올림(0.5는 올림). 부가세·카드 해외결제 수수료·앱스토어 가격 차이는 포함하지 않음.")
    w("")
    w("| 서비스 | 요금제 | 정가 | 원화 환산·공식 원화 | 부가세 | 출처 |")
    w("|---|---|---|---|---|---|")
    for p in d["metrics"]["prices"]:
        price = p.get("price_label") or (f"${p['price']:g}" if p.get("price") is not None else "미확인")
        krw = p.get("krw_label") or (won(p["price"], fx["usd_krw"]) if p.get("price") else "—")
        vat = {True: "포함", False: "별도"}.get(p.get("vat_included"), "미확인")
        w(f"| {p['service']} | {p['plan']} | {price} | {krw} | {vat} | <{p['source_url']}> |")
    w("")
    w(f"API 가격(USD/100만 토큰, 확인일 {d['report_date_kst']}):")
    w("")
    w("| 개발사 | 모델 | 입력 | 출력 | 비고 | 출처 |")
    w("|---|---|---|---|---|---|")
    for p in d["metrics"]["api_prices"]:
        w(f"| {p['vendor']} | {p['model']} | ${p['input']:g} | ${p['output']:g} | {p.get('note', '')} | <{p['source_url']}> |")
    w("")
    w("리더보드(독립 측정만, 자체 발표치 제외):")
    w("")
    for lb in d["metrics"]["leaderboards"]:
        top = " / ".join(f"{r['rank']}. {r['model']} {fmt_score(r['score'])}" + (f" ±{r['ci_plus']}" if r.get("ci_plus") else "") for r in lb["rows"][:5])
        w(f"- **{lb['name']}** ({lb['version']}, 측정·확인 {lb['checked_at']}, {lb['method']}) — {top} · <{lb['source_url']}>")
        w(f"  - 해석 한계: {lb['note']}")
    w("")
    w("가능 수준 판정: 공식 문서 기준(실측 아님). 판정별 근거 URL은 data.json `metrics.capabilities`·`metrics.file_support` 에 칸마다 기록.")
    w("")
    w("## 5. 미확인·충돌 항목 (결론·순위·가격 표에 넣지 않음)")
    w("")
    for x in d.get("unconfirmed", []):
        w(f"- {x}")
    w("")
    w("## 6. 조사 한계")
    w("")
    for x in d["limitations"]:
        w(f"- {x}")
    w("")
    w("## 7. 검색 쿼리 목록")
    w("")
    if a.queries and Path(a.queries).exists():
        w(Path(a.queries).read_text(encoding="utf-8").strip())
    else:
        w("(쿼리 목록 파일이 제공되지 않음)")
    w("")
    w("## 8. 이미지·로고 사용 근거")
    w("")
    w("- 서비스 로고·제품 화면·보도 이미지는 사용 권한을 확인하지 못해 쓰지 않았다.")
    w("- 모든 그림(타임라인·점 그림·막대·타일 지도·생애주기·흐름도)은 data.json 으로 직접 그린 SVG이며, 아이콘도 직접 그린 선 아이콘이다. AI 생성 이미지는 없다.")
    w("- 글꼴: Pretendard(SIL Open Font License 1.1, assets/fonts/LICENSE.txt), PPTX는 맑은 고딕.")
    w("")
    w("## 9. 품질 검수 결과 (지시서 10장)")
    w("")
    if a.qa and Path(a.qa).exists():
        qa = json.loads(Path(a.qa).read_text(encoding="utf-8"))
        for group, rows in qa.items():
            w(f"**{group}**")
            w("")
            for r in rows:
                mark = {"통과": "[x]", "보완 필요": "[ ]", "보류": "[ ]", "해당 없음": "[-]"}.get(r["result"], "[ ]")
                w(f"- {mark} {r['check']} — **{r['result']}**{(' · ' + r['note']) if r.get('note') else ''}")
            w("")
    else:
        w("(검수 결과 파일이 제공되지 않음)")
    out = ROOT / "reports" / a.issue / "research.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps({"research_md": str(out), "lines": len(L), "sources": len(srcs)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
