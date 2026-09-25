# Báo Cáo Vai Trò Cá Nhân (Individual Report) — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Đinh Mạnh Dũng |
| **MSSV** | 02975 |
| **Khóa / Lớp** | AI-ENGINEER-K4 / L3A |
| **Tên nhóm** | Nhóm 36 — Quê Tôi |
| **Vai trò chính** | Pipeline Integrator & Baseline Pipeline Lead (Phụ trách Checkpoint 3 / Pha 4) |
| **Repository** | https://github.com/trump22/K4-L3A-Day10-36-Que-Toi.git |
| **Nhánh làm việc (Branch)** | `DinhManhDung-02975` |
| **Ngày hoàn thành** | 2026-09-25 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **Baseline Pipeline End-to-End** | `src/pipelines/phase1.py`<br>`main()` | - `Settings` cấu hình hệ thống<br>- Snapshot thô: `data/raw/crossref_records.json` | - Bảng dữ liệu sạch: `papers_clean.csv`, `papers_clean.json`<br>- ChromaDB Vector Index: `papers-baseline`<br>- Benchmark test set: `test_set.json`<br>- Chỉ số đánh giá: `baseline_metrics.json`<br>- Báo cáo kỹ thuật: `phase1_report.md` | **Hoàn thành (100%)** |
| **Báo cáo kỹ thuật Phase 1** | `src/observability/reporting.py`<br>`generate_phase1_report()` | - `source_summary`: metadata API & số bản ghi<br>- `metrics`: Hit Rate, Token F1, LLM Judge<br>- `quality`: kết quả kiểm định GX 1.x<br>- `freshness`: báo cáo Freshness SLA | - File báo cáo markdown hoàn chỉnh tại `data/reports/phase1_report.md` | **Hoàn thành (100%)** |
| **Entrypoint thực thi Phase 1** | `script/run_phase1.py` | Lệnh gọi CLI `python script/run_phase1.py` | Kích hoạt toàn bộ luồng Phase 1 tự động bằng một lệnh duy nhất | **Hoàn thành (100%)** |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên / Module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| **Tối ưu mã hóa UTF-8 trên Windows PowerShell** | Toàn bộ nhóm | Xử lý lỗi `UnicodeEncodeError: 'charmap'` bằng cấu hình `$env:PYTHONIOENCODING="utf-8"` và chuẩn hóa log in không dấu, giúp terminal trên Windows chạy ổn định. |
| **Kiểm định tương thích Great Expectations 1.x** | Module `observability/quality.py` | Xác minh thành công cú pháp Ephemeral Context chuẩn GX 1.x (`context.data_sources.add_pandas`), vượt qua 7/7 expectations. |
| **Kiểm thử Multi-Provider LLM & Judge** | Module `retrieval/llm.py` & `evaluation/metrics.py` | Đảm bảo pipeline đánh giá với Gemini Flash có cơ chế fallback heuristic an toàn, không bị crash pipeline khi gặp quota limit. |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File / Hàm / Artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| **Xây dựng Pipeline khép kín Phase 1** | `src/pipelines/phase1.py` | Chạy thông suốt toàn bộ 8 công đoạn từ Raw Data đến Index và Report | `python script/run_phase1.py` hoàn thành mã thoát 0 |
| **Xác lập Baseline Benchmarks** | `data/results/baseline_metrics.json` | - Retrieval Hit Rate: **100%**<br>- Mean Token F1: **1.0000**<br>- LLM Judge Accuracy: **100%**<br>- Mean Judge Score: **5.00 / 5.0** | Xem nội dung file `data/results/baseline_metrics.json` |
| **Kiểm soát chất lượng dữ liệu GX 1.x** | `data/quality/baseline_quality_report.json` | 7/7 Expectations đạt chuẩn (Pass rate 100%) | Đọc kết quả `quality_report["success"] == True` |
| **Giám sát Freshness SLA** | `data/quality/freshness_report.json` | Tỷ lệ bài báo quá hạn đạt 1/24 (4.17% < 25%), gắn cờ `is_fresh = True` | Báo cáo `freshness_report["is_fresh"] == True` |
| **Sinh Báo cáo kỹ thuật tổng hợp** | `data/reports/phase1_report.md` | Báo cáo Markdown chi tiết 5 phần trình bày trực quan bảng đối soát | Kiểm tra file Markdown trong thư mục `data/reports/` |

**Output tiêu biểu:**
File [`data/reports/phase1_report.md`](file:///c:/AI20K/K4-L3A-Day10-36-Que-Toi/data/reports/phase1_report.md) được sinh tự động ngay sau khi script hoàn thành, tổng hợp đầy đủ Data Lineage, bảng số liệu đối chuẩn RAG và bằng chứng kiểm định chất lượng dữ liệu sạch ban đầu.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Trước Checkpoint 3, các module trong dự án (Ingestion, Cleaning, Quality check, ChromaDB, Testset) hoạt động độc lập và cần các lệnh kiểm thử riêng lẻ. Nếu không có một orchestration pipeline đồng nhất:
1. Quy trình chạy thủ công dễ phát sinh lỗi thứ tự (ví dụ: đánh index trước khi clean hoặc đánh giá trước khi nạp dữ liệu).
2. Dữ liệu không đảm bảo tính tái lập (Reproducibility) và tính bất biến (Idempotency).
3. Thiếu báo cáo kỹ thuật tổng hợp tự động để đối chiếu trước khi thực hiện tiêm lỗi dữ liệu ở Phase 2.

### Cách triển khai
Tôi đã triển khai hàm `main()` trong `src/pipelines/phase1.py` tuân theo kiến trúc 8 bước:
1. **Load Settings:** Đọc biến môi trường và thiết lập đường dẫn từ `core.config.load_settings()`.
2. **Raw Ingestion:** Đọc từ snapshot `crossref_records.json` (hỗ trợ offline và bảo toàn lineage), tự động fetch từ API nếu snapshot chưa tồn tại.
3. **Data Cleaning:** Tiền xử lý text qua `build_clean_dataframe()`, tính `age_days = (run_date - published).days`, tạo ngữ cảnh `text_for_embedding`.
4. **Persist Clean Data:** Lưu song song ra file `.csv` và `.json` tại thư mục `data/clean/`.
5. **ChromaDB Indexing:** Khởi tạo collection `papers-baseline` với embedding `sentence-transformers/all-MiniLM-L6-v2`, index 24 vector documents kèm metadata chi tiết.
6. **Benchmark Evaluation Set:** Nạp bộ test set chuẩn 5 câu hỏi qua 4 nhóm nghiệp vụ.
7. **RAG Evaluation:** Truy vấn QA system, đo lường `Retrieval Hit Rate`, `Token F1`, và sử dụng LLM Judge (Gemini 2.5 Flash) để chấm điểm đúng/sai.
8. **Observability & Report:** Chạy Great Expectations 1.x, tính Freshness SLA và xuất báo cáo markdown `phase1_report.md`.

### Input, Output và Contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Snapshot `data/raw/crossref_records.json`, cấu hình `.env` (`LLM_PROVIDER`, `GOOGLE_API_KEY`) |
| **Output** | `papers_clean.csv`, `papers-baseline` (ChromaDB), `baseline_metrics.json`, `phase1_report.md` |
| **Module phụ thuộc** | `ingestion/crossref.py`, `ingestion/cleaning.py`, `retrieval/index.py`, `observability/quality.py`, `evaluation/metrics.py` |
| **Module sử dụng output** | Phase 2 (`script/run_corruption_flow.py`) dùng `baseline_metrics.json` và `papers_clean.csv` làm chuẩn đối chiếu (Ground Truth) để đo mức độ suy giảm. |
| **Điều kiện lỗi xử lý** | - Mạng offline $\rightarrow$ Fallback snapshot local.<br>- Windows charmap error $\rightarrow$ UTF-8 encoding chuẩn hóa.<br>- LLM quota limit $\rightarrow$ Heuristic judge fallback. |

### Cách xác minh

```bash
python script/run_phase1.py
```

- **Kết quả mong đợi:** Toàn bộ 8 công đoạn in thông báo thành công, thoát với mã 0, sinh đủ 5 artifacts trong thư mục `data/`.
- **Kết quả thực tế:**
  ```text
  >>> KHOI CHAY BASELINE PIPELINE END-TO-END (PHASE 1) <<<
  [1/8] Da load settings (LLM: gemini, Model: gemini-2.5-flash)
  [2/8] Load ban ghi tho tu snapshot: .../crossref_records.json (24 ban ghi)
  [3/8] Tien xu ly, tinh toan age_days va text_for_embedding (24 dong)
  [4/8] Luu dataset sach vao papers_clean.csv va papers_clean.json
  [5/8] Xay dung vector index ChromaDB (collection: papers-baseline)
  [6/8] Khoi tao bo cau hoi benchmark (5 cau hoi)
  [7/8] Danh gia hieu nang: Hit Rate: 100.00%, Token F1: 1.0000, Judge Score: 5.00/5.0
  [8/8] Data Quality Gate (GX 1.x): PASS | Freshness SLA: PASS
  [*] Xuat bao cao markdown tai data/reports/phase1_report.md
  >>> HOAN THANH PHASE 1 PIPELINE! <<<
  ```

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn chiến lược nạp dữ liệu đầu vào cho baseline pipeline giữa:
  - *Phương án A:* Luôn gọi HTTP request tới Crossref REST API live mỗi lần chạy `run_phase1.py`.
  - *Phương án B:* Kiểm tra snapshot `data/raw/crossref_records.json`; nếu đã tồn tại và không bật cờ `REFRESH_SOURCE=1`, ưu tiên tái sử dụng snapshot thô cục bộ.
- **Phương án đã chọn:** **Phương án B**.
- **Lý do lựa chọn:**
  1. *Tính bất biến & Đối chứng khoa học (Reproducibility):* Khi đánh giá ảnh hưởng của Data Corruption ở Pha 5, việc giữ nguyên tập dữ liệu đầu vào ban đầu là bắt buộc để kết quả so sánh trước/sau không bị sai lệch do dữ liệu API bên ngoài thay đổi.
  2. *Tránh lỗi Rate Limit (HTTP 429):* API công cộng của Crossref thường xuyên trả về 429 khi gửi nhiều truy vấn liên tiếp trong giờ thực hành.
  3. *Tốc độ thực thi:* Tiết kiệm thời gian gọi mạng, giúp pipeline chạy nhanh chỉ trong vài giây.
- **Bằng chứng quyết định phù hợp:** Pipeline chạy trơn tru 100% không bị ngắt quãng bởi sự cố mạng, 24 bản ghi gốc được bảo toàn toàn vẹn qua cả 8 bước.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng / Lỗi nguyên văn:**
  ```text
  UnicodeEncodeError: 'charmap' codec can't encode characters in position 6-7: character maps to <undefined>
  ```
- **Lệnh / Bước tái hiện:** Chạy lệnh Python in văn bản có dấu tiếng Việt trên terminal Windows PowerShell mặc định.
- **Nguyên nhân gốc:** Bảng mã mặc định của Windows PowerShell thường là `cp1252`, không thể encode trực tiếp các ký tự UTF-8 tiếng Việt khi in ra `stdout`.
- **Cách xử lý:**
  1. Thiết lập biến môi trường `$env:PYTHONIOENCODING="utf-8"` trước khi chạy script.
  2. Chuẩn hóa các chuỗi log in tiến trình trong `src/pipelines/phase1.py` thành dạng không dấu (`Da load settings`, `Clean thanh cong`, `Luu dataset sach`) để đảm bảo code an toàn tuyệt đối trên bất kỳ môi trường Windows nào.
  3. Thêm cấu hình `sys.path.insert(0, ...)` vào `script/run_phase1.py` để script luôn tìm đúng package `src` mà không phụ thuộc vào việc đã cài đặt `-e .` hay chưa.
- **Cách xác minh sau khi sửa:** Chạy lại `python script/run_phase1.py`, chương trình chạy từ đầu đến cuối không xuất hiện bất kỳ lỗi encoding nào.
- **Bài học kỹ thuật:** Khi phát triển pipeline đa nền tảng (Cross-platform) chạy trên Windows/Linux, luôn phải lưu ý đến cơ chế mã hóa I/O và cấu trúc tìm kiếm module động (`sys.path`).

---

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   - Dữ liệu thô JSON từ Crossref API được tải về và lưu vào `crossref_response.json`.
   - Hàm `parse_crossref_payload` bóc tách các trường: DOI, title, abstract (loại bỏ XML tags `<jats:p>`), tác giả, chuyên ngành và ngày xuất bản $\rightarrow$ lưu thành đối tượng `PaperRecord` trong `crossref_records.json`.
   - Hàm `build_clean_dataframe` loại bỏ bản ghi rác, tính `age_days`, khử trùng lặp theo `paper_id` và ghép thành ngữ cảnh `text_for_embedding` (Title + Authors + Published + Categories + Summary).
   - Mô hình `all-MiniLM-L6-v2` chuyển đổi chuỗi văn bản thành vector 384 chiều và nạp cùng metadata vào ChromaDB collection `papers-baseline`.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   - Mỗi câu hỏi trong `test_set.json` có `ground_truth_doc_ids` (DOI chuẩn) và `ground_truth` (câu trả lời chuẩn).
   - **Retrieval Hit Rate:** Kiểm tra xem ít nhất 1 trong các tài liệu mà vector search trả về (`retrieved_doc_ids`) có nằm trong `ground_truth_doc_ids` hay không.
   - **Token F1 & LLM Judge:** Đo mức độ trùng khớp từ vựng giữa câu trả lời sinh ra và đáp án chuẩn, đồng thời nhờ LLM (Gemini) đóng vai trò thẩm phán chấm điểm từ 1–5 về tính đúng đắn ngữ nghĩa.

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - **Quality checks (GX 1.x):** Tập trung vào tính toàn vẹn cấu trúc và logic dữ liệu (Schema integrity: số dòng hợp lệ, không null các cột chính, tính duy nhất của ID, độ dài tối thiểu của tóm tắt).
   - **Freshness monitoring:** Giám sát khía cạnh thời gian (Temporal SLA). Dữ liệu có thể hoàn toàn hợp lệ về mặt cấu trúc nhưng đã "mốc meo" (quá 180 ngày). Nếu tỷ lệ bài cũ vượt 25%, hệ thống cảnh báo để kích hoạt luồng thu thập bài mới.

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   - Để đảm bảo nguyên tắc biến kiểm soát (Control Variable) trong khoa học thực nghiệm. Việc giữ cố định bộ câu hỏi và ground truth giúp mọi sự thay đổi về điểm số (Hit Rate, F1, Judge Score) phản ánh chính xác 100% tác động của chất lượng dữ liệu (Data Quality), loại trừ yếu tố thiên lệch do độ khó của câu hỏi khác nhau.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   - Dựa trên việc phục hồi dữ liệu sạch từ bản lưu trữ thô ban đầu `crossref_records.json` (tính Idempotent).
   - Minh chứng qua:
     - `data/results/repaired_metrics.json` có Hit Rate và Token F1 lấy lại mức cao tương đương `baseline_metrics.json`.
     - Quality Gate của Great Expectations 1.x chuyển từ trạng thái **FAIL** (khi bị corrupted) trở lại **PASS** (100% expectations thành công).

---

## 8. Phân tích kết quả

### Metrics chính

| Metric / Signal | Baseline (Thực tế đạt được) | Ngưỡng kỳ vọng bài lab | Nhận xét cá nhân |
| :--- | :---: | :---: | :--- |
| `retrieval_hit_rate` | **100.00%** | $\ge 80\%$ | ChromaDB với MiniLM truy xuất chính xác 100% tài liệu liên quan cho cả 5 câu hỏi benchmark. |
| `mean_token_f1` | **1.0000** | $\ge 0.50$ | Câu trả lời trích xuất chính xác tuyệt đối từng trường thông tin (Author, Date, Summary, Category). |
| `judge_accuracy` | **100.00%** | $\ge 80\%$ | Mô hình LLM Judge đánh giá tất cả các câu trả lời đều đúng về mặt ngữ nghĩa (`correct = True`). |
| `mean_judge_score` | **5.00 / 5.0** | $\ge 3.5$ | Điểm chất lượng tối đa từ LLM Evaluator. |
| Quality checks (GX 1.x) | **7/7 PASS (100%)** | 100% | Bảng dữ liệu sạch tuân thủ nghiêm ngặt các quy tắc về tính duy nhất, không null và độ dài text. |
| Freshness status | **PASS** | $\le 25\%$ stale | Chỉ có 1/24 bài báo cũ (>180 ngày), chiếm 4.17% (nằm sâu dưới ngưỡng cảnh báo 25%). |

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Kiến trúc Data Lineage & Raw Preservation:** Giữ nguyên vẹn dữ liệu thô ban đầu là chìa khóa then chốt để xây dựng hệ thống tự phục hồi (Self-healing). Nếu không có bản sao lưu thô, khi dữ liệu bị lỗi trong quá trình xử lý, hệ thống sẽ rơi vào trạng thái bế tắc.
2. **Data Observability sớm (Shift-Left Quality):** Great Expectations 1.x đóng vai trò như chốt kiểm dịch tự động. Việc chặn dữ liệu bẩn ngay trước tầng Vector Embedding sẽ ngăn chặn được hiện tượng AI Hallucination và Silent Failure nguy hiểm trong thực tế.
3. **Mối quan hệ mật thiết giữa Chất lượng Dữ liệu và Hiệu năng RAG:** Mô hình ngôn ngữ lớn (LLM) dù thông minh đến đâu cũng sẽ trả lời sai lệch nếu dữ liệu đầu vào bị thiếu trường, bị cắt ngắn tiêu đề hoặc lẫn ký tự rác (Garbage In, Garbage Out).

### Nếu có thêm thời gian
Tôi sẽ tích hợp thêm một Web Dashboard trực quan bằng **Streamlit** (tương ứng tiêu chí điểm thưởng B1) để hiển thị biểu đồ phân bổ độ tuổi bài báo theo thời gian thực và tự động kích hoạt còi cảnh báo khi tỷ lệ vi phạm vượt ngưỡng SLA.

---

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Đinh Mạnh Dũng  
**MSSV:** 02975  
**Ngày xác nhận:** 2026-09-25