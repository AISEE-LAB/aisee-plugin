# Tasks

- [ ] TASK-001 Provider implementation: add `src/auth/passwordless.py` request and verify handlers.
- [ ] TASK-001 Consumer integration: update `app/login/page.tsx` for request-code and verify-code states.
- [ ] TASK-001 Mock / SDK / generated client: update or document `contracts/openapi.yaml` usage.
- [ ] TEST-001 Contract test: cover `POST /auth/passwordless/request` and `POST /auth/passwordless/verify` in `tests/auth/test_passwordless.py`.
- [ ] TEST-001 Consumer flow test: cover code sent and verification error states in `tests/ui/test_login_flow.ts`.
- [ ] TEST-001 Backward compatibility check: confirm existing password login remains available during rollout.
