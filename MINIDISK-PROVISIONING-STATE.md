# Minidisk provisioning — live test state (2026-11-15)

Resume point for the direct-directory minidisk work. Read with
`MINIDISK-PROVISIONING.md` and `AGENTS.md`.

## Decision

DirMaint is out. Allocations will be made by editing the CP source directory
(`USER DIRECT`) and activating it with `DIRECTXA`. No DirMaint, SMAPI, or
3270 path is in scope for this task. Access is by line-mode Telnet
(`192.168.200.2:23`) through `cms_telnet_driver.py`, not s3270.

## Confirmed live facts and test result (2026-11-15)

- Telnet driver `probe` reached CMS as MAINT. CMS Level 27.
- `CP QUERY ALLOC`:
  - `M01RES` DRCT total 20 cylinders, 1 in use, **ACTIVE**.
  - `M01S01` SPOOL 10999 cylinders.
  - `M01P01` PAGE 10999 cylinders.
  - `VMCOM1` has no DRCT/SPOOL/PAGE allocation.
- `CP QUERY DASD`: 0123 M01RES, 0124 M01S01, 0125 M01P01, 0126 M01W01,
  0127 VMCOM1, 0128 630RL1.
- `CP QUERY DASD DETAILS` reports all six devices as 3390-0C with exactly
  11000 cylinders. This supersedes the old MDISKMAP geometry.
- Directory source found: **`USER DIRECT` is on minidisk `02CC` (volser
  MNT2CC on VMCOM1), filemode `C` or `P`**. Also present on that disk:
  `USER MDISKMAP P` (392 recs, 2026-10-08), `USER DISKMAP P` (356),
  `M173BAK DIRECT P` (4282, 2026-10-08), `M173NEW DIRECT P` (4283, 2026-10-08),
  `M173NEW MDISKMAP P` (394).
- `USER DIRECT` = 4282 F80 records, dated 2026-09-27 18:20:23.
- `ACCESS 0551 Z` exposes `DIRECTXA MODULE Z2`, `DIRMAP MODULE Z2`, and
  `DISKMAP EXEC Z2`. `STATE DIRECTXA MODULE Z` returns Ready RC0.
- `DIRECTXA M173BAK DIRECT C (EDIT` completed with
  `EOJ DIRECTORY NOT UPDATED` and Ready RC0. This confirms syntax-only
  compilation works after accessing 0551. This was the earlier read-only gate.
- Read-only `CP QUERY ALLOC MAP` reports active DRCT allocation on M01RES at
  cylinders 1–20; SPOOL and PAGE allocations span cylinders 1–10999 on
  M01S01 and M01P01. `CP QUERY DASD` identifies the mounted/CP-owned volumes.
  These CP reservations do not describe the locations of ordinary user MDISKs.
- `CP QUERY VIRTUAL 600` reports vdev 0600 attached R/W from VMCOM1 with 1600
  cylinders. A sanitized in-memory parse of the live `USER DIRECT`,
  `M173BAK DIRECT`, and `M173NEW DIRECT` files found 0600 only in M173NEW; its
  only physical-extent difference from USER DIRECT is the VMCOM1 allocation
  recorded above. This strongly suggests the candidate definition is active,
  but does not prove which source file CP loaded. Treat 0600 as used.
- `CP QUERY MDISK USERID MAINT 0600 LOCATION DIRECT` confirms the active CP
  directory maps MAINT 0600 to VMCOM1, cylinders 6000–7599. This matches
  M173NEW. It confirms the active directory definition, not its source filename.
- `USER DIRECT` and `M173BAK DIRECT` are 4282 F80 records; `M173NEW DIRECT` is
  4283 records. `M173NEW MDISKMAP` shows a MAINT `0600` allocation on VMCOM1
  at cylinders 6000–7599; the `USER MDISKMAP` does not. The candidate was
  previously syntax-checked on 2026-10-08. Its 0600 allocation is currently
  attached to MAINT, so M173NEW or a directory containing the same extent is
  likely active; CP does not identify the source filename.
- The read-only parser processed live `USER DIRECT` and `M173NEW DIRECT` in
  memory using the live geometry and CP allocation map. Both reconciled across
  the six attached volumes. It emitted no source lines or passwords. M173NEW
  includes the active 0600 extent; USER DIRECT does not.
- `parse_cp_dasd_details` was exercised on fresh CP output; the parser,
  directory reader, and CP-map reconciler completed end-to-end for M173NEW
  across all six attached volumes. This is read-only parser validation, not
  approval to allocate any of the free gaps.
- **Approved 50 MiB CMS test minidisk was created and tested.** The protected
  backup is `M50BAK DIRECT C0` (4283 F80 records); the separate candidate is
  `M50NEW DIRECT C1` (4284 F80 records) and is now the active source used for
  this test.
- The only candidate change was
  `MDISK 0601 3390 3331 72 M01W01 W`. `DIRECTXA ... (EDIT` passed without
  updating the directory; non-EDIT `DIRECTXA M50NEW DIRECT C` returned
  `EOJ DIRECTORY UPDATED AND ON LINE`.
- CP confirmed vdev 0601 maps to M01W01 cylinders 3331–3402. CMS formatted 72
  cylinders at BLKSIZE 4096 and label `M50B50`; CMS accessed it as filemode B.
  A scratch file was created, read, erased, and verified absent. The disk is
  empty. Its nominal capacity is 50.625 MiB (72 × 180 × 4096 bytes).
- A signed ownership receipt was issued and stored under
  `~/.config/cms-minidisk-provisioning/receipts/`; key and ledger remain
  owner-only outside the repository.
- The old MDISKMAP reports 455 cylinders for M01S01 and M01P01, while the live
  CP geometry and allocation map report 11000 cylinders and extents through
  cylinder 10999. This resolves the geometry discrepancy; the old map's sizes
  and gap rows are stale and must not be used.
- Freshly issued `TYPE` of the saved `USER MDISKMAP` still carries an
  2026-10-08 map timestamp. It is historical evidence, not a current inventory.
- No `USER DIRECT` on A/F/G/S/T/Y, 0CF1 (CP IPL), 0CF3, 0CFD, 019D/0401/0402
  (only HELPCP files), 0990, 049E, 0600.
- System has 37 `USER` entries.

## Volume/alloc evidence

Historical `USER MDISKMAP P` (DISKMAP output, dated 2026-10-08) reported:

| Volume | Size (cyl) | Full-pack holder | Free gaps |
|--------|-----------:|------------------|-----------|
| M01RES | 10017 | MAINT/CMS1 0123, SYSDUMP1 | 9413–9419 (7), 9440–10016 (577) |
| M01W01 | 3339 | MAINT 0124 | 3331–3338 (8) |
| VMCOM1 | 10017 | PMAINT 0141 | 5936–10016 (4081) |
| 630RL1 | 10017 | MAINT630 0131 | 5959–10016 (4058) |

Those map cylinder counts are stale: `CP QUERY DASD DETAILS` now reports 11000
cylinders for all six attached 3390 volumes. Do not use the old map's geometry
or free-gap rows for a current plan.

Every volume carries a full-pack definition. The planner now models the known
system full-pack owners (`DEFAULT`, `CMS1`, `SYSDUMP1`, `MAINT`, `PMAINT`,
`MAINT630`, `$PAGE$`, `$SPOOL$`) as overlay markers and counts explicit MDISK
extents as occupancy, but a separate per-volume overlay approval is also
required. This is a planner policy only; it does not certify an extent.
Inventory schema v2 requires fresh, hash-linked source captures and eligibility
reviews bound to the active-directory digest, CP allocation evidence must refer
to the same directory digest, and geometry must cover exactly the inventoried
volumes. Those references do not authenticate the collector or prove the
normalized allocations were correctly derived. `CP QUERY ALLOC MAP` locates
CP-owned extents, but not ordinary user-MDISK gaps. Live source/CP allocation
reconciliation now succeeds for the six attached volumes. The exact source
filename remains unverified even though M173NEW matches the active 0600 entry.

## Remaining work

`DIRECTXA` is not a CP command, but its CMS module is available on 0551. It
works after `ACCESS 0551 Z`; the prior `Unknown CP/CMS command` occurred before
that module was in the search order. The one-off live creation used the
user-approved M173NEW base and activated M50NEW. No generic live executor exists
yet; the candidate-building, backup, activation, format, verification, and
receipt workflow must be made repeatable and fail closed before `cms-tooling`
integration.

Deletion remains plan-only. The signed receipt store and matching/link/access
checks are tested offline, but no deletion executor has been tested on CMS.
Keep the test disk attached; do not delete it without a separate explicit
request, fresh detached/unlinked evidence, and a deletion candidate/EDIT review.

## Local artifacts

- `probe_direct_source.py` — removed after the survey; re-create only as a
  disposable scratch probe. It contained no credentials.
- `/tmp/cms-direct/user-direct.txt`, `user-mdiskmap.txt`, `user-diskmap.txt` —
  TYPE captures, mode 600. **`USER DIRECT` contains password material: never
  copy into the repo, never commit, never paste.** Re-download after a reboot.

## Next steps

1. Turn the tested one-off creation sequence into a disabled-by-default live
   executor with fresh inventory, private FTP staging, backup, and candidate
   verification.
2. Add a similarly gated delete executor that only accepts signed receipts and
   consumes the receipt after verified removal.
3. Integrate into `cms-tooling` after repeatable create and delete tests pass.

## Safety

Never modify protected disks, directory entries, or other users without the
exact task authorization. No cleanup or extent release after a failure.
Host success does not prove CMS behavior; report target validation separately.
