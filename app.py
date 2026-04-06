
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

# ------------------------- STYLE -------------------------
st.markdown("""
<style>
:root{
    --bg1:#020814; --bg2:#071326; --panel:#081a31; --text:#eef5ff; --muted:#adc1de;
    --blue:#4ba7ff; --cyan:#37ddff; --green:#35d48a; --orange:#ffb44a; --red:#ff6363;
}
html, body, [class*="css"] { color: var(--text); }
.stApp{
    background:
        radial-gradient(circle at 12% 4%, rgba(75,167,255,0.16), transparent 18%),
        radial-gradient(circle at 88% 8%, rgba(55,221,255,0.10), transparent 14%),
        radial-gradient(circle at 70% 85%, rgba(255,180,74,0.12), transparent 18%),
        linear-gradient(180deg, #020814 0%, #041021 45%, #030915 100%);
}
[data-testid="stHeader"]{background: rgba(2,8,20,0.0); height: 0rem;}
.block-container{padding-top: 0.35rem !important; padding-bottom: 1rem !important; max-width: 1540px;}
h1,h2,h3,h4,h5,h6,p,div,span,label{color: var(--text) !important;}
.small{color: var(--muted) !important; font-size: .92rem; line-height: 1.7;}
.brand, .panel, .kpi{
    background: linear-gradient(180deg, rgba(10,24,46,0.98), rgba(7,17,31,0.98));
    border: 1px solid rgba(112,156,212,0.17);
    box-shadow: 0 14px 32px rgba(0,0,0,0.24);
}
.brand{border-radius: 28px; padding: 18px 22px; min-height: 132px;}
.panel{border-radius: 26px; padding: 16px 18px 12px 18px; margin-top: 10px;}
.kpi{border-radius: 24px; padding: 18px; min-height: 138px;}
.label{color:#b9cae6!important;font-size:.90rem;margin-bottom:8px;}
.title{font-size:2.08rem;font-weight:800;line-height:1.15;}
.value{font-size:2.05rem;font-weight:800;line-height:1.1;}
.blue{color:var(--blue)!important;} .green{color:var(--green)!important;}
.orange{color:var(--orange)!important;} .red{color:var(--red)!important;} .cyan{color:var(--cyan)!important;}
.pill{
    display:inline-block;padding:7px 13px;border-radius:999px;margin:4px 6px 0 0;
    font-size:.82rem;border:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.05);
}
.state{border-radius:20px;padding:16px;min-height:142px;border:1px solid rgba(255,255,255,0.08);}
.accept{background: linear-gradient(180deg, rgba(9,58,42,0.95), rgba(6,34,26,0.96));}
.risk{background: linear-gradient(180deg, rgba(76,49,6,0.95), rgba(46,27,5,0.96));}
.reject{background: linear-gradient(180deg, rgba(70,18,20,0.95), rgba(41,10,11,0.96));}
[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #07111f 0%, #091727 100%);
    border-right: 1px solid rgba(118,154,210,0.16);
}
[data-testid="stSidebar"] *{color:#f2f7ff !important;}
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stRadio > label{
    font-weight:700 !important;
    color:#ffffff !important;
    opacity:1 !important;
}
[data-testid="stSidebar"] input{
    background: rgba(255,255,255,0.10) !important;
    color: #4ba7ff !important;
    -webkit-text-fill-color: #4ba7ff !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    border-radius: 12px !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] input[type="number"]{
    color: #4ba7ff !important;
    -webkit-text-fill-color: #4ba7ff !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
}
[data-testid="stSidebar"] button[title="Increment value"],
[data-testid="stSidebar"] button[title="Decrement value"]{
    color:#4ba7ff !important;
    opacity:1 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="tag"]{
    background: rgba(255,255,255,0.08) !important;
    color:#ffffff !important;
    border-radius: 12px !important;
}
.stDataFrame{border-radius:20px; overflow:hidden;}
.rule-box{
    background: linear-gradient(180deg, rgba(13,31,58,0.98), rgba(8,18,34,0.98));
    border: 1px solid rgba(112,156,212,0.20);
    border-left: 4px solid #4ba7ff;
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    margin-top: 10px;
}
.rule-title{
    color:#4ba7ff !important;
    font-size:1.02rem;
    font-weight:800;
    margin-bottom:8px;
}
.rule-text{
    color:#d8e5f7 !important;
    font-size:0.92rem;
    line-height:1.7;
}

</style>
""", unsafe_allow_html=True)

# ------------------------- HELPERS -------------------------
def money(v: float) -> str:
    return f"{v:,.2f}M"

def calc_row(revenue: float, current_margin: float, discount: float, current_profit: float) -> dict:
    # Corrected board logic:
    # 1) Net margin baseline is fixed at 20% and already fully loaded.
    # 2) Discount reduces margin directly.
    # 3) Decision is NOT based on "profit > current profit" only.
    # 4) A minimum uplift threshold is required to justify the extra scale and risk.
    expected_margin = current_margin - discount
    real_margin = expected_margin
    net_profit = revenue * real_margin / 100.0
    delta_profit = net_profit - current_profit

    MIN_UPLIFT = 6.0  # minimum extra profit required vs current 30M baseline
    if revenue < 230:
        decision = "Reject"
    elif discount >= 5.0 and revenue < 250:
        decision = "Reject"
    elif delta_profit < MIN_UPLIFT:
        decision = "Reject"
    elif discount >= 5.0 and revenue >= 250:
        decision = "Review"
    elif 2.5 <= discount <= 3.0 and revenue >= 230:
        decision = "Accept"
    else:
        decision = "Review"

    return {
        "Revenue": revenue,
        "Discount %": round(discount, 2),
        "Net Margin %": round(real_margin, 2),
        "Net Profit (M)": round(net_profit, 2),
        "Delta Profit (M)": round(delta_profit, 2),
        "Decision": decision,
    }

def decision_color(decision: str) -> str:
    return {"Accept":"#35d48a", "Review":"#ffb44a", "Reject":"#ff6363"}.get(decision, "#4ba7ff")

def build_pdf(summary: dict, scenario_df: pd.DataFrame) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # background
    c.setFillColorRGB(0.03, 0.07, 0.14)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # header
    c.setFillColorRGB(0.05, 0.12, 0.24)
    c.roundRect(12*mm, height-45*mm, width-24*mm, 28*mm, 8*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(18*mm, height-27*mm, "MST Executive Decision Dashboard")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.75, 0.82, 0.92)
    c.drawString(18*mm, height-34*mm, "Final commercial logic: fixed 20% net margin, discount directly reduces margin.")

    # summary
    y = height - 58*mm
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(16*mm, y, "Executive Summary")
    y -= 7*mm
    c.setFont("Helvetica", 10.5)
    lines = [
        f"Current Revenue: {summary['current_revenue']}",
        f"Fixed Net Margin Baseline: {summary['current_margin']}",
        f"Current Net Profit: {summary['current_profit']}",
        f"Scenario Discounts: 2.5%, 3.0%, 5.0%",
        f"Scenario Revenues: 200M, 230M, 250M",
        f"Best Case: {summary['best_case']}",
        f"Recommendation: {summary['recommendation']}",
    ]
    for line in lines:
        c.drawString(18*mm, y, line)
        y -= 6*mm

    # table
    y -= 4*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(16*mm, y, "Scenario Table")
    y -= 7*mm

    cols = ["Revenue", "Discount %", "Net Margin %", "Net Profit (M)", "Decision"]
    col_x = [16*mm, 48*mm, 82*mm, 118*mm, 154*mm]
    c.setFillColorRGB(0.05, 0.09, 0.50)
    c.rect(14*mm, y-5*mm, width-28*mm, 8*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    for x, col in zip(col_x, cols):
        c.drawString(x, y-1*mm, col)
    y -= 10*mm

    c.setFont("Helvetica", 9)
    for row in scenario_df.to_dict(orient="records"):
        if y < 30*mm:
            c.showPage()
            y = height - 25*mm
        c.setFillColorRGB(0.93, 0.95, 0.98)
        c.rect(14*mm, y-4*mm, width-28*mm, 7*mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.drawString(col_x[0], y, str(int(row["Revenue"])))
        c.drawString(col_x[1], y, f'{row["Discount %"]:.1f}%')
        c.drawString(col_x[2], y, f'{row["Net Margin %"]:.1f}%')
        c.drawString(col_x[3], y, f'{row["Net Profit (M)"]:.2f}')
        c.drawString(col_x[4], y, str(row["Decision"]))
        y -= 8*mm

    c.setFillColorRGB(0.75, 0.82, 0.92)
    c.setFont("Helvetica", 8.5)
    c.drawString(16*mm, 10*mm, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    buffer.seek(0)
    return buffer

# ------------------------- SIDEBAR -------------------------
st.sidebar.image("brand_logo.png", use_container_width=True)
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("", ["🏠 Executive Overview", "🎯 Discount Simulator", "⚠️ Review Center"], index=0)

st.sidebar.markdown("### Final Commercial Inputs")
current_revenue = st.sidebar.number_input("Current Revenue (M SAR)", min_value=0.0, value=150.0, step=10.0, format="%.2f")
current_margin = st.sidebar.number_input("Current Net Margin %", min_value=0.0, value=20.0, step=0.5, format="%.2f")
discount_value = st.sidebar.number_input("Discount %", min_value=0.0, value=3.0, step=0.5, format="%.2f")
# kept for UI continuity only; not used in final calculation
operational_impact = st.sidebar.number_input("Operational Impact % (already absorbed)", min_value=0.0, value=0.0, step=0.5, format="%.2f")
proposed_revenues = st.sidebar.multiselect("Proposed Revenues (M SAR)", [200, 230, 250], default=[200, 230, 250])

st.sidebar.markdown("### Branding")
dashboard_title = st.sidebar.text_input("Dashboard Title", value="MST Executive")
dashboard_subtitle = st.sidebar.text_input("Subtitle", value="Commercial Decision Dashboard")

current_profit = round(current_revenue * current_margin / 100.0, 2)

# final board scenarios per latest instruction
scenario_discounts = [2.5, 3.0, 5.0]
rows = []
for revenue in [200, 230, 250]:
    for d in scenario_discounts:
        rows.append(calc_row(revenue, current_margin, d, current_profit))
scenario_df = pd.DataFrame(rows)

# selected view row
selected_row = calc_row(
    revenue=max(proposed_revenues) if proposed_revenues else 250,
    current_margin=current_margin,
    discount=discount_value,
    current_profit=current_profit
)

best_row = scenario_df.sort_values(["Net Profit (M)", "Revenue"], ascending=[False, False]).iloc[0]

summary = {
    "current_revenue": money(current_revenue),
    "current_margin": f"{current_margin:.2f}%",
    "current_profit": money(current_profit),
    "best_case": f'{int(best_row["Revenue"])}M @ {best_row["Discount %"]:.1f}% => {best_row["Net Profit (M)"]:.2f}M',
    "recommendation": "Optimal discount range is 2.5%–3.0% only from 230M upward. 5.0% is not approved automatically and should only be reviewed at 250M with strong safeguards."
}
pdf_buffer = build_pdf(summary, scenario_df)

# ------------------------- HEADER -------------------------
top1, top2 = st.columns([5, 1.5])
with top1:
    st.markdown(f"""
    <div class="brand">
        <div class="title">{dashboard_title}</div>
        <div class="small">{dashboard_subtitle}</div>
        <div style="margin-top:10px;">
            <span class="pill">Current Revenue: {money(current_revenue)}</span>
            <span class="pill">Fixed Net Margin: {current_margin:.2f}%</span>
            <span class="pill">Selected Discount: {discount_value:.2f}%</span>
            <span class="pill">Operating Impact: already absorbed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.download_button(
        "📄 Download Final PDF",
        data=pdf_buffer,
        file_name="mst_final_dashboard_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown(f"""
    <div class="small" style="margin-top:10px;">
    Best Case:<br>
    <b>{int(best_row["Revenue"])}M</b><br>
    Discount: <b>{best_row["Discount %"]:.1f}%</b><br>
    Net Profit: <b>{best_row["Net Profit (M)"]:.2f}M</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- PAGE: OVERVIEW -------------------------
if page == "🏠 Executive Overview":
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi"><div class="label">Current Revenue</div><div class="value blue">{money(current_revenue)}</div><div class="small">Baseline for decision making</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi"><div class="label">Current Net Profit</div><div class="value green">{money(current_profit)}</div><div class="small">Based on fixed 20% net margin</div></div>""", unsafe_allow_html=True)
    with k3:
        cls = "green" if selected_row["Delta Profit (M)"] >= 0 else "red"
        st.markdown(f"""<div class="kpi"><div class="label">Selected Scenario Profit</div><div class="value orange">{money(selected_row["Net Profit (M)"])}</div><div class="small">Delta vs current: <span class="{cls}">{selected_row["Delta Profit (M)"]:+.2f}M</span></div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi"><div class="label">Selected Scenario Margin</div><div class="value cyan">{selected_row["Net Margin %"]:.2f}%</div><div class="small">Discount directly reduces the fixed net margin</div></div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([1.45, 1.0])
    with c1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Scenario Profit Comparison</div>', unsafe_allow_html=True)
        fig = go.Figure()
        for d in scenario_discounts:
            sub = scenario_df[scenario_df["Discount %"] == d]
            fig.add_scatter(
                x=sub["Revenue"],
                y=sub["Net Profit (M)"],
                mode="lines+markers+text",
                text=[f'{v:.2f}' for v in sub["Net Profit (M)"]],
                textposition="top center",
                name=f"{d:.1f}% Discount"
            )
        fig.add_hline(y=current_profit, line_dash="dash", line_color="#4ba7ff", annotation_text="Current Net Profit")
        fig.update_layout(
            height=390,
            margin=dict(l=10,r=10,t=10,b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#eef5ff"),
            xaxis=dict(title="Revenue (M SAR)", showgrid=False),
            yaxis=dict(title="Net Profit (M)", showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Decision Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="state accept"><b>✅ Accept</b><br><span class="small">2.5%–3.0% is acceptable only when awarded revenue is at least 230M and profit uplift is meaningful.</span></div><br>
        <div class="state risk"><b>⚠️ Review</b><br><span class="small">5.0% is rejected below 250M and only reviewed at 250M with strategic safeguards.</span></div><br>
        <div class="state reject"><b>❌ Not Preferred</b><br><span class="small">Any scenario with low uplift versus the current baseline is rejected even if it remains mathematically profitable.</span></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


    st.markdown(
        '''
        <div class="rule-box">
            <div class="rule-title">Decision Logic Applied</div>
            <div class="rule-text">
                • Fixed net margin baseline = <b>20%</b>; all operating costs and depreciation are already absorbed.<br>
                • Discounts directly reduce the net margin.<br>
                • A scenario is <b>not accepted</b> merely because profit is above the current baseline.<br>
                • Minimum required profit uplift versus the current case = <b>6.0M</b>.<br>
                • Any scenario below <b>230M</b> is rejected because the uplift is not considered strategically sufficient.<br>
                • <b>2.5%–3.0%</b> is acceptable only when revenue is at least <b>230M</b> and uplift is meaningful.<br>
                • <b>5.0%</b> is rejected below <b>250M</b> and only reviewed at <b>250M</b> with contractual safeguards.
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Final Scenario Table</div>', unsafe_allow_html=True)
    st.dataframe(scenario_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- PAGE: SIMULATOR -------------------------
elif page == "🎯 Discount Simulator":
    st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Discount Simulator</div>', unsafe_allow_html=True)
    sim_revenue = st.selectbox("Revenue to Simulate", [200, 230, 250], index=2)
    sim_discounts = [x / 2 for x in range(5, 11)]  # 2.5 to 5.0
    sim_df = pd.DataFrame([calc_row(sim_revenue, current_margin, d, current_profit) for d in sim_discounts])

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""<div class="kpi"><div class="label">Simulated Revenue</div><div class="value blue">{money(sim_revenue)}</div><div class="small">Fixed revenue for sensitivity view</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="kpi"><div class="label">Selected Discount</div><div class="value orange">{discount_value:.2f}%</div><div class="small">Controlled from sidebar</div></div>""", unsafe_allow_html=True)
    with s3:
        decision = selected_row["Decision"]
        cls = "green" if decision == "Accept" else "orange" if decision == "Review" else "red"
        st.markdown(f"""<div class="kpi"><div class="label">Current Decision</div><div class="value {cls}">{decision}</div><div class="small">Based on selected revenue and discount</div></div>""", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_scatter(
        x=sim_df["Discount %"],
        y=sim_df["Net Profit (M)"],
        mode="lines+markers+text",
        text=[f'{v:.2f}' for v in sim_df["Net Profit (M)"]],
        textposition="top center"
    )
    fig.add_hline(y=current_profit, line_dash="dash", line_color="#4ba7ff", annotation_text="Current Net Profit")
    fig.update_layout(
        height=420,
        margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eef5ff"),
        xaxis=dict(title="Discount %", showgrid=False),
        yaxis=dict(title="Net Profit (M)", showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(sim_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- PAGE: RISK -------------------------
else:
    risk_df = pd.DataFrame({
        "Review Area": ["Margin Erosion", "Deviation / Penalty Exposure", "Materials & Fuel Escalation", "Revenue Shortfall"],
        "Review Level": ["Medium", "Medium", "High", "High"],
        "Board Comment": [
            "Controlled if discount stays within 2.5%–3.0%",
            "Manageable under secured annual planning",
            "Requires contractual review / escalation protection",
            "Critical if awarded revenue drops closer to 200M with higher discount"
        ]
    })
    st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">Review Center</div>', unsafe_allow_html=True)
    st.dataframe(risk_df, use_container_width=True, hide_index=True)

    st.markdown(
        '''
        <div class="rule-box">
            <div class="rule-title">Decision Logic Applied</div>
            <div class="rule-text">
                • Board logic is based on <b>risk-adjusted profit</b>, not mathematical profit only.<br>
                • Small uplift does not justify discount plus extra scale and exposure.<br>
                • Revenue below <b>230M</b> does not provide sufficient strategic upside under the agreed assumptions.<br>
                • A <b>5.0%</b> discount requires upper-range revenue and protection clauses before any approval discussion.
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="panel">
        <div class="label" style="font-size:1.02rem;">Board Recommendation</div>
        <div class="small">
        The final preferred range is 2.5%–3.0% because it preserves stronger profitability across the 200M–250M range.
        A 5.0% discount should only be reviewed at 250M with contractual safeguards; otherwise it is rejected.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.caption("Final GitHub-ready dashboard package with fixed 20% net margin logic and visible blue bold sidebar values.")
