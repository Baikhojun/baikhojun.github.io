# UNFADE repository consolidation

`Baikhojun/baikhojun.github.io` is the sole deployment and source-management repository for the `unfade.is-a.dev` domain.

## Sources now managed here

| Published route | Source of truth in this repository | Rebuild action |
| --- | --- | --- |
| `/house/` | `projects/house-guide/` | `python scripts/build_deploy.py` |
| `/cukoo/` | `projects/cuckoo-decoder/` | `python scripts/build_deploy.py` |
| `/tv/` | `projects/cuckoo-decoder/TV/` | `python scripts/build_deploy.py` |
| `/lk1800/` | `lk1800/` | edit directly |

The dated Cuckoo archive folders (`260825/`, `260916/`) are intentionally not imported: the root source tree already contains the current build pipeline, current data, snapshots, and TV source.

## Deployment flow

1. Edit a project source or a published page in this repository.
2. Run `python scripts/build_deploy.py` after changing the house, Cuckoo, or TV source.
3. Review the resulting changes, then commit and push `main`.
4. GitHub Pages serves the same repository through `https://unfade.is-a.dev/`.

## Domain record

The active custom-domain record is `unfade.is-a.dev` with CNAME target `baikhojun.github.io`. The earlier `Baikhojun/register` fork was only used to propose that record and is not part of the runtime or build path.
