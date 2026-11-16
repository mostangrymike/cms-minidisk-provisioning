# cms-git: Steady-State Readiness

Objective
- Establish a stable, governance-driven baseline for offline evidence tooling and deletion governance.

Current state (high level)
- Evidence schema and tooling exist (evidence_schema.py, evidence_tools.py) with tests.
- Offline end-to-end coverage introduced (test_cms_profiles_offline_end2end.py, test_evidence.py).
- No credentials stored in code or profiles; credentials sourced at runtime.
- Production-readiness docs and CI scaffolding added.

Success criteria (production readiness)
- CI passes for cms-git (unit tests and offline checks).
- Production Runbook published with clear deletion and evidence lifecycle steps.
- End-to-end lifecycle (plan/create/activate/delete) can be simulated offline with receipts, without live CMS actions.
- A signed-public receipt flow exists and is exercised in tests.
- No credentials are embedded in code or profile data.

Gaps to address (prioritized)
- Add a small CLI to manage evidence lifecycle end-to-end (summarize/validate/diff).
- Expand tests for edge cases (missing keys, invalid values, extra fields).
- Add a lightweight GitHub Action to run the offline-end-to-end checks on PRs.
- Document a formal rollback/incident path for failed life-cycle steps.

Planned next steps
- Publish a production-focused Runbook and ensure it’s linked from the main README.
- Implement an offline end-to-end test that covers the full lifecycle with receipts.
- Add a short governance checklist for deletion plans and receipts.
