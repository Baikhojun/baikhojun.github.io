# -*- coding: utf-8 -*-
"""cuckoo-source-v3.json 갱신 (재사용 가능).
쿠쿠몰 리스트 REST API로 기존 모델의 가격·리뷰수·재고·NEW 표시를 최신화하고,
새로 등장한 모델은 다나와 등록월(meta_item mt_date)을 찾아 추가한다.
몰 stockYn 은 'Y' 가 품절(N 이 판매중) — crawl_detail 의 스냅샷 'so' 와 같은 의미.
사용법: python update_source.py   (이후 python crawl_detail.py → build_v3 → crawl_danawa_spec → build_all)"""
import urllib.request, urllib.parse, json, re, time, datetime

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'
CATS = {1: 'TP', 252: 'SI', 52: 'IH', 49: 'PL', 58: 'WM', 71: 'LS', 54: 'AS'}  # 대용량 57 제외

def api_list(cat):
    hdr = {'User-Agent': UA, 'Content-Type': 'application/json;charset=UTF-8',
           'Referer': f'https://www.cuckoo.co.kr/mall/productList?categoryCd={cat}',
           'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://www.cuckoo.co.kr'}
    body = json.dumps({"categoryCd": str(cat), "page": "1", "pageSize": "500"}).encode()
    req = urllib.request.Request('https://www.cuckoo.co.kr/rest/mall/mallProductSearch', data=body, headers=hdr)
    return json.loads(urllib.request.urlopen(req, timeout=25).read().decode('utf-8')).get('productList') or []

def danawa_reg(model):
    """다나와 검색 → '26.08. 등록' 형태의 등록월. 없으면 None."""
    try:
        url = 'https://search.danawa.com/dsearch.php?query=' + urllib.parse.quote(model)
        h = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=25).read().decode('utf-8', 'ignore')
        for m in re.finditer(r'class="prod_name"(.{0,800}?)</a>(.{0,6000}?)mt_date">\s*(\d\d\.\d\d)\.\s*등록', h, re.S):
            name = re.sub(r'<[^>]+>', '', m.group(1)).upper().replace(' ', '')
            if model.replace('-', '') in name.replace('-', ''):
                return m.group(3)
    except Exception as e:
        print('  다나와 실패:', model, e)
    return None

def main():
    src = json.load(open('cuckoo-source-v3.json', encoding='utf-8'))
    # 키 = 괄호 서픽스 제거한 모델코드 (소스 'CRP-CHB1075FD(면세점, 중국어)' ↔ 몰 'CRP-CHB1075FD',
    # 소스 'CRP-CHB1060FSM' ↔ 몰 'CRP-CHB1060FSM(C)' 처럼 표기가 어긋나는 경우 대응)
    base = lambda m: re.sub(r'\(.*?\)$', '', m.strip().upper())
    by = {base(s['model']): s for s in src}
    mall, cats = {}, {}
    for c, code in CATS.items():
        for p in api_list(c):
            cd = base(p.get('productCd') or '')
            if not cd: continue
            mall.setdefault(cd, p)
            cats.setdefault(cd, []).append(code)
        time.sleep(0.3)
    print('몰 고유 모델:', len(mall), '· 기존 소스:', len(src))

    changed, gone, added = 0, [], []
    for key, s in by.items():
        p = mall.get(key)
        if not p:
            gone.append(key); continue
        before = (s['lp'], s['sp'], s['rc'], s['status'], s['new'])
        s['lp'] = p.get('price'); s['sp'] = p.get('salePrice'); s['rc'] = p.get('reviewCnt') or 0
        if s['status'] != '면세점':
            s['status'] = '품절' if p.get('stockYn') == 'Y' else '판매중'
        s['new'] = p.get('newYn') == 'Y'
        if p.get('note') and not s.get('desc'): s['desc'] = p['note']
        s['cats'] = cats[key]
        if before != (s['lp'], s['sp'], s['rc'], s['status'], s['new']): changed += 1

    for key, p in mall.items():
        if key in by: continue
        reg = danawa_reg(key); est = False
        if not reg:
            m = re.search(r'([A-Z][a-z]{2}) \d+, (\d{4})', p.get('regDt') or '')
            if m:
                mon = datetime.datetime.strptime(m.group(1), '%b').month
                reg, est = f'{m.group(2)[2:]}.{mon:02d}', True   # 다나와 미등록 → 몰 등록일로 추정
        e = {'model': p['productCd'].strip(), 'name': p.get('productNm') or '', 'lp': p.get('price'),
             'sp': p.get('salePrice'), 'rc': p.get('reviewCnt') or 0, 'desc': p.get('note') or '',
             'cats': cats[key], 'status': '품절' if p.get('stockYn') == 'Y' else '판매중',
             'reg': reg, 'reg_est': est, 'new': p.get('newYn') == 'Y'}
        src.append(e); added.append((key, reg, est))
        time.sleep(0.5)

    json.dump(src, open('cuckoo-source-v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'갱신 {changed}건 · 몰에서 사라진 모델(상태 유지) {gone} · 신규 {added}')
    print('저장: cuckoo-source-v3.json', len(src), '개')

if __name__ == '__main__':
    main()
