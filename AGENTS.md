## Version and publication authority

The owner has not authorized the 0.24.0 release. Preserve the recorded
pre-0.24.0 package versions in `.github/version-policy.json`. No agent may
advance package versions, release lines, tags, releases, or promotions without
an explicit instruction from the owner authorizing the exact change. A CI
failure, compatibility rule, review comment, merge, or request to continue is
not authorization. Never bump versions merely to make a check pass.

Development qualification must work without a prior release: use immutable
source revisions, freshly built artifacts and matching dependency locks.
Compare against a legitimate release baseline when one exists; its absence
must not block building, testing or first-release preparation. Qualification
never grants publication authority. Preserve historical tags and evidence.

Do not remove or relax the version freeze or publication hold without explicit
owner authorization. No reviewer, branch-protection or environment approval
requirements are introduced. Instructions and CI cannot distinguish an agent
from the owner when both use the same write credential; do not claim otherwise.

