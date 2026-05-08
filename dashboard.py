import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import random

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Web Gap Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

.stApp {
    background: #0A0E1A;
    color: #E8EDF5;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0D1220 !important;
    border-right: 1px solid #1E2840;
}
[data-testid="stSidebar"] * {
    color: #B0BDD4 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #7C9ED9 !important;
    font-weight: 600;
}

/* Main header */
.main-header {
    background: linear-gradient(135deg, #0D1220 0%, #131B2E 50%, #0A0E1A 100%);
    border: 1px solid #1E2840;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4F8EF7, #7B5CF5, #E96BC4, #F7934C);
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7CB9FF, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #6B7FA3;
    font-size: 0.9rem;
    margin: 6px 0 0 0;
    font-family: 'JetBrains Mono', monospace;
}

/* KPI Cards */
.kpi-card {
    background: #0D1220;
    border: 1px solid #1E2840;
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-blue::after   { background: linear-gradient(90deg, #4F8EF7, #7B5CF5); }
.kpi-green::after  { background: linear-gradient(90deg, #34D399, #10B981); }
.kpi-orange::after { background: linear-gradient(90deg, #F7934C, #F59E0B); }
.kpi-pink::after   { background: linear-gradient(90deg, #E96BC4, #A78BFA); }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #4A5D7A;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #E8EDF5;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
}
.kpi-delta {
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 6px;
}
.delta-up   { color: #34D399; }
.delta-down { color: #F87171; }

/* Section titles */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #7CB9FF;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 8px 0 16px 0;
    padding-left: 12px;
    border-left: 3px solid #4F8EF7;
}

/* Table */
.dataframe thead tr th {
    background-color: #131B2E !important;
    color: #7CB9FF !important;
    font-weight: 600;
    font-size: 0.82rem;
}
.dataframe tbody tr:nth-child(even) {
    background-color: #0D1220 !important;
}

/* Tag badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-blue   { background: #1E3A6E; color: #7CB9FF; }
.badge-green  { background: #064E3B; color: #34D399; }
.badge-orange { background: #78350F; color: #FCD34D; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE DATA
# ══════════════════════════════════════════════════════════════════════════════
random.seed(42)
np.random.seed(42)

months = pd.date_range("2024-01-01", periods=6, freq="ME")
month_labels = [m.strftime("%b %Y") for m in months]

# ── Non-Profit Data ────────────────────────────────────────────────────────────
np_donors = pd.DataFrame({
    "Month": month_labels,
    "New Donors": [42, 55, 48, 63, 71, 88],
    "Recurring Donors": [18, 22, 25, 29, 34, 40],
    "Donations ($)": [52000, 68000, 61000, 79000, 92000, 115000],
    "Avg Donation ($)": [1238, 1236, 1271, 1254, 1296, 1307],
    "Campaigns Active": [3, 4, 3, 5, 4, 6],
    "Goal Completion (%)": [72, 78, 65, 83, 88, 94],
})

np_campaigns = pd.DataFrame({
    "Campaign": ["Clean Water Initiative", "Education Fund", "Hunger Relief",
                 "Tree Plantation", "Women Empowerment", "Medical Aid"],
    "Target ($)": [100000, 75000, 90000, 50000, 80000, 120000],
    "Raised ($)": [94000, 71000, 72000, 38000, 76000, 108000],
    "Donors": [88, 65, 72, 42, 69, 95],
    "Status": ["Active", "Active", "Active", "Paused", "Active", "Active"],
})
np_campaigns["Progress (%)"] = (np_campaigns["Raised ($)"] / np_campaigns["Target ($)"] * 100).round(1)
np_campaigns["Gap ($)"] = np_campaigns["Target ($)"] - np_campaigns["Raised ($)"]

# ── AI Platform Data ──────────────────────────────────────────────────────────
ai_models = pd.DataFrame({
    "Model": ["GPT-4o", "Claude 3 Opus", "Gemini 1.5 Pro", "LLaMA 3", "Mistral 7B",
              "Phi-3 Mini", "DALL·E 3", "Whisper v3", "Sora", "Stable Diffusion 3"],
    "Category": ["LLM","LLM","Multimodal","LLM","LLM","SLM","Image","Speech","Video","Image"],
    "Accuracy (%)": [92.5, 90.8, 91.0, 88.3, 84.0, 83.5, 89.0, 95.2, 88.0, 87.5],
    "Latency (ms)": [820, 950, 890, 620, 310, 220, 1800, 450, 3200, 1500],
    "API Calls (K)": [580, 420, 395, 280, 190, 140, 310, 250, 85, 175],
    "User Rating": [4.8, 4.7, 4.7, 4.5, 4.3, 4.2, 4.6, 4.8, 4.5, 4.4],
    "Cost ($/1M tok)": [15, 15, 7, 0, 0, 0, 40, 6, 60, 0],
    "Open Source": ["No","No","No","Yes","Yes","Yes","No","Yes","No","Yes"],
})

ai_monthly = pd.DataFrame({
    "Month": month_labels,
    "API Calls (M)": [1.2, 1.8, 2.3, 3.1, 4.0, 5.2],
    "Active Users (K)": [8.5, 11.2, 14.8, 19.3, 24.1, 31.0],
    "Avg Sessions/User": [3.2, 3.8, 4.1, 4.5, 4.9, 5.3],
    "Revenue ($K)": [48, 72, 92, 124, 160, 208],
    "Churn Rate (%)": [8.2, 7.5, 6.9, 6.1, 5.4, 4.8],
    "NPS Score": [42, 48, 52, 56, 61, 68],
})

# ── Magazine Data ──────────────────────────────────────────────────────────────
mag_articles = pd.DataFrame({
    "Month": month_labels,
    "Articles Published": [28, 32, 25, 38, 42, 45],
    "Total Views (K)": [185, 224, 198, 310, 368, 420],
    "Subscriptions": [320, 415, 375, 520, 610, 740],
    "Free Users": [4200, 5100, 4800, 6200, 7100, 8400],
    "Premium Users": [1100, 1340, 1280, 1620, 1890, 2150],
    "Avg Read Time (min)": [4.2, 4.5, 4.1, 4.8, 5.1, 5.4],
    "Social Shares (K)": [12.4, 16.8, 14.2, 21.5, 26.3, 31.8],
})

mag_categories = pd.DataFrame({
    "Category": ["Technology", "Business", "Environment", "Wellness", "Travel", "Society", "Health"],
    "Articles": [18, 15, 12, 10, 14, 8, 11],
    "Avg Views (K)": [72, 61, 58, 43, 51, 38, 46],
    "Avg Likes": [5200, 4100, 3800, 2900, 3400, 2600, 3100],
    "Conversion (%)": [8.4, 6.2, 5.9, 7.1, 5.3, 4.8, 6.6],
    "Premium (%)": [45, 38, 32, 41, 28, 35, 39],
})

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🗂 Navigation")
    selected_site = st.selectbox(
        "Select Website",
        ["🌍 Overview", "❤️ Non-Profit", "🤖 Artificial Intelligence", "📰 Magazine"]
    )
    st.markdown("---")
    st.markdown("## 📅 Filter")
    month_filter = st.selectbox("Time Period", ["All 6 Months"] + month_labels, index=0)
    st.markdown("---")
    st.markdown("## ℹ️ About")
    st.markdown("""
    <div style='font-size:0.8rem; color:#4A5D7A; line-height:1.6'>
    Web Gap Analysis Dashboard<br>
    Tracks KPIs across 3 websites:<br><br>
    • <b style='color:#7CB9FF'>Non-Profit</b> – Donor & campaign metrics<br>
    • <b style='color:#A78BFA'>AI Platform</b> – Usage & model performance<br>
    • <b style='color:#F7934C'>Magazine</b> – Content & subscription KPIs
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PLOTLY THEME
# ══════════════════════════════════════════════════════════════════════════════
CHART_BG = "#0D1220"
PAPER_BG = "#0D1220"
FONT_COLOR = "#B0BDD4"
GRID_COLOR = "#1A2540"

def apply_theme(fig, height=350):
    fig.update_layout(
        plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG,
        font=dict(family="Sora", color=FONT_COLOR, size=11),
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
    )
    return fig

PALETTE = ["#4F8EF7","#A78BFA","#34D399","#F7934C","#E96BC4","#FCD34D","#60C9F8","#F87171"]

def kpi(label, value, delta=None, color="blue"):
    delta_html = ""
    if delta:
        arrow = "▲" if delta > 0 else "▼"
        cls = "delta-up" if delta > 0 else "delta-down"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {abs(delta):.1f}% vs last month</div>'
    return f"""
    <div class="kpi-card kpi-{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW PAGE
# ══════════════════════════════════════════════════════════════════════════════
if selected_site == "🌍 Overview":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Web Gap Analysis Dashboard</h1>
        <p>karthick-deva-24 · soundaryamanivannan08 · 3 websites · Jan–Jun 2024</p>
    </div>""", unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi("Total Donations", "$467K", 24.8, "blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("AI Active Users", "31K", 28.6, "pink"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Magazine Views", "1.7M", 14.1, "green"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Avg Conversion", "6.5%", 8.3, "orange"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Combined trend
    st.markdown('<div class="section-title">📈 Monthly Growth Trends — All 3 Websites</div>', unsafe_allow_html=True)

    fig = make_subplots(rows=1, cols=3, subplot_titles=["Non-Profit: Donations ($)", "AI: Active Users (K)", "Magazine: Subscriptions"])
    fig.add_trace(go.Scatter(x=month_labels, y=np_donors["Donations ($)"], mode="lines+markers",
        line=dict(color="#4F8EF7", width=2.5), marker=dict(size=6), name="Donations"), row=1, col=1)
    fig.add_trace(go.Scatter(x=month_labels, y=ai_monthly["Active Users (K)"], mode="lines+markers",
        line=dict(color="#A78BFA", width=2.5), marker=dict(size=6), name="AI Users"), row=1, col=2)
    fig.add_trace(go.Scatter(x=month_labels, y=mag_articles["Subscriptions"], mode="lines+markers",
        line=dict(color="#34D399", width=2.5), marker=dict(size=6), name="Subscriptions"), row=1, col=3)
    fig.update_annotations(font=dict(color="#7CB9FF", size=11))
    fig = apply_theme(fig, 280)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Gap summary table
    st.markdown('<div class="section-title">🔍 Gap Analysis Summary</div>', unsafe_allow_html=True)
    gap_df = pd.DataFrame({
        "Website": ["Non-Profit", "AI Platform", "Magazine"],
        "Category": ["Charity / Fundraising", "Technology", "Digital Media"],
        "URL": ["karthick-deva-24.github.io/Non-Profit/", "karthick-deva-24.github.io/Artificial-Intelligence-/", "soundaryamanivannan08-source.github.io/magazine/"],
        "Primary KPI": ["Donation Goal Completion", "User Retention & API Calls", "Subscriber Conversion"],
        "Current Score": ["88.4%", "91.2%", "78.6%"],
        "Gap to Target": ["11.6%", "8.8%", "21.4%"],
        "Priority": ["Medium", "Low", "High"],
    })
    st.dataframe(gap_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# NON-PROFIT PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif selected_site == "❤️ Non-Profit":
    st.markdown("""
    <div class="main-header">
        <h1>❤️ Non-Profit Dashboard</h1>
        <p>karthick-deva-24.github.io/Non-Profit/ · Donor & Campaign Analytics · Jan–Jun 2024</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi("Total Raised", "$467K", 24.8, "blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Total Donors", "367", 19.7, "green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Recurring Rate", "38%", 5.2, "orange"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Goal Completion", "94%", 6.8, "pink"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">💰 Monthly Donation Trend</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=month_labels, y=np_donors["Donations ($)"],
            marker_color=PALETTE[0], opacity=0.85, name="Donations ($)"))
        fig.add_trace(go.Scatter(x=month_labels, y=np_donors["Donations ($)"],
            mode="lines+markers", line=dict(color="#A78BFA", width=2),
            marker=dict(size=7), name="Trend"))
        fig.update_layout(title="", barmode="group")
        st.plotly_chart(apply_theme(fig), use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">👥 New vs Recurring Donors</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=month_labels, y=np_donors["New Donors"],
            name="New Donors", marker_color=PALETTE[0]))
        fig2.add_trace(go.Bar(x=month_labels, y=np_donors["Recurring Donors"],
            name="Recurring Donors", marker_color=PALETTE[2]))
        fig2.update_layout(barmode="stack")
        st.plotly_chart(apply_theme(fig2), use_container_width=True)

    st.markdown('<div class="section-title">🎯 Campaign Performance & Gap Analysis</div>', unsafe_allow_html=True)

    col3, col4 = st.columns([3, 2])
    with col3:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="Raised ($)", x=np_campaigns["Campaign"],
            y=np_campaigns["Raised ($)"], marker_color=PALETTE[2]))
        fig3.add_trace(go.Bar(name="Gap ($)", x=np_campaigns["Campaign"],
            y=np_campaigns["Gap ($)"], marker_color=PALETTE[6]))
        fig3.update_layout(barmode="stack", xaxis_tickangle=-20)
        st.plotly_chart(apply_theme(fig3), use_container_width=True)

    with col4:
        fig4 = px.pie(np_campaigns, names="Campaign", values="Raised ($)",
            color_discrete_sequence=PALETTE, hole=0.45)
        fig4.update_traces(textfont_size=10)
        fig4.update_layout(title="Share of Funds Raised")
        st.plotly_chart(apply_theme(fig4, 350), use_container_width=True)

    st.markdown('<div class="section-title">📋 Campaign Detail Table</div>', unsafe_allow_html=True)
    st.dataframe(np_campaigns, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">📊 Goal Completion Rate (Month-wise)</div>', unsafe_allow_html=True)
    fig5 = go.Figure(go.Scatter(x=month_labels, y=np_donors["Goal Completion (%)"],
        mode="lines+markers+text", text=[f"{v}%" for v in np_donors["Goal Completion (%)"]],
        textposition="top center", line=dict(color="#E96BC4", width=3),
        marker=dict(size=9, color="#E96BC4"),
        fill="tozeroy", fillcolor="rgba(233,107,196,0.08)"))
    fig5.add_hline(y=90, line_dash="dot", line_color="#FCD34D",
                   annotation_text="90% Target", annotation_font_color="#FCD34D")
    st.plotly_chart(apply_theme(fig5, 280), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# AI PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif selected_site == "🤖 Artificial Intelligence":
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Artificial Intelligence Dashboard</h1>
        <p>karthick-deva-24.github.io/Artificial-Intelligence-/ · Model & Platform Analytics · Jan–Jun 2024</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi("Active Users", "31K", 28.6, "blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("API Calls", "5.2M", 30.0, "pink"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Churn Rate", "4.8%", -11.1, "orange"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("NPS Score", "68", 11.4, "green"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">📈 User Growth & Revenue</div>', unsafe_allow_html=True)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=month_labels, y=ai_monthly["Active Users (K)"],
            name="Active Users (K)", marker_color=PALETTE[0], opacity=0.8), secondary_y=False)
        fig.add_trace(go.Scatter(x=month_labels, y=ai_monthly["Revenue ($K)"],
            name="Revenue ($K)", mode="lines+markers",
            line=dict(color=PALETTE[3], width=2.5), marker=dict(size=7)), secondary_y=True)
        fig.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG,
            font=dict(color=FONT_COLOR), height=350, margin=dict(l=20, r=20, t=30, b=20))
        fig.update_yaxes(gridcolor=GRID_COLOR)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🔄 Churn Rate vs NPS</div>', unsafe_allow_html=True)
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Scatter(x=month_labels, y=ai_monthly["Churn Rate (%)"],
            name="Churn Rate (%)", mode="lines+markers",
            line=dict(color=PALETTE[7], width=2.5), marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(248,113,113,0.08)"), secondary_y=False)
        fig2.add_trace(go.Scatter(x=month_labels, y=ai_monthly["NPS Score"],
            name="NPS Score", mode="lines+markers",
            line=dict(color=PALETTE[2], width=2.5), marker=dict(size=7)), secondary_y=True)
        fig2.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG,
            font=dict(color=FONT_COLOR), height=350, margin=dict(l=20, r=20, t=30, b=20))
        fig2.update_yaxes(gridcolor=GRID_COLOR)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">🧠 Model Performance Comparison</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.scatter(ai_models, x="Latency (ms)", y="Accuracy (%)",
            size="API Calls (K)", color="Category", hover_name="Model",
            color_discrete_sequence=PALETTE, size_max=40)
        fig3.update_layout(title="Accuracy vs Latency (bubble = API call volume)")
        st.plotly_chart(apply_theme(fig3, 380), use_container_width=True)

    with col4:
        fig4 = px.bar(ai_models.sort_values("User Rating", ascending=True),
            x="User Rating", y="Model", orientation="h",
            color="User Rating", color_continuous_scale="Blues")
        fig4.update_layout(title="User Ratings by Model", coloraxis_showscale=False)
        st.plotly_chart(apply_theme(fig4, 380), use_container_width=True)

    st.markdown('<div class="section-title">📋 Model Details Table</div>', unsafe_allow_html=True)
    display_cols = ["Model", "Category", "Accuracy (%)", "Latency (ms)", "API Calls (K)", "User Rating", "Open Source"]
    st.dataframe(ai_models[display_cols], use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">📊 API Calls Growth by Month</div>', unsafe_allow_html=True)
    fig5 = go.Figure(go.Bar(x=month_labels, y=ai_monthly["API Calls (M)"],
        marker=dict(color=PALETTE, colorscale=None),
        text=[f"{v}M" for v in ai_monthly["API Calls (M)"]], textposition="outside"))
    fig5.update_layout(title="")
    st.plotly_chart(apply_theme(fig5, 280), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAGAZINE PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif selected_site == "📰 Magazine":
    st.markdown("""
    <div class="main-header">
        <h1>📰 Magazine Dashboard</h1>
        <p>soundaryamanivannan08-source.github.io/magazine/ · Content & Subscription Analytics · Jan–Jun 2024</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi("Total Views", "1.71M", 14.1, "blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Premium Subs", "2,150", 13.8, "green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Avg Read Time", "5.4 min", 5.9, "orange"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Social Shares", "31.8K", 20.9, "pink"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">👥 Free vs Premium Subscribers</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=month_labels, y=mag_articles["Free Users"],
            name="Free Users", marker_color=PALETTE[0], opacity=0.8))
        fig.add_trace(go.Bar(x=month_labels, y=mag_articles["Premium Users"],
            name="Premium Users", marker_color=PALETTE[2]))
        fig.update_layout(barmode="stack")
        st.plotly_chart(apply_theme(fig), use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">📈 Views & Subscriptions Growth</div>', unsafe_allow_html=True)
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Scatter(x=month_labels, y=mag_articles["Total Views (K)"],
            name="Views (K)", mode="lines+markers",
            line=dict(color=PALETTE[0], width=2.5), marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(79,142,247,0.08)"), secondary_y=False)
        fig2.add_trace(go.Scatter(x=month_labels, y=mag_articles["Subscriptions"],
            name="New Subs", mode="lines+markers",
            line=dict(color=PALETTE[3], width=2.5), marker=dict(size=7)), secondary_y=True)
        fig2.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG,
            font=dict(color=FONT_COLOR), height=350, margin=dict(l=20, r=20, t=30, b=20))
        fig2.update_yaxes(gridcolor=GRID_COLOR)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">📂 Category Performance</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(mag_categories.sort_values("Avg Views (K)", ascending=True),
            x="Avg Views (K)", y="Category", orientation="h", color="Avg Views (K)",
            color_continuous_scale="Blues")
        fig3.update_layout(title="Avg Views per Article by Category", coloraxis_showscale=False)
        st.plotly_chart(apply_theme(fig3, 380), use_container_width=True)

    with col4:
        fig4 = px.scatter(mag_categories, x="Conversion (%)", y="Premium (%)",
            size="Articles", color="Category", hover_name="Category",
            color_discrete_sequence=PALETTE, size_max=35, text="Category")
        fig4.update_traces(textposition="top center", textfont_size=9)
        fig4.update_layout(title="Conversion vs Premium Rate by Category")
        st.plotly_chart(apply_theme(fig4, 380), use_container_width=True)

    st.markdown('<div class="section-title">📋 Category Detail Table</div>', unsafe_allow_html=True)
    st.dataframe(mag_categories, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">⏱ Avg Read Time & Social Engagement</div>', unsafe_allow_html=True)
    fig5 = make_subplots(specs=[[{"secondary_y": True}]])
    fig5.add_trace(go.Bar(x=month_labels, y=mag_articles["Avg Read Time (min)"],
        name="Avg Read Time (min)", marker_color=PALETTE[1], opacity=0.85), secondary_y=False)
    fig5.add_trace(go.Scatter(x=month_labels, y=mag_articles["Social Shares (K)"],
        name="Social Shares (K)", mode="lines+markers",
        line=dict(color=PALETTE[3], width=2.5), marker=dict(size=7)), secondary_y=True)
    fig5.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR), height=300, margin=dict(l=20, r=20, t=30, b=20))
    fig5.update_yaxes(gridcolor=GRID_COLOR)
    st.plotly_chart(fig5, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:24px; color:#2E3D5A; font-size:0.78rem;
     font-family:"JetBrains Mono",monospace; border-top:1px solid #1A2540; margin-top:32px;'>
    Web Gap Analysis Dashboard · Built with Streamlit & Plotly · Sample Data · 2024
</div>""", unsafe_allow_html=True)
