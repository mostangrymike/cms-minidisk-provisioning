# cms-tooling Production Runbook (profiles, evidence, and delivery)

Overview
- Defines how to promote profile-driven destinations to production and how to handle evidence lifecycle in a production pipeline.

Runbook outline
- Prepare profiles at ~/.config/cms-tooling/cms_profiles.json and validate via test_cms_profiles_offline_end2end.py
- Run offline end-to-end tests for profile-based Telnet/FTP paths
- Run credential checks (cms-git/credential_check.py) as part of PR gate
- Deploy CI changes and ensure main tests pass
- Publish Runbook and update README with production guidance

Rollout plan
- Phase 1: CI gates for unit tests and offline end-to-end tests
- Phase 2: Documentation updates and Runbook publication
- Phase 3: Monitor and iterate on feedback
