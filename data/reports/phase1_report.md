# Phase 1 Baseline Report

## Source
- **api**: Crossref REST API
- **query**: agentic retrieval augmented generation large language model
- **filter**: from-pub-date:2026-03-29,has-abstract:true
- **records**: 24
- **clean_rows**: 24

## Retrieval & Answer Metrics
| Metric | Value |
| --- | --- |
| Samples | 5 |
| Retrieval hit rate | 100.00% |
| Mean token F1 | 1.0000 |
| Judge accuracy | 100.00% |
| Mean judge score | 5.00 / 5 |

## Data Quality
Overall status: **PASS** (7 passed, 0 failed)

| Expectation | Column | Result |
| --- | --- | --- |
| ExpectTableRowCountToBeBetween | - | PASS |
| ExpectColumnValuesToNotBeNull | paper_id | PASS |
| ExpectColumnValuesToNotBeNull | title | PASS |
| ExpectColumnValuesToNotBeNull | text_for_embedding | PASS |
| ExpectColumnValuesToBeUnique | paper_id | PASS |
| ExpectColumnValueLengthsToBeBetween | summary | PASS |
| FreshnessCheck | age_days | PASS |

## Freshness
- Latest published: 2026-07-22
- Oldest published: 2026-03-28
- Stale rows: 1 / 24
- Is fresh: True
