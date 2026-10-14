# -*- coding: utf-8 -*-
"""전체 재생성 파이프라인 (v3.4).
순서가 중요: 감가 곡선은 가중치 산출물이라, 기준선(build_v3)이 곡선을 반영하려면 2회 실행이 필요.
  1) build_v3       — 소스+상세스펙+스냅샷 → products (감가: 곡선 있으면 곡선, 없으면 보수 가정)
  2) build_weights  — 회귀 v2 + 감가 곡선 + 라인 주기 → cuckoo-weights.json
  3) build_v3       — 경험 감가 곡선으로 기준선 재계산
  4) build_html_v3 / build_html_mobile — HTML 2종
(선행 크롤이 필요할 때만: python crawl_detail.py / python crawl_danawa_spec.py / python build_snapshot.py)"""
import subprocess, sys

for step in ["build_v3.py", "build_weights.py", "build_v3.py",
             "build_html_v3.py", "build_html_mobile.py"]:
    print(f"\n━━ {step} ━━")
    r = subprocess.run([sys.executable, "-X", "utf8", step])
    if r.returncode != 0:
        sys.exit(f"실패: {step}")
print("\n전체 재생성 완료")
