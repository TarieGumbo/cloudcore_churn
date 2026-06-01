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
    background-color: #0f1117;
    color: #e8eaf0;
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
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.high::before { background: #ef4444; }
.metric-card.medium::before { background: #f59e0b; }
.metric-card.low::before { background: #10b981; }
.metric-card.total::before { background: #3b82f6; }

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
.high .metric-value { color: #ef4444; }
.medium .metric-value { color: #f59e0b; }
.low .metric-value { color: #10b981; }
.total .metric-value { color: #3b82f6; }

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
.badge-high { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.badge-medium { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-low { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }

/* Status badges */
.status-pending { background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }
.status-review { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
.status-stable { background: rgba(16,185,129,0.1); color: #10b981; border: 1px solid rgba(16,185,129,0.2); }

/* Section headers */
.section-header {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #6b7280;
    font-weight: 600;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2a2f3e;
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
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.alert-medium {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.25);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}

/* Button styling */
.stButton button {
    background: #1a1f2e !important;
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
    border-top: 1px solid #2a2f3e;
    margin: 1.5rem 0;
}

/* Info chip */
.info-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #1a1f2e;
    border: 1px solid #2a2f3e;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #9ca3af;
    font-family: 'DM Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ── API config ────────────────────────────────────────────────────────────────
try:
    API_URL = st.secrets["API_URL"]
except:
    API_URL = "https://cloudcore-churn.onrender.com/results"

# ── Helper functions ──────────────────────────────────────────────────────────
def get_status(risk):
    if risk == "High":
        return "Pending Review"
    elif risk == "Medium":
        return "Needs Investigation"
    else:
        return "Stable"

def get_status_badge(risk):
    if risk == "High":
        return '<span class="badge badge-high">⚠ High Risk</span>'
    elif risk == "Medium":
        return '<span class="badge badge-medium">◑ Medium Risk</span>'
    else:
        return '<span class="badge badge-low">✓ Low Risk</span>'

def get_review_badge(risk):
    if risk == "High":
        return '<span class="badge status-pending">🔴 Pending Review</span>'
    elif risk == "Medium":
        return '<span class="badge status-review">🟡 Needs Investigation</span>'
    else:
        return '<span class="badge status-stable">🟢 Stable</span>'

def get_score_bar(usage_drop, tickets, payment_delay):
    score = 0
    if usage_drop > 0.30: score += 40
    elif usage_drop > 0.15: score += 20
    if tickets > 3: score += 35
    elif tickets > 2: score += 20
    if str(payment_delay).lower() == "yes": score += 25
    return min(score, 100)

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

    # Apply filters
    filtered_df = df.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df["Churn Risk"] == risk_filter]
    if show_pending_only:
        filtered_df = filtered_df[filtered_df["Churn Risk"] == "High"]

    # Counts
    high_count = len(df[df["Churn Risk"] == "High"])
    med_count = len(df[df["Churn Risk"] == "Medium"])
    low_count = len(df[df["Churn Risk"] == "Low"])
    total = len(df)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

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
            <div class="metric-sub">↻ Last updated: {perth_time} AWST</div>
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
                        fillcolor=colors[risk_level].replace(")", ",0.15)").replace("rgb", "rgba") if "rgb" in colors[risk_level] else colors[risk_level],
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
            fig_scatter = px.scatter(
                df,
                x="Usage Drop",
                y="Number of Support Tickets",
                color="Churn Risk",
                color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
                hover_data=["Customer Name", "CustomerID"] if "Customer Name" in df.columns else ["CustomerID"],
                size_max=10
            )
            fig_scatter.update_traces(marker=dict(size=8, opacity=0.8))
            fig_scatter.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#9ca3af", size=11),
                xaxis=dict(gridcolor="#2a2f3e", tickformat=".0%", title="Usage Drop"),
                yaxis=dict(gridcolor="#2a2f3e", title="Support Tickets"),
                legend=dict(
                    title="",
                    font=dict(color="#9ca3af", size=10),
                    bgcolor="rgba(0,0,0,0)"
                ),
                margin=dict(t=10, b=10, l=10, r=10),
                height=220
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Pending Review Section ────────────────────────────────────────────────
    pending_df = df[df["Churn Risk"] == "High"]

    if not pending_df.empty:
        st.markdown(f'<div class="section-header">⚠ Pending Review — {len(pending_df)} Account{"s" if len(pending_df) > 1 else ""} Require Action</div>', unsafe_allow_html=True)

        for _, row in pending_df.iterrows():
            score = row.get("Risk Score", 0)
            cname = row.get("Customer Name", row.get("CustomerID", "Unknown"))
            cid = row.get("CustomerID", "—")
            usage = float(row.get("Usage Drop", 0))
            tickets = int(row.get("Number of Support Tickets", 0))
            payment = str(row.get("Payment Delay", "No"))

            with st.container():
                st.markdown(f"""
                <div class="alert-high">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <span class="customer-id">{cid}</span>
                            <span style="font-weight:600; color:#e8eaf0; margin-left:0.75rem;">{cname}</span>
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
                        <div style="background:#2a2f3e; border-radius:4px; height:6px; overflow:hidden;">
                            <div style="background: linear-gradient(90deg, #ef4444, #dc2626); width:{score}%; height:100%; border-radius:4px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 4])
                with btn_col1:
                    st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
                    if st.button(f"✓ Approve", key=f"approve_{cid}"):
                        st.success(f"✓ {cname} marked as reviewed")
                    st.markdown('</div>', unsafe_allow_html=True)
                with btn_col2:
                    st.markdown('<div class="escalate-btn">', unsafe_allow_html=True)
                    if st.button(f"↑ Escalate", key=f"escalate_{cid}"):
                        st.error(f"↑ {cname} escalated to senior manager")
                    st.markdown('</div>', unsafe_allow_html=True)
                with btn_col3:
                    if st.button(f"→ View Details", key=f"details_{cid}"):
                        st.info(f"Viewing full profile for {cname}")

    # ── Medium Risk Section ───────────────────────────────────────────────────
    medium_df = df[df["Churn Risk"] == "Medium"]

    if not medium_df.empty:
        st.markdown(f'<div class="section-header">◑ Needs Investigation — {len(medium_df)} Account{"s" if len(medium_df) > 1 else ""}</div>', unsafe_allow_html=True)

        for _, row in medium_df.iterrows():
            score = row.get("Risk Score", 0)
            cname = row.get("Customer Name", row.get("CustomerID", "Unknown"))
            cid = row.get("CustomerID", "—")
            usage = float(row.get("Usage Drop", 0))
            tickets = int(row.get("Number of Support Tickets", 0))
            payment = str(row.get("Payment Delay", "No"))

            with st.container():
                st.markdown(f"""
                <div class="alert-medium">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                        <div>
                            <span class="customer-id">{cid}</span>
                            <span style="font-weight:600; color:#e8eaf0; margin-left:0.75rem;">{cname}</span>
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
                        <div style="background:#2a2f3e; border-radius:4px; height:6px; overflow:hidden;">
                            <div style="background: linear-gradient(90deg, #f59e0b, #d97706); width:{score}%; height:100%; border-radius:4px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col1, btn_col2, _ = st.columns([1, 1, 5])
                with btn_col1:
                    if st.button(f"→ Investigate", key=f"inv_{cid}"):
                        st.info(f"Investigation started for {cname}")
                with btn_col2:
                    if st.button(f"✓ Clear", key=f"clear_{cid}"):
                        st.success(f"✓ {cname} cleared — no action needed")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Full Customer Table ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">All Customers</div>', unsafe_allow_html=True)

    display_df = filtered_df.copy()

    # Format columns for display
    if "Usage Drop" in display_df.columns:
        display_df["Usage Drop"] = display_df["Usage Drop"].apply(lambda x: f"{float(x):.0%}")
    if "Risk Score" in display_df.columns:
        display_df["Score"] = display_df["Risk Score"].apply(lambda x: f"{x}/100")
        display_df = display_df.drop(columns=["Risk Score"])

    # Reorder columns
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
            "Churn Risk": st.column_config.TextColumn("Churn Risk", width="medium"),
            "Review Status": st.column_config.TextColumn("Review Status", width="medium"),
            "Score": st.column_config.TextColumn("Risk Score", width="small"),
            "Usage Drop": st.column_config.TextColumn("Usage Drop", width="small"),
            "Number of Support Tickets": st.column_config.NumberColumn("Tickets", width="small"),
        }
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem 0 1rem 0; color: #4b5563; font-size: 0.75rem; font-family: 'DM Mono', monospace;">
        CloudCore Churn Risk Dashboard · ISYS6020 PoC · {total} customers scored · Human-in-the-loop enabled
    </div>
    """, unsafe_allow_html=True)

except requests.exceptions.ConnectionError:
    st.error("Cannot connect to the API. Check that Render is running.")
except Exception as e:
    st.error(f"Dashboard error: {e}")
    st.info("Try clicking Refresh — Render may be waking up (free tier takes ~30 seconds)")
