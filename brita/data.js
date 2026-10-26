/* BRITA 신혼부부 정수기 비교 — 데이터 원장
 * 기준일 2026-10-26(KST). 가격·판매 구성은 사용자가 첨부한 브리타 공식몰 화면 5장(I1~I5)의 관측값이다.
 * 사양은 브리타 한국 공식 사이트 등 [S1]~[S11]을 따른다. 미확정 수량은 null로 두고 0으로 바꾸지 않는다.
 */
window.BRITA = {
  asOf: '2026-10-26',
  store: {
    name: '브리타 공식 네이버 브랜드스토어',
    home: 'https://brand.naver.com/brita_official',
    note: '브리타 한국 공식 홈페이지의 "구매하기" 버튼이 연결하는 네이버 공식 스토어입니다.'
  },

  /* 본체 7종 */
  models: [
    { id: 'B01', name: '리켈리', size: '2.2L', family: '리켈리', total: 2.2, filtered: 1.1, timer: '메모', material: '플라스틱',
      dims: '20.2 × 11.0 × 28.4', colors: ['화이트', '블루'], img: 'liquelli.webp',
      naver: 'https://brand.naver.com/brita_official/products/10390864477', official: 'https://www.brita.kr/water-filter-system/liquelli',
      one: '가장 싸고 가장 작은 물통', fit: '1인 또는 물을 적게 마시는 집, 냉장고 문 수납',
      pros: ['본체+필터 1개 19,510원으로 가장 저렴', '슬림해서 냉장고 문 칸에 쏙'],
      cons: ['정수 보관량 1.1L — 2인 가구는 하루 3~4번 채워야 함', '교체 알림이 시간만 세는 메모 방식'],
      src: 'S1' },
    { id: 'B02', name: '스타일에센셜 쿨', size: '2.4L', family: '스타일에센셜', total: 2.4, filtered: 1.4, timer: '스마트라이트', material: '플라스틱',
      dims: '23.9 × 10.5 × 25.7', colors: ['화이트', '샌드'], img: 'style-essential.webp',
      naver: 'https://mkt.shopping.naver.com/link/6953828c9ee9dc532374c3c4', official: 'https://www.brita.kr/water-filter-system/style-essential',
      one: '작지만 편의 기능은 다 있는 신형', fit: '냉장고 공간이 좁은데 편한 뚜껑을 원하는 집',
      pros: ['한 손 플립탑·출수구 덮개', '스마트라이트(시간+사용량 추정) 알림'],
      cons: ['정수 1.4L로 2인 가구엔 여전히 작음', "'쿨'은 크기 이름일 뿐 냉각 기능 없음"],
      src: 'S3' },
    { id: 'B03', name: '글라스저그', size: '2.5L', family: '글라스저그', total: 2.5, filtered: 1.5, timer: '스마트라이트', material: '붕규산 유리',
      dims: '19.8 × 13.8 × 27.7', colors: ['라이트블루'], img: 'glass-jug.webp',
      naver: 'https://brand.naver.com/brita_official/products/10603388274', official: 'https://www.brita.kr/water-filter-system/glass-jug',
      one: '유리 물통 — 플라스틱이 꺼려질 때', fit: '물통 소재·외관을 중시하는 집',
      pros: ['물이 고이는 아래 물통이 유리(냄새·착색에 강함)', '식기세척기 사용 가능(50℃ 이하, 스마트라이트 분리)'],
      cons: ['XL보다 2.4배 비싼데 정수 성능은 같은 필터라 동일', '무겁고 깨질 수 있음, 정수 1.5L'],
      src: 'S4 · S10' },
    { id: 'B04', name: '글라스저그 리미티드', size: '2.5L', family: '글라스저그', total: 2.5, filtered: 1.5, timer: '스마트라이트', material: '붕규산 유리 + 실리콘 범퍼',
      dims: '19.8 × 13.8 × 27.7', colors: ['라이트그린'], img: 'glass-jug-limited.webp',
      naver: 'https://brand.naver.com/brita_official', official: 'https://store.brita.com.au/products/limited-edition-glass-2-5l-water-filter-jug',
      one: '60주년 한정 색상 + 바닥 실리콘 범퍼', fit: '유리 저그를 고르면서 색상·범퍼를 원할 때',
      pros: ['바닥 실리콘 범퍼로 미끄럼·충격 완화', '한정판 라이트그린 색상'],
      cons: ['국내 구성의 필터 수가 화면에서 확인되지 않음', '정수 성능은 일반 글라스저그와 동일'],
      src: 'S6' },
    { id: 'B05', name: '마렐라 XL', size: '3.5L', family: '마렐라', total: 3.5, filtered: 2.0, timer: '메모', material: '플라스틱',
      dims: '25.8 × 14.8 × 25.8', colors: ['화이트'], img: 'marella.webp',
      naver: 'https://brand.naver.com/brita_official/products/5776391312', official: 'https://www.brita.kr/water-filter-system/marella',
      one: '오래된 기본형 대용량', fit: '단순한 대용량 저그면 충분한 집',
      pros: ['정수 2.0L', '스타일에센셜 XL과 같은 가격'],
      cons: ['같은 값의 스타일에센셜 XL보다 정수량 0.3L 적고 알림도 단순', '구형 디자인'],
      src: 'S2' },
    { id: 'B06', name: '스타일에센셜 XL', size: '3.6L', family: '스타일에센셜', total: 3.6, filtered: 2.3, timer: '스마트라이트', material: '플라스틱',
      dims: '25.9 × 13.5 × 25.7', colors: ['화이트', '샌드', '스톤블루'], img: 'style-essential.webp',
      naver: 'https://mkt.shopping.naver.com/link/6953828c9ee9dc532374c3c4', official: 'https://www.brita.kr/water-filter-system/style-essential',
      one: '신혼부부 기본값 — 같은 돈에 가장 많이 담김', fit: '2인 가구 대부분',
      pros: ['정수 2.3L — 저그 중 최대, 1L당 본체가 가장 저렴', '스마트라이트·플립탑·출수구 덮개 등 신형 편의 기능', '색상 3종(화이트·샌드·스톤블루)'],
      cons: ['물이 가득 차면 약 3kg 이상 — 한 손 따르기 무거움', '냉장고 선반 높이 25.7cm 확인 필요'],
      src: 'S3' },
    { id: 'B07', name: '플로우', size: '8.2L', family: '플로우', total: 8.2, filtered: 5.2, timer: '메모', material: '플라스틱 탱크',
      dims: '30.4 × 21.4 × 22.0', colors: ['블루'], img: 'flow.webp',
      naver: 'https://brand.naver.com/brita_official/products/5768594007', official: 'https://www.brita.kr/water-filter-system/flow',
      one: '수도꼭지 달린 물탱크', fit: '물을 아주 많이 쓰거나 냉장고에 큰 칸이 있는 집',
      pros: ['정수 5.2L — 하루 한 번만 채우면 됨', '앞쪽 꼭지로 따라 쓰기'],
      cons: ['필터 1개 150L는 동일 → 많이 쓰면 교체가 더 잦아짐', '한국 화면에서는 13개 필터 묶음(110,670원)만 판매', '자리 차지가 큼(30×21cm)'],
      src: 'S5' }
  ],

  /* 필터 2종 */
  filters: [
    { id: 'F-PURE', name: '막스트라 프로 퓨어 퍼포먼스', en: 'PURE PERFORMANCE', img: 'filter-pure.webp',
      naver: 'https://brand.naver.com/brita_official/products/10578307319', official: 'https://www.brita.kr/filters-cartridges/maxtra-pro-pure-performance-valuepack-3-cartridges',
      purpose: '일상 음용·요리, 수돗물 냄새와 물맛 개선',
      does: ['염소(소독약) 냄새·맛 감소', '일부 유기물질 감소', '납·구리 감소', '석회질(경도) 감소', '30μm 이상 입자 걸름'] },
    { id: 'F-LIME', name: '막스트라 프로 라임스케일 엑스퍼트', en: 'LIMESCALE EXPERT', img: 'filter-lime.webp',
      naver: 'https://brand.naver.com/brita_official/products/10578320190', official: 'https://www.brita.kr/filters-cartridges/maxtra-pro-limescale-expert-valuepack-3-cartridges',
      purpose: '석회질 관리 — 전기포트·커피머신·차',
      does: ['퓨어 퍼포먼스의 기능 모두', '석회질 감소 성능 퓨어 대비 +50%(제조사 수치)'] }
  ],
  filterSpec: { liters: 150, weeks: 4, lowUseMonths: '1~2개월', maxMonths: 2 },

  /* 판매 구성 33개 (부록 B와 동일) — total: 전체 필터 수, null=미확정 */
  skus: [
    ['SKU001', 'F', null, '라임스케일 6 + 퓨어 6', null, 6, 6, 12, '사진 판독 추정', 94600, 84140],
    ['SKU002', 'F', null, '퓨어 퍼포먼스 3입', null, 3, 0, 3, '확인', 26500, 22850],
    ['SKU003', 'F', null, '라임스케일 엑스퍼트 6입+6입', null, 0, 12, 12, '확인', 100600, 89600],
    ['SKU004', 'F', null, '라임스케일 3 + 퓨어 4', null, 4, 3, 7, '사진 판독 추정', 59400, 52460],
    ['SKU005', 'F', null, '라임스케일 엑스퍼트 3입+3입', null, 0, 6, 6, '확인', 47400, 41660],
    ['SKU006', 'F', null, '퓨어 퍼포먼스 8입+8입', null, 16, 0, 16, '확인', 117800, 106800],
    ['SKU007', 'F', null, '퓨어 퍼포먼스 4입+4입', null, 8, 0, 8, '확인', 58800, 51920],
    ['SKU008', 'F', null, '라임스케일 엑스퍼트 3입', null, 0, 3, 3, '확인', 25900, 22310],
    ['SKU009', 'F', null, '퓨어 퍼포먼스 4입', null, 4, 0, 4, '확인', 30200, 26180],
    ['SKU010', 'J', 'B04', '글라스저그 리미티드 2.5L', '라이트그린', null, null, null, '수량 미확정', 73900, 64510],
    ['SKU011', 'J', 'B03', '글라스저그 2.5L', '라이트블루', null, null, 5, '확인', 92200, 80980],
    ['SKU012', 'J', 'B03', '글라스저그 2.5L', '라이트블루', null, null, 4, '확인', 87900, 77110],
    ['SKU013', 'J', 'B03', '글라스저그 2.5L', '라이트블루', null, null, 13, '확인', 150600, 131140],
    ['SKU014', 'J', 'B03', '글라스저그 2.5L', '라이트블루', null, null, 1, '확인', 70000, 61000],
    ['SKU015', 'J', 'B02', '스타일에센셜 쿨 2.4L', '화이트', null, null, 1, '확인', 27900, 23110],
    ['SKU016', 'J', 'B06', '스타일에센셜 XL 3.6L', '화이트', null, null, 1, '확인', 30900, 25810],
    ['SKU017', 'J', 'B06', '스타일에센셜 XL 3.6L', '샌드', null, null, 5, '확인', 57100, 49390],
    ['SKU018', 'J', 'B02', '스타일에센셜 쿨 2.4L', '화이트', null, null, 5, '확인', 55100, 47590],
    ['SKU019', 'J', 'B06', '스타일에센셜 XL 3.6L', '화이트', null, null, 5, '확인', 57100, 49390],
    ['SKU020', 'J', 'B06', '스타일에센셜 XL 3.6L + 라임스케일', '스톤블루', null, null, null, '수량 미확정', 44900, 38410],
    ['SKU021', 'J', 'B02', '스타일에센셜 쿨 2.4L', '샌드', null, null, 1, '확인', 27900, 23110],
    ['SKU022', 'J', 'B02', '스타일에센셜 쿨 2.4L (1년팩)', '화이트', null, null, 13, '확인', 113500, 96420],
    ['SKU023', 'J', 'B06', '스타일에센셜 XL 3.6L', '샌드', null, null, 1, '확인', 30900, 25810],
    ['SKU024', 'J', 'B06', '스타일에센셜 XL 3.6L', '스톤블루', null, null, 1, '확인', 30900, 25810],
    ['SKU025', 'J', 'B02', '스타일에센셜 쿨 2.4L', '샌드', null, null, 5, '확인', 55100, 47590],
    ['SKU026', 'J', 'B06', '스타일에센셜 XL 3.6L (1년팩)', '화이트', null, null, 13, '확인', 115500, 98320],
    ['SKU027', 'J', 'B07', '플로우 8.2L (1년팩)', '블루', null, null, 13, '확인', 128500, 110670],
    ['SKU028', 'J', 'B01', '리켈리 2.2L (1년팩)', '화이트', null, null, 13, '확인', 108500, 96500],
    ['SKU029', 'J', 'B05', '마렐라 XL 3.5L (1년팩)', '화이트', null, null, 13, '확인', 115500, 98320],
    ['SKU030', 'J', 'B05', '마렐라 XL 3.5L', '화이트', null, null, 1, '확인', 30900, 25810],
    ['SKU031', 'J', 'B01', '리켈리 2.2L', '화이트', null, null, 1, '확인', 23900, 19510],
    ['SKU032', 'J', 'B01', '리켈리 2.2L', '화이트', null, null, 5, '확인', 50100, 43090],
    ['SKU033', 'J', 'B01', '리켈리 2.2L', '블루', null, null, 1, '확인', 23900, 19510]
  ].map(([id, kind, model, name, color, pure, lime, total, status, sale, member]) =>
    ({ id, kind, model, name, color, pure, lime, total, status, sale, member })),

  /* 한국·유럽 수돗물 비교 (박사 검토서의 수치로 갱신) */
  hardness: [],
  review: null,

  sources: [
    ['S1', '브리타 한국 · 리켈리', 'https://www.brita.kr/water-filter-system/liquelli'],
    ['S2', '브리타 한국 · 마렐라', 'https://www.brita.kr/water-filter-system/marella'],
    ['S3', '브리타 한국 · 스타일에센셜', 'https://www.brita.kr/water-filter-system/style-essential'],
    ['S4', '브리타 한국 · 글라스저그', 'https://www.brita.kr/water-filter-system/glass-jug'],
    ['S5', '브리타 한국 · 플로우', 'https://www.brita.kr/water-filter-system/flow'],
    ['S6', '브리타 호주 · 60주년 글라스저그 한정판', 'https://store.brita.com.au/products/limited-edition-glass-2-5l-water-filter-jug'],
    ['S7', '브리타 한국 · 막스트라 프로 퓨어 퍼포먼스', 'https://www.brita.kr/filters-cartridges/maxtra-pro-pure-performance-valuepack-3-cartridges'],
    ['S8', '브리타 한국 · 막스트라 프로 라임스케일 엑스퍼트', 'https://www.brita.kr/filters-cartridges/maxtra-pro-limescale-expert-valuepack-3-cartridges'],
    ['S9', '브리타 한국 · FAQ', 'https://www.brita.kr/faq'],
    ['S10', 'GS SHOP · 브리타 공식 판매 상세', 'https://www.gsshop.com/prd/prd.gs?prdid=1077980828'],
    ['S11', '브리타 영국 · 글라스저그', 'https://www.brita.co.uk/products/glass-jug']
  ]
};
