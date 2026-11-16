Integrate profile-driven destinations and offline evidence tooling into cms-tooling

Summary
- Replace hard-coded destinations with profile-driven lookups for Telnet/FTP paths.
- Add offline evidence end-to-end tests, profile utilities, and a minimal governance scaffold for evidence lifecycle.
- Introduce a small Runbook and CI coverage to support production-readiness checks.

What changed
- New: cms_profiles.py and profile-driven destination resolution
- Integration of --profile CLI path for cms_telnet_driver and cms_ftpput
- New tests: test_cms_profiles.py, test_cms_telnet_profile.py, test_cms_profiles_offline_end2end.py
- Evidence tooling scaffolding (cms-git side) and tests for offline validation
- CI workflow for offline/production-readiness checks
- Runbook and PRODUCTION_READINESS documentation updates

Rationale
- Eliminates hard-coded destinations and enables multi-environment support via profiles.
- Supports offline validation and guarded deletion via receipts for governance.

Testing and validation
- All unit tests pass in CI for the updated modules (unit tests cover profiles, telnet profile overrides, and offline end-to-end paths).
- Offline end-to-end tests simulate profile lookups and FTP destination resolution without touching live CMS.

How to review
- Review the new PROFILE handling code paths in cms_tooling:
  - cms_profiles.py
  - cms_telnet_driver.py (profile_name usage)
  - cms_ftpput.py (profile-based FTP destination)
- Review tests: test_cms_profiles.py, test_cms_telnet_profile.py
- Review Production_Readiness and Runbook docs
