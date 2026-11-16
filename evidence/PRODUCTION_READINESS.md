# Production Readiness – cms-git

This document outlines the current production-readiness status for the cms-git component and the remaining gaps to reach production-grade readiness.

1) Scope and governance
- The codebase now includes evidence schema and tools, and a lightweight governance model for evidence artifacts.
- Deletion workflows are offline/receipt-gated; no destructive actions will run without explicit, signed gates.

2) Current maturation state
- Evidence tooling: cms-git/evidence_schema.py, cms-git/evidence_tools.py, with tests (test_evidence.py).
- Profile-driven destinations implemented on cms-tooling side; credentials remain runtime-sourced.
- No hard-coded credentials in code or profile files.
- Tests exist for the new features and offline end-to-end coverage for profile usage.
- Documentation and Runbooks: Runbooks exist for profiles and a basic production-readiness narrative; no formal production-approved Runbook published yet.

3) Gaps to production
- CI/CD coverage for cms-git evidence tools (unit tests only; no end-to-end live flows in CI).
- Production Runbook with explicit rollback, incident response, and monitoring integration.
- End-to-end lifecycle coverage (plan/create/activate/delete) in a production-style pipeline with mocked CMS.
- Formal security review of evidence pipeline (signing/validation/ledger) and access controls.
- Monitoring hooks and alerting for failures in the evidence lifecycle.
- Documentation: consolidated production-readiness section and onboarding guide.

4) Acceptance criteria to move to production
- All tests pass in CI for cms-git (unit tests + offline end-to-end tests).
- A production-readiness Runbook is published.
- A signed-deletion workflow is implemented and exercised in offline tests.
- A lightweight production pipeline draft exists (e.g., PR gate criteria, tests, and rollback steps).

5) Next steps (recommended)
- Add CI job for production-readiness checks (lint, tests, offline end-to-end).
- Expand tests for edge-cases (invalid profiles, missing keys, malformed evidence).
- Publish Runbook and update runbooks with explicit production steps.
- Conduct a security review of the receipts and deletion flows.
