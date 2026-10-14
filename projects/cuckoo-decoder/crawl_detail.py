# -*- coding: utf-8 -*-
"""쿠쿠 공식몰 1회성 크롤 (v4 데이터 확장 + 가격 스냅샷).
① 리스트 REST API로 model↔productNo + 오늘 가격/재고/리뷰 → snapshots/price-YYMMDD.json
② 각 상세페이지(서버렌더 HTML)에서 소비전력·에너지효율등급·중량·크기 파싱 → cuckoo-detail.json
서버·DB 불필요: 결과는 로컬 JSON으로 누적되고, 빌드 시 HTML에 임베드된다.
사용법: python crawl_detail.py [--list-only]
"""
import urllib.request, json, re, time, os, sys, datetime

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'
CATS = [1, 252, 52, 49, 58, 71, 54]   # TP·사일런스·IH·열판·보온·저당·올스텐 (대용량 57 제외)

def api_list(cat):
    hdr = {'User-Agent': UA, 'Content-Type': 'application/json;charset=UTF-8',
           'Referer': f'https://www.cuckoo.co.kr/mall/productList?categoryCd={cat}',
           'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://www.cuckoo.co.kr'}
    body = json.dumps({"categoryCd": str(cat), "page": "1", "pageSize": "500"}).encode()
    req = urllib.request.Request('https://www.cuckoo.co.kr/rest/mall/mallProductSearch', data=body, headers=hdr)
    res = json.loads(urllib.request.urlopen(req, timeout=25).read().decode('utf-8'))
    return res.get('productList') or []

def fetch_view(no):
    req = urllib.request.Request(f'https://www.cuckoo.co.kr/mall/productView?productNo={no}',
                                 headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'ignore')

def parse_detail(html):
    txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html))
    d = {}
    m = re.search(r'정격전압\s*,?\s*소비전력\s*,?\s*에너지\s*(?:소비)?효율등급\s*([^가-힣]{0,60}?)(?:\d\s*등급|등급|해당\s*없음|미적용)', txt)
    seg = None
    m2 = re.search(r'정격전압\s*,?\s*소비전력\s*,?\s*에너지\s*(?:소비)?효율등급\s*(.{0,80})', txt)
    if m2:
        seg = m2.group(1)
        pw = re.search(r'([\d,]{2,6})\s*W', seg)
        if pw: d['power_w'] = int(pw.group(1).replace(',', ''))
        eg = re.search(r'(\d)\s*등급', seg)
        if eg: d['energy_grade'] = int(eg.group(1))
        elif '해당' in seg or '미적용' in seg: d['energy_grade'] = 0
        vt = re.search(r'(\d{3}V\s*/\s*\d{2}Hz)', seg)
        if vt: d['volt'] = vt.group(1).replace(' ', '')
        d['power_raw'] = seg.strip()[:70]
    wm = re.search(r'중량\s*\(?\s*kg\s*\)?\s*[:：]?\s*(?:약\s*)?([\d.]+)\s*kg', txt)
    if wm:
        try: d['weight_kg'] = float(wm.group(1))
        except ValueError: pass
    sm = re.search(r'크기\s*[:：]?\s*([\d.]+\s*cm[^가-힣]{0,50}?[\d.]+\s*cm[^가-힣]{0,30}?[\d.]+\s*cm)', txt)
    if sm: d['size'] = re.sub(r'\s+', '', sm.group(1))[:60]
    return d

def main():
    today = datetime.date.today().strftime('%y%m%d')
    os.makedirs('snapshots', exist_ok=True)

    # ── ① 리스트 + 스냅샷 ──
    mapping, snap = {}, {}
    for c in CATS:
        pl = api_list(c)
        print(f'category {c}: {len(pl)}개')
        for p in pl:
            cd = (p.get('productCd') or '').strip().upper()
            if not cd: continue
            if cd not in mapping:
                mapping[cd] = p['productNo']
                snap[cd] = {'lp': p.get('price'), 'sp': p.get('salePrice'),
                            'so': p.get('stockYn') == 'Y', 'rc': p.get('reviewCnt')}
        time.sleep(0.3)
    print('고유 모델:', len(mapping))
    json.dump(mapping, open('cuckoo-productno.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    snap_path = f'snapshots/price-{today}.json'
    json.dump({'date': today, 'prices': snap}, open(snap_path, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('스냅샷 저장:', snap_path)
    if '--list-only' in sys.argv: return

    # ── ② 상세 크롤 ──
    detail = {}
    if os.path.exists('cuckoo-detail.json'):
        detail = json.load(open('cuckoo-detail.json', encoding='utf-8'))
    todo = [(cd, no) for cd, no in mapping.items() if cd not in detail]
    print('상세 크롤 대상:', len(todo))
    for i, (cd, no) in enumerate(todo):
        try:
            d = parse_detail(fetch_view(no))
            d['product_no'] = no
            detail[cd] = d
        except Exception as e:
            print('  실패:', cd, no, e)
            detail[cd] = {'product_no': no, 'error': str(e)[:80]}
        if (i + 1) % 20 == 0:
            print(f'  {i+1}/{len(todo)}')
            json.dump(detail, open('cuckoo-detail.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        time.sleep(0.4)
    json.dump(detail, open('cuckoo-detail.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ok = sum(1 for v in detail.values() if 'power_w' in v)
    eg = sum(1 for v in detail.values() if v.get('energy_grade'))
    print(f'상세 저장: {len(detail)}개 중 소비전력 {ok}개 · 에너지등급 {eg}개')

if __name__ == '__main__':
    main()
