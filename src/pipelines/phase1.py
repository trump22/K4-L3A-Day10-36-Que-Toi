from __future__ import annotations

from pathlib import Path
import pandas as pd

from core.config import load_settings
from core.utils import now_utc, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import load_or_create_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.agent import build_agent, run_agent_question
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    """Xay dung baseline pipeline end-to-end cho Phase 1."""
    print("=" * 60)
    print(">>> KHOI CHAY BASELINE PIPELINE END-TO-END (PHASE 1) <<<")
    print("=" * 60)

    # 1. Load settings
    settings = load_settings()
    print(f"[1/8] Da load settings (LLM: {settings.llm_provider}, Model: {settings.model_name})")

    # 2. Load hoac fetch raw records
    if settings.paths.raw_records_json.exists() and not settings.refresh_source:
        print(f"[2/8] Load ban ghi tho tu snapshot: {settings.paths.raw_records_json}")
        records = load_raw_records(settings.paths.raw_records_json)
    else:
        print(f"[2/8] Thu thap du lieu tho tu {settings.source_api}...")
        records = fetch_source_records(settings)
    print(f"      -> Da nap {len(records)} ban ghi tho.")

    # 3. Clean data
    print("[3/8] Tien xu ly, tinh toan age_days va text_for_embedding...")
    clean_df = build_clean_dataframe(records, run_date=now_utc())
    print(f"      -> Clean thanh cong {len(clean_df)} dong du lieu.")

    # 4. Save clean CSV/JSON
    print(f"[4/8] Luu dataset sach vao {settings.paths.clean_csv} va {settings.paths.clean_json}...")
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(settings.paths.clean_csv, index=False)
    clean_df.to_json(settings.paths.clean_json, orient="records", indent=2)

    # 5. Build Chroma index
    print(f"[5/8] Xay dung vector index ChromaDB (collection: {settings.baseline_collection_name})...")
    index = LocalEmbeddingIndex.build(
        df=clean_df,
        settings=settings,
        embeddings_output_path=settings.paths.embeddings_json,
    )
    print(f"      -> Da index {len(clean_df)} tai lieu vao ChromaDB tai {settings.paths.chroma_dir}.")

    # 6. Tao hoac load evaluation set
    print(f"[6/8] Khoi tao bo cau hoi benchmark tai {settings.paths.eval_testset}...")
    test_set = load_or_create_test_set(
        df=clean_df,
        output_path=settings.paths.eval_testset,
        force_refresh=settings.refresh_test_set,
    )
    print(f"      -> Bo test set san sang voi {len(test_set)} cau hoi.")

    # 7. Evaluate
    print("[7/8] Danh gia hieu nang Baseline RAG tren benchmark test set...")
    bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )
    print(f"      -> Retrieval Hit Rate : {bundle.summary.get('retrieval_hit_rate', 0.0):.2%}")
    print(f"      -> Mean Token F1      : {bundle.summary.get('mean_token_f1', 0.0):.4f}")
    print(f"      -> LLM Judge Accuracy : {bundle.summary.get('judge_accuracy', 0.0):.2%}")
    print(f"      -> Mean Judge Score   : {bundle.summary.get('mean_judge_score', 0.0):.2f} / 5.0")

    # 8. Run quality checks va freshness report
    print("[8/8] Kiem tra chat luong du lieu (GX 1.x) va Freshness SLA...")
    quality_report = run_data_quality_checks(
        df=clean_df,
        settings=settings,
        report_name="baseline_quality_report",
    )
    freshness_report = build_freshness_report(
        df=clean_df,
        settings=settings,
        report_path=settings.paths.freshness_report,
    )
    print(f"      -> Data Quality Gate (GX 1.x) : {'PASS' if quality_report.get('success') else 'FAIL'}")
    print(f"      -> Freshness SLA Status       : {'PASS' if freshness_report.get('is_fresh') else 'WARNING'}")

    # 9. Tao markdown report
    print(f"[*] Xuat bao cao markdown tai {settings.paths.baseline_report}...")
    source_summary = {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "total_records": len(records),
        "clean_records": len(clean_df),
        "embedding_model": settings.embedding_model,
        "collection_name": settings.baseline_collection_name,
        "llm_provider": settings.llm_provider,
        "model_name": settings.model_name,
    }
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=bundle.summary,
        quality=quality_report,
        freshness=freshness_report,
    )

    # 10. Demo agent tren sample question (neu co)
    try:
        agent = build_agent(settings=settings, index=index)
        sample_q = test_set[0]["question"] if test_set else "What are the main findings?"
        sample_a = run_agent_question(agent, sample_q)
        demo_record = [{"question": sample_q, "answer": sample_a}]
        write_json(settings.paths.demo_answers, demo_record)
        print(f"      -> Demo agent answer da luu vao {settings.paths.demo_answers}")
    except Exception as exc:
        print(f"      (Agent demo bo qua: {exc})")

    print("\n" + "=" * 60)
    print(">>> HOAN THANH PHASE 1 PIPELINE! <<<")
    print(f"Artifacts tao ra:")
    print(f" 1. Clean CSV:        {settings.paths.clean_csv}")
    print(f" 2. Chroma DB:        {settings.paths.chroma_dir}")
    print(f" 3. Test Set:         {settings.paths.eval_testset}")
    print(f" 4. Baseline Metrics: {settings.paths.baseline_metrics}")
    print(f" 5. Phase 1 Report:   {settings.paths.baseline_report}")
    print("=" * 60)
