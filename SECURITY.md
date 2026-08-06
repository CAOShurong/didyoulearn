# Security policy

## Supported versions

Only the latest released version receives security fixes.

## Reporting a vulnerability

Please email `shurongcao0819@gmail.com` instead of opening a public issue. Include the affected
version, reproduction steps, impact, and any suggested mitigation. Do not include real learner
records, authentication tokens, or provider credentials.

## Data boundary

The default browser application is static and local-first. It does not call model APIs, load remote
scripts, or transmit study records. A hosted deployment can serve the same static assets, but study
owners remain responsible for consent, access control, retention, and deletion when they add a
backend or collect human-subject data.
