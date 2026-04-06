
import io
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="MST Executive Decision Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- STYLING -------------------------
st.markdown("""
<style>
:root{
    --bg1:#020814; --bg2:#071326; --panel:#081a31; --panel2:#0c223f; --text:#eef5ff; --muted:#adc1de;
    --blue:#4ba7ff; --cyan:#37ddff; --green:#35d48a; --orange:#ffb44a; --red:#ff6363; --line:rgba(115,156,212,0.17);
}
html, body, [class*="css"] { color: var(--text); }
.stApp{
    background:
        radial-gradient(circle at 12% 4%, rgba(75,167,255,0.16), transparent 18%),
        radial-gradient(circle at 88% 8%, rgba(55,221,255,0.10), transparent 14%),
        radial-gradient(circle at 70% 85%, rgba(255,180,74,0.12), transparent 18%),
        linear-gradient(180deg, #020814 0%, #041021 45%, #030915 100%);
}
[data-testid="stAppViewContainer"]{
    background: transparent;
}
[data-testid="stHeader"]{
    background: rgba(2,8,20,0.0);
    height: 0rem;
}
[data-testid="stToolbar"]{
    right: 0.6rem;
}
.block-container{
    padding-top: 0.35rem !important;
    padding-bottom: 1rem !important;
    max-width: 1540px;
}
h1,h2,h3,h4,h5,h6,p,div,span,label{
    color: var(--text) !important;
}
.small{
    color: var(--muted) !important;
    font-size: .92rem;
    line-height: 1.7;
}
.brand{
    background: linear-gradient(180deg, rgba(8,24,48,0.96), rgba(6,16,30,0.98));
    border: 1px solid rgba(112,156,212,0.17);
    border-radius: 28px;
    padding: 18px 22px;
    box-shadow: 0 14px 34px rgba(0,0,0,0.30);
    min-height: 132px;
}
.kpi{
    background: linear-gradient(180deg, rgba(10,24,46,0.98), rgba(7,17,31,0.98));
    border: 1px solid rgba(112,156,212,0.17);
    border-radius: 24px;
    padding: 18px;
    min-height: 138px;
    box-shadow: 0 14px 32px rgba(0,0,0,0.24);
}
.panel{
    background: linear-gradient(180deg, rgba(10,24,46,0.98), rgba(7,17,31,0.98));
    border: 1px solid rgba(112,156,212,0.17);
    border-radius: 26px;
    padding: 16px 18px 12px 18px;
    box-shadow: 0 16px 34px rgba(0,0,0,0.24);
    margin-top: 10px;
}
.label{color:#b9cae6!important;font-size:.90rem;margin-bottom:8px;}
.title{font-size:2.08rem;font-weight:800;line-height:1.15;}
.value{font-size:2.05rem;font-weight:800;line-height:1.1;}
.blue{color:var(--blue)!important;} .green{color:var(--green)!important;} .orange{color:var(--orange)!important;}
.red{color:var(--red)!important;} .cyan{color:var(--cyan)!important;}
.pill{
    display:inline-block;padding:7px 13px;border-radius:999px;margin:4px 6px 0 0;
    font-size:.82rem;border:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.05);
}
.state{
    border-radius:20px;padding:16px;min-height:142px;border:1px solid rgba(255,255,255,0.08);
}
.accept{background: linear-gradient(180deg, rgba(9,58,42,0.95), rgba(6,34,26,0.96));}
.risk{background: linear-gradient(180deg, rgba(76,49,6,0.95), rgba(46,27,5,0.96));}
.reject{background: linear-gradient(180deg, rgba(70,18,20,0.95), rgba(41,10,11,0.96));}
[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #07111f 0%, #091727 100%);
    border-right: 1px solid rgba(118,154,210,0.16);
}
[data-testid="stSidebar"] > div:first-child{
    padding-top: .65rem;
}
[data-testid="stSidebar"] *{
    color:#f2f7ff !important;
}
[data-testid="stSidebar"] .stRadio > label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSelectbox label{
    font-weight: 700 !important;
    color: #ffffff !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"]{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 8px;
}
[data-testid="stSidebar"] [data-baseweb="radio"] > div{
    gap: 4px;
}
[data-testid="stSidebar"] [data-baseweb="radio"] label{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 9px 10px;
    width: 100%;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="tag"],
[data-testid="stSidebar"] input{
    background: rgba(255,255,255,0.08) !important;
    color:#ffffff !important;
    border-radius: 12px !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"]{
    padding-top: 8px;
}
[data-testid="stSidebar"] .stSlider [role="slider"]{
    box-shadow: none !important;
}
[data-testid="stSidebar"] hr{
    border-color: rgba(255,255,255,0.08);
}
.stDataFrame{
    border-radius:20px;
    overflow:hidden;
}
</style>
""", unsafe_allow_html=True)

# ------------------------- HELPERS -------------------------
def money(v):
    return f"{v:,.1f}M"

def break_even_margin(current_profit, revenue):
    return (current_profit / revenue) * 100

def zone_from_margin(real_margin, be_margin):
    if real_margin >= be_margin + 1:
        return "Accept"
    elif real_margin >= be_margin:
        return "Risk"
    return "Reject"

def zone_ar(z):
    return {"Accept":"موافقة مشروطة", "Risk":"مراجعة مشروطة", "Reject":"غير موصى به"}[z]

def zone_color(z):
    return {"Accept":"#35d48a", "Risk":"#ffb44a", "Reject":"#ff6363"}[z]

def calc_row(revenue, current_margin, discount, op_impact, current_profit):
    expected_margin = current_margin - discount
    real_margin = expected_margin - op_impact
    net_profit = revenue * real_margin / 100.0
    be = break_even_margin(current_profit, revenue)
    decision = zone_from_margin(real_margin, be)
    return {
        "Revenue": revenue,
        "Expected Margin %": round(expected_margin,2),
        "Real Margin %": round(real_margin,2),
        "Break-even Margin %": round(be,2),
        "Net Profit": round(net_profit,2),
        "Delta Profit": round(net_profit - current_profit,2),
        "Decision Zone": decision
    }

def gauge(value, title, min_v, max_v, color, suffix="", threshold=None):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': suffix, 'font': {'size': 34, 'color': '#edf5ff'}},
        title={'text': title, 'font': {'size': 17, 'color': '#dce8fa'}},
        gauge={
            'axis': {'range': [min_v, max_v], 'tickcolor': '#aec3df', 'tickfont': {'color':'#bfd0e8'}},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': 'rgba(255,255,255,0.04)',
            'borderwidth': 0,
            'steps': [
                {'range': [min_v, max_v*0.45], 'color': 'rgba(255,99,99,0.16)'},
                {'range': [max_v*0.45, max_v*0.7], 'color': 'rgba(255,180,74,0.16)'},
                {'range': [max_v*0.7, max_v], 'color': 'rgba(53,212,138,0.16)'}
            ],
            'threshold': {
                'line': {'color': '#ffffff', 'width': 4},
                'thickness': 0.8,
                'value': threshold if threshold is not None else value
            }
        }
    ))
    fig.update_layout(height=255, margin=dict(l=12, r=12, t=55, b=8), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"))
    return fig

def build_pdf(summary, df):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Background
    c.setFillColorRGB(0.02, 0.07, 0.14)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Header
    c.setFillColorRGB(0.04, 0.12, 0.24)
    c.roundRect(14*mm, height-48*mm, width-28*mm, 30*mm, 8*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, height-27*mm, "MST Executive Decision Dashboard")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.75, 0.82, 0.92)
    c.drawString(20*mm, height-34*mm, "Executive summary with profitability and scenario analysis")

    y = height - 60*mm
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(18*mm, y, "Key Metrics")
    y -= 7*mm
    c.setFont("Helvetica", 10.5)
    lines = [
        f"Current Revenue: {summary['current_revenue']}",
        f"Current Net Margin: {summary['current_margin']}",
        f"Current Net Profit: {summary['current_profit']}",
        f"Discount: {summary['discount']} | Operational Impact: {summary['op_impact']}",
        f"Best Scenario Revenue: {summary['best_revenue']}",
        f"Best Real Margin: {summary['best_real_margin']}",
        f"Best Net Profit: {summary['best_net_profit']}",
        f"Recommendation: {summary['recommendation']}",
    ]
    for line in lines:
        c.drawString(20*mm, y, line)
        y -= 6.5*mm

    # Bar chart
    y_chart_top = y - 8*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.white)
    c.drawString(18*mm, y_chart_top, "Scenario Profit Comparison")
    chart_x = 22*mm
    chart_y = y_chart_top - 48*mm
    chart_w = 88*mm
    chart_h = 38*mm
    c.setStrokeColorRGB(0.45, 0.55, 0.7)
    c.rect(chart_x, chart_y, chart_w, chart_h, fill=0, stroke=1)

    if len(df) > 0:
        max_profit = max(df["Net Profit"].max(), 1)
        bar_gap = 6*mm
        bar_w = (chart_w - (len(df)+1)*bar_gap) / max(len(df),1)
        for i, row in enumerate(df.itertuples(index=False)):
            bx = chart_x + bar_gap + i*(bar_w + bar_gap)
            bh = (row._4 / max_profit) * (chart_h - 8*mm)  # Net Profit position after columns order
            by = chart_y + 4*mm
            color = row._7
            if color == "Accept":
                c.setFillColorRGB(0.21, 0.83, 0.54)
            elif color == "Risk":
                c.setFillColorRGB(1.0, 0.71, 0.29)
            else:
                c.setFillColorRGB(1.0, 0.39, 0.39)
            c.rect(bx, by, bar_w, bh, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica", 8)
            c.drawCentredString(bx + bar_w/2, chart_y - 4*mm, f"{int(row._0)}M")
            c.drawCentredString(bx + bar_w/2, by + bh + 2*mm, f"{row._4:.1f}")

    # Margin mini chart
    mx = 120*mm
    my = chart_y
    mw = 70*mm
    mh = chart_h
    c.setStrokeColorRGB(0.45, 0.55, 0.7)
    c.rect(mx, my, mw, mh, fill=0, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(120*mm, y_chart_top, "Real Margin Trend")
    if len(df) > 1:
        max_m = max(df["Real Margin %"].max(), 1)
        min_m = min(df["Real Margin %"].min(), 0)
        rng = max(max_m - min_m, 1)
        points = []
        for i, row in enumerate(df.itertuples(index=False)):
            px = mx + 7*mm + i*((mw-14*mm)/(len(df)-1))
            py = my + 6*mm + ((row._2 - min_m)/rng)*(mh-12*mm)
            points.append((px, py))
        c.setStrokeColorRGB(0.22, 0.87, 1.0)
        c.setLineWidth(2)
        for i in range(len(points)-1):
            c.line(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        for i, pt in enumerate(points):
            c.setFillColorRGB(0.29, 0.65, 1.0)
            c.circle(pt[0], pt[1], 2.3, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica", 8)
            c.drawCentredString(pt[0], my - 4*mm, f"{int(df.iloc[i]['Revenue'])}M")

    y2 = chart_y - 18*mm
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(18*mm, y2, "Management Notes")
    y2 -= 8*mm
    c.setFont("Helvetica", 10)
    notes = [
        "1. Conditional approval is preferred only if real margin stays above break-even plus safety buffer.",
        "2. Strengths: secured pipeline, early procurement planning, resource readiness, and financial visibility.",
        "3. Main risks: discount erosion, operating pressure, penalties, and material/fuel escalation.",
        "4. Full rejection may reduce next year's market share if volume is redistributed to other contractors."
    ]
    for note in notes:
        c.drawString(20*mm, y2, note[:112])
        y2 -= 6.7*mm

    c.setFillColorRGB(0.7, 0.78, 0.9)
    c.setFont("Helvetica", 8.5)
    c.drawString(18*mm, 10*mm, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    buffer.seek(0)
    return buffer

# ------------------------- SIDEBAR -------------------------
st.sidebar.image("brand_logo.png", use_container_width=True)

st.sidebar.markdown("### Navigation")
menu = st.sidebar.radio(
    "",
    ["🏠 Executive Overview", "🎯 Discount Simulator", "⚠️ Risk Center"],
    index=0
)

st.sidebar.markdown("### Final Commercial Inputs")
current_revenue = st.sidebar.number_input("Current Revenue (M SAR)", min_value=0.0, value=150.0, step=10.0)
current_margin = st.sidebar.number_input("Current Net Margin %", min_value=0.0, value=20.0, step=0.5)
discount = st.sidebar.number_input("Discount %", min_value=0.0, value=5.0, step=0.5)
op_impact = st.sidebar.number_input("Operational Impact %", min_value=0.0, value=3.0, step=0.5)
proposed_revenues = st.sidebar.multiselect("Proposed Revenues (M SAR)", [180,200,220,230,250,275,300], default=[200,230,250])

st.sidebar.markdown("### Branding")
dashboard_title = st.sidebar.text_input("Dashboard Title", value="MST Executive")
dashboard_subtitle = st.sidebar.text_input("Subtitle", value="Commercial Decision Dashboard")
show_management_notes = st.sidebar.checkbox("Show management notes", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="small">
Use the final commercial inputs to update all KPIs, charts, simulator results, risks, and PDF export automatically.
</div>
""", unsafe_allow_html=True)

current_profit = round(current_revenue * current_margin / 100.0, 2)
rows = [calc_row(r, current_margin, discount, op_impact, current_profit) for r in proposed_revenues]
df = pd.DataFrame(rows)
if not df.empty:
    df = df.sort_values(["Net Profit", "Real Margin %"], ascending=[False, False]).reset_index(drop=True)
    best = df.iloc[0]
else:
    best = None
safe_margin = round((best["Break-even Margin %"] + 1), 2) if best is not None else 0

summary = {
    "current_revenue": money(current_revenue),
    "current_margin": f"{current_margin:.1f}%",
    "current_profit": money(current_profit),
    "discount": f"{discount:.1f}%",
    "op_impact": f"{op_impact:.1f}%",
    "best_revenue": money(best["Revenue"]) if best is not None else "-",
    "best_real_margin": f"{best['Real Margin %']:.1f}%" if best is not None else "-",
    "best_net_profit": money(best["Net Profit"]) if best is not None else "-",
    "recommendation": zone_ar(best["Decision Zone"]) if best is not None else "-",
}
pdf_buffer = build_pdf(summary, df if not df.empty else pd.DataFrame(columns=["Revenue","Expected Margin %","Real Margin %","Break-even Margin %","Net Profit","Delta Profit","Decision Zone"]))

# ------------------------- TOP BAR -------------------------
top1, top2 = st.columns([5, 1.3])
with top1:
    st.markdown(f"""
    <div class="brand">
        <div class="title">{dashboard_title}</div>
        <div class="small">{dashboard_subtitle}</div>
        <div style="margin-top:10px;">
            <span class="pill">Current Revenue: {money(current_revenue)}</span>
            <span class="pill">Current Margin: {current_margin:.1f}%</span>
            <span class="pill">Discount: {discount:.1f}%</span>
            <span class="pill">Operating Impact: {op_impact:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.download_button(
        "📄 Download Consulting PDF",
        data=pdf_buffer,
        file_name="mst_executive_dashboard_summary.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown(f"""
    <div class="small" style="margin-top:10px;">
    Best current scenario:<br>
    <b>{money(best["Revenue"]) if best is not None else "-"}</b><br>
    Real Margin: <b>{best["Real Margin %"]:.1f}%</b><br>
    Recommendation: <b>{zone_ar(best["Decision Zone"]) if best is not None else "-"}</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- PAGES -------------------------
if menu == "🏠 Executive Overview":
    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi"><div class="label">Current Revenue</div><div class="value blue">{money(current_revenue)}</div><div class="small">Baseline for the entire discussion</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi"><div class="label">Current Net Profit</div><div class="value green">{money(current_profit)}</div><div class="small">Before applying the new offer</div></div>""", unsafe_allow_html=True)
    with k3:
        delta = best["Delta Profit"] if best is not None else 0
        delta_cls = "green" if delta >= 0 else "red"
        st.markdown(f"""<div class="kpi"><div class="label">Best Expected Net Profit</div><div class="value orange">{money(best["Net Profit"]) if best is not None else "-"}</div><div class="small">Delta vs current: <span class="{delta_cls}">{delta:+.1f}M</span></div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi"><div class="label">Safe Margin Required</div><div class="value">{safe_margin:.1f}%</div><div class="small">Break-even plus safety buffer</div></div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.5,1,1])
    with c1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Scenario Profit Comparison</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(
            x=[f"{int(v)}M" for v in df["Revenue"]],
            y=df["Net Profit"],
            text=[f"{v:.1f}M" for v in df["Net Profit"]],
            textposition="outside",
            marker=dict(color=[zone_color(z) for z in df["Decision Zone"]], line=dict(color="rgba(255,255,255,0.18)", width=1)),
            hovertemplate="%{x}<br>Net Profit %{y:.1f}M<extra></extra>"
        )
        fig.add_hline(y=current_profit, line_dash="dash", line_color="#48a7ff", annotation_text="Current Profit", annotation_position="top left")
        fig.update_layout(height=365, margin=dict(l=10,r=10,t=10,b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="M SAR"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Real Margin Gauge</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge(best["Real Margin %"] if best is not None else 0, "Real Margin", 0, 25, "#37ddff", "%", threshold=safe_margin), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        score = 82 if best is not None and best["Decision Zone"]=="Accept" else 58 if best is not None and best["Decision Zone"]=="Risk" else 28
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Decision Strength</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge(score, "Decision Strength", 0, 100, zone_color(best["Decision Zone"]) if best is not None else "#ff6363", "%", threshold=75), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    m1,m2,m3 = st.columns([1.45,1,1])
    with m1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Comparison Table</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="panel"><div class="label" style="font-size:1.02rem;">Decision Zones</div>
            <div class="state accept"><b>🟢 Accept</b><br><span class="small">Higher profit than baseline with safe real margin.</span></div><br>
            <div class="state risk"><b>🟡 Review</b><br><span class="small">Acceptable result, but margin is close to break-even.</span></div><br>
            <div class="state reject"><b>🔴 Reject</b><br><span class="small">Profitability does not justify the risk level.</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        final_cls = "green" if best is not None and best["Decision Zone"]=="Accept" else "orange" if best is not None and best["Decision Zone"]=="Risk" else "red"
        notes_html = """
        <hr><div class="small"><b>Management Note:</b> A full rejection may reduce next year's workshare if volume is redistributed to other contractors.</div>
        """ if show_management_notes else ""
        st.markdown(f"""
        <div class="panel">
            <div class="label" style="font-size:1.02rem;">Executive Summary</div>
            <div class="small">Recommended current decision:</div>
            <div class="value {final_cls}" style="margin-top:8px;">{zone_ar(best["Decision Zone"]) if best is not None else "-"}</div>
            <div class="small" style="margin-top:10px;">
            Conditional approval is preferred only if real margin remains above break-even with a safety buffer and the business can control deviations, penalties, and procurement volatility.
            </div>
            {notes_html}
        </div>
        """, unsafe_allow_html=True)

elif menu == "🎯 Discount Simulator":
    d_min, d_max = st.slider("Discount Simulation Range %", 0.0, 12.0, (0.0, 10.0), 0.5)
    selected_revenue = st.selectbox("Revenue to Simulate", [180,200,220,230,250,275,300], index=4)
    step = st.selectbox("Simulation Step", [0.5, 1.0], index=0)
    active_discount = st.slider("Current Tested Discount %", d_min, d_max, min(discount, d_max), step)

    discount_values = []
    x = d_min
    while x <= d_max + 1e-9:
        discount_values.append(round(x,2))
        x += step
    sim_df = pd.DataFrame([calc_row(selected_revenue, current_margin, d, op_impact, current_profit) | {"Discount %": d} for d in discount_values])
    current_row = sim_df[sim_df["Discount %"] == round(active_discount,2)]
    current_row = current_row.iloc[0] if not current_row.empty else sim_df.iloc[0]
    safe_df = sim_df[sim_df["Decision Zone"]=="Accept"]
    best_safe_discount = safe_df["Discount %"].max() if not safe_df.empty else None

    s1,s2,s3,s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="kpi"><div class="label">Tested Discount</div><div class="value orange">{current_row['Discount %']:.1f}%</div><div class="small">The discount being evaluated now</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="kpi"><div class="label">Real Margin</div><div class="value cyan">{current_row['Real Margin %']:.1f}%</div><div class="small">After discount and operating impact</div></div>""", unsafe_allow_html=True)
    with s3:
        cls = "green" if current_row["Delta Profit"] >= 0 else "red"
        st.markdown(f"""<div class="kpi"><div class="label">Expected Net Profit</div><div class="value {cls}">{money(current_row['Net Profit'])}</div><div class="small">Delta vs current: <span class="{cls}">{current_row['Delta Profit']:+.1f}M</span></div></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="kpi"><div class="label">Best Acceptable Discount</div><div class="value green">{f"{best_safe_discount:.1f}%" if best_safe_discount is not None else "None"}</div><div class="small">Highest discount still inside the accept zone</div></div>""", unsafe_allow_html=True)

    p1,p2 = st.columns([1.4,1])
    with p1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Discount vs Net Profit</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_scatter(x=sim_df["Discount %"], y=sim_df["Net Profit"], mode="lines+markers", line=dict(color="#48a7ff", width=4), marker=dict(size=10, color=[zone_color(z) for z in sim_df["Decision Zone"]]), hovertemplate="Discount %{x:.1f}%<br>Profit %{y:.1f}M<extra></extra>")
        fig.add_hline(y=current_profit, line_dash="dash", line_color="#35d48a", annotation_text="Current Profit", annotation_position="top left")
        fig.update_layout(height=390, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(title="Discount %", showgrid=False), yaxis=dict(title="Net Profit (M SAR)", showgrid=True, gridcolor="rgba(255,255,255,0.08)"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Discount vs Real Margin</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_scatter(x=sim_df["Discount %"], y=sim_df["Real Margin %"], mode="lines+markers", line=dict(color="#37ddff", width=4), marker=dict(size=10, color=[zone_color(z) for z in sim_df["Decision Zone"]]), hovertemplate="Discount %{x:.1f}%<br>Real Margin %{y:.1f}%<extra></extra>")
        fig2.add_hline(y=current_row["Break-even Margin %"], line_dash="dash", line_color="#ffb44a", annotation_text=f"Break-even {current_row['Break-even Margin %']:.1f}%", annotation_position="top left")
        fig2.update_layout(height=390, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(title="Discount %", showgrid=False), yaxis=dict(title="Real Margin %", showgrid=True, gridcolor="rgba(255,255,255,0.08)"))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Simulation Table</div>', unsafe_allow_html=True)
    st.dataframe(sim_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    risk_names = ["Operational Pressure", "Deviations", "Penalties", "Materials/Fuel"]
    risk_values = [
        2 if op_impact <= 2 else 3 if op_impact <= 4 else 4,
        2 if discount <= 3 else 3 if discount <= 5 else 4,
        2 if discount <= 4 else 3 if discount <= 6 else 4,
        4
    ]
    risk_colors = ["#35d48a" if v<=2 else "#ffb44a" if v==3 else "#ff6363" for v in risk_values]

    r1,r2,r3 = st.columns(3)
    with r1:
        st.markdown(f"""<div class="kpi"><div class="label">Operational Pressure</div><div class="value {'green' if risk_values[0]<=2 else 'orange' if risk_values[0]==3 else 'red'}">{['-','Low','Medium','High','Critical'][risk_values[0]]}</div><div class="small">Driven by the operating impact input</div></div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""<div class="kpi"><div class="label">Profitability Risk</div><div class="value {'green' if best is not None and best['Decision Zone']=='Accept' else 'orange' if best is not None and best['Decision Zone']=='Risk' else 'red'}">{zone_ar(best['Decision Zone']) if best is not None else '-'}</div><div class="small">Based on real margin versus break-even</div></div>""", unsafe_allow_html=True)
    with r3:
        st.markdown(f"""<div class="kpi"><div class="label">Material & Fuel Risk</div><div class="value red">High</div><div class="small">External exposure that may require escalation clause</div></div>""", unsafe_allow_html=True)

    rc1,rc2 = st.columns([1.15,1])
    with rc1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Risk Matrix</div>', unsafe_allow_html=True)
        risk_fig = go.Figure()
        risk_fig.add_bar(x=risk_names, y=risk_values, text=["L" if v==1 else "M" if v==2 else "H" if v==3 else "C" for v in risk_values], textposition="inside", marker=dict(color=risk_colors), hovertemplate="%{x}<extra></extra>")
        risk_fig.update_layout(height=370, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", tickvals=[1,2,3,4], ticktext=["Low","Medium","High","Critical"], range=[0,4.5]), showlegend=False)
        st.plotly_chart(risk_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with rc2:
        st.markdown("""
        <div class="panel">
            <div class="label" style="font-size:1.02rem;">Risk Response Plan</div>
            <div class="small">
            • Set a firm discount cap linked to secured annual volume.<br>
            • Add a material and fuel escalation review clause where possible.<br>
            • Monitor deviations, penalties, and extra operating cost monthly.<br>
            • Prepare a resource and procurement plan from the start of the year.<br>
            • Do not approve based on revenue growth alone; approve based on real profitability.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
        <div class="label" style="font-size:1.02rem;">Consulting Readout</div>
        <div class="small">
        The key issue is not only the discount itself, but the combined impact of discount plus operating pressure on real margin. 
        If the offer is accepted without commercial protections, the company could gain volume but lose profitability quality. 
        If the offer is rejected entirely, part of next year's workload may shift to other contractors. 
        Therefore, the best path is typically conditional approval with a clear discount cap, scenario tracking, and monthly risk review.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.caption("Consulting-style executive dashboard with integrated simulator, risk center, branding, and PDF export.")
