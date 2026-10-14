# -*- coding: utf-8 -*-
"""다나와 검색 결과의 스펙 텍스트로 v4 스펙 보완 (1회성 크롤).
쿠쿠몰 상세는 40/212만 텍스트 스펙을 제공(나머지는 이미지) → 다나와 spec_list로 보완.
스템(색상형제 그룹) 단위 검색 — 색상만 다르면 스펙 동일.
출력: cuckoo-danawa-spec.json {stem: {atm, power_w, energy_grade, size_mm, spec}}"""
import urllib.request, urllib.parse, json, re, time, os

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'

def fetch(stem):
    url = 'https://search.danawa.com/dsearch.php?query=' + urllib.parse.quote(stem)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'ignore')

def parse(html, stem):
    """danawa 정식 상품 블록: 상품명(prod_name)에 스템 포함 + spec_list 텍스트.
    소비전력 등 확장 스펙은 '더보기' 펼침 영역(같은 상품 블록 뒤쪽)에 있어 넓은 범위에서 추가 탐색."""
    best, wide = None, None
    for m in re.finditer(r'class="prod_name"(.{0,1200}?)class="spec_list"(.{0,4000}?)</div>', html, re.S):
        name = re.sub(r'<[^>]+>', ' ', m.group(1)).upper().replace(' ', '')
        if stem.replace('-', '') not in name.replace('-', ''):
            continue
        spec = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(2))).strip()
        if len(spec) < 30:
            continue
        best = spec
        wide = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html[m.start():m.start() + 15000]))
        break
    if not best:
        return None
    d = {'spec': best[:400]}
    if wide:
        pw2 = re.search(r'소비전력\s*[:：]?\s*([\d,]{3,6})\s*W', wide)
        if pw2: d['power_w'] = int(pw2.group(1).replace(',', ''))
        am2 = re.findall(r'(\d(?:\.\d)?)\s*기압', wide)
        if am2 and 'atm' not in d:
            v = max(float(x) for x in am2)
            if 1.0 <= v <= 2.5: d['atm'] = v
    am = re.findall(r'(\d(?:\.\d)?)\s*기압', best)
    if am: d['atm'] = max(float(x) for x in am)
    pw = re.search(r'소비전력\s*[:：]?\s*([\d,]{3,6})\s*W', best)
    if pw: d['power_w'] = int(pw.group(1).replace(',', ''))
    eg = re.search(r'에너지\s*[:：]?\s*(\d)\s*등급', best)
    if eg: d['energy_grade'] = int(eg.group(1))
    sz = re.search(r'크기\(가로x세로x깊이\)\s*[:：]?\s*([\dx.]+)\s*mm', best)
    if sz: d['size_mm'] = sz.group(1)
    return d

def main():
    DB = json.load(open('cuckoo-products.json', encoding='utf-8'))
    stems = sorted({r['stem'] for r in DB})
    out = {}
    if os.path.exists('cuckoo-danawa-spec.json'):
        out = json.load(open('cuckoo-danawa-spec.json', encoding='utf-8'))
    todo = [s for s in stems if s not in out
            or (out[s].get('spec') and 'power_w' not in out[s])]
    print('스템', len(stems), '중 크롤 대상', len(todo))
    for i, s in enumerate(todo):
        try:
            d = parse(fetch(s), s)
            out[s] = d or {}
        except Exception as e:
            print('  실패:', s, e)
            out[s] = {'error': str(e)[:60]}
        if (i + 1) % 15 == 0:
            print(f'  {i+1}/{len(todo)}')
            json.dump(out, open('cuckoo-danawa-spec.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        time.sleep(0.5)
    json.dump(out, open('cuckoo-danawa-spec.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    hit = sum(1 for v in out.values() if v.get('spec'))
    atm = sum(1 for v in out.values() if v.get('atm'))
    pw = sum(1 for v in out.values() if v.get('power_w'))
    eg = sum(1 for v in out.values() if v.get('energy_grade'))
    print(f'완료: 스템 {len(out)}개 — 스펙 {hit} · 기압 {atm} · 소비전력 {pw} · 에너지등급 {eg}')

if __name__ == '__main__':
    main()
