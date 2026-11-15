# cms-minidisk-provisioning

Read-only planning for a MAINT CMS minidisk on z/VM, plus the notes for a
future guarded executor.

## Contents

| Path | Purpose |
| --- | --- |
| `cms_mdisk_plan.py` | Planner: prompts for a CMS filemode and size in MiB, then picks a best-fit extent from a recent inventory. |
| `test_cms_mdisk_plan.py` | Offline unit tests (7). |
| `MINIDISK-PROVISIONING.md` | Scope, inventory contract, and required executor gates. |
| `MINIDISK-PROVISIONING-STATE.md` | Live survey results and the current `DIRECTXA` blocker. |

## Behaviour

`plan_minidisk(filemode, size_mb, inventory, now=None)` returns a proposal,
the proposed `MDISK` statement, and the eventual `FORMAT`/`ACCESS` lines as
review data only. It never connects to CMS, edits a directory, links, formats,
or accesses a disk.

It fails closed on:

- inventory older than 15 minutes, future-dated, or incomplete
- full-pack or ineligible volumes
- overlapping or out-of-range allocations
- reserved or already-used CMS filemodes
- virtual device `0192`

## Usage

```sh
python3 cms_mdisk_plan.py --inventory inventory.json
python3 -m unittest -v test_cms_mdisk_plan
```

Runtime is Python 3.12+ and the standard library only.

## Deliberate limits

Directory changes are made by editing the CP source directory and activating it
with `DIRECTXA`, never in place. The executor must keep a protected backup and a
separate candidate, run `DIRECTXA candidate (EDIT` first, and stop for explicit
approval before non-EDIT activation and again before `FORMAT`.

Live CMS access and file transfer are not implemented here. Use the line-mode
Telnet driver and FTP helper in
[mostangrymike/cms-tooling](https://github.com/mostangrymike/cms-tooling).
There is no 3270 path in this project.
