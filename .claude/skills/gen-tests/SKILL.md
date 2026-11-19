---
name: gen-tests
description: Write automated tests for cases already designed in docs/cahier-de-test.md, tagged with requirement and case IDs, and prove each test fails when the rule is broken. Use after /test-design.
argument-hint: <REQ-ID> <unit|integration|api|e2e>
arguments: [req, level]
---
Write the $level tests for the cases of $req in docs/cahier-de-test.md.

Rules:
- One test per case. Test id = case ID. pytest: @pytest.mark.req("$req"); Playwright: "@$req" in the title.
- Arrange-Act-Assert. Assert the expected result copied from the cahier, never a value read from the code.
- API tests assert status, body AND the real effect (database state or a follow-up GET). A 500 is a defect.
- No fixed sleeps, no dependency on test order or on data left by another test.
Then:
1. Run the new tests and show the summary line.
2. Break the rule in the code on purpose (for example change >= into >), run the tests, show that at least one
   fails, restore the code, run them again.
3. If a test fails because the code is wrong, run /anomalie instead of changing the expectation.
