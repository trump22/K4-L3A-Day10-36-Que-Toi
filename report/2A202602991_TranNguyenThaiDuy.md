# Báo Cáo Vai Trò Cá Nhân - Trần Nguyễn Thái Duy

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| :--- | :--- |
| **Họ và tên** | Trần Nguyễn Thái Duy |
| **MSSV** | 2A202602991 |
| **Khóa / Lớp** | K4 / L3A |
| **Tên nhóm** | Nhóm 36 - Quê Tôi |
| **Vai trò chính** | RAG, Vector Index và Benchmark Test Set (Pha 3) |
| **Repository** | https://github.com/trump22/K4-L3A-Day10-36-Que-Toi.git |
| **Ngày hoàn thành** | 2026-09-25 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module / Deliverable | File / Hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| Embedding backend | `src/retrieval/embeddings.py`: `MiniLMEmbeddings`, `_load_model` | `text_for_embedding` và query | Vector normalized từ `sentence-transformers/all-MiniLM-L6-v2` | Hoàn thành |
| ChromaDB vector index | `src/retrieval/index.py`: `LocalEmbeddingIndex.build`, `_build_documents`, `search` | Clean/corrupted/repaired DataFrame | Ba collection và embedding manifests | Hoàn thành |
| Document metadata contract | `src/retrieval/index.py`: `_build_documents` | Paper rows | `record_id`, DOI, title, content và metadata truy vấn | Hoàn thành |
| Benchmark test set | `src/evaluation/testset.py`: `build_test_set`, `load_or_create_test_set` | Clean DataFrame | `data/eval/test_set.json` gồm 5 câu hỏi và ground truth | Hoàn thành |
| QA retrieval handoff | `src/retrieval/qa.py`: `answer_question` | Question và vector index | Retrieved IDs, contexts, titles và answer | Hoàn thành |

Ownership của phần này là bảo đảm dữ liệu sạch được chuyển thành vector có định danh ổn định, truy vấn được bằng top-k và có bộ benchmark cố định để đánh giá công bằng giữa baseline, corrupted và repaired.

## 3. Kết quả theo vai trò

| Nhiệm vụ | File / Hàm / Artifact | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Load embedding model | `src/retrieval/embeddings.py::MiniLMEmbeddings` | Dùng model `all-MiniLM-L6-v2`, normalize embedding | Manifest ghi đúng model name |
| Build baseline index | `LocalEmbeddingIndex.build()` | Collection `papers-baseline` với 24 documents | `data/embeddings/papers_embeddings.json`, `data/chroma/` |
| Tách collection theo trạng thái | `_derive_collection_name()` | `papers-baseline`, `papers-corrupted`, `papers-repaired` | Ba manifest và các metrics tương ứng |
| Chuẩn hóa document | `_build_documents()` | `record_id = paper_id::index`, metadata gồm DOI/title/date/authors/categories/summary | Manifest documents |
| Sinh benchmark | `build_test_set()` | 5 câu: summary, authors, date, category, multi-hop | `data/eval/test_set.json` |
| Handoff cho QA | `answer_question()` | Exact title lookup kết hợp semantic search, top-k context | `data/results/*_answers.json` |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Embedding và index

`MiniLMEmbeddings` cache model bằng `lru_cache`, cung cấp `embed_documents()` và `embed_query()`. Các vector được normalize trước khi đưa vào ChromaDB. `LocalEmbeddingIndex.build()` tạo PersistentClient, xóa collection cùng tên nếu tồn tại, tạo collection cosine, add IDs/documents/metadatas và ghi manifest JSON.

Mỗi document có `record_id` ổn định dạng `paper_id::index`. Nội dung vector là toàn bộ `text_for_embedding`; metadata giữ các trường cần cho trả lời như `authors_joined`, `published`, `categories_joined` và `summary`. Cách tách collection theo output path giúp ba trạng thái không ghi đè lẫn nhau.

### Search và QA

`search()` embed query rồi gọi ChromaDB với `top_k` mặc định 4, chuyển cosine distance thành score và trả về `SearchResult`. `answer_question()` ưu tiên exact title lookup nếu câu hỏi chứa title trong dấu nháy, sau đó bổ sung semantic results đã deduplicate. QA extractor lấy authors, published date, categories hoặc first sentence của summary từ metadata.

### Benchmark test set

`build_test_set()` lấy 5 record đầu của clean DataFrame và tạo ground truth trực tiếp từ dữ liệu thật:

1. Summary của paper thứ nhất.
2. Authors của paper thứ hai.
3. Published date của paper thứ ba.
4. Categories của paper thứ tư.
5. Multi-hop summary liên hệ paper thứ năm với paper thứ nhất.

Mỗi item có `id`, `question_type`, `question`, `ground_truth` và `ground_truth_doc_ids`. `load_or_create_test_set()` chỉ tái tạo khi file không tồn tại hoặc không có đúng 5 item, nhờ đó baseline/corrupted/repaired dùng cùng đề và ground truth.

## 5. Kết quả thực tế

### Index và evaluation artifacts

| Artifact | Giá trị |
| :--- | :--- |
| Clean documents indexed | 24 |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Chroma collections | `papers-baseline`, `papers-corrupted`, `papers-repaired` |
| Evaluation samples | 5 |
| Retrieval `top_k` | 4 |
| Question types | `summary`, `authors`, `date`, `category`, `multi_hop` |

### Metrics trên cùng test set

| Metric | Baseline | Corrupted | Repaired |
| :--- | ---: | ---: | ---: |
| `retrieval_hit_rate` | 1.000 | 0.000 | 1.000 |
| `mean_token_f1` | 1.000 | 0.548 | 1.000 |
| `judge_accuracy` | 1.000 | 0.600 | 1.000 |
| `mean_judge_score` | 5.00 | 3.00 | 5.00 |

Baseline truy xuất đúng ground-truth cho cả 5 câu hỏi. Khi corrupted index được build từ dữ liệu bị drop/truncate/noise, không có ground-truth document nào được hit trong test set hiện tại và hit rate về 0%. Sau repair từ raw snapshot, index repaired trả lại hit rate 100% và Token F1 1.000.

## 6. Quyết định kỹ thuật quan trọng

Nhóm chọn ChromaDB PersistentClient với ba collection riêng thay vì dùng chung một collection rồi thay thế dữ liệu. Cách này giúp so sánh độc lập baseline, corrupted và repaired, đồng thời manifest lưu lại model, collection name, persist path và documents.

Test set được tạo trước corruption và giữ nguyên trong cả ba lần evaluate. Đây là biến kiểm soát quan trọng: nếu tạo lại câu hỏi sau khi dữ liệu bị hỏng, metric có thể thay đổi do đề khác thay vì do index khác.

Một giới hạn cần ghi nhận là test set lấy 5 record đầu sau khi clean sort theo ngày mới nhất. Corruption cũng drop đúng 5 record mới nhất, nên kết quả hit rate corrupted phản ánh cả thiết kế test set. Cần chọn test documents rải đều để đánh giá tổng quát hơn.

## 7. Blocker và cách xử lý

- **Blocker:** Môi trường ban đầu chưa có pandas, ChromaDB và sentence-transformers; Python mặc định 3.14 không phù hợp constraint `<3.14`.
- **Cách xử lý:** Dùng Python 3.13, cài dependencies trong `.venv`, tải model MiniLM và chạy với `LLM_PROVIDER=mock` để tách phần vector/index khỏi API key.
- **Xác minh:** Baseline và corruption flow đều build được index và sinh manifest/answers/metrics đầy đủ.

## 8. Bài học và hướng cải thiện

1. Document ID phải ổn định từ DOI, vì evaluation dùng `ground_truth_doc_ids` để đo retrieval hit.
2. Metadata trong vector store quan trọng không kém embedding content, vì QA trả lời date/authors/category trực tiếp từ metadata.
3. Cần kiểm tra cả exact lookup và semantic search; exact lookup làm benchmark ổn định hơn với câu hỏi chứa nguyên title, còn semantic search là đường đi thực tế cho query không khớp tuyệt đối.
4. Có thể mở rộng benchmark lên nhiều câu hỏi và thêm negative queries, rồi chạy ablation từng corruption để đo riêng tác động của index content và metadata.

## 9. Cam kết của thành viên

- [x] Nội dung phản ánh phần việc embedding, ChromaDB, QA retrieval và test set.
- [x] Các metric được đối chiếu với artifacts trong `data/results/`.
- [x] Không đưa API key, token hoặc secret vào báo cáo.
- [x] Có thể giải thích cách document ID, metadata và ground truth liên kết với nhau.

**Họ và tên:** Trần Nguyễn Thái Duy  
**MSSV:** 2A202602991  
**Ngày xác nhận:** 2026-09-25