# cms-tooling: Steady-State Readiness

Objective
- Ensure the cms-tooling repository is in a stable, production-ready state before adding new features.

Current state (high level)
- Profile-driven destinations implemented (Telnet/FTP) with offline tests.
- Evidence lifecycle groundwork prepared (offline tests and governance scaffolding).
- Runbooks and CI scaffolding present to support a production-grade posture.
- No credentials or secrets stored in code or profiles; credentials read at runtime.

Success criteria (production readiness)
- All unit tests pass in CI for the current scope (profiles, telnet/ftp flows, evidence tooling).
- Offline end-to-end end-to-end tests pass (profile lookup, FTP destination resolution, and basic evidence lifecycle flows) without touching live CMS.
- Production Runbook is published and reviewed.
- A signed/deletion governance flow is wired to receipts and deletions remain guarded by policy.
- No new features are introduced until the production readiness is validated.
- Code remains surgical; no unnecessary refactors introduced.

Gaps to address (prioritized)
- Add a dedicated end-to-end offline suite that exercises plan/create/activate/delete lifecycle with receipts.
- Enhance CI to gate on runbook validation, security checks, and offline tests.
- Strengthen the Runbook with rollback, monitoring hooks, and incident response steps.
- Add explicit tests for edge-cases (invalid profiles, missing keys, malformed evidence, etc.).

Planned next steps
- Publish the production Runbook in cms-tooling and align with cms-git governance.
- Add a lightweight end-to-end offline test harness for lifecycle flows.
- Integrate a lightweight pre-merge gating policy that enforces testing gates before merging to main.
