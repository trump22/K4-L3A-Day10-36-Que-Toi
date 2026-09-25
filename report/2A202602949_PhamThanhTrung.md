# Báo Cáo Vai Trò Cá Nhân - Phạm Thành Trung

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Phạm Thành Trung |
| **MSSV** | 2A202602949 |
| **Khóa / Lớp** | K4 / L3A |
| **Tên nhóm** | Nhóm 36 - Quê Tôi |
| **Vai trò chính** | Trưởng nhóm, Pipeline Integration & Corruption/Repair |
| **Repository** | https://github.com/trump22/K4-L3A-Day10-36-Que-Toi.git |
| **Ngày hoàn thành** | 2026-09-25 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| Cấu hình và artifact paths | `src/core/config.py`: `load_settings`, `Paths`, `Settings` | Biến môi trường, project root | Settings thống nhất, đường dẫn raw/clean/index/eval/results | Hoàn thành |
| Baseline orchestration | `src/pipelines/phase1.py`: `main()` | Raw snapshot hoặc Crossref source | Clean data, quality/freshness, index, test set, baseline metrics/report | Hoàn thành |
| Corruption/repair orchestration | `src/pipelines/corruption_flow.py`: `main()` | Baseline metrics, clean dataset, raw snapshot | Corrupted/repaired datasets, indexes, metrics và comparison report | Hoàn thành |
| Corruption suite và log | `src/ingestion/corruption.py`: `corrupt_clean_dataframe()` | `papers_clean.json` | `data/results/corruption_log.json` và corrupted dataframe | Hoàn thành |

### Công việc điều phối

Trưởng nhóm chịu trách nhiệm thống nhất artifact paths, thứ tự chạy giữa các module, kiểm tra baseline trước khi chạy corruption và đối chiếu consistency giữa metrics, quality reports và báo cáo Markdown. Repair được thiết kế idempotent: đọc lại raw snapshot, cleaning lại từ đầu, build collection repaired rồi đánh giá trên đúng evaluation set.

## 3. Kết quả theo vai trò

| Nhiệm vụ | File / Hàm / Artifact | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Điều phối baseline | `src/pipelines/phase1.py::main` | Baseline chạy qua ingestion, cleaning, quality, index, evaluation và reporting | `python script/run_phase1.py` thoát mã 0 |
| Điều phối corruption flow | `src/pipelines/corruption_flow.py::main` | Corrupted và repaired được build/evaluate bằng cùng test set | `python script/run_corruption_flow.py` thoát mã 0 |
| Tiêm lỗi có kiểm soát | `src/ingestion/corruption.py::corrupt_clean_dataframe` | 6 scenarios, seed 42, 24 dòng trước/sau | `data/results/corruption_log.json` |
| So sánh ba trạng thái | `data/reports/corruption_report.md` | Quality `PASS -> FAIL -> PASS`; metrics suy giảm rồi phục hồi | Đối chiếu baseline/corrupted/repaired JSON |
| Bảo đảm repair từ nguồn | `load_raw_records()` + `build_clean_dataframe()` | Repaired dataset trở về 24 dòng sạch, không sửa trực tiếp corrupted output | `repaired_quality_report.json`, `repaired_metrics.json` |

## 4. Cách triển khai kỹ thuật

### Baseline flow

`phase1.main()` tải settings, ưu tiên raw snapshot khi đã tồn tại, cleaning thành DataFrame, ghi CSV/JSON, chạy Quality Gate và freshness, build ChromaDB index, tạo hoặc đọc test set, evaluate rồi sinh `phase1_report.md`. Việc gom thứ tự vào một entrypoint giúp tránh đánh index trước khi cleaning hoặc đánh giá bằng test set khác.

### Corruption flow

`corruption_flow.main()` đọc baseline metrics và clean JSON làm control, gọi `corrupt_clean_dataframe()`, lưu corrupted artifacts, build collection `papers-corrupted`, evaluate và chạy quality/freshness. Sau đó pipeline đọc lại `data/raw/crossref_records.json`, gọi lại cleaning, build collection `papers-repaired`, evaluate và sinh `corruption_report.md`.

### Sáu corruption đã kiểm chứng

| Scenario | Số record bị tác động | Tín hiệu chính |
| :--- | ---: | :--- |
| `drop_latest_records` | 5 | Mất đúng các bài mới nhất, ảnh hưởng retrieval |
| `blank_summary` | 6 | Summary dưới ngưỡng 30 ký tự |
| `inject_text_noise` | 6 | Nhiễu nội dung summary/embedding |
| `truncate_title` | 8 | Title bị cắt còn 8 ký tự |
| `stale_date` | 6 | Lùi ngày 5 năm, freshness tăng lên 7/24 stale |
| `duplicate_rows` | 5 | Append bản sao, unique `paper_id` fail với 10 unexpected values |

## 5. Kết quả thực tế

| Metric / Signal | Baseline | Corrupted | Repaired |
| :--- | ---: | ---: | ---: |
| `retrieval_hit_rate` | 1.000 | 0.000 | 1.000 |
| `mean_token_f1` | 1.000 | 0.548 | 1.000 |
| `judge_accuracy` | 1.000 | 0.600 | 1.000 |
| `mean_judge_score` | 5.00 | 3.00 | 5.00 |
| Quality checks | PASS 7/7 | FAIL 4/7 | PASS 7/7 |
| Freshness | 1/24 stale | 7/24 stale | 1/24 stale |

Corrupted data không gây runtime error nhưng tạo silent failure ở agent. Quality Gate phát hiện ba lỗi: duplicate `paper_id`, summary quá ngắn và freshness vượt tỷ lệ cho phép. Repair từ raw snapshot phục hồi toàn bộ bốn metric đánh giá và cả hai nhóm tín hiệu observability.

## 6. Quyết định kỹ thuật quan trọng

Nhóm chọn giữ raw snapshot làm nguồn repair thay vì sửa trực tiếp corrupted dataset. Cách này giữ được data lineage và cho phép kiểm chứng rằng kết quả repaired không phải do che các lỗi đã phát hiện. Đồng thời, dùng chung `data/eval/test_set.json` cho baseline, corrupted và repaired giúp metrics có cùng biến kiểm soát.

Corruption sử dụng `SEED = 42` và giữ tổng số dòng 24 bằng cách duplicate sau bước drop. Đây là quyết định giúp comparison dễ đọc nhưng cũng cần ghi rõ: test set được tạo từ 5 record đầu, trùng với 5 bài mới nhất bị drop, nên hit rate corrupted giảm về 0% có thể mạnh hơn kết quả khi test set chọn document rải đều.

## 7. Blocker và cách xử lý

- **Blocker:** Python mặc định là 3.14 nhưng project yêu cầu `<3.14`, đồng thời môi trường ban đầu thiếu dependency.
- **Cách xử lý:** Tạo virtual environment bằng Python 3.13, cài requirements, đặt `PYTHONPATH=src` và chạy với `LLM_PROVIDER=mock` để không phụ thuộc secret/API key.
- **Xác minh:** Hai entrypoint chạy thành công và sinh đầy đủ artifacts trong `data/`.

## 8. Bài học và hướng cải thiện

1. Orchestration phải kiểm soát thứ tự và artifact paths, vì một module chạy đúng riêng lẻ vẫn có thể làm hỏng contract của module sau.
2. Raw preservation là điều kiện để repair có ý nghĩa; nếu chỉ lọc các dòng lỗi trên corrupted output thì không chứng minh được dữ liệu đã phục hồi.
3. Nên chạy ablation từng corruption riêng biệt và mở rộng test set để tách tác động của drop, noise, title truncation và stale date.
4. Lần chạy tiếp theo nên dùng LLM provider thật trong môi trường có secret được quản lý an toàn và bật `RUN_RAGAS=1` nếu cần thêm context metrics.

## 9. Cam kết của thành viên

- [x] Nội dung phản ánh phần việc orchestration, corruption và repair.
- [x] Các kết luận đều có artifact hoặc metric đối chiếu.
- [x] Không đưa API key, token hoặc secret vào báo cáo.
- [x] Có thể giải thích luồng baseline -> corruption -> repair -> comparison.

**Họ và tên:** Phạm Thành Trung  
**MSSV:** 2A202602949  
**Ngày xác nhận:** 2026-09-25