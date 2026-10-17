# Evidence Ledger — pat-db-01

## Status

- Pattern: pat-db-01, ACTIVE @ v1.1.0 lineage
- effective_confidence: 0.80 (posterior mean, alpha=4.0, beta=1.0)
- Oracle: DETERMINISTIC, 7/7 PASS

## Test results

- T1 SELECT returns rows: PASS
- T2 partial DML rollback: PASS
- T3: FAIL (harness bug) -> assertion amended -> PASS; amended_after_failure=true; rationale: harness committed a second row via separate connection, count==2 is correct; property under test (success_txn_clean) passed first-run
- T4' failure propagation + cleanup: PASS
- T5 repeated failure stability: PASS
- T6 DDL commit/rollback semantics: PASS
- T7: PASS — close() invoked on failure path, 3/3 (proxy spy; measures closure invocation, not OS handle release; equivalent for sqlite3)

## Preconditions

- Caller-owned connection unsupported under current design.
- beta=1.0 has orphaned provenance (flagged to governance owner).

## Tier 2 exclusion

pool.py and transactions.py are NOT included: new unverified subsystems require fresh pattern IDs, PROVISIONAL status, and pre-registered falsification statements before implementation.
