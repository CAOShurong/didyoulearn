# Statistical interpretation

## Descriptive measures

DidYouLearn reports:

- pretest, post-test, transfer, and retention proportions;
- raw gain (`post - pre`);
- perceived-understanding gap (`self-report - post`);
- learning gain per ten minutes;
- correctness-gate pass rate;
- sample size and interval estimates.

## Adjusted comparison

When assignment is randomized, a common-slope covariance adjustment estimates tutor means at the
pooled average pretest score. This is more efficient than ranking raw change scores alone in many
randomized pre/post designs. The report must disclose the model, missing-data rules, and whether the
common-slope assumption was checked.

## Repeated observations

Public studies may contain multiple trials from one participant or task. Confirmatory analyses must
cluster or model those dependencies. The dependency-free built-in report is appropriate for pilot
diagnostics; it is not a replacement for a pre-registered mixed-effects or hierarchical analysis.

## Minimum evidence gate

The default report withholds a rank when a tutor has fewer than five complete trials. Five is only a
software safety floor, not a claim of statistical adequacy. Study owners must justify sample size
before collecting confirmatory data.

## Missing delayed tests

Retention is reported with its own denominator. It is never silently imputed from the immediate
post-test. Attrition by tutor condition must be shown.
