# Evidence Ledger — pat-db-01

## Status

- Pattern: pat-db-01, ACTIVE @ v1.1.0 lineage
- effective_confidence: 0.80 (posterior mean, alpha=4.0, beta=1.0)
- Oracle: DETERMINISTIC, 7/7 PASS on the earlier inline-script runs. The packaged pytest run does NOT reproduce this: 8 passed, 2 failed (T2, T6). See "Packaged-test verification".

## Test results

- T1 SELECT returns rows: PASS
- T2 partial DML rollback: PASS
- T3: FAIL (harness bug) -> assertion amended -> PASS; amended_after_failure=true; rationale: harness committed a second row via separate connection, count==2 is correct; property under test (success_txn_clean) passed first-run
- T4' failure propagation + cleanup: PASS
- T5 repeated failure stability: PASS
- T6 DDL commit/rollback semantics: PASS
- T7: PASS — close() invoked on failure path, 3/3 (proxy spy; measures closure invocation, not OS handle release; equivalent for sqlite3)

## Packaged-test verification

- Run: `pip install -e ".[dev]" && python -m pytest -v` on commit b9da9afd (local clone, 2026-10-18).
- Result: 8 passed, 2 failed.
- FAIL `test_t2_partial_dml_rollback`: expected count 1, got 2.
- FAIL `test_t6_ddl_commit_and_rollback`: `rolled_back` table exists, expected absent.
- Diagnosis: test-design bug, not an executor bug. Both tests issue two separate `execute()` calls inside `pytest.raises` and assume one transaction spans both. Each call commits independently, so the first statement is already committed when the second fails. The failing statement itself is rolled back correctly.
- Not yet done: the tests have not been amended. Changing them is an amendment after failure and should be recorded like T3 (`amended_after_failure=true`) before the T2/T6 results above can be called PASS in packaged form.
- CI (GitHub Actions) run: not inspected; add the run URL here once checked.

## Preconditions

- Caller-owned connection unsupported under current design.
- If the connection already has a transaction open, `execute()` raises and its rollback discards the caller's uncommitted work (verified 2026-10-18). Default `isolation_level` connections with no open transaction work.
- beta=1.0 has orphaned provenance (flagged to governance owner).

## Tier 2 exclusion

pool.py and transactions.py are NOT included: new unverified subsystems require fresh pattern IDs, PROVISIONAL status, and pre-registered falsification statements before implementation.
