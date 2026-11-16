# MAINT minidisk provisioning

## Scope

CMS has no ordinary host-style folders. The “create folder” user request must
first supply the desired capacity; the implementation then provisions a
CMS-formatted minidisk and accesses it using a CMS filemode. This repository is
where that capability is designed and proven before a “create folder” command
is integrated into `cms-tooling`.

`cms_mdisk_plan.py` is currently read-only. It asks for requested size in MiB
first, then a CMS filemode; given those and a recent
`cms-minidisk-inventory-v2` snapshot, it proposes one MAINT 3390 minidisk. It
does not connect to CMS, edit a directory, issue `DIRECTXA`, format, link, or
access a minidisk.

`cms_mdisk_directory.py` parses CP directory text into a sanitized snapshot of
3390 MDISK extents, full-pack owners, and used virtual devices. It discards
password fields and never returns a source line. The snapshot is not a complete
planner inventory: CP allocation evidence, current volume geometry, active
directory identity, and per-volume policy review must still be collected and
reconciled.

`cms_mdisk_cp.py` parses `CP QUERY ALLOC MAP` and merges its CP-owned extents
with directory allocations. It deduplicates exact matches, adds CP-only
reservations, and refuses partial overlaps or extents outside the supplied
geometry. CP's map describes CP-owned extents; it does not locate ordinary
user-MDISK gaps.

`cms_mdisk_inventory.py` combines the directory snapshot, CP map,
`CP QUERY DASD DETAILS` geometry, capture times, and explicit volume reviews
into the planner's v2 inventory. It requires an explicit caller confirmation
that the directory identity is active. That confirmation is an operator
assertion, not a machine-verifiable fact; CP queries the loaded allocation
definitions but does not report the source filename.

Live work in this tree uses line-mode Telnet for commands
(`cms_telnet_driver.py`) and FTP for file transfer. There is no 3270 path.

The plan includes a hash of the inventory and plan. A later provisioning stage
must require that exact plan hash before it changes CMS state. Use the directory
CP actually loaded, not a filename assumption. Although `USER DIRECT` was the
intended source, active CP queries show the MAINT 0600 definition that is present
in `M173NEW` but absent from `USER DIRECT`; the source filename remains
unconfirmed. Find free extents from all explicit MDISK allocations in the
confirmed active directory, then reconcile them against CP allocation evidence
and verified volume geometry. Never infer free space from `DIRMAP` alone. The
chosen directory-update method is `DIRECTXA`; no activation or format executor
exists yet.

## Inventory contract

The planner requires one complete snapshot containing:

- Capture time with timezone, no more than 15 minutes old.
- Complete active CP directory, CP allocation-map, and physical-volume geometry
  evidence, each with its own capture time and SHA-256 digest. All captures
  must be within 5 minutes of one another.
- Reconciliation records linking the captured directory, CP allocation, and
  geometry digests. CP allocation evidence must identify the same active
  directory digest; geometry evidence must name exactly the inventoried
  volumes. The directory source must have an explicit identity.
- An administrator-reviewed MAINT virtual-address allowlist.
- Current used virtual addresses, accessed filemodes, and reserved filemodes.
- Each volume's verified cylinder count, 3390 4-KiB block geometry, all
  full-pack owners, and every explicit MDISK/system-reservation interval.
- For every eligible volume, a review bound to the active-directory digest;
  eligible full-pack volumes also need separate overlay approval.

Full-pack definitions owned by the known system overlay users (`DEFAULT`,
`CMS1`, `SYSDUMP1`, `MAINT`, `PMAINT`, `MAINT630`, `$PAGE$`, `$SPOOL$`) are
markers, not exclusive reservations. The inventory must omit each marker's
whole-volume interval while retaining every explicit MDISK extent. Unknown
full-pack owners, ineligible or unreviewed volumes, unapproved full-pack
overlays, overlapping intervals, stale or unreconciled evidence, a proposed
extent starting at cylinder zero, CMS filemodes `D` and `S`, and CP virtual
address `0192` fail closed. The planner selects the smallest fitting
contiguous extent. It emits a proposed `MDISK` statement and the future
`FORMAT`/`ACCESS` lines only as review data.

Do not create this inventory from `DIRMAP` alone. Existing project evidence
shows that `DIRMAP` can omit full-pack overlaps and assume geometry that differs
from CP. The inventory collector must reconcile the active directory,
`CP QUERY ALLOC MAP`, and verified volume geometry. `CP QUERY ALLOC` is an
aggregate consistency check; it does not establish the location of a free
extent by itself. Hash and reconciliation fields check source references and
consistency; they do not authenticate the collector or prove that the
normalized allocations were correctly derived from the raw source or that the
named directory was loaded. That still requires independent live verification.

The directory parser has been exercised against the saved `USER DIRECT` text
only as a syntax check. That capture is historical and contains password
material; it remains outside the repository. Parsing it does not establish that
`USER DIRECT` is the directory CP currently has loaded.

## Future agentic executor

The executor must be a separate, disabled-by-default capability. It must:

1. Recollect inventory and reject stale or changed plan hashes.
2. Confirm the chosen directory source and unique backup target.
3. Create a protected backup and separate candidate; never edit the active
   directory in place.
4. Insert exactly one MAINT MDISK line and run `DIRECTXA candidate (EDIT`.
5. Stop for explicit approval before non-EDIT `DIRECTXA`.
6. Verify CP location and directory mapping before `CP LINK`.
7. Stop for a second explicit, plan-bound approval before destructive `FORMAT`.
8. Verify formatted geometry, label, and CMS `ACCESS` mode afterward.
9. Only after every creation check passes, sign and persist an ownership receipt
   binding the plan hash to the exact owner, vdev, volume, and extent.

No cleanup or extent release runs automatically after failure. Preserve
candidate, backup, and partial target for review.

## Deleting a provisioner-created minidisk

`cms_mdisk_lifecycle.py` only plans deletion; no delete executor exists. It will
accept only a valid HMAC-signed receipt issued after this provisioner verified
creation. It then requires a fresh active-directory inventory with exactly the
same MAINT vdev and physical extent, current CP evidence that the disk is
detached and has no links, a non-consumed receipt ID, and the exact confirmation
`DELETE MAINT <vdev> <receipt-id>`.

This does not authorize deleting pre-existing disks. A disk without a valid
receipt from a successful run of this provisioner is ineligible, even if it is
owned by MAINT or its extent appears unused.

The deletion plan removes only that MDISK from a separate directory candidate.
It never formats or erases the disk. Removing the definition makes its contents
inaccessible and allows the physical extent to be reused, which may overwrite
them. The candidate still requires `DIRECTXA ... (EDIT`, backup, and separate
approval before activation. After verified deletion, the executor must mark
the receipt consumed in a protected local ledger so it cannot be replayed.

`cms_mdisk_receipts.py` stores the signing key, receipt files, and
consumed-receipt ledger in `~/.config/cms-minidisk-provisioning/`, requiring
owner-only files and directories and refusing symlinks. Receipt signatures
establish that this local provisioner issued the receipt; they do not replace
fresh CP and directory checks.

## Similar projects and preferred interface

The closest public implementation is IBM's
[zvm_ansible_collection](https://github.com/IBM/zvm_ansible_collection):
`zvm_minidisk.py` calls SMAPI `Image_Disk_Create_DM` /
`Image_Disk_Delete_DM` through Feilong `smcli`. It needs an authorized Linux
management guest, zthin, SMAPI, and a configured directory manager. Its
optional formatting path runs Linux `dasdfmt`; that is not the right formatter
for this CMS minidisk.

IBM's native [DirMaint `AMDISK`](https://www.ibm.com/docs/en/zvm/7.2.0?topic=tasks-step-managing-users)
is a closer fit for MAINT: `AUTOG`, `AUTOR`, or `AUTOV` allocates from its
configured EXTENT CONTROL group, region, or volume. IBM describes DirMaint as
performing allocation checks and managing directory transactions. The
[SMAPI `Image_Disk_Create_DM`](https://www.ibm.com/docs/en/zvm/7.3.0?topic=interfaces-image-disk-create-dm)
API can create a CMS-formatted disk and may finish asynchronously; callers must
poll the operation ID.

IBM Cloud Infrastructure Center also allocates from configured DirMaint DASD
groups, but brings a much larger cloud-management stack. VMLINK only automates
links to already-authorized disks; it does not allocate extents.

The direct-directory `DIRECTXA` route is the chosen method for this project;
DirMaint and SMAPI are out of scope. Do not write a candidate until the active
directory source, current allocations, and protected backup procedure are
established. The existing `USER DIRECT` and `M173NEW` records do not yet prove
which directory CP loaded or a currently available extent.

## Current target boundary

The repository's saved records do not prove a currently free extent. Fresh
`USER MDISKMAP` and CP allocation totals are useful cross-checks, but do not
replace reconciling the exact active directory and every explicit extent.
End-to-end execution and later `cms-tooling` integration require separate
qualification; this planner makes no target change.
