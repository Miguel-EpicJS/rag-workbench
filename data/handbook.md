# Engineering Handbook

## Remote work

The team supports focused remote work. Core collaboration hours are 13:00 to 17:00 UTC.
Written decisions should be recorded in the project workspace so asynchronous teammates can
review context without attending every meeting.

## Deployments

Production deployments require a passing test suite, a rollback plan, and an owner for the
release. Changes that affect customer data must include a migration note and an observability
check. Emergency changes may skip the normal window, but the incident review must document why.

## Security

Secrets must never be committed to source control. Customer data must be filtered from logs,
and access to production systems must use individual accounts with multi-factor authentication.
