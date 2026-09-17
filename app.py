import streamlit as st

st.set_page_config(
    page_title="KYC Intelligence Copilot",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Demo data and lightweight rules
# -----------------------------

SAMPLE_CASE = {
    "case_id": "CASE-001",
    "name": "Aarav Mehta",
    "customer_type": "Individual",
    "country": "India",
    "document": "Passport",
    "document_status": "Valid",
    "occupation": "Business owner",
    "screening": "Potential match",
    "match_confidence": 72,
}

POLICY_DOCS = [
    {
        "title": "Screening Alerts",
        "keywords": ["screening", "match", "sanctions", "watchlist", "alert"],
        "text": (
            "A potential screening match is an alert, not proof of a true match. "
            "Analysts should compare available identifiers and relevant customer context "
            "before deciding the disposition."
        ),
    },
    {
        "title": "Identity Verification",
        "keywords": ["identity", "document", "passport", "verification", "kyc"],
        "text": (
            "Customer identity information should be checked against the required "
            "documentation. Incomplete, expired, or inconsistent information may require "
            "additional verification before the case is closed."
        ),
    },
    {
        "title": "Enhanced Review",
        "keywords": ["risk", "occupation", "business", "review", "information"],
        "text": (
            "Where available information creates unresolved review signals, the analyst "
            "may request additional information and document the rationale for the final "
            "case disposition."
        ),
    },
]


def run_checks(case):
    signals = []

    if case["document_status"] != "Valid":
        signals.append(
            ("High", "Identity document requires verification",
             "The current document status is not marked as valid.")
        )

    if case["screening"] == "Potential match":
        signals.append(
            ("Review", "Potential screening match",
             f"Screening returned a potential match with {case['match_confidence']}% match confidence. "
             "This requires contextual analyst review.")
        )

    if case["occupation"] == "Business owner":
        signals.append(
            ("Review", "Additional customer context may be useful",
             "Occupation information may warrant additional context during review.")
        )

    return signals


def retrieve_policy(question):
    words = set(re.findall(r"[a-zA-Z]+", question.lower()))
    scored = []
    for doc in POLICY_DOCS:
        score = len(words.intersection(doc["keywords"]))
        if score:
            scored.append((score, doc))

    if not scored:
        return POLICY_DOCS[0]

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


# -----------------------------
# Styling
# -----------------------------

st.markdown(
    """
    <style>
    :root {
        --ivory: #F7F1E8;
        --plum: #3D2637;
        --plum2: #5B3A50;
        --rose: #D8B4B8;
        --sage: #A9B7A2;
        --terra: #B56F55;
        --ink: #292329;
        --muted: #756B72;
        --card: #FFFDFC;
        --line: #E7DDD3;
    }

    .stApp {
        background: var(--ivory);
        color: var(--ink);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--plum) !important;
        letter-spacing: -0.02em;
    }

    .hero {
        background: var(--plum);
        color: white;
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 18px;
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: .14em;
        font-size: 11px;
        font-weight: 700;
        opacity: .72;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 34px;
        line-height: 1.1;
        font-weight: 750;
        margin: 0;
    }

    .hero-subtitle {
        font-size: 15px;
        line-height: 1.55;
        margin-top: 10px;
        max-width: 760px;
        opacity: .86;
    }

    .case-strip {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 18px;
    }

    .case-id {
        color: var(--plum);
        font-weight: 750;
        font-size: 14px;
    }

    .muted {
        color: var(--muted);
        font-size: 13px;
    }

    .metric {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 16px 18px;
        min-height: 92px;
    }

    .metric-label {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: .08em;
        font-size: 10px;
        font-weight: 750;
    }

    .metric-value {
        color: var(--plum);
        font-size: 20px;
        font-weight: 750;
        margin-top: 7px;
    }

    .section-label {
        color: var(--plum);
        text-transform: uppercase;
        letter-spacing: .11em;
        font-size: 11px;
        font-weight: 800;
        margin: 26px 0 10px 0;
    }

    .signal {
        background: var(--card);
        border: 1px solid var(--line);
        border-left: 4px solid var(--terra);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .signal-high {
        border-left-color: #9B4E4E;
    }

    .signal-title {
        color: var(--plum);
        font-weight: 750;
        font-size: 14px;
    }

    .signal-text {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
        margin-top: 4px;
    }

    .policy {
        background: #F0E8DF;
        border: 1px solid #DFD0C1;
        border-radius: 14px;
        padding: 17px 19px;
    }

    .policy-title {
        color: var(--plum);
        font-weight: 800;
        margin-bottom: 7px;
    }

    .policy-text {
        color: var(--ink);
        font-size: 13px;
        line-height: 1.6;
    }

    .footer-note {
        color: var(--muted);
        font-size: 11px;
        line-height: 1.5;
        margin-top: 26px;
    }

    div[data-testid="stForm"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 18px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header
# -----------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AML / KYC Decision Support Prototype</div>
        <div class="hero-title">KYC Intelligence Copilot</div>
        <div class="hero-subtitle">
            A lightweight analyst workflow that structures a KYC case, surfaces explainable
            review signals, retrieves relevant policy guidance, and keeps the final decision
            with the human analyst.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="case-strip">
        <span class="case-id">{SAMPLE_CASE['case_id']}</span>
        <span class="muted"> &nbsp; | &nbsp; Fictional demonstration case &nbsp; | &nbsp;
        Customer: {SAMPLE_CASE['name']}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Summary metrics
# -----------------------------

signals = run_checks(SAMPLE_CASE)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        '<div class="metric"><div class="metric-label">Identity</div>'
        '<div class="metric-value">✓ Verified</div></div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        '<div class="metric"><div class="metric-label">Screening</div>'
        '<div class="metric-value">⚠ Review</div></div>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f'<div class="metric"><div class="metric-label">Review signals</div>'
        f'<div class="metric-value">{len(signals)} identified</div></div>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        '<div class="metric"><div class="metric-label">Routing</div>'
        '<div class="metric-value">Analyst review</div></div>',
        unsafe_allow_html=True,
    )

# -----------------------------
# Main workspace
# -----------------------------

left, right = st.columns([1, 1.15], gap="large")

with left:
    st.markdown('<div class="section-label">Customer profile</div>', unsafe_allow_html=True)

    profile = [
        ("Name", SAMPLE_CASE["name"]),
        ("Customer type", SAMPLE_CASE["customer_type"]),
        ("Country", SAMPLE_CASE["country"]),
        ("Document", SAMPLE_CASE["document"]),
        ("Document status", SAMPLE_CASE["document_status"]),
        ("Occupation", SAMPLE_CASE["occupation"]),
        ("Screening", SAMPLE_CASE["screening"]),
    ]

    for label, value in profile:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;
                        padding:9px 0;border-bottom:1px solid #E7DDD3;">
                <span class="muted">{label}</span>
                <span style="font-weight:700;color:#3D2637;">{value}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Review signals</div>', unsafe_allow_html=True)

    for severity, title, text in signals:
        cls = "signal-high" if severity == "High" else "signal"
        st.markdown(
            f"""
            <div class="signal {cls}">
                <div class="signal-title">{severity} · {title}</div>
                <div class="signal-text">{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with right:
    st.markdown('<div class="section-label">Policy assist</div>', unsafe_allow_html=True)

    question = st.text_input(
        "Ask a policy question",
        value="What should an analyst do with a potential screening match?",
        label_visibility="collapsed",
    )

    policy = retrieve_policy(question)

    st.markdown(
        f"""
        <div class="policy">
            <div class="policy-title">{policy['title']}</div>
            <div class="policy-text">{policy['text']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Human review</div>', unsafe_allow_html=True)

    with st.form("review_form"):
        disposition = st.selectbox(
            "Disposition",
            [
                "Request more information",
                "Clear after analyst review",
                "Escalate for enhanced review",
            ],
        )

        confidence = st.slider("Analyst confidence", 0, 100, 70, 5)

        rationale = st.text_area(
            "Rationale",
            value="Potential screening match requires contextual review before final disposition.",
            height=100,
        )

        submitted = st.form_submit_button("Save review", use_container_width=True)

        if submitted:
            st.success(
                f"Review captured: {disposition}. "
                f"Analyst confidence: {confidence}%."
            )

st.markdown(
    """
    <div class="footer-note">
        <strong>Prototype note:</strong> This is a fictional decision-support demonstration,
        not an AML/KYC compliance engine. The rules and policy content are illustrative.
        Production use would require approved policies, governed data sources, validated
        screening providers, audit controls, and appropriate compliance oversight.
    </div>
    """,
    unsafe_allow_html=True,
)
