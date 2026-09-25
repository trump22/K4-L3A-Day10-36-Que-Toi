# Corruption & Repair Comparison Report

| Metric | Baseline (Dữ liệu sạch) | Corrupted (Dữ liệu bị lỗi) | Repaired (Sau phục hồi) |
| --- | --- | --- | --- |
| Data Quality Gate | ✅ PASSED | ❌ FAILED | ✅ PASSED |
| Freshness | ✅ Đạt chuẩn | ❌ Vi phạm (7/24 stale) | ✅ Đạt chuẩn (1/24 stale) |
| Retrieval Hit Rate | 100.00% | 0.00% | 100.00% |
| Mean Token F1 | 1.000 | 0.548 | 1.000 |
| Judge Accuracy | 100.00% | 60.00% | 100.00% |
| Mean Judge Score (1-5) | 5.00 | 3.00 | 5.00 |

## Failed expectations
- Corrupted: ExpectColumnValuesToBeUnique, ExpectColumnValueLengthsToBeBetween, FreshnessCheck
- Repaired: -

## Kết luận
Dữ liệu bẩn không gây lỗi runtime nhưng làm RAG trả lời sai (silent failure); Data Quality Gate và Freshness check phát hiện được sự cố, và repair từ raw snapshot đưa các chỉ số về mức baseline.
