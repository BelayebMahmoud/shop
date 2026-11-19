---
name: phase-done
description: Close one phase of tonight's plan by running the checks, updating the journal, reviewing and committing.
argument-hint: <phase-number>
arguments: [n]
disable-model-invocation: true
allowed-tools: Bash(make *) Bash(git add *) Bash(git commit *) Bash(git status *) Read Edit
---
Close phase $n.
1. Run `make check` and show its real summary lines.
2. Append to docs/journal.md (in French): phase $n, heure, ce qui a été fait, fichiers de preuve produits
   (paths under reports/), écarts, points ouverts.
3. Ask the test-reviewer subagent to review the test files changed in this phase. If it reports a blocker,
   stop before committing and show it.
4. git add -A, then git commit -m "phase $n: <one-line summary>".
5. Stop and wait for "go phase <next>".
