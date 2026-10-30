# Gradual repository structure proposal

No historical source directory is migrated in R1. Frozen manifests and tests refer to exact phase paths, and some source/reference builds cannot yet be reproduced byte-for-byte. Keeping these references now is safer than an uncontrolled rename/delete operation.

Proposed future layout after explicit adoption: src/PdfEditor for current application/worker/core, tests/fixtures for approved shared regression inputs, docs/phases for handovers, dependency lock metadata in source, artifacts/staging and .local-generated for ignored bulk builds/tests, and approved immutable releases/evidence archives externally. Git commits identify old implementation states; tags can be added later with a documented policy, but none are created/deleted here.

Transition steps: (1) retain this branch's audit/policies and use the safe output wrapper; (2) in a separately scoped development phase move only the current source to a shared location and adapt tests with before/after fidelity proof; (3) keep earlier phase sources/builds until recipes and verified archive retrieval preserve their role; (4) replace repeated native-file checkouts only after every historical build/manifest consumer is migrated; (5) reduce current-tree artifact paths only after approved archive verification. Ordinary commits preserve history; no force push/rewrite.

Do not copy complete phase run/runtime/evidence directories into each new phase. A phase brief explicitly requiring isolation can still isolate changed source, but must define a size/retention plan rather than cloning historical bulky evidence. Existing user instructions take priority; do not infer permission to discard older releases from this proposal.
