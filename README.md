# cms-minidisk-provisioning

Build and test the capability that will let CMS tooling satisfy a “create a
folder” request by provisioning a CMS minidisk. CMS has no ordinary host-style
folders: the durable storage unit is a minidisk. This repo owns sizing,
allocation planning, and eventually the guarded provisioning flow; integration
into `cms-tooling` comes only after this capability is tested and working.

## Contents

| Path | Purpose |
| --- | --- |
| `cms_mdisk_directory.py` | Password-safe parser for CP directory MDISK extents and full-pack markers. |
| `test_cms_mdisk_directory.py` | Offline parser tests, including a guard that credentials are not returned. |
| `cms_mdisk_cp.py` | Parser and reconciler for CP `QUERY ALLOC MAP` reserved extents. |
| `test_cms_mdisk_cp.py` | Offline CP-map parsing and reconciliation tests. |
| `cms_mdisk_inventory.py` | Assembles the sanitized v2 planner inventory from captures, geometry, target-volume scope, and explicit reviews. |
| `test_cms_mdisk_inventory.py` | Offline end-to-end inventory assembly and planner test. |
| `cms_mdisk_lifecycle.py` | Signs ownership receipts after verified creation and produces receipt-bound, read-only deletion plans. |
| `test_cms_mdisk_lifecycle.py` | Offline ownership, exact-match, usage-gate, and deletion-plan tests. |
| `cms_mdisk_receipts.py` | Owner-only HMAC key, receipt, and consumed-receipt ledger storage. |
| `test_cms_mdisk_receipts.py` | Offline permission, symlink, signature, and replay tests. |
| `cms_mdisk_plan.py` | Planner: asks for capacity first, then a CMS filemode, and picks a best-fit extent from a recent inventory. |
| `test_cms_mdisk_plan.py` | Offline unit tests. |
| `MINIDISK-PROVISIONING.md` | Scope, inventory contract, and required executor gates. |
| `MINIDISK-PROVISIONING-STATE.md` | Live survey results and remaining source/policy gates. |

## Behaviour

The request must provide the desired capacity first. The planner then finds a
contiguous free extent from the authoritative CP directory's explicit MDISK
allocations, cross-checks the result against CP allocation data and verified
volume geometry, and proposes a minidisk and CMS filemode. Always use the source
CP actually loaded. Current CP queries confirm a MAINT 0600 definition that is
in `M173NEW` but not `USER DIRECT`; the exact loaded source filename remains
unconfirmed.

`parse_directory(source, volume_geometry, identity)` returns a sanitized
directory snapshot: physical extents, full-pack owners, used virtual devices,
and a digest of the input. It never returns source records or directory
passwords. This snapshot is one input to inventory collection, not a complete
plan inventory.

`parse_cp_alloc_map(source)` extracts CP-owned extent ranges.
`reconcile_directory(directory_snapshot, cp_alloc_map)` merges exact duplicate
reservations and refuses unknown volumes, out-of-geometry extents, or partial
overlaps. The reconciled result is still not a planner inventory; active-source
identity, current geometry, and per-volume review are required.

`build_inventory(...)` combines those pieces with `CP QUERY DASD DETAILS`
geometry, requires explicit confirmation of the active-directory identity, and
validates the resulting inventory before it can reach the planner. It checks
consistency only; it cannot prove the confirmation or authenticate the
captures.

`plan_minidisk(filemode, size_mb, inventory, now=None)` returns a proposal,
the proposed `MDISK` statement, and the eventual `FORMAT`/`ACCESS` lines as
review data only. It never connects to CMS, edits a directory, links, formats,
or accesses a disk.

For the future executor, `create_ownership_receipt(...)` can issue a signed
receipt only after creation, CP mapping, FORMAT, and ACCESS are verified.
`plan_minidisk_deletion(...)` accepts only a valid receipt and a fresh inventory
with the exact same MAINT MDISK extent. It also requires fresh evidence that
the disk is detached and has no links, a protected consumed-receipt ledger,
and exact `DELETE MAINT vdev receipt-id` confirmation. It returns a plan only;
it never edits or activates the directory.

It fails closed on:

- source captures older than 15 minutes, future-dated, more than 5 minutes
  apart, incomplete, or not reconciled by digest
- unapproved full-pack owners, unreviewed volumes, or unapproved overlays
- overlapping or out-of-range allocations
- CMS filemodes `S`, `D`, or already-used filemodes
- extents that would start at cylinder zero
- virtual device `0192`

Known system full-pack entries are treated as overlay markers, not as
whole-volume occupancy. Only explicit MDISK/system-reservation intervals count
as occupied; eligible volumes require a review bound to the active-directory
digest, and full-pack overlays require separate approval. Digests and
reconciliation check source references but do not authenticate the collector,
prove normalized allocations match raw source data, or prove which directory
CP loaded.

## Usage

```sh
python3 cms_mdisk_plan.py --inventory inventory.json
python3 -m unittest discover -v
```

Runtime is Python 3.12+ and the standard library only.

## Current limits and integration boundary

Directory changes are made by editing the CP source directory and activating it
with `DIRECTXA`, never in place. The executor must keep a protected backup and a
separate candidate, run `DIRECTXA candidate (EDIT` first, and stop for explicit
approval before non-EDIT activation and again before `FORMAT`.

This repo does not yet create a CMS minidisk. The planner is read-only; the
authoritative directory source, current extent inventory, and candidate-write
path must be established and tested before an executor is enabled. Do not
integrate a “create folder” command into `cms-tooling` until the end-to-end
provisioning flow is tested and its live-operation gates are reviewed.

Deletion is equally not implemented. A future executor must not remove a disk
unless the protected HMAC receipt proves this provisioner created that exact
MAINT vdev and extent. Store the signing key, receipts, and consumed-receipt
ledger in `~/.config/cms-minidisk-provisioning/` with owner-only permissions.
The receipt store rejects permissive files and symlinks. Removing the
directory entry does not erase disk contents; the released extent may later be
reused. Require separate approval before activating a deletion candidate.
Pre-existing minidisks without a valid provisioner receipt are not eligible for
this deletion path.

Live CMS command access and file transfer are provided by the line-mode Telnet
driver and FTP helper in
[mostangrymike/cms-tooling](https://github.com/mostangrymike/cms-tooling).
There is no 3270 path in this project.
