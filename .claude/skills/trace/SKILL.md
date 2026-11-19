---
name: trace
description: Regenerate the traceability matrix from the test reports and list every requirement that is not at PASS.
disable-model-invocation: true
allowed-tools: Bash(python tools/trace.py *) Read
---
## Matrix run
!`python tools/trace.py --requirements docs/exigences.yaml --reports reports --out docs/tracabilite 2>&1 | tail -25 || true`

From the output above and docs/tracabilite/matrice.csv:
1. List every P0 requirement that is NOT RUN, FAIL or PARTIAL, grouped by characteristic, with the smallest
   next step for each.
2. List test IDs that reference an unknown requirement.
3. Quote statuses exactly as the CSV has them. Never edit the matrix: it is regenerated, not written.
