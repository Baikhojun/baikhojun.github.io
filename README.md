# UNFADE

The one repository for every tool published at [unfade.is-a.dev](https://unfade.is-a.dev/).

## Published tools

| Route | Purpose | Managed source |
| --- | --- | --- |
| `/house/` | 신혼부부 내집마련 가이드 | `projects/house-guide/` |
| `/cukoo/` | 쿠쿠 밥솥 모델코드 해독기 | `projects/cuckoo-decoder/` |
| `/tv/` | 대형 TV 해독기 | `projects/cuckoo-decoder/TV/` |
| `/lk1800/` | LK1800 매트리스 비교 | `lk1800/` |
| `/plan/`, `/schedule/`, `/m/` | 업무 일정표와 모바일 조회 | repository root |

## Shared design

`css/unfade-shell.css` and `js/unfade-shell.js` provide the shared bright site shell:

- Pretendard + Inter typography
- sticky UNFADE header and project drawer
- one navigation map for every tool
- print-safe hiding of site chrome

The tool interfaces keep their own interaction and print styles, while the surrounding navigation follows the UNFADE design system.

## Build and deploy

Run this after changing the house, Cuckoo, or TV source:

```bash
python scripts/build_deploy.py
```

It rebuilds the current checked-in data only, regenerates the published HTML, and reapplies the shared site shell. Review the diff, commit, and push `main`; GitHub Pages publishes the result to `https://unfade.is-a.dev/`.

See [docs/MIGRATION.md](docs/MIGRATION.md) for the consolidation map and retired repositories.
