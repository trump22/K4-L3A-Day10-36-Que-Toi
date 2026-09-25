from __future__ import annotations

from typing import Any


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Viet markdown report cho baseline phase."""
    from pathlib import Path

    out_file = Path(report_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    checks = quality.get("checks", [])
    quality_rows = []
    for c in checks:
        status_icon = "PASS" if c.get("success") else "FAIL"
        col = c.get("column") or "N/A"
        quality_rows.append(f"| `{c.get('expectation')}` | `{col}` | **{status_icon}** |")

    quality_table = "\n".join(quality_rows) if quality_rows else "| No checks recorded | - | - |"

    hit_rate = metrics.get("retrieval_hit_rate", 0.0)
    token_f1 = metrics.get("mean_token_f1", 0.0)
    judge_acc = metrics.get("judge_accuracy", 0.0)
    judge_score = metrics.get("mean_judge_score", 0.0)
    samples = metrics.get("samples", 0)

    report_content = f"""# Báo Cáo Kỹ Thuật Phase 1: Baseline Pipeline & Data Observability

## 1. Thông Tin Nguồn Dữ Liệu & Pipeline (Data Lineage)

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Nguồn API** | {source_summary.get('source_api', 'Crossref REST API')} |
| **Truy vấn (Query)** | `{source_summary.get('source_query', 'N/A')}` |
| **Số bản ghi thô (Raw Records)** | {source_summary.get('total_records', 'N/A')} |
| **Số bản ghi làm sạch (Clean Records)** | {source_summary.get('clean_records', 'N/A')} |
| **Mô hình Embedding** | `{source_summary.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')}` |
| **Vector Database** | ChromaDB (Collection: `{source_summary.get('collection_name', 'papers-baseline')}`) |
| **LLM Provider / Model** | {source_summary.get('llm_provider', 'N/A')} / {source_summary.get('model_name', 'N/A')} |

---

## 2. Kết Quả Đo Lường Baseline (Baseline Benchmarks)

Bảng chỉ số đánh giá hiệu năng hệ thống RAG trên dữ liệu sạch:

| Chỉ số (Metric) | Giá trị đạt được | Ngưỡng kỳ vọng | Trạng thái |
| :--- | :---: | :---: | :---: |
| **Số mẫu kiểm thử (Samples)** | {samples} | >= 5 | Đạt |
| **Retrieval Hit Rate** | **{hit_rate:.2%}** | >= 80% | {"Đạt" if hit_rate >= 0.8 else "Cần tối ưu"} |
| **Mean Token F1** | **{token_f1:.4f}** | >= 0.50 | {"Đạt" if token_f1 >= 0.5 else "Cần tối ưu"} |
| **LLM Judge Accuracy** | **{judge_acc:.2%}** | >= 80% | {"Đạt" if judge_acc >= 0.8 else "Cần tối ưu"} |
| **Mean LLM Judge Score** | **{judge_score:.2f} / 5.0** | >= 3.5 | {"Đạt" if judge_score >= 3.5 else "Cần tối ưu"} |

---

## 3. Trạm Kiểm Soát Chất Lượng Dữ Liệu (Great Expectations 1.x Gate)

- **Trạng thái chung:** {"**PASS (Đạt Chuẩn)**" if quality.get("success") else "**FAIL (Phát hiện lỗi)**"}
- **Tổng số Expectation kiểm tra:** {len(checks)}
- **Đạt:** {quality.get("passed", 0)} | **Không đạt:** {quality.get("failed", 0)}

| Expectation Name | Cột kiểm tra | Kết quả |
| :--- | :--- | :---: |
{quality_table}

---

## 4. Báo Cáo Độ Tươi Mới (Freshness SLA Monitoring)

- **Trạng thái Freshness SLA:** {"**PASS (Dữ liệu tươi mới)**" if freshness.get("is_fresh") else "**WARNING (Dữ liệu quá hạn)**"}
- **Bài báo mới nhất (Latest):** {freshness.get("latest_published", "N/A")}
- **Bài báo cũ nhất (Oldest):** {freshness.get("oldest_published", "N/A")}
- **Số bản ghi quá hạn (> 180 ngày):** {freshness.get("stale_rows", 0)} / {freshness.get("total_rows", 0)}

---

## 5. Kết Luận Checkpoint 3
Pipeline Phase 1 đã hoàn thành đầy đủ chu trình: Thu thập thô -> Tiền xử lý & Làm sạch -> Kiểm dịch Great Expectations 1.x -> Đánh chỉ mục ChromaDB -> Đánh giá đối chuẩn Benchmark (Hit Rate & Token F1). Toàn bộ Artifacts được lưu trữ đầy đủ và sẵn sàng cho kịch bản Stress-test ở Phase 2.
"""
    out_file.write_text(report_content.strip() + "\n", encoding="utf-8")



def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report so sanh baseline/corrupted/repaired."""
    raise NotImplementedError("Student task: implement corruption comparison report.")
