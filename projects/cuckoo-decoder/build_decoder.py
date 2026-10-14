# -*- coding: utf-8 -*-
"""
쿠쿠 공식몰(cuckoo.co.kr) 전 카테고리 제품 데이터 + 모델코드 디코더
출처: 사용자 제공 공식몰 카테고리 페이지 (2026-08 기준), 대용량밥솥 제외
"""
import json, csv, re
from collections import Counter, defaultdict

# ============================================================
# 원본 데이터: model | 정가 | 할인가 | 카테고리 | 상태 | 공식설명(키워드)
# 카테고리: TP=트윈프레셔 IH=IH전기압력 PL=전기압력(열판) WM=전기보온
#           LS=저당 AS=올스테인리스 SI=사일런스
# ============================================================
RAW = """
CRP-LHTR0610FWM|598000|350000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FW|598000|350000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FGWM|598000|359000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FGIM|598000|359000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FGBM|598000|359000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FB|598000|350000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FS|598000|470000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FGB|598000||TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FGW|598000||TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR0610FGI|598000||TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FWM|698000|400000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FW|698000|400000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FGWM|698000|419000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FD|698000|400000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FGBM|698000|400000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FGIM|698000|400000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FB|698000|400000|TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FGB|698000||TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FGW|698000||TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-LHTR1010FGI|698000||TP||트윈프레셔;오픈쿠킹;에코스텐커브드내솥
CRP-KHTS1060FD|598000|305000|TP||트윈프레셔;원터치분리형커버;대기전력차단
CRP-KHTS1060FLB|598000|418000|TP||초고압무압취사;분리형커버;풀스테인리스내솥
CRP-KHTS1060FWM|598000|385000|TP||초고압무압취사;분리형커버;에코스텐내솥
CRP-KHTS1060FG|598000||TP||트윈프레셔;원터치분리형커버;대기전력차단
CRP-MHTR0310FW|478000|270000|TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;커브드내솥
CRP-MHTR0310FG|478000|270000|TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;커브드내솥
CRP-NHTR0610FGW|638000|420000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR0610FW|638000|420000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR0610FP|658000|420000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR0610FB|658000|420000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR0610FT|658000|420000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR1010FGW|738000|480000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR1010FW|738000|480000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR1010FP|758000|480000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR1010FB|758000|480000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTR1010FT|758000|480000|TP;SI||미니멀디자인;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHTRNL0610TFGW|648000|500000|TP;SI||심리스디자인;IoT앱연동;트윈프레셔;오토락킹
CRP-NHTRNL1010TFGW|748000|550000|TP;SI||심리스디자인;IoT앱연동;트윈프레셔;오토락킹
CRP-OHTR0610FWM|618000|440000|TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-OHTR0610FIM|618000|440000|TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-OHTR0610FGW|618000||TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-OHTR0610FP|618000||TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-OHTR1010FWM|718000|480000|TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-OHTR1010FIM|718000|480000|TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-OHTR1010FGW|718000||TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-OHTR1010FP|718000||TP;SI||사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-PHTR0610FSM|608000|380000|TP;SI||더헤리티지디자인;사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-PHTR0610FDM|608000|380000|TP;SI||더헤리티지디자인;사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-PHTR0610FWS|608000||TP;SI||더헤리티지디자인;사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-PHTR0610FR|608000||TP;SI||더헤리티지디자인;사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-PHNLTR0610FGW|608000|440000|TP;SI||더헤리티지디자인;사일런트압력시스템;트윈프레셔;오픈쿠킹;코팅무코팅호환
CRP-QHLRNL0610FGW|688000||TP;SI||사일런스큐브
CRP-JHTS0660FS|568000|325500|TP||트윈프레셔;에코스텐내솥;원터치분리형커버;대기전력차단
CRP-JHTS0660FB|568000||TP||트윈프레셔;에코스텐내솥;원터치분리형커버;대기전력차단
CRP-JHTS1060FB|658000|579300|TP||트윈프레셔;에코스텐내솥;원터치분리형커버;대기전력차단
CRP-JHTR1010FD|698000||TP|품절|트윈프레셔;원터치분리형커버;에코스텐커브드내솥;이중모션패킹
CRP-JHTR0610FD|568000||TP|일시품절|트윈프레셔;원터치분리형커버;에코스텐커브드내솥;이중모션패킹
CRP-FHTS0610FB|508000||TP||트윈프레셔;원터치분리형커버;에코스텐내솥;이중모션패킹
CRP-FHTS1010FB|618000|419500|TP||트윈프레셔;원터치분리형커버;에코스텐내솥;이중모션패킹
CRP-UT0610FGW|348000|255000|TP||사일런스어반
CRP-UT0610FGG|348000|289000|TP||사일런스압력시스템;이지오픈핸들;트윈프레셔;오픈쿠킹
CRP-UT1010FGW|378000|315000|TP||사일런트압력시스템;트윈프레셔;오픈쿠킹;히든디스플레이
CRP-UT1010FGG|378000|315000|TP||사일런트압력시스템;트윈프레셔;오픈쿠킹;히든디스플레이
CRP-TT0310FGW|318000|212500|TP||미니멀디자인;히든디스플레이;트윈프레셔;슈퍼쾌속
CRP-TT0310FPP|318000|212500|TP||슈퍼쾌속;엑스월블랙코팅;이지분리형커버
CRP-ST0615FWGM|333000|200000|TP||오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST0615FWSM|333000|200000|TP||오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST0615FGSM|333000|228000|TP||오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST0615FLSM|333000|228000|TP||오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST0615FW|333000|240000|TP||오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST0695FGW|333000||TP||오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST0695FGB|333000||TP||오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1015FGSM|363000|240000|TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1015FWSM|363000|240000|TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1015FWGM|363000|240000|TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1015FLSM|363000|259000|TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1015FW|363000||TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1095FGW|363000||TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1095FGB|363000||TP||트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1010FG|348000|232100|TP|품절|트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-ST1010FGI|363000|239000|TP|품절|트윈프레셔;오픈쿠킹;슈퍼쾌속;냉동보관밥
CRP-JHR0660FD|598000|285000|IH||스테인리스분리형커버;원터치분리형커버;2중모션패킹
CRP-JHR1060FD|718000|305000|IH||스테인리스분리형커버;원터치분리형커버;2중모션패킹
CRP-JHR0610FC|598000|260000|IH||풀스테인리스;원터치분리형커버;에너지아이
CRP-JHR1010FC|718000|290000|IH||풀스테인리스;원터치분리형커버;에너지아이
CRP-JHP0610FG|578000|299000|IH||풀스테인리스;원터치분리형커버;에코스텐내솥
CRP-JHP0610FC|578000||IH||풀스테인리스;원터치분리형커버;에코스텐내솥
CRP-JHP0610FGPS|578000|330000|IH||풀스테인리스;이지분리형커버;에코스텐내솥
CRP-JHP0660FSM|578000|299000|IH||풀스테인리스;원터치분리형커버;에코스텐내솥
CRP-JHP1010FG|698000|380000|IH||풀스테인리스;원터치분리형커버;에코스텐내솥
CRP-JHP1010FC|698000||IH||풀스테인리스;원터치분리형커버;에코스텐내솥
CRP-JHP1010FGPS|698000|360000|IH||풀스테인리스;이지분리형커버;에코스텐내솥
CRP-JHP1060FSM|698000|319000|IH||풀스테인리스;원터치분리형커버;에코스텐내솥
CRP-JHPNL0610GPS|578000|320000|IH||풀스테인리스;에코스텐내솥
CRP-JHPNL1010GPS|698000|360000|IH||풀스테인리스;에코스텐내솥
CRP-JHPFF0610GPS|578000||IH||풀스테인리스;에코스텐내솥;홀더분리형커버
CRP-JHPFF1010GPS|698000||IH||풀스테인리스;에코스텐내솥;홀더분리형커버
CRP-JHF0610FLB|528000||IH||루미다크실버
CRP-JHF1010FLB|638000||IH||루미다크실버
CRP-CHP1010FD|608000|270000|IH||스테인리스분리형커버;패킹워시분리형커버;2중모션패킹
CRP-CHP1060FSM|638000|289000|IH||안과밖모두스테인리스;패킹워시분리형커버;스테인리스내솥
CRP-CHPNL1015FGW|528000|260000|IH||화이트디자인;패킹워시분리형커버;스테인리스내솥
CRP-CHB1060FSM|598000|309000|IH||다이아쉴드내솥;패킹워시분리형커버;안과밖모두스테인리스
CRP-CHB1075FD|578000||IH|면세점|스테인리스분리형커버;패킹워시분리형커버;에너지아이
CRP-DHP0610FD|468000|265000|IH||풀스테인리스;2중모션패킹;패킹워시분리형커버
CRP-DHP0610FW|488000|265000|IH||화이트디자인;패킹워시분리형커버;스테인리스내솥
CRP-DHP0660FSM|488000|269000|IH||안과밖모두스테인리스;패킹워시분리형커버;스테인리스내솥
CRP-DHPNL0615FGW|488000|230000|IH||에코스텐내솥;2중모션패킹;패킹워시분리형커버
CRP-DHPNL0615FGG|488000|258000|IH||에코스텐내솥;2중모션패킹;패킹워시분리형커버
CRP-DHPFF0615FGW|488000||IH||에코스텐내솥;2중모션패킹;패킹워시분리형커버
CRP-DHXB0610FS|458000|247000|IH||패킹워시분리형커버;2중모션패킹
CRP-DHR0610FS|498000||IH||풀스테인리스;패킹워시분리형커버;2중모션패킹
CRP-DHB0660FT|478000||IH||스테인리스분리형커버;패킹워시분리형커버;에너지아이
CRP-DHB0660FDM|478000|259000|IH|품절|스테인리스분리형커버;패킹워시분리형커버;2중모션패킹
CRP-DHASNL0615FGW|488000|280000|IH;AS||올스테인리스
CRP-FHS0610FD|508000|260000|IH||에너지아이;패킹워시분리형커버;초고압2기압;이중모션패킹
CRP-FHS0610FG|508000|260000|IH||에너지아이;패킹워시분리형커버;초고압2기압;이중모션패킹
CRP-FHS0610FMG|508000|299000|IH||에코스텐내솥;패킹워시분리형커버;에너지아이
CRP-FHS1010FD|668000|300000|IH||에너지아이;패킹워시분리형커버;초고압2기압;이중모션패킹
CRP-FHS1010FG|668000|300000|IH||에너지아이;패킹워시분리형커버;초고압2기압;이중모션패킹
CRP-FHS1010FMG|668000|334000|IH||에코스텐내솥;패킹워시분리형커버;에너지아이
CRP-FHR0610FS|528000|420000|IH||스테인리스내솥;이중모션패킹;에너지아이;초고압2기압
CRP-FHR107FD|658000||IH||스테인리스내솥;이중모션패킹;에너지아이;초고압2기압
CRP-FHXB0610FD|478000|296400|IH||다이아쉴드내솥;이중모션패킹;에너지아이;초고압2기압
CRP-FHB0610FD|458000|378000|IH||스테인리스내솥;이중모션패킹;에너지아이
CRP-FHB0610EL|468000||IH||스테인리스분리형커버;패킹워시분리형커버;2중모션패킹
CRP-EHS0320FB|418000|260000|IH||2기압;풀스테인리스내솥;엑스월블랙샤인코팅
CRP-EHS0320FGW|418000||IH||스마트알고리즘;논스톱스팀배출;현미발아기능
CRP-MHR0310FW|478000|260000|IH||슈퍼쾌속;에코스텐커브드내솥;풀스테인리스분리형커버
CRP-LHR0610FGW|578000|399000|IH||2중모션패킹;에코스텐커브드내솥
CRP-LHR1010FGW|678000|459000|IH||패킹워시분리형;2중모션패킹;에코스텐커브드내솥
CRP-BHF0670FD|408000|252000|IH||이지분리형커버;이중모션패킹;타철명장엑스월내솥
CRP-AHF1020FD|488000||IH||분리형커버;이중모션패킹;타철명장내솥
CRP-AHF1060FD|458000|236700|IH||이지분리형커버;이중모션패킹;타철명장엑스월내솥
CRP-AHP1010FD|488000|340000|IH||분리형커버;이중모션패킹;스테인리스내솥
CRP-AHXB1060FD|478000|252000|IH||스테인리스분리형커버;패킹워시분리형커버;2중모션패킹
CRP-BDHF065BD|458000|378800|IH||스테인리스분리형커버;패킹워시분리형커버;에너지아이
CRP-BDHF067FW|458000||IH||타철명장;분리형커버;스마트알고리즘
CRP-BCHF107FW|598000||IH||타철명장;분리형커버;스마트알고리즘
CRP-HQB0310FS|298000|170000|IH||분리형커버;다이아쉴드코팅내솥;자동살균세척
CRP-HUF105SDB|338000|229000|IH||스테인리스분리형커버;타철명장엑스월블랙코팅내솥
CRP-HUF10BS|338000|214200|IH||
CRP-HUF1080BE|338000||IH||
CRP-HVB06BS|318000|290000|IH||
CRP-HVB0680BE|318000||IH||
CRP-HWF1060FB|398000||IH||
CRP-HWF1060FS|398000|294000|IH||
CRP-P1055FD|233000|170000|PL||
CRP-P0620FDM|223000||PL||
CRP-P1015FBB|223000|178000|PL||14중안전장치;자동살균스팀세척;엑스월블랙코팅내솥
CRP-P0660FD|223000|219000|PL|품절|
CRP-P0610FT|223000|208000|PL|품절|
CRP-PK0610BGI|223000|155000|PL||2중모션패킹;엑스월블랙코팅내솥;이지분리형커버
CRP-PK0620BS|223000||PL||이지분리형커버;다양한메뉴;엑스월블랙코팅내솥
CRP-PK0620BUG|223000||PL||2중모션패킹;엑스월블랙코팅내솥;이지분리형커버
CRP-R1025FBS|293000|219000|PL||풀스테인리스분리형커버;2중모션패킹;엑스월다이아몬드코팅
CRP-R1015FBB|293000||PL||
CRP-R1095FGW|293000||PL||
CRP-R0695FGW|263000||PL||
CRP-R0625FBB|263000||PL||
CRP-R0615FWS|263000||PL||풀스테인리스분리형커버;2중모션패킹;스테인리스재질
CRP-R0615FBS|269000||PL||간편분리세척;풀스테인리스분리형커버;엑스월다이아몬드코팅
CRP-RK0615FWS|253000|160000|PL||
CRP-QK1010BGW|243000||PL||
CRP-QKNL1010BGB|243000|165000|PL||
CRP-QKNL1010BGW|243000||PL||
CRP-T0310FGW|268000|200000|PL||슈퍼쾌속;엑스월블랙코팅내솥;이지분리형커버
CR-0375FW|109000|71400|WM||에그밥솥
CR-0675FW|119000|73500|WM||에그밥솥
CR-0155MW|79000|44700|WM||소담밥솥1인용
CR-0155MG|79000|44700|WM||소담밥솥1인용
CR-0215MW|109000|66900|WM||마시멜로2인용;논스틱코팅내솥;분리형커버
CR-0215MV|109000|53600|WM||마시멜로2인용;논스틱코팅내솥;분리형커버
CR-0215MP|109000|66900|WM||마시멜로2인용;논스틱코팅내솥;분리형커버
CR-0365FR|93000|64100|WM||
CR-0655FR|104000|70000|WM||
CR-1055B|79000||WM||
CR-0485GW|139000|79000|WM||논스틱코팅내솥;미니멀심리스디자인
CR-0685GW|149000||WM||논스틱코팅내솥;간편분리형커버
CR-0685GWM|149000|79000|WM||미니멀심리스디자인;논스틱코팅내솥;간편분리형커버
CR-0415MW|139000|89000|WM||스퀘어보온밥솥
CR-3515GG|239000|169000|WM||대용량35인용
CRP-LHLR0610FW|618000|389000|LS||초고압무압취사;에코스텐커브드내솥;저당질밥
CRP-LHLR0610FGWM|618000|380000|LS||당질저감;이중모션밸브;에코스텐커브드내솥
CRP-LHLR1010FW|718000|430000|LS||초고압무압취사;당질저감;풀스테인리스분리형커버
CRP-LHLR1010FGWM|718000|430000|LS||당질저감;이중모션밸브;에코스텐커브드내솥
CRP-KHLR1010FGW|678000||LS||초고압무압취사;당질저감;풀스테인리스분리형커버
CRP-OHNLLR0610FGW|638000|500000|LS;SI||4세대저당밥솥;사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-OHNLLR1010FGW|738000|550000|LS;SI||4세대저당밥솥;사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-OHFFLR0610FGW|638000||LS;SI||저속노화밥모드;사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-OHFFLR1010FGW|718000||LS;SI||저속노화밥모드;사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-PHNLLR0610FGW|628000|490000|LS;SI||저속노화밥모드;사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-PHFFLR0610FGW|628000||LS;SI||저속노화밥모드;사일런트압력시스템;트윈프레셔;오픈쿠킹
CRP-NHNLLR0610FGW|658000|550000|LS;SI||저속노화밥모드;사일런트압력시스템;트윈프레셔;오토락킹
CRP-NHFFLR0610FGW|748000||LS;SI||저속노화밥모드;사일런트압력시스템;트윈프레셔;오토락킹
CRP-DHAS069FW|528000|310000|AS||올스테인리스;수비드기능;패킹워시분리형커버
CRP-DHAS069FWM|528000|310000|AS||올스테인리스;수비드기능;패킹워시분리형커버
CRP-DHAS069FB|528000|285000|AS||올스테인리스;수비드기능;패킹워시분리형커버
CRP-CHAS109FW|598000|310000|AS||올스테인리스;수비드기능;패킹워시분리형커버
CRP-CHAS109FB|598000|310000|AS||올스테인리스;수비드기능;패킹워시분리형커버
CRP-CHAS109FWM|598000|300000|AS||올스테인리스;수비드기능;패킹워시분리형커버
CRP-FHTAS0610FW|548000|310000|AS;TP||트윈프레셔;올스테인리스내솥
CRP-FHTAS1010FW|658000|340000|AS;TP||트윈프레셔;올스테인리스내솥
CRP-KHTAS1010FWM|618000|367500|AS;TP||초고압무압취사;분리형커버;올스테인리스내솥
CRP-LHTAR0610FGI|789000||AS;TP||마스터셰프;트윈프레셔;올스테인리스내솥
CRP-LHTAR1010FGI|890000||AS;TP||마스터셰프;트윈프레셔;올스테인리스내솥
"""

# ============================================================
# 디코더 테이블
# ============================================================
DESIGN_IH = {  # [글자]+H 형태 = 신형 명명 (2018~)
    "AH": "A형(구형)", "BH": "B형(구형)", "CH": "C형(10인용 주력)",
    "DH": "D형(6인용 주력)", "EH": "E형(3인용 전용)", "FH": "F형(중상급)",
    "JH": "J형(중급)", "KH": "K형(트윈프레셔)", "LH": "L형(마스터셰프)",
    "MH": "M형(쁘띠/소용량)", "NH": "N형(사일런스)", "OH": "O형(사일런스 오브제)",
    "PH": "P형(사일런스 프로)", "QH": "Q형(사일런스 큐브)",
    "BDH": "BD형(타철명장)", "BCH": "BC형(타철명장)",
}
DESIGN_IH_OLD = {  # H+[글자] 형태 = 구형 명명 (~2018)
    "HQ": "HQ형(구형)", "HU": "HU형(구형)", "HV": "HV형(구형)",
    "HW": "HW형(구형)", "HM": "HM형(구형)",
}
GROUP_PLATE = {  # 열판(비IH) 그룹. (표기, 트윈프레셔여부, 설명)
    "ST": (True,  "더 라이트 (열판 트윈프레셔)"),
    "UT": (True,  "사일런스 어반 (열판 트윈프레셔)"),
    "TT": (True,  "트윈프레셔 미니 (3인용)"),
    "RT": (True,  "열판 트윈프레셔"),
    "QK": (False, "Q형 열판압력"),
    "PK": (False, "P형 열판압력"),
    "RK": (False, "R형 열판압력"),
    "P":  (False, "P형 열판압력"),
    "R":  (False, "R형 열판압력"),
    "T":  (False, "미니 열판압력 (3인용)"),
}
POT = [  # 긴 것부터 매칭
    ("AS", "올스테인리스 무코팅(와이드앤플랫)", 5),
    ("AR", "올스테인리스 무코팅(라운드/커브드)", 5),
    ("XB", "일반 코팅(다이아 계열)", 1),
    ("R",  "투톤코팅 + 라운드(커브드)", 4),
    ("S",  "하단 투톤코팅(에코스텐)", 3),
    ("P",  "스테인리스 외피 코팅내솥", 2),
    ("B",  "일반 코팅(다이아쉴드/블랙)", 1),
    ("F",  "타철명장/플랫 계열(구형)", 1),
]
VARIANT = {"NL": "구세대 변형 코드(의미 미확정)", "FF": "신세대 변형 코드(의미 미확정)"}
DISPLAY = {"F": "LCD(퍼지) 디스플레이", "S": "일반 숫자/램프 표시",
           "B": "버튼식/일반 표시", "M": "구형 소형 표시(추정)", "G": "미확정"}
COLOR = {
    "W": "화이트", "S": "실버", "B": "블랙", "D": "다크실버/다크그레이",
    "G": "그레이", "P": "핑크", "T": "테라코타", "R": "로즈/레드",
    "C": "캐비어블루", "GW": "그레이스화이트", "GB": "그레이스블랙",
    "GI": "그레이스아이보리", "GG": "어반그레이", "MG": "메탈릭그린",
    "LB": "루미다크실버/루미블랙", "GPS": "그레이스핑크실버",
    "WS": "화이트스톤", "BS": "블랙실버", "BB": "블랙브라운",
    "WG": "화이트그레이", "GS": "그레이실버", "LS": "루미실버",
    "BE": "베이지(추정)", "BD": "블랙다크(추정)", "EL": "미확정",
    "BGI": "블랙그레이아이보리(추정)", "BUG": "미확정", "PP": "핑크",
    "SDB": "미확정", "FR": "미확정", "I": "아이보리", "GPS": "그레이스핑크실버",
    "DB": "다크블랙(추정)", "E": "미확정", "UG": "미확정", "V": "바이올렛(추정)",
    "WM": "화이트무광(추정)", "PS": "핑크실버",
}
CAPACITY = {"01":1,"02":2,"03":3,"04":4,"06":6,"08":8,"10":10,"35":35}

def decode(model):
    r = {"model": model, "flags": [], "confidence": "high"}
    m = model.replace(" ", "").upper()
    m = re.sub(r"\(.*?\)$", "", m)

    if m.startswith("CRP-"):
        r["pressure"] = "압력식"; core = m[4:]
    elif m.startswith("CR-"):
        r["pressure"] = "비압력(보온)"; core = m[3:]
    else:
        r["flags"].append("접두사 인식 실패"); r["confidence"]="fail"; return r

    mnum = re.search(r"\d", core)
    if not mnum:
        r["flags"].append("숫자 블록 없음"); r["confidence"]="fail"; return r
    letters, rest = core[:mnum.start()], core[mnum.start():]

    # --- 비압력 계열: 문자 블록 없음
    if r["pressure"].startswith("비압력"):
        r["design"] = "-"; r["heating"] = "비압력(열판 보온)"
        r["twin_pressure"] = False; r["low_sugar"] = False
        r["pot_code"] = "-"; r["pot"] = "논스틱 코팅(일반)"; r["pot_grade"] = 0
        r["variant"] = ""
    else:
        # --- 디자인 + 가열방식
        design = heat = None
        if letters[:3] in DESIGN_IH:
            design, heat, letters = DESIGN_IH[letters[:3]], "IH", letters[3:]
        elif letters[:2] in DESIGN_IH:
            design, heat, letters = DESIGN_IH[letters[:2]], "IH", letters[2:]
        elif letters[:2] in DESIGN_IH_OLD:
            design, heat, letters = DESIGN_IH_OLD[letters[:2]], "IH", letters[2:]
            r["flags"].append("구형 명명체계(H가 앞)")
        else:
            for g in sorted(GROUP_PLATE, key=len, reverse=True):
                if letters.startswith(g):
                    tw, desc = GROUP_PLATE[g]
                    design, heat, letters = desc, "열판", letters[len(g):]
                    r["_plate_twin"] = tw
                    break
        if design is None:
            r["flags"].append(f"디자인 코드 미등록: {letters}")
            r["confidence"] = "low"; design, heat = f"미상({letters})", "미상"
            letters = ""
        r["design"], r["heating"] = design, heat

        # --- 변형 코드 NL / FF 제거
        var = ""
        for v in VARIANT:
            if v in letters:
                var = v; letters = letters.replace(v, "", 1)
        r["variant"] = var

        # --- 특수기능 T(트윈프레셔) / L(저당)
        tw = r.pop("_plate_twin", False)
        ls = False
        if letters.startswith("T"):
            tw = True; letters = letters[1:]
        elif letters.startswith("L"):
            ls = True; tw = True; letters = letters[1:]
        r["twin_pressure"], r["low_sugar"] = tw, ls

        # --- 내솥
        pot = None
        for code, name, grade in POT:
            if letters.startswith(code):
                pot = (code, name, grade); letters = letters[len(code):]
                break
        if pot:
            r["pot_code"], r["pot"], r["pot_grade"] = pot
        else:
            r["pot_code"], r["pot"], r["pot_grade"] = "-", "미표기(기본 코팅)", 0
        if letters:
            r["flags"].append(f"미해독 문자: {letters}"); r["confidence"]="low"

    # --- 숫자: 용량 + 유통
    mnum2 = re.match(r"(\d+)", rest)
    digits, tail = mnum2.group(1), rest[mnum2.end():]
    cap = digits[:2]
    r["capacity"] = CAPACITY.get(cap, None)
    if r["capacity"] is None:
        r["flags"].append(f"용량 코드 미상: {cap}"); r["confidence"]="low"
    r["dist_code"] = digits[2:]

    # --- 꼬리: 표시창 + 색상 + 서픽스
    suffix = ""
    if len(tail) > 2 and tail.endswith("M") and tail[:-1] not in COLOR:
        suffix, tail = "M", tail[:-1]
    r["suffix"] = suffix
    if tail and len(tail)>1 and tail[0] in DISPLAY and tail[1:] in COLOR:
        r["display_code"]=tail[0]; r["display"]=DISPLAY[tail[0]]
        r["color_code"]=tail[1:]; r["color"]=COLOR[tail[1:]]
    elif tail and tail in COLOR:
        r["display_code"] = "-"; r["display"] = "표시창 코드 생략"
        r["color_code"] = tail; r["color"] = COLOR[tail]
        r["flags"].append("표시창 코드 생략형")
    elif tail:
        r["display_code"] = tail[0]
        r["display"] = DISPLAY.get(tail[0], "미상")
        ccode = tail[1:]
        r["color_code"] = ccode
        r["color"] = COLOR.get(ccode, "미등록")
        if ccode and ccode not in COLOR:
            r["flags"].append(f"색상 코드 미등록: {ccode}")
    else:
        r["display_code"] = r["display"] = r["color_code"] = r["color"] = "-"
    if r["flags"] and r["confidence"] == "high":
        r["confidence"] = "medium"
    return r

# ============================================================
# 실행
# ============================================================
rows, seen = [], {}
for line in RAW.strip().split("\n"):
    p = line.split("|")
    model, lp, sp, cats, status, desc = p[0], p[1], p[2], p[3], p[4], p[5]
    if model in seen:
        seen[model]["categories"] = sorted(set(seen[model]["categories"] + cats.split(";")))
        continue
    d = decode(model)
    d["list_price"] = int(lp) if lp else None
    d["sale_price"] = int(sp) if sp else None
    d["discount_rate"] = round((1 - int(sp)/int(lp))*100) if (lp and sp) else None
    d["categories"] = cats.split(";")
    d["status"] = status or "판매중"
    d["official_features"] = desc.split(";") if desc else []
    rows.append(d); seen[model] = d

print(f"총 제품 수: {len(rows)}")
print("신뢰도:", Counter(r["confidence"] for r in rows))
print("\n[미해독/경고 발생 모델]")
for r in rows:
    if r["flags"]:
        print(" ", r["model"], "->", r["flags"])

print("\n[가열방식 분포]", Counter(r["heating"] for r in rows))
print("[내솥 분포]", Counter(r["pot_code"] for r in rows))
print("[변형코드 분포]", Counter(r.get("variant","") for r in rows))
print("[용량 분포]", Counter(r["capacity"] for r in rows))

# 할인율 통계
dr = [r["discount_rate"] for r in rows if r["discount_rate"] is not None]
print(f"\n[할인율] n={len(dr)} 평균 {sum(dr)/len(dr):.1f}% 최소 {min(dr)}% 최대 {max(dr)}%")

with open("/home/claude/out/cuckoo-products.json","w",encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

cols = ["model","pressure","design","heating","twin_pressure","low_sugar",
        "pot_code","pot","pot_grade","variant","capacity","dist_code",
        "display","color_code","color","suffix","list_price","sale_price",
        "discount_rate","categories","status","confidence"]
with open("/home/claude/out/cuckoo-products.csv","w",encoding="utf-8-sig",newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in rows:
        w.writerow([("|".join(r[c]) if isinstance(r.get(c),list) else r.get(c,"")) for c in cols])
print("\n저장 완료")
