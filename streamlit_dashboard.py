import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CloudCore Churn Prediction",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background-color: #ffffff;
    color: #111827;
}

/* Header */
.dash-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 100%);
    border-bottom: 1px solid #2a2f3e;
    padding: 2.5rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
}
.dash-title {
    font-size: 2.8rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin: 0;
}
.dash-subtitle {
    font-size: 1rem;
    color: #6b7280;
    margin: 0.2rem 0 0 0;
    font-family: 'DM Mono', monospace;
}

/* Metric cards */
.metric-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.high::before     { background: #ef4444; }
.metric-card.medium::before   { background: #f59e0b; }
.metric-card.low::before      { background: #10b981; }
.metric-card.total::before    { background: #3b82f6; }
.metric-card.cleared::before  { background: #6b7280; }
.metric-card.approved::before { background: #8b5cf6; }

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1;
    margin: 0.5rem 0 0.25rem 0;
}
.metric-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6b7280;
    font-weight: 500;
}
.metric-sub {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 0.25rem;
    font-family: 'DM Mono', monospace;
}
.high     .metric-value { color: #ef4444; }
.medium   .metric-value { color: #f59e0b; }
.low      .metric-value { color: #10b981; }
.total    .metric-value { color: #3b82f6; }
.cleared  .metric-value { color: #6b7280; }
.approved .metric-value { color: #8b5cf6; }

/* Risk badges */
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-high   { background: rgba(239,68,68,0.15);  color: #dc2626; border: 1px solid rgba(239,68,68,0.3); }
.badge-medium { background: rgba(245,158,11,0.15); color: #d97706; border: 1px solid rgba(245,158,11,0.3); }
.badge-low    { background: rgba(16,185,129,0.15); color: #059669; border: 1px solid rgba(16,185,129,0.3); }
.badge-cleared  { background: rgba(107,114,128,0.12); color: #4b5563; border: 1px solid rgba(107,114,128,0.3); }
.badge-approved { background: rgba(139,92,246,0.12);  color: #7c3aed; border: 1px solid rgba(139,92,246,0.3); }

/* Status badges */
.status-pending  { background: rgba(239,68,68,0.1);    color: #dc2626; border: 1px solid rgba(239,68,68,0.2); }
.status-review   { background: rgba(245,158,11,0.1);   color: #d97706; border: 1px solid rgba(245,158,11,0.2); }
.status-stable   { background: rgba(16,185,129,0.1);   color: #059669; border: 1px solid rgba(16,185,129,0.2); }
.status-cleared  { background: rgba(107,114,128,0.08); color: #4b5563; border: 1px solid rgba(107,114,128,0.2); }
.status-approved { background: rgba(139,92,246,0.08);  color: #7c3aed; border: 1px solid rgba(139,92,246,0.2); }

/* Alert rows — cleared and approved */
.alert-cleared {
    background: rgba(107,114,128,0.04);
    border: 1px solid rgba(107,114,128,0.18);
    border-left: 4px solid #9ca3af;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.alert-approved {
    background: rgba(139,92,246,0.04);
    border: 1px solid rgba(139,92,246,0.18);
    border-left: 4px solid #8b5cf6;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}

/* Section headers */
.section-header {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #6b7280;
    font-weight: 600;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
}

/* Customer row card */
.customer-card {
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.customer-id {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: #6b7280;
    min-width: 60px;
}
.customer-name {
    font-weight: 500;
    flex: 1;
    color: #e8eaf0;
}

/* Alert box */
.alert-high {
    background: rgba(239,68,68,0.05);
    border: 1px solid rgba(239,68,68,0.2);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.alert-medium {
    background: rgba(245,158,11,0.05);
    border: 1px solid rgba(245,158,11,0.2);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}

/* Button styling */
.stButton button {
    background: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    color: #3b82f6 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 1rem !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    background: #3b82f6 !important;
    color: #ffffff !important;
}

/* Approve button */
.approve-btn button {
    border-color: #10b981 !important;
    color: #10b981 !important;
}
.approve-btn button:hover {
    background: #10b981 !important;
    color: #ffffff !important;
}

/* Escalate button */
.escalate-btn button {
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}
.escalate-btn button:hover {
    background: #ef4444 !important;
    color: #ffffff !important;
}

/* Dataframe styling */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 1.5rem 0;
}

/* Info chip */
.info-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #6b7280;
    font-family: 'DM Mono', monospace;
}

/* ── Modal styles (injected into dialog via st.markdown) ── */
.modal-timeline-item {
    border-left: 3px solid;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.modal-factor-row {
    margin-bottom: 14px;
}

/* ── Dialog / modal: dark background ──────────────────────────────────────── */
div[data-testid="stDialog"] > div > div {
    background-color: #0f1117 !important;
    border: 1px solid #2a2f3e !important;
    border-radius: 14px !important;
    color: #e8eaf0 !important;
}
div[data-testid="stDialog"] p,
div[data-testid="stDialog"] span,
div[data-testid="stDialog"] label,
div[data-testid="stDialog"] .stMarkdown {
    color: #e8eaf0 !important;
}
div[data-testid="stDialog"] hr { border-color: #2a2f3e !important; }
div[data-testid="stDialog"] h1,
div[data-testid="stDialog"] h2,
div[data-testid="stDialog"] h3 { color: #ffffff !important; }
div[data-testid="stDialog"] .stButton button {
    background: #1a1f2e !important;
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
}
div[data-testid="stDialog"] .stButton button:hover { background: #3b82f6 !important; color: #ffffff !important; }
div[data-testid="stDialog"] .approve-btn  button { border-color: #10b981 !important; color: #10b981 !important; }
div[data-testid="stDialog"] .approve-btn  button:hover { background: #10b981 !important; color: #ffffff !important; }
div[data-testid="stDialog"] .escalate-btn button { border-color: #ef4444 !important; color: #ef4444 !important; }
div[data-testid="stDialog"] .escalate-btn button:hover { background: #ef4444 !important; color: #ffffff !important; }
div[data-testid="stDialog"] [data-testid="stMetricValue"] { color: #e8eaf0 !important; }
div[data-testid="stDialog"] [data-testid="stMetricLabel"] { color: #9ca3af !important; }
</style>
""", unsafe_allow_html=True)

# ── API config ────────────────────────────────────────────────────────────────
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = "https://cloudcore-churn.onrender.com/results"

# ── Session state — manual overrides (persist across reruns this session) ─────
# Each dict maps CustomerID → override action applied by a human reviewer.
# "escalated" : Medium → treated as High (Pending Review)
# "cleared"   : Medium → moved to Cleared
# "approved"  : High   → moved to Approved
if "escalated" not in st.session_state:
    st.session_state["escalated"] = set()   # CustomerIDs escalated to High
if "cleared" not in st.session_state:
    st.session_state["cleared"] = {}        # CustomerID → row dict
if "approved" not in st.session_state:
    st.session_state["approved"] = {}       # CustomerID → row dict

# ── Helper functions ──────────────────────────────────────────────────────────
def get_status(risk):
    if risk == "High":   return "Pending Review"
    if risk == "Medium": return "Needs Investigation"
    return "Stable"

def get_status_badge(risk):
    if risk == "High":
        return '<span class="badge badge-high">⚠ High Risk</span>'
    if risk == "Medium":
        return '<span class="badge badge-medium">◑ Medium Risk</span>'
    return '<span class="badge badge-low">✓ Low Risk</span>'

def get_review_badge(risk):
    if risk == "High":
        return '<span class="badge status-pending">🔴 Pending Review</span>'
    if risk == "Medium":
        return '<span class="badge status-review">🟡 Needs Investigation</span>'
    return '<span class="badge status-stable">🟢 Stable</span>'

def get_score_bar(usage_drop, tickets, payment_delay):
    score = 0
    if usage_drop > 0.30:    score += 40
    elif usage_drop > 0.15:  score += 20
    if tickets > 3:          score += 35
    elif tickets > 2:        score += 20
    if str(payment_delay).lower() == "yes": score += 25
    return min(score, 100)


# ══════════════════════════════════════════════════════════════════════════════
# MODAL: INVESTIGATE  ─ activity log timeline (Medium risk)
# ══════════════════════════════════════════════════════════════════════════════

@st.dialog("🔍 Customer Investigation", width="large")
def show_investigate_modal(row: dict):
    cid     = row.get("CustomerID", "—")
    cname   = row.get("Customer Name", cid)
    usage   = float(row.get("Usage Drop", 0))
    tickets = int(row.get("Number of Support Tickets", 0))
    payment = str(row.get("Payment Delay", "No"))
    score   = row.get("Risk Score", 0)

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        <div>
            <span style="font-family:'DM Mono',monospace; font-size:0.8rem; color:#6b7280;">{cid}</span>
            <span style="font-size:1.2rem; font-weight:700; color:#e8eaf0; margin-left:0.75rem;">{cname}</span>
        </div>
        <span class="badge badge-medium">◑ Medium Risk · {score}/100</span>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── Build timeline events from customer data ───────────────────────────
    # Events are derived from the fields you already track.
    # Replace or extend this list with real log data if your API exposes it.
    events = []

    # Usage drop signal
    if usage > 0.30:
        events.append({
            "icon": "📉", "severity": "critical", "color": "#ef4444", "bg": "rgba(239,68,68,0.08)",
            "title": "Severe Usage Drop Detected",
            "detail": f"Platform usage has fallen by {usage:.0%} — significantly above the 30% critical threshold.",
            "when": "This month"
        })
    elif usage > 0.15:
        events.append({
            "icon": "📉", "severity": "warning", "color": "#f59e0b", "bg": "rgba(245,158,11,0.08)",
            "title": "Moderate Usage Drop",
            "detail": f"Usage down {usage:.0%}. Warrants a check-in but not yet critical.",
            "when": "This month"
        })
    else:
        events.append({
            "icon": "✅", "severity": "ok", "color": "#10b981", "bg": "rgba(16,185,129,0.08)",
            "title": "Usage Stable",
            "detail": f"Usage drop of only {usage:.0%} — within normal variance.",
            "when": "This month"
        })

    # Support ticket signals
    if tickets > 3:
        events.append({
            "icon": "🎫", "severity": "critical", "color": "#ef4444", "bg": "rgba(239,68,68,0.08)",
            "title": f"{tickets} Support Tickets Open",
            "detail": "High ticket volume suggests unresolved product or service issues. Escalation risk is elevated.",
            "when": "Past 30 days"
        })
    elif tickets > 2:
        events.append({
            "icon": "🎫", "severity": "warning", "color": "#f59e0b", "bg": "rgba(245,158,11,0.08)",
            "title": f"{tickets} Support Tickets Raised",
            "detail": "Above average support activity. Review ticket themes for recurring pain points.",
            "when": "Past 30 days"
        })
    elif tickets == 0:
        events.append({
            "icon": "🎫", "severity": "ok", "color": "#10b981", "bg": "rgba(16,185,129,0.08)",
            "title": "No Open Support Tickets",
            "detail": "Customer has not raised any support issues this period.",
            "when": "Past 30 days"
        })
    else:
        events.append({
            "icon": "🎫", "severity": "info", "color": "#3b82f6", "bg": "rgba(59,130,246,0.08)",
            "title": f"{tickets} Support Ticket{'s' if tickets > 1 else ''}",
            "detail": "Normal support activity. Monitor for increases.",
            "when": "Past 30 days"
        })

    # Payment delay signal
    if payment.lower() == "yes":
        events.append({
            "icon": "💳", "severity": "critical", "color": "#ef4444", "bg": "rgba(239,68,68,0.08)",
            "title": "Payment Delay on Record",
            "detail": "At least one payment overdue. Combined with usage drop, this is a strong churn indicator.",
            "when": "Current billing cycle"
        })
    else:
        events.append({
            "icon": "💳", "severity": "ok", "color": "#10b981", "bg": "rgba(16,185,129,0.08)",
            "title": "Payments Up to Date",
            "detail": "No payment delays recorded for this account.",
            "when": "Current billing cycle"
        })

    # Overall assessment
    events.append({
        "icon": "📋", "severity": "info", "color": "#3b82f6", "bg": "rgba(59,130,246,0.08)",
        "title": "AI Risk Assessment: Medium",
        "detail": f"Composite risk score of {score}/100. Account requires investigation but not immediate escalation.",
        "when": f"Generated {datetime.now(timezone.utc).strftime('%-d %b %Y')}"
    })

    # ── Render timeline ───────────────────────────────────────────────────────
    st.markdown("**Activity Log**")
    for ev in events:
        st.markdown(f"""
        <div style="
            border-left: 3px solid {ev['color']};
            background: {ev['bg']};
            border-radius: 0 8px 8px 0;
            padding: 10px 14px;
            margin-bottom: 8px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <span style="font-size:1rem;">{ev['icon']}</span>
                    <span style="font-weight:600; color:#e8eaf0; margin-left:0.5rem; font-size:0.9rem;">{ev['title']}</span>
                </div>
                <span style="font-size:0.72rem; color:#6b7280; font-family:'DM Mono',monospace; white-space:nowrap; margin-left:1rem;">{ev['when']}</span>
            </div>
            <div style="margin-top:0.3rem; font-size:0.83rem; color:#9ca3af; margin-left:1.5rem;">{ev['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Action buttons ────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
        if st.button("✓ Clear — No Action", key=f"modal_clear_{cid}", use_container_width=True):
            # Move to Cleared: remove from escalated if previously set, add to cleared
            st.session_state["escalated"].discard(cid)
            st.session_state["cleared"][cid] = row
            st.session_state["approved"].pop(cid, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="escalate-btn">', unsafe_allow_html=True)
        if st.button("↑ Escalate to High", key=f"modal_esc_{cid}", use_container_width=True):
            # Move to Pending Review: add to escalated, remove from cleared/approved
            st.session_state["escalated"].add(cid)
            st.session_state["cleared"].pop(cid, None)
            st.session_state["approved"].pop(cid, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        if st.button("✕ Close", key=f"modal_close_inv_{cid}", use_container_width=True):
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MODAL: APPROVE  ─ risk score breakdown (High risk)
# ══════════════════════════════════════════════════════════════════════════════

@st.dialog("✅ Risk Score Breakdown", width="large")
def show_approve_modal(row: dict):
    cid     = row.get("CustomerID", "—")
    cname   = row.get("Customer Name", cid)
    usage   = float(row.get("Usage Drop", 0))
    tickets = int(row.get("Number of Support Tickets", 0))
    payment = str(row.get("Payment Delay", "No"))
    score   = row.get("Risk Score", 0)

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        <div>
            <span style="font-family:'DM Mono',monospace; font-size:0.8rem; color:#6b7280;">{cid}</span>
            <span style="font-size:1.2rem; font-weight:700; color:#e8eaf0; margin-left:0.75rem;">{cname}</span>
        </div>
        <span class="badge badge-high">⚠ High Risk</span>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── Overall score headline ────────────────────────────────────────────────
    col_score, col_label = st.columns([1, 2])
    with col_score:
        st.metric("Overall Risk Score", f"{score} / 100")
    with col_label:
        bar_pct = score
        st.markdown(f"""
        <div style="margin-top:1.1rem;">
            <div style="background:#2a2f3e; border-radius:6px; height:14px; overflow:hidden;">
                <div style="
                    background: linear-gradient(90deg, #ef4444, #dc2626);
                    width:{bar_pct}%;
                    height:14px;
                    border-radius:6px;
                "></div>
            </div>
            <div style="font-size:0.72rem; color:#6b7280; font-family:'DM Mono',monospace; margin-top:4px;">
                Threshold for High Risk: 40+ pts
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Per-factor breakdown ──────────────────────────────────────────────────
    # These weights EXACTLY match get_score_bar() in your existing code.
    st.markdown("**How the score was calculated**")

    # Factor 1: Usage Drop  (max 40 pts)
    usage_pts = 40 if usage > 0.30 else 20 if usage > 0.15 else 0
    usage_pct = (usage_pts / 40) * 100
    usage_color = "#ef4444" if usage_pts == 40 else "#f59e0b" if usage_pts == 20 else "#10b981"
    usage_verdict = "Critical (>30% drop)" if usage_pts == 40 else "Elevated (15–30% drop)" if usage_pts == 20 else "Normal (<15% drop)"

    # Factor 2: Support Tickets  (max 35 pts)
    ticket_pts = 35 if tickets > 3 else 20 if tickets > 2 else 0
    ticket_pct = (ticket_pts / 35) * 100
    ticket_color = "#ef4444" if ticket_pts == 35 else "#f59e0b" if ticket_pts == 20 else "#10b981"
    ticket_verdict = "Critical (>3 tickets)" if ticket_pts == 35 else "Elevated (3 tickets)" if ticket_pts == 20 else "Normal (≤2 tickets)"

    # Factor 3: Payment Delay  (max 25 pts)
    payment_pts = 25 if payment.lower() == "yes" else 0
    payment_pct = (payment_pts / 25) * 100 if payment_pts else 0
    payment_color = "#ef4444" if payment_pts else "#10b981"
    payment_verdict = "Payment overdue" if payment_pts else "Payments current"

    factors = [
        {
            "name": "Usage Drop",
            "weight_label": "40 pts max",
            "earned": usage_pts,
            "max": 40,
            "pct": usage_pct,
            "color": usage_color,
            "verdict": usage_verdict,
            "detail": f"Actual drop: {usage:.0%}",
        },
        {
            "name": "Support Tickets",
            "weight_label": "35 pts max",
            "earned": ticket_pts,
            "max": 35,
            "pct": ticket_pct,
            "color": ticket_color,
            "verdict": ticket_verdict,
            "detail": f"{tickets} ticket{'s' if tickets != 1 else ''} this period",
        },
        {
            "name": "Payment Delay",
            "weight_label": "25 pts max",
            "earned": payment_pts,
            "max": 25,
            "pct": payment_pct,
            "color": payment_color,
            "verdict": payment_verdict,
            "detail": f"Status: {'Overdue' if payment_pts else 'Current'}",
        },
    ]

    for f in factors:
        st.markdown(f"""
        <div style="
            background: #1a1f2e;
            border: 1px solid #2a2f3e;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div>
                    <span style="font-weight:600; color:#e8eaf0; font-size:0.9rem;">{f['name']}</span>
                    <span style="
                        font-size:0.72rem; color:{f['color']};
                        background: {'rgba(239,68,68,0.12)' if f['color']=='#ef4444' else 'rgba(245,158,11,0.12)' if f['color']=='#f59e0b' else 'rgba(16,185,129,0.12)'};
                        border-radius:12px; padding:2px 8px; margin-left:8px;
                    ">{f['verdict']}</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-family:'DM Mono',monospace; font-size:0.9rem; font-weight:700; color:{f['color']};">{f['earned']}</span>
                    <span style="font-family:'DM Mono',monospace; font-size:0.8rem; color:#6b7280;">/{f['max']} pts</span>
                </div>
            </div>
            <div style="background:#0f1117; border-radius:4px; height:8px; overflow:hidden; margin-bottom:5px;">
                <div style="background:{f['color']}; width:{f['pct']:.0f}%; height:8px; border-radius:4px;"></div>
            </div>
            <div style="font-size:0.75rem; color:#6b7280; font-family:'DM Mono',monospace;">{f['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Score total summary ───────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 10px;
        padding: 12px 16px;
        display:flex; justify-content:space-between; align-items:center;
        margin-top: 4px;
    ">
        <span style="font-weight:600; color:#e8eaf0;">Total Risk Score</span>
        <span style="font-family:'DM Mono',monospace; font-size:1.2rem; font-weight:700; color:#ef4444;">{score} / 100</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Recommendation ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("**Recommended Action**")

    if score >= 75:
        reco_icon, reco_color, reco_bg = "🚨", "#ef4444", "rgba(239,68,68,0.08)"
        reco_text = "Immediate CSM outreach required. Schedule a call within 48 hours and prepare a retention offer."
    elif score >= 40:
        reco_icon, reco_color, reco_bg = "⚠️", "#f59e0b", "rgba(245,158,11,0.08)"
        reco_text = "Proactive check-in recommended within 7 days. Review ticket history and flag for account health review."
    else:
        reco_icon, reco_color, reco_bg = "✅", "#10b981", "rgba(16,185,129,0.08)"
        reco_text = "No immediate action required. Continue standard monitoring cadence."

    st.markdown(f"""
    <div style="
        background:{reco_bg};
        border-left: 4px solid {reco_color};
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
    ">
        <span style="font-size:1rem;">{reco_icon}</span>
        <span style="margin-left:0.5rem; font-size:0.88rem; color:#e8eaf0;">{reco_text}</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Action buttons ────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
        if st.button("✓ Approve & Mark Reviewed", key=f"modal_approve_{cid}", use_container_width=True):
            # Move to Approved: remove from any other state buckets
            st.session_state["approved"][cid] = row
            st.session_state["cleared"].pop(cid, None)
            st.session_state["escalated"].discard(cid)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="escalate-btn">', unsafe_allow_html=True)
        if st.button("↑ Escalate to Manager", key=f"modal_escalate_{cid}", use_container_width=True):
            st.error(f"↑ {cname} escalated to senior manager.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        if st.button("✕ Close", key=f"modal_close_app_{cid}", use_container_width=True):
            st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <p class="dash-title">🔵 CloudCore — Customer Churn Risk</p>
    <p class="dash-subtitle">AI-supported retention intelligence · Account Manager Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1, 1, 1, 4])
with col_ctrl1:
    refresh = st.button("↻ Refresh Data")
with col_ctrl2:
    show_pending_only = st.checkbox("Pending only", value=False)
with col_ctrl3:
    risk_filter = st.selectbox("Risk filter", ["All", "High", "Medium", "Low"], label_visibility="collapsed")

if refresh:
    st.rerun()

# ── Fetch data ────────────────────────────────────────────────────────────────
try:
    response = requests.get(API_URL, timeout=15)
    data = response.json()

    if isinstance(data, dict):
        data = [data] if data else []

    if not data:
        st.markdown("""
        <div style="text-align:center; padding: 4rem; color: #6b7280;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <div style="font-size: 1.1rem; font-weight: 500; color: #9ca3af;">No customers scored yet</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">Waiting for Google Sheets data to flow through</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    df = pd.DataFrame(data)

    # Add derived columns
    df["Review Status"] = df["Churn Risk"].apply(get_status)
    df["Risk Score"] = df.apply(
        lambda r: get_score_bar(
            float(r.get("Usage Drop", 0)),
            int(r.get("Number of Support Tickets", 0)),
            r.get("Payment Delay", "no")
        ), axis=1
    )

    # ── Apply session state overrides ─────────────────────────────────────────
    # Escalated: Medium customers promoted to High by reviewer
    if st.session_state["escalated"]:
        mask = df["CustomerID"].astype(str).isin(st.session_state["escalated"])
        df.loc[mask, "Churn Risk"]    = "High"
        df.loc[mask, "Review Status"] = "Pending Review"

    # Cleared and Approved: remove from main df so they don't appear in
    # their original sections — they render in dedicated sections below
    override_ids = (
        set(st.session_state["cleared"].keys()) |
        set(st.session_state["approved"].keys())
    )
    active_df = df[~df["CustomerID"].astype(str).isin(override_ids)].copy()

    # Apply filters (on active customers only)
    filtered_df = active_df.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df["Churn Risk"] == risk_filter]
    if show_pending_only:
        filtered_df = filtered_df[filtered_df["Churn Risk"] == "High"]

    # Counts reflect active (non-overridden) customers
    high_count = len(active_df[active_df["Churn Risk"] == "High"])
    med_count  = len(active_df[active_df["Churn Risk"] == "Medium"])
    low_count  = len(active_df[active_df["Churn Risk"] == "Low"])
    total      = len(df)  # total always shows full dataset size

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    cleared_count  = len(st.session_state["cleared"])
    approved_count = len(st.session_state["approved"])

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class="metric-card high">
            <div class="metric-label">High Risk</div>
            <div class="metric-value">{high_count}</div>
            <div class="metric-sub">⚠ Pending Review</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card medium">
            <div class="metric-label">Medium Risk</div>
            <div class="metric-value">{med_count}</div>
            <div class="metric-sub">◑ Needs Investigation</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card low">
            <div class="metric-label">Low Risk</div>
            <div class="metric-value">{low_count}</div>
            <div class="metric-sub">✓ Stable Accounts</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        perth_time = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%d %b %Y %I:%M %p')
        st.markdown(f"""
        <div class="metric-card total">
            <div class="metric-label">Total Customers</div>
            <div class="metric-value">{total}</div>
            <div class="metric-sub">↻ {perth_time} AWST</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card cleared">
            <div class="metric-label">Cleared</div>
            <div class="metric-value">{cleared_count}</div>
            <div class="metric-sub">✕ No Action Needed</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="metric-card approved">
            <div class="metric-label">Approved</div>
            <div class="metric-value">{approved_count}</div>
            <div class="metric-sub">✓ Review Complete</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Charts Row ────────────────────────────────────────────────────────────
    chart_col1, chart_col2, chart_col3 = st.columns([1.2, 1.2, 1.6])

    with chart_col1:
        st.markdown('<div class="section-header">Risk Distribution</div>', unsafe_allow_html=True)
        fig_donut = go.Figure(data=[go.Pie(
            labels=["High Risk", "Medium Risk", "Low Risk"],
            values=[high_count, med_count, low_count],
            hole=0.65,
            marker=dict(colors=["#ef4444", "#f59e0b", "#10b981"]),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} customers<br>%{percent}<extra></extra>"
        )])
        fig_donut.add_annotation(
            text=f"<b>{total}</b><br><span style='font-size:10px'>Total</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#e8eaf0")
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(
                font=dict(color="#9ca3af", size=11),
                bgcolor="rgba(0,0,0,0)",
                orientation="h",
                yanchor="bottom", y=-0.15
            ),
            margin=dict(t=10, b=10, l=10, r=10),
            height=220
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.markdown('<div class="section-header">Usage Drop by Risk</div>', unsafe_allow_html=True)
        if "Usage Drop" in df.columns:
            fig_box = go.Figure()
            colors = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}
            for risk_level in ["High", "Medium", "Low"]:
                subset = df[df["Churn Risk"] == risk_level]["Usage Drop"].astype(float)
                if not subset.empty:
                    fig_box.add_trace(go.Box(
                        y=subset,
                        name=risk_level,
                        marker_color=colors[risk_level],
                        line_color=colors[risk_level],
                        boxmean=True
                    ))
            fig_box.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#9ca3af", size=11),
                xaxis=dict(gridcolor="#2a2f3e", showgrid=False),
                yaxis=dict(gridcolor="#2a2f3e", tickformat=".0%"),
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=220
            )
            st.plotly_chart(fig_box, use_container_width=True)

    with chart_col3:
        st.markdown('<div class="section-header">Support Tickets vs Usage Drop</div>', unsafe_allow_html=True)
        if "Usage Drop" in df.columns and "Number of Support Tickets" in df.columns:
            hover_cols = ["Customer Name", "CustomerID"] if "Customer Name" in df.columns else ["CustomerID"]
            fig_scatter = px.scatter(
                df,
                x="Usage Drop",
                y="Number of Support Tickets",
                color="Churn Risk",
                color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
                hover_data=hover_cols,
                size_max=10
            )
            fig_scatter.update_traces(marker=dict(size=8, opacity=0.8))
            fig_scatter.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#9ca3af", size=11),
                xaxis=dict(gridcolor="#2a2f3e", tickformat=".0%", title="Usage Drop"),
                yaxis=dict(gridcolor="#2a2f3e", title="Support Tickets"),
                legend=dict(title="", font=dict(color="#9ca3af", size=10), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=220
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Pending Review Section (High Risk) ────────────────────────────────────
    pending_df = active_df[active_df["Churn Risk"] == "High"]

    if not pending_df.empty:
        st.markdown(
            f'<div class="section-header">⚠ Pending Review — {len(pending_df)} Account{"s" if len(pending_df) > 1 else ""} Require Action</div>',
            unsafe_allow_html=True
        )

        for _, row in pending_df.iterrows():
            score   = row.get("Risk Score", 0)
            cname   = row.get("Customer Name", row.get("CustomerID", "Unknown"))
            cid     = row.get("CustomerID", "—")
            usage   = float(row.get("Usage Drop", 0))
            tickets = int(row.get("Number of Support Tickets", 0))
            payment = str(row.get("Payment Delay", "No"))

            with st.container():
                st.markdown(f"""
                <div class="alert-high">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <span class="customer-id">{cid}</span>
                            <span style="font-weight:600; color:#111827; margin-left:0.75rem;">{cname}</span>
                        </div>
                        <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
                            <span class="badge badge-high">⚠ High Risk</span>
                            <span class="badge status-pending">Pending Review</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:1.5rem; margin-top:0.75rem; flex-wrap:wrap;">
                        <span class="info-chip">📉 Usage Drop: {usage:.0%}</span>
                        <span class="info-chip">🎫 Tickets: {tickets}</span>
                        <span class="info-chip">💳 Payment Delay: {payment}</span>
                        <span class="info-chip">🔥 Risk Score: {score}/100</span>
                    </div>
                    <div style="margin-top:0.75rem;">
                        <div style="background:#e5e7eb; border-radius:4px; height:6px; overflow:hidden;">
                            <div style="background: linear-gradient(90deg, #ef4444, #dc2626); width:{score}%; height:100%; border-radius:4px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 4])

                with btn_col1:
                    st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
                    if st.button("✓ Approve", key=f"approve_{cid}"):
                        show_approve_modal(row.to_dict())
                    st.markdown('</div>', unsafe_allow_html=True)

                with btn_col2:
                    st.markdown('<div class="escalate-btn">', unsafe_allow_html=True)
                    if st.button("↑ Escalate", key=f"escalate_{cid}"):
                        st.error(f"↑ {cname} escalated to senior manager")
                    st.markdown('</div>', unsafe_allow_html=True)

                with btn_col3:
                    if st.button("→ View Details", key=f"details_{cid}"):
                        show_approve_modal(row.to_dict())

    # ── Medium Risk Section ───────────────────────────────────────────────────
    medium_df = active_df[active_df["Churn Risk"] == "Medium"]

    if not medium_df.empty:
        st.markdown(
            f'<div class="section-header">◑ Needs Investigation — {len(medium_df)} Account{"s" if len(medium_df) > 1 else ""}</div>',
            unsafe_allow_html=True
        )

        for _, row in medium_df.iterrows():
            score   = row.get("Risk Score", 0)
            cname   = row.get("Customer Name", row.get("CustomerID", "Unknown"))
            cid     = row.get("CustomerID", "—")
            usage   = float(row.get("Usage Drop", 0))
            tickets = int(row.get("Number of Support Tickets", 0))
            payment = str(row.get("Payment Delay", "No"))

            with st.container():
                st.markdown(f"""
                <div class="alert-medium">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <span class="customer-id">{cid}</span>
                            <span style="font-weight:600; color:#111827; margin-left:0.75rem;">{cname}</span>
                        </div>
                        <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
                            <span class="badge badge-medium">◑ Medium Risk</span>
                            <span class="badge status-review">Needs Investigation</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:1.5rem; margin-top:0.75rem; flex-wrap:wrap;">
                        <span class="info-chip">📉 Usage Drop: {usage:.0%}</span>
                        <span class="info-chip">🎫 Tickets: {tickets}</span>
                        <span class="info-chip">💳 Payment Delay: {payment}</span>
                        <span class="info-chip">⚡ Risk Score: {score}/100</span>
                    </div>
                    <div style="margin-top:0.75rem;">
                        <div style="background:#e5e7eb; border-radius:4px; height:6px; overflow:hidden;">
                            <div style="background: linear-gradient(90deg, #f59e0b, #d97706); width:{score}%; height:100%; border-radius:4px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col1, btn_col2, _ = st.columns([1, 1, 5])

                with btn_col1:
                    if st.button("→ Investigate", key=f"inv_{cid}"):
                        show_investigate_modal(row.to_dict())

                with btn_col2:
                    st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
                    # Direct clear without modal — moves immediately to Cleared section
                    if st.button("✓ Clear", key=f"clear_{cid}"):
                        st.session_state["cleared"][cid] = row.to_dict()
                        st.session_state["escalated"].discard(cid)
                        st.session_state["approved"].pop(cid, None)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # ── Cleared Section ───────────────────────────────────────────────────────
    if st.session_state["cleared"]:
        st.markdown(
            f'<div class="section-header">✕ Cleared — {len(st.session_state["cleared"])} Account{"s" if len(st.session_state["cleared"]) > 1 else ""} — No Action Needed</div>',
            unsafe_allow_html=True
        )
        for cid, row in st.session_state["cleared"].items():
            cname   = row.get("Customer Name", row.get("CustomerID", "Unknown"))
            usage   = float(row.get("Usage Drop", 0))
            tickets = int(row.get("Number of Support Tickets", 0))
            payment = str(row.get("Payment Delay", "No"))
            score   = row.get("Risk Score", 0)
            orig_risk = row.get("Churn Risk", "Medium")

            with st.container():
                st.markdown(f"""
                <div class="alert-cleared">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <span class="customer-id">{cid}</span>
                            <span style="font-weight:600; color:#6b7280; margin-left:0.75rem; text-decoration:line-through;">{cname}</span>
                        </div>
                        <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
                            <span class="badge badge-cleared">✕ Cleared</span>
                            <span class="badge status-cleared">Was {orig_risk} Risk</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:1.5rem; margin-top:0.5rem; flex-wrap:wrap; opacity:0.6;">
                        <span class="info-chip">📉 {usage:.0%}</span>
                        <span class="info-chip">🎫 {tickets} tickets</span>
                        <span class="info-chip">💳 {payment}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                b1, b2, _ = st.columns([1, 1, 5])
                with b1:
                    st.markdown('<div class="escalate-btn">', unsafe_allow_html=True)
                    if st.button("↺ Reopen", key=f"reopen_cleared_{cid}"):
                        st.session_state["cleared"].pop(cid, None)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # ── Approved Section ──────────────────────────────────────────────────────
    if st.session_state["approved"]:
        st.markdown(
            f'<div class="section-header">✓ Approved — {len(st.session_state["approved"])} Account{"s" if len(st.session_state["approved"]) > 1 else ""} — Review Complete</div>',
            unsafe_allow_html=True
        )
        for cid, row in st.session_state["approved"].items():
            cname   = row.get("Customer Name", row.get("CustomerID", "Unknown"))
            usage   = float(row.get("Usage Drop", 0))
            tickets = int(row.get("Number of Support Tickets", 0))
            payment = str(row.get("Payment Delay", "No"))
            score   = row.get("Risk Score", 0)

            with st.container():
                st.markdown(f"""
                <div class="alert-approved">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <span class="customer-id">{cid}</span>
                            <span style="font-weight:600; color:#7c3aed; margin-left:0.75rem;">{cname}</span>
                        </div>
                        <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
                            <span class="badge badge-approved">✓ Approved</span>
                            <span class="badge status-approved">Review Complete</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:1.5rem; margin-top:0.5rem; flex-wrap:wrap; opacity:0.7;">
                        <span class="info-chip">📉 {usage:.0%}</span>
                        <span class="info-chip">🎫 {tickets} tickets</span>
                        <span class="info-chip">💳 {payment}</span>
                        <span class="info-chip">🔥 {score}/100</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                b1, _ = st.columns([1, 6])
                with b1:
                    st.markdown('<div class="escalate-btn">', unsafe_allow_html=True)
                    if st.button("↺ Reopen", key=f"reopen_approved_{cid}"):
                        st.session_state["approved"].pop(cid, None)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Full Customer Table ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">All Customers</div>', unsafe_allow_html=True)

    display_df = filtered_df.copy()

    if "Usage Drop" in display_df.columns:
        display_df["Usage Drop"] = display_df["Usage Drop"].apply(lambda x: f"{float(x):.0%}")
    if "Risk Score" in display_df.columns:
        display_df["Score"] = display_df["Risk Score"].apply(lambda x: f"{x}/100")
        display_df = display_df.drop(columns=["Risk Score"])

    cols_order = ["CustomerID"]
    if "Customer Name" in display_df.columns:
        cols_order.append("Customer Name")
    cols_order += ["Usage Drop", "Number of Support Tickets", "Payment Delay", "Churn Risk", "Review Status", "Score"]
    cols_order = [c for c in cols_order if c in display_df.columns]
    display_df = display_df[cols_order]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Churn Risk":                    st.column_config.TextColumn("Churn Risk",    width="medium"),
            "Review Status":                 st.column_config.TextColumn("Review Status", width="medium"),
            "Score":                         st.column_config.TextColumn("Risk Score",    width="small"),
            "Usage Drop":                    st.column_config.TextColumn("Usage Drop",    width="small"),
            "Number of Support Tickets":     st.column_config.NumberColumn("Tickets",     width="small"),
        }
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem 0 1rem 0; color: #9ca3af; font-size: 0.75rem; font-family: 'DM Mono', monospace;">
        CloudCore Churn Risk Dashboard · ISYS6020 PoC · {total} customers scored · Human-in-the-loop enabled
    </div>
    """, unsafe_allow_html=True)

except requests.exceptions.ConnectionError:
    st.error("Cannot connect to the API. Check that Render is running.")
except Exception as e:
    st.error(f"Dashboard error: {e}")
    st.info("Try clicking Refresh — Render may be waking up (free tier takes ~30 seconds)")
