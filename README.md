# KYC Intelligence Copilot

Independent portfolio prototype supporting an AI-enabled AML/KYC transformation case study.

## What it demonstrates
- Structured KYC case intake
- Rule-based validation
- Explainable risk signals
- Confidence/risk-based routing
- Human-in-the-loop analyst review
- Policy retrieval using semantic embeddings when `sentence-transformers` is available
- Zero-key fallback mode so the demo can still run

## Positioning
This is an independent research prototype. It does not represent employment or client experience and does not make regulatory decisions.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The first run may download the `all-MiniLM-L6-v2` embedding model. If model loading is unavailable, the policy assistant uses a deterministic keyword fallback.

## Suggested portfolio story

Business problem -> KYC process analysis -> AI/automation opportunity -> working prototype -> human-in-the-loop controls -> KPI framework.

## Future extension
- PDF/image document ingestion with OCR
- entity-resolution model
- configurable business rules
- real policy-document upload and RAG
- case-level audit log
- analyst dashboard
- evaluation set for retrieval quality
