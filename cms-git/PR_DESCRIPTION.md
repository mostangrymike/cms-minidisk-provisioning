cms-git: Production readiness for evidence governance and offline validation

Summary
- Introduce evidence_schema.py and evidence_tools.py for offline validation and governance of CMS evidence.
- Add credential-safety guard (no credentials in code or profiles).
- Add offline tests for evidence lifecycle and a lightweight CLI for evidence checks.
- Add production-readiness docs (PRODUCTION_READINESS.md) and an offline CI path.

What changed
- Evidence schema and tooling
- Tests for evidence lifecycle
- Guarding credentials; no credentials in code or profiles
- Production-readiness documentation and CI hooks

How to review
- Review cms-git/evidence_schema.py and cms-git/evidence_tools.py
- Review tests/cms-git/tests/test_evidence.py
- Review PRODUCTION_READINESS.md and the production CI workflow
- Check Runbook and Runbook-like guidance in the repo

Testing and validation
- Unit tests added and executed in CI
- Offline validation scaffolding for deletion plans and receipts

Notes
- No live CMS actions are executed in this branch; all changes are offline/validation-oriented
