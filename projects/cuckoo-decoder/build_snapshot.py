# -*- coding: utf-8 -*-
"""가격 스냅샷 시드 생성 — 과거 크롤 데이터에서 소급 생성 (1회용, 이미 있으면 건너뜀).
- snapshots/price-260818.json ← 260825/_backup/cuckoo-products.json (v2.1 크롤)
- snapshots/price-260825.json ← cuckoo-source-v3.json (v3.0 크롤)
이후 스냅샷은 crawl_detail.py 실행 시 자동 누적된다. 서버·DB 불필요."""
import json, os

os.makedirs('snapshots', exist_ok=True)

def save(day, prices):
    p = f'snapshots/price-{day}.json'
    if os.path.exists(p):
        print('이미 있음:', p); return
    json.dump({'date': day, 'prices': prices}, open(p, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('생성:', p, len(prices), '개')

# 26.08.18 (v2.1)
old = json.load(open('260825/_backup/cuckoo-products.json', encoding='utf-8'))
save('260818', {r['model'].upper(): {'lp': r.get('list_price'), 'sp': r.get('sale_price'),
                                     'so': r.get('status') != '판매중', 'rc': r.get('review_count')}
                for r in old})

# 26.08.25 (v3.0)
src = json.load(open('cuckoo-source-v3.json', encoding='utf-8'))
save('260825', {s['model'].upper(): {'lp': s.get('lp'), 'sp': s.get('sp'),
                                     'so': s.get('status') != '판매중', 'rc': s.get('rc')}
                for s in src})
