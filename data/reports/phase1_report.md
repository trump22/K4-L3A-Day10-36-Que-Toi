# Báo Cáo Kỹ Thuật Phase 1: Baseline Pipeline & Data Observability

## 1. Thông Tin Nguồn Dữ Liệu & Pipeline (Data Lineage)

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Nguồn API** | Crossref REST API |
| **Truy vấn (Query)** | `agentic retrieval augmented generation large language model` |
| **Số bản ghi thô (Raw Records)** | 24 |
| **Số bản ghi làm sạch (Clean Records)** | 24 |
| **Mô hình Embedding** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Database** | ChromaDB (Collection: `papers-baseline`) |
| **LLM Provider / Model** | gemini / gemini-2.5-flash |

---

## 2. Kết Quả Đo Lường Baseline (Baseline Benchmarks)

Bảng chỉ số đánh giá hiệu năng hệ thống RAG trên dữ liệu sạch:

| Chỉ số (Metric) | Giá trị đạt được | Ngưỡng kỳ vọng | Trạng thái |
| :--- | :---: | :---: | :---: |
| **Số mẫu kiểm thử (Samples)** | 5 | >= 5 | Đạt |
| **Retrieval Hit Rate** | **100.00%** | >= 80% | Đạt |
| **Mean Token F1** | **1.0000** | >= 0.50 | Đạt |
| **LLM Judge Accuracy** | **100.00%** | >= 80% | Đạt |
| **Mean LLM Judge Score** | **5.00 / 5.0** | >= 3.5 | Đạt |

---

## 3. Trạm Kiểm Soát Chất Lượng Dữ Liệu (Great Expectations 1.x Gate)

- **Trạng thái chung:** **PASS (Đạt Chuẩn)**
- **Tổng số Expectation kiểm tra:** 7
- **Đạt:** 7 | **Không đạt:** 0

| Expectation Name | Cột kiểm tra | Kết quả |
| :--- | :--- | :---: |
| `ExpectTableRowCountToBeBetween` | `N/A` | **PASS** |
| `ExpectColumnValuesToNotBeNull` | `paper_id` | **PASS** |
| `ExpectColumnValuesToNotBeNull` | `title` | **PASS** |
| `ExpectColumnValuesToNotBeNull` | `text_for_embedding` | **PASS** |
| `ExpectColumnValuesToBeUnique` | `paper_id` | **PASS** |
| `ExpectColumnValueLengthsToBeBetween` | `summary` | **PASS** |
| `FreshnessCheck` | `age_days` | **PASS** |

---

## 4. Báo Cáo Độ Tươi Mới (Freshness SLA Monitoring)

- **Trạng thái Freshness SLA:** **PASS (Dữ liệu tươi mới)**
- **Bài báo mới nhất (Latest):** 2026-07-22
- **Bài báo cũ nhất (Oldest):** 2026-03-28
- **Số bản ghi quá hạn (> 180 ngày):** 1 / 24

---

## 5. Kết Luận Checkpoint 3
Pipeline Phase 1 đã hoàn thành đầy đủ chu trình: Thu thập thô -> Tiền xử lý & Làm sạch -> Kiểm dịch Great Expectations 1.x -> Đánh chỉ mục ChromaDB -> Đánh giá đối chuẩn Benchmark (Hit Rate & Token F1). Toàn bộ Artifacts được lưu trữ đầy đủ và sẵn sàng cho kịch bản Stress-test ở Phase 2.
