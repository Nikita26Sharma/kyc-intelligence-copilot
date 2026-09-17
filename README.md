# KYC Intelligence Copilot

**AML/KYC Decision Support Prototype**

A small, portfolio-ready Streamlit prototype showing how an analyst-facing KYC workflow can combine structured case information, explainable review signals, lightweight policy retrieval, and human-in-the-loop decision making.

## Live demo

Add the Streamlit URL here after deployment.

## What the prototype demonstrates

- Structured KYC case intake
- Basic identity and screening checks
- Explainable review signals
- Lightweight policy retrieval from a local knowledge base
- Analyst disposition and rationale
- Human-in-the-loop review rather than automated case closure

## Why this is intentionally lightweight

This is a **case-study prototype**, not a production AML/KYC platform.

The demo avoids external APIs, databases, paid services, and large ML dependencies so it can be deployed quickly on Streamlit Community Cloud.

A production implementation could extend the workflow with:

- Approved sanctions / PEP screening providers
- Governed policy-document RAG
- Document/OCR verification
- Case-management integration
- Audit trails and role-based access
- Model and rule validation
- Compliance controls and monitoring

## Architecture

```text
Fictional KYC case
        |
        v
  Automated checks
        |
        v
 Explainable signals
        |
        +------> Policy assist
        |
        v
 Analyst review
        |
        v
 Final disposition
```

## Tech stack

- Python
- Streamlit
- Pandas

The current prototype uses deterministic rules and a small local policy knowledge base. This keeps the demo reproducible and dependency-light.

## Important limitation

The customer, screening result, policy text, and review outputs are fictional and illustrative. Nothing in this prototype should be treated as regulatory advice or as a validated compliance decision engine.

## Run locally

If you already have Python:

```bash
pip install -r requirements.txt
streamlit run app.py
```

No local setup is required for the hosted version.

## Portfolio positioning

This project is intended to demonstrate **business analysis, process design, risk thinking, workflow automation, and human-in-the-loop product thinking**, rather than full-stack engineering depth.
