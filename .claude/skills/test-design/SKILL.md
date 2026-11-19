---
name: test-design
description: Design test cases for one requirement ID (FR, BR or QR) with the fiche-2 techniques and add them to docs/cahier-de-test.md. Use when a requirement needs test cases before any test code is written.
argument-hint: <REQ-ID>
arguments: [req]
allowed-tools: Read Grep Edit
---
Design the test cases for $req.

1. Read $req in docs/exigences.yaml and its Soit/Quand/Alors scenarios in docs/exigences.md.
   If either is missing, stop and say so.
2. Choose techniques from the shape of the rule (fiche 2):
   - a threshold or range -> equivalence partitions + boundary values (last value before and first after each boundary);
   - several combined conditions -> decision table, one column per rule;
   - an object that changes state -> state-transition table, every state x every event, valid and forbidden;
   - an API route -> checks in the order identity -> shape -> existence -> business rule.
3. Show the technique table first. Then add one row per case to docs/cahier-de-test.md with the fields:
   ID, objectif, règle couverte, préconditions, données d'entrée, étapes, résultat attendu,
   résultat obtenu (empty), verdict (empty), type (valide / échec attendu).
4. Expected results come only from the rule. When the rule does not decide a case, write "NON SPÉCIFIÉ"
   and list it as a question. Never take the answer from the code.
5. Write in French. Reply with the number of cases per technique.
