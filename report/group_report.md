# Group Report - Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| --- | --- |
| Khóa/Lớp | K4 - L3A |
| Tên nhóm | 36 Quê Tôi |
| Repository | https://github.com/trump22/K4-L3A-Day10-36-Que-Toi |
| Ngày hoàn thành | 2026-09-25 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Phạm Thành Trung | 2A202602949 | Trưởng nhóm, Pipeline Integration & Corruption/Repair | `src/core/config.py`, `src/core/utils.py`, `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`; `data/results/`, `data/reports/` |
| 2 | Nguyễn Mạnh Hải | 2A202602988 | Data Foundation & Quality Gate (Pha 2) | `src/ingestion/crossref.py`, `src/ingestion/cleaning.py`, `src/observability/quality.py`; `data/raw/`, `data/clean/`, `data/quality/` |
| 3 | Đinh Mạnh Dũng | 02975 | Baseline Pipeline End-to-End & Baseline Reporting (Pha 4) | `script/run_phase1.py`, `src/observability/reporting.py::generate_phase1_report`; `data/results/baseline_metrics.json`, `data/reports/phase1_report.md` |
| 4 | Trần Nguyễn Thái Duy | 2A202602991 | RAG, Vector Index và Benchmark Test Set (Pha 3) | `src/retrieval/embeddings.py`, `src/retrieval/index.py`, `src/evaluation/testset.py`; ChromaDB và `data/eval/test_set.json` |

## 2. Tóm tắt kết quả

Nhóm đã hoàn thành pipeline end-to-end từ raw snapshot Crossref, cleaning, Quality Gate bằng Great Expectations 1.x, embedding MiniLM, ChromaDB, benchmark evaluation đến corruption, re-index, repair và báo cáo so sánh. Baseline tạo được 24 record sạch, 24 vector document, bộ test cố định 5 câu hỏi thuộc các dạng summary, authors, date, category và multi-hop, cùng các artifact metrics, quality, freshness và Markdown report. Corruption flow tiêm đủ 6 kịch bản: drop 5 bản ghi mới nhất, blank summary, inject noise, truncate title, stale date và duplicate rows. Dữ liệu corrupted làm Quality Gate chuyển từ PASS sang FAIL (4/7 pass), freshness từ 1/24 stale lên 7/24 stale, retrieval hit rate từ 100% xuống 0%, Token F1 từ 1.000 xuống 0.548 và judge accuracy từ 100% xuống 60%. Repair dựng lại dataset từ raw snapshot đáng tin cậy, sau đó re-index và đánh giá lại; tất cả quality checks, freshness và bốn metric đánh giá trở về đúng baseline. Giới hạn chính là lần tái hiện này dùng `LLM_PROVIDER=mock` để chạy offline, Ragas chưa chạy, và test set nhỏ nên mức giảm hit rate chịu ảnh hưởng bởi việc 5 câu đầu trùng với 5 bài mới nhất bị drop.

## 3. Kiến trúc và luồng dữ liệu

```text
Crossref snapshot/API
    -> data/raw/crossref_response.json, crossref_records.json
    -> build_clean_dataframe()
    -> data/clean/papers_clean.csv/json
    -> Quality Gate + freshness
    -> MiniLM embeddings + ChromaDB collections
    -> fixed evaluation set + baseline metrics
    -> corruption + corrupted metrics/quality
    -> rebuild from raw snapshot + repaired metrics/quality
    -> data/reports/corruption_report.md
```

| Khối | Input | Xử lý chính | Output/artifact | Owner |
| --- | --- | --- | --- | --- |
| Ingestion | Crossref API hoặc `data/raw/crossref_response.json` | Retry 429/5xx tối đa 3 lần, fallback snapshot, parse DOI/title/abstract/authors/subject/ngày | `data/raw/crossref_records.json` | Nguyễn Mạnh Hải |
| Cleaning | `crossref_records.json` | Chuẩn hóa text, tính `age_days`, tạo `text_for_embedding`, deduplicate `paper_id` | `data/clean/papers_clean.csv/json` | Nguyễn Mạnh Hải |
| Embedding/index | Clean dataset | `sentence-transformers/all-MiniLM-L6-v2`, cosine ChromaDB, metadata theo DOI | `data/embeddings/`, `data/chroma/` | Trần Nguyễn Thái Duy |
| Evaluation | Clean/index + test set | Retrieval hit, Token F1, judge accuracy/score | `data/eval/test_set.json`, `data/results/*metrics.json` | Đinh Mạnh Dũng, Trần Nguyễn Thái Duy |
| Observability | Clean/corrupted/repaired DataFrame | 6 GX expectations và freshness SLA `age_days > 180` | `data/quality/*.json` | Nguyễn Mạnh Hải |
| Corruption/repair | Clean dataset/raw snapshot | Tiêm 6 lỗi; repair idempotent từ raw snapshot | `corruption_log.json`, corrupted/repaired artifacts | Phạm Thành Trung |
| Orchestration | Settings và các module | Chạy đúng thứ tự baseline -> corruption -> repair -> report | `phase1_report.md`, `corruption_report.md` | Phạm Thành Trung, Đinh Mạnh Dũng |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình | Giá trị sử dụng |
| --- | --- |
| `LLM_PROVIDER` | `mock` trong lần chạy kiểm chứng offline; mặc định project là `gemini` |
| `LLM_MODEL` | `gemini-2.5-flash` theo `src/core/config.py` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24 |
| Retrieval `top_k` | 4 |
| Freshness threshold | 180 ngày; quality gate cho phép tối đa 25% stale |
| Random seed | 42 cho corruption |

### Lệnh cài đặt và chạy

```bash
python -m pip install -e .
python script/run_phase1.py
python script/run_corruption_flow.py
```

Lần chạy kiểm chứng trên Windows dùng Python 3.13, `PYTHONPATH=src` và `LLM_PROVIDER=mock`. Cả hai lệnh thoát thành công; baseline report ghi hit rate 100% và corruption flow ghi quality `PASS -> FAIL -> PASS`.

| Lệnh | Trạng thái | Bằng chứng |
| --- | --- | --- |
| Baseline pipeline | Thành công | `data/results/baseline_metrics.json`, `data/quality/baseline_quality_report.json`, `data/reports/phase1_report.md` |
| Corruption flow | Thành công | `data/results/corruption_log.json`, `data/results/corrupted_metrics.json`, `data/results/repaired_metrics.json`, `data/reports/corruption_report.md` |

## 5. Ingestion, cleaning và data contract

Nguồn là Crossref REST API với snapshot offline trong `data/raw/`. Query là `agentic retrieval augmented generation large language model`, filter theo `has-abstract:true` và cửa sổ 180 ngày. Snapshot có 24 record và cleaning giữ lại 24 dòng. Record thiếu DOI/title/abstract/ngày bị loại; DOI được chuẩn hóa chữ thường, abstract bỏ JATS/HTML, danh sách authors/categories để rỗng khi thiếu. `text_for_embedding` gồm 5 dòng Title, Authors, Published, Categories và Summary. `age_days` được tính bằng số ngày giữa thời điểm chạy và ngày published.

Quality baseline xác nhận 24 dòng, không null ở các cột chính, DOI duy nhất, summary đạt độ dài tối thiểu và freshness trong ngưỡng. Baseline có 1/24 dòng stale (4.17%), thấp hơn ngưỡng 25%.

## 6. Evaluation setup

| Thành phần | Cấu hình thực tế |
| --- | --- |
| Số câu hỏi | 5 |
| `question_type` | `summary`, `authors`, `date`, `category`, `multi_hop` |
| Ground-truth document ID | DOI `paper_id` trong `data/eval/test_set.json` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store/collection | ChromaDB PersistentClient; `papers-baseline`, `papers-corrupted`, `papers-repaired` |
| Retrieval `top_k` | 4 |
| LLM provider/model | `mock` khi kiểm chứng offline; model cấu hình mặc định `gemini-2.5-flash` |
| Test set dùng chung | `data/eval/test_set.json`, được giữ cố định cho cả ba trạng thái |

Cùng test set và ground truth giúp thay đổi metrics phản ánh thay đổi dữ liệu/index thay vì thay đổi độ khó câu hỏi. Ragas không chạy vì `RUN_RAGAS` không được bật; metrics chính vẫn được ghi đầy đủ.

## 7. Kết quả baseline

| Artifact | Đường dẫn | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| Raw response/records | `data/raw/` | Có | Snapshot và 24 raw records |
| Cleaned dataset | `data/clean/` | Có | CSV/JSON, 24 dòng |
| Embedding manifest/index | `data/embeddings/`, `data/chroma/` | Có | ChromaDB baseline/corrupted/repaired |
| Evaluation set | `data/eval/test_set.json` | Có | 5 câu hỏi cố định |
| Baseline metrics | `data/results/baseline_metrics.json` | Có | Đầy đủ 4 metric chính |
| Quality/freshness | `data/quality/` | Có | Baseline, corrupted, repaired reports |
| Baseline report | `data/reports/phase1_report.md` | Có | Sinh tự động sau baseline |

| Metric | Baseline | Diễn giải |
| --- | ---: | --- |
| `retrieval_hit_rate` | 1.000 (100%) | 5/5 câu có tài liệu ground truth trong kết quả truy xuất |
| `mean_token_f1` | 1.000 | Câu trả lời khớp ground truth theo token |
| `judge_accuracy` | 1.000 (100%) | 5/5 câu được judge đánh dấu đúng |
| `mean_judge_score` | 5.00/5 | Điểm trung bình tối đa |
| Ragas | N/A | Chưa bật `RUN_RAGAS` |

## 8. Data quality và freshness

Baseline có 7/7 checks PASS: row count, `paper_id` not-null, `title` not-null, `text_for_embedding` not-null, unique `paper_id`, summary dài tối thiểu 30 ký tự và freshness. Bằng chứng là `data/quality/baseline_quality_report.json`.

| Freshness signal | Baseline | Corrupted | Repaired |
| --- | --- | --- | --- |
| Stale rows | 1/24 (4.17%) | 7/24 (29.17%) | 1/24 (4.17%) |
| Trạng thái | Fresh | Stale | Fresh |
| Artifact | `baseline_freshness_report.json` | `corrupted_freshness_report.json` | `repaired_freshness_report.json` |

## 9. Corruption scenarios và repair

| Corruption | Record bị tác động | Quality signal kỳ vọng/tác động | Repair |
| --- | ---: | --- | --- |
| `drop_latest_records` | 5 | Mất các tài liệu mới nhất, ảnh hưởng retrieval | Dựng lại từ raw |
| `blank_summary` | 6 | Summary dưới ngưỡng độ dài | Dựng lại từ raw |
| `inject_text_noise` | 6 | Nhiễu nội dung embedding/answer | Dựng lại từ raw |
| `truncate_title` | 8 | Mất thông tin định danh trong title | Dựng lại từ raw |
| `stale_date` | 6 | Freshness tăng lên 7/24 stale | Dựng lại từ raw |
| `duplicate_rows` | 5 | Unique `paper_id` fail với 10 unexpected values | Dựng lại từ raw |

Tổng thể bảng vẫn có 24 dòng vì 5 dòng bị drop sau đó 5 dòng duplicate được append. Log đầy đủ tại `data/results/corruption_log.json`, seed 42, 24 dòng trước và sau corruption. Repair gọi lại `load_raw_records()` rồi `build_clean_dataframe()`, không che lỗi hay sửa trực tiếp output corrupted; sau đó build collection repaired và đánh giá lại.

## 10. So sánh baseline, corrupted và repaired

| Metric/signal | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi |
| --- | ---: | ---: | ---: | ---: | ---: |
| `retrieval_hit_rate` | 1.000 | 0.000 | 1.000 | -1.000 | 100% |
| `mean_token_f1` | 1.000 | 0.548 | 1.000 | -0.452 | 100% |
| `judge_accuracy` | 1.000 | 0.600 | 1.000 | -0.400 | 100% |
| `mean_judge_score` | 5.00 | 3.00 | 5.00 | -2.00 | 100% |
| Quality checks | PASS 7/7 | FAIL 4/7 | PASS 7/7 | 3 checks fail | 100% |
| Freshness | Fresh, 1/24 | Stale, 7/24 | Fresh, 1/24 | +6 stale rows | 100% |

Hai kết luận nhân quả được artifacts hỗ trợ:

1. Drop/duplicate/blank summary/stale date làm unique, summary length và freshness fail; cùng lúc tài liệu ground truth bị mất khỏi index nên hit rate giảm 100% xuống 0% và Token F1 xuống 0.548.
2. Repair từ raw snapshot khôi phục dataset 24 dòng, quality/freshness PASS và re-index đúng tài liệu; cả retrieval hit, Token F1, judge accuracy và judge score trở về baseline.

Không tách riêng được tác động của từng corruption vì sáu lỗi được tiêm trong cùng một lần chạy. Hit rate về 0% cũng chịu ảnh hưởng bởi test set được tạo từ 5 record đầu, trùng với 5 record mới nhất bị drop.

## 11. Vấn đề tích hợp quan trọng

- **Triệu chứng:** Môi trường Python mặc định là 3.14 và thiếu dependency, trong khi project yêu cầu Python `<3.14`; artifact ban đầu chưa được sinh.
- **Nguyên nhân:** Chưa tạo virtual environment tương thích và chưa cài `requirements.txt`.
- **Cách xử lý:** Dùng Python 3.13, tạo `.venv`, cài dependency, đặt `PYTHONPATH=src` và dùng `LLM_PROVIDER=mock` để không phụ thuộc API key.
- **Cách xác minh:** `script/run_phase1.py` và `script/run_corruption_flow.py` đều chạy thành công; các JSON/Markdown artifact được sinh đầy đủ.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng | Hướng cải thiện có thể kiểm chứng |
| --- | --- | --- |
| Test set chỉ có 5 câu và 5 câu đầu trùng record mới nhất | Hit rate corrupted có thể giảm quá mạnh so với tác động tổng quát | Tạo test set lớn hơn, chọn document rải đều và chạy ablation từng corruption |
| Lần kiểm chứng dùng mock LLM | Chưa phản ánh đầy đủ hành vi Gemini thật | Chạy lại với provider thật trong môi trường có secret được quản lý an toàn |
| Ragas chưa bật | Chưa có context precision/recall và faithfulness | Chạy `RUN_RAGAS=1` rồi lưu kết quả vào metrics |
| Chưa có test tự động/CI | Regression có thể không được phát hiện sớm | Thêm pytest cho ingestion, cleaning, quality, corruption và pipeline exit code |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm, repository và ngày hoàn thành đã điền.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Baseline, corrupted và repaired dùng cùng `data/eval/test_set.json`.
- [x] Metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness kết luận khớp với `data/quality/`.
- [x] Corruption log có đủ 6 loại lỗi, seed và số record bị tác động.
- [x] Repair lấy lại dữ liệu từ raw snapshot và đã được kiểm chứng.
- [x] Báo cáo không chứa API key, token hoặc secret.
- [ ] Cần nhóm xác nhận lại email/MSSV của các thành viên trước khi nộp chính thức.