
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# Optional semantic retrieval with sentence-transformers.
# The app still runs in DEMO mode if the model/API is unavailable.
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except Exception:
    EMBEDDINGS_AVAILABLE = False

st.set_page_config(
    page_title="KYC Intelligence Copilot",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- BRAND --------------------
INK = "#252331"
IVORY = "#F7F3EC"
PLUM = "#5B405A"
TERRACOTTA = "#C8795E"
SAGE = "#879A87"
ROSE = "#C99AA5"
SAND = "#E7DED2"
GREY = "#686870"

st.markdown(f"""
<style>
html, body, [class*="css"] {{
    font-family: Inter, Aptos, sans-serif;
}}
.stApp {{
    background: {IVORY};
    color: {INK};
}}
section[data-testid="stSidebar"] {{
    background: {PLUM};
}}
section[data-testid="stSidebar"] * {{
    color: white !important;
}}
h1, h2, h3 {{
    color: {INK};
    letter-spacing: -0.02em;
}}
.hero {{
    background: {PLUM};
    color: white;
    padding: 28px 32px;
    border-radius: 18px;
    margin-bottom: 20px;
}}
.hero .eyebrow {{
    color: {ROSE};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .12em;
}}
.hero h1 {{
    color: white;
    font-size: 34px;
    margin: 8px 0;
}}
.hero p {{
    color: #eee7ee;
    font-size: 15px;
    max-width: 900px;
}}
.card {{
    background: white;
    border: 1px solid {SAND};
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
}}
.label {{
    color: {GREY};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .09em;
}}
.value {{
    color: {INK};
    font-size: 25px;
    font-weight: 750;
    margin-top: 5px;
}}
.insight {{
    background: #F0E8EF;
    border-left: 5px solid {PLUM};
    padding: 14px 18px;
    border-radius: 8px;
}}
.warning {{
    background: #F8EEE8;
    border-left: 5px solid {TERRACOTTA};
    padding: 14px 18px;
    border-radius: 8px;
}}
.success {{
    background: #EEF3EE;
    border-left: 5px solid {SAGE};
    padding: 14px 18px;
    border-radius: 8px;
}}
.small {{
    color: {GREY};
    font-size: 12px;
}}
div[data-testid="stMetric"] {{
    background: white;
    border: 1px solid {SAND};
    padding: 12px;
    border-radius: 12px;
}}
.stButton > button {{
    border-radius: 10px;
    border: 1px solid {PLUM};
}}
</style>
""", unsafe_allow_html=True)

# -------------------- SAMPLE CASE --------------------
SAMPLE_CASE = {
    "customer_name": "Aarav Mehta",
    "customer_type": "Individual",
    "country": "India",
    "document_type": "Passport",
    "document_status": "Valid",
    "dob": "14 Aug 1988",
    "address": "New Delhi, India",
    "occupation": "Business owner",
    "expected_activity": "Domestic consulting and business transactions",
    "screening_result": "Potential match requiring analyst review",
    "match_confidence": 0.72,
    "risk_flags": ["Name similarity", "Higher-risk occupation context"],
}

POLICY_DOCS = [
    ("CDD - Identity Verification",
     "Customer identification should establish reasonable confidence in the customer's identity using reliable and independent source information. Missing, inconsistent or low-confidence identity information should be resolved before completion."),
    ("Risk-Based Approach",
     "Customer due diligence should be proportionate to the risk presented by the customer, product, geography and relationship. Higher-risk situations may require enhanced due diligence and additional scrutiny."),
    ("Screening Alerts",
     "A potential screening match is an alert, not proof of a true match. Analysts should compare available identifiers and relevant context before dispositioning the alert."),
    ("Human Review",
     "Materially ambiguous or higher-risk cases should be escalated to an appropriately authorised reviewer. Automated recommendations should not remove required human decision-making."),
    ("Audit Trail",
     "The review record should retain relevant inputs, checks performed, analyst actions, overrides and the rationale for the final decision so that the case can be reconstructed."),
]

# -------------------- FUNCTIONS --------------------
def extract_fields(text):
    fields = {}
    patterns = {
        "customer_name": r"(?:Name|Customer Name)\s*[:\-]\s*([^\n]+)",
        "document_type": r"(?:Document Type)\s*[:\-]\s*([^\n]+)",
        "country": r"(?:Country)\s*[:\-]\s*([^\n]+)",
        "dob": r"(?:DOB|Date of Birth)\s*[:\-]\s*([^\n]+)",
        "address": r"(?:Address)\s*[:\-]\s*([^\n]+)",
        "occupation": r"(?:Occupation)\s*[:\-]\s*([^\n]+)",
        "screening_result": r"(?:Screening Result)\s*[:\-]\s*([^\n]+)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.I)
        if m:
            fields[key] = m.group(1).strip()
    return fields

def run_rules(case):
    rules = []
    if case.get("document_status", "Valid").lower() == "valid":
        rules.append(("PASS", "Document validity", "Document is marked valid."))
    else:
        rules.append(("FAIL", "Document validity", "Document requires remediation."))

    if case.get("customer_name"):
        rules.append(("PASS", "Customer name present", "Required identity field is available."))
    else:
        rules.append(("FAIL", "Customer name present", "Customer identity field is missing."))

    screening = case.get("screening_result", "").lower()
    if "potential" in screening or "match" in screening:
        rules.append(("REVIEW", "Screening alert", "Potential match requires contextual analyst review."))
    else:
        rules.append(("PASS", "Screening alert", "No potential match indicated in the case input."))

    return rules

def risk_score(case):
    score = 20
    flags = []
    if "Potential" in case.get("screening_result", "") or "match" in case.get("screening_result", "").lower():
        score += 35
        flags.append("Potential screening match")
    if case.get("match_confidence", 0) >= 0.7:
        score += 20
        flags.append("Material name-match confidence")
    if case.get("occupation", "").lower() in {"business owner", "cash intensive"}:
        score += 10
        flags.append("Occupation context requires additional context")
    return min(score, 100), flags

@st.cache_resource
def load_model():
    if not EMBEDDINGS_AVAILABLE:
        return None
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None

def retrieve_policy(query, top_k=3):
    model = load_model()
    docs = [x[1] for x in POLICY_DOCS]
    if model is not None:
        emb = model.encode(docs, normalize_embeddings=True)
        q = model.encode([query], normalize_embeddings=True)[0]
        scores = emb @ q
        idx = np.argsort(scores)[::-1][:top_k]
        return [(POLICY_DOCS[i][0], POLICY_DOCS[i][1], float(scores[i])) for i in idx], "semantic embeddings"
    # deterministic fallback for a zero-key demo
    q = set(re.findall(r"\w+", query.lower()))
    scored = []
    for title, doc in POLICY_DOCS:
        words = set(re.findall(r"\w+", doc.lower()))
        overlap = len(q & words) / max(1, len(q))
        scored.append((title, doc, overlap))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k], "keyword fallback"

# -------------------- SIDEBAR --------------------
st.sidebar.markdown("## KYC Intelligence Copilot")
st.sidebar.markdown("**Prototype**\n\nAI-assisted KYC review for analyst decision support.")
st.sidebar.divider()
mode = st.sidebar.radio("Case mode", ["Demo case", "Upload case text"])
st.sidebar.markdown("---")
st.sidebar.caption("Independent portfolio prototype\nIllustrative data only")

# -------------------- HEADER --------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">INDEPENDENT PROTOTYPE · AML / KYC</div>
  <h1>KYC Intelligence Copilot</h1>
  <p>Turn customer information into structured review signals, route exceptions intelligently, and give analysts grounded policy context before a human decision.</p>
</div>
""", unsafe_allow_html=True)

if mode == "Upload case text":
    uploaded = st.file_uploader("Upload a text-based case file", type=["txt", "csv"])
    if uploaded:
        raw = uploaded.read().decode("utf-8", errors="ignore")
        extracted = extract_fields(raw)
        case = {**SAMPLE_CASE, **extracted}
        st.success("Case information extracted into the review workspace.")
    else:
        case = SAMPLE_CASE
else:
    case = SAMPLE_CASE

# -------------------- CASE SUMMARY --------------------
score, flags = risk_score(case)
routing = "Analyst review" if score >= 40 else "Streamlined processing"

c1, c2, c3, c4 = st.columns(4)
for col, label, value in [
    (c1, "CASE", "KYC-001"),
    (c2, "RISK SIGNAL", f"{score}/100"),
    (c3, "ROUTING", routing),
    (c4, "AI MODE", "Assist + explain"),
]:
    with col:
        st.markdown(f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)

st.write("")
left, right = st.columns([1.05, 1.0])

with left:
    st.subheader("Customer profile")
    profile = pd.DataFrame([
        ["Customer", case.get("customer_name", "Not extracted")],
        ["Type", case.get("customer_type", "Individual")],
        ["Country", case.get("country", "Not extracted")],
        ["Document", case.get("document_type", "Not extracted")],
        ["DOB", case.get("dob", "Not extracted")],
        ["Occupation", case.get("occupation", "Not extracted")],
        ["Address", case.get("address", "Not extracted")],
    ], columns=["Field", "Value"])
    st.dataframe(profile, hide_index=True, use_container_width=True)

with right:
    st.subheader("Rules & risk signals")
    for status, rule, detail in run_rules(case):
        icon = "✓" if status == "PASS" else ("!" if status == "REVIEW" else "×")
        st.markdown(f"**{icon} {rule}**  \n<span class='small'>{detail}</span>", unsafe_allow_html=True)
    if flags:
        st.markdown(f'<div class="warning"><b>Escalation signals</b><br/>{"; ".join(flags)}</div>', unsafe_allow_html=True)

st.write("")
st.markdown('<div class="insight"><b>Routing rationale</b><br/>The prototype does not make a final compliance decision. A potential screening match and material matching confidence route the case to an analyst for contextual review.</div>', unsafe_allow_html=True)

# -------------------- RAG / POLICY ASSISTANT --------------------
st.write("")
st.subheader("Policy Assist")
st.caption("Retrieval is grounded in the prototype's policy knowledge base. The analyst remains responsible for the decision.")

query = st.text_input(
    "Ask a KYC review question",
    value="What should an analyst do with a potential screening match?"
)

if query:
    results, retrieval_mode = retrieve_policy(query)
    st.caption(f"Retrieval mode: {retrieval_mode}")
    for title, doc, score_value in results:
        st.markdown(f"**{title}**  ·  relevance {score_value:.2f}")
        st.markdown(f"> {doc}")

# -------------------- HUMAN REVIEW --------------------
st.write("")
st.subheader("Analyst review")
review_col1, review_col2 = st.columns([1, 1])
with review_col1:
    decision = st.selectbox(
        "Analyst disposition",
        ["Pending review", "Clear after review", "Escalate for enhanced due diligence", "Request more information"]
    )
with review_col2:
    reviewer_confidence = st.slider("Reviewer confidence", 0, 100, 70)

rationale = st.text_area(
    "Decision rationale",
    placeholder="Record the evidence reviewed, the reasoning, and any override of the AI-assisted routing."
)

if st.button("Save review decision", type="primary"):
    if decision == "Pending review" or not rationale.strip():
        st.warning("Complete the disposition and rationale before saving.")
    else:
        st.success("Review decision captured in the prototype audit trail.")
        st.json({
            "case_id": "KYC-001",
            "ai_risk_signal": score,
            "routing": routing,
            "analyst_disposition": decision,
            "reviewer_confidence": reviewer_confidence,
            "rationale": rationale,
        })

st.markdown("---")
st.caption("Prototype note: This is an independent research artifact using illustrative data. It is not a production AML/KYC system and does not provide legal or regulatory advice.")
