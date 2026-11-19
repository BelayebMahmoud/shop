---
name: anomalie
description: Log a defect revealed by a failing test in docs/anomalies.md, fix it, then run the confirmation test and the regression suite. Use whenever a test fails because the code is wrong, not the expectation.
argument-hint: <test-id>
arguments: [test]
---
The test $test failed.
1. Re-read the rule behind it. If the expected result is wrong, say so and stop: that is a test defect.
2. Otherwise add an entry to docs/anomalies.md (in French): ANO-xx, date, exigence, test, étapes de
   reproduction, résultat attendu, résultat obtenu, gravité, erreur (the human mistake), défaut (where in the
   code), défaillance (what a user would see).
3. Fix the defect with the smallest change.
4. Confirmation: re-run $test alone and record its result.
5. Non-régression: run `make check` and record the summary line.
6. Mark the entry "Corrigée" with both results and the commit SHA.
