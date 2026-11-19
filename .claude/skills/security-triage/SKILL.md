---
name: security-triage
description: Triage every SAST, SCA and DAST finding into docs/securite/triage.md with a written decision, following fiche 4. Use after the security scans have run.
disable-model-invocation: true
---
## Report files available now
!`ls reports/sast reports/sca reports/dast 2>/dev/null || true`

For each finding in those files (read the JSON itself, never a summary):
1. One row in docs/securite/triage.md: outil, règle / CWE / CVE, fichier ou paquet, gravité,
   vraie / fausse / à surveiller, justification, décision, statut après relance.
2. SAST: a false positive is justified in writing, never silently removed. A true finding is fixed, then the
   tool is re-run.
3. SCA: transitive dependencies count too. Decide: update (to the highest "fixed in" version listed for that
   package), replace, or accept with reachability (is the vulnerable code actually called?). Re-run the tests
   after any update.
4. DAST: only results from the local stack named in docs/securite/autorisation.md.
5. Never accept a risk yourself: list the candidates and ask me.
6. End with before/after counts by severity, read from the re-run report files.
