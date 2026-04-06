
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Executive Decision Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- THEME -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Tajawal', sans-serif;
}

:root{
    --bg-1:#030916;
    --bg-2:#071326;
    --panel:#0a1a31;
    --panel-2:#0d223f;
    --line:rgba(113,149,201,0.18);
    --text:#edf5ff;
    --muted:#a7b8d3;
    --blue:#48a7ff;
    --cyan:#32e0ff;
    --green:#35d48a;
    --orange:#ffb44a;
    --red:#ff6363;
    --violet:#8b6dff;
}

.stApp{
    background:
        radial-gradient(circle at 15% 5%, rgba(72,167,255,0.20), transparent 18%),
        radial-gradient(circle at 85% 10%, rgba(50,224,255,0.11), transparent 16%),
        radial-gradient(circle at 70% 85%, rgba(255,180,74,0.12), transparent 20%),
        linear-gradient(180deg, var(--bg-1) 0%, #061121 44%, #040b17 100%);
    color: var(--text);
}

.block-container{
    max-width: 1550px;
    padding-top: 1rem;
    padding-bottom: 1rem;
}

h1,h2,h3,h4,h5,h6,p,div,span,label{
    color: var(--text) !important;
}

.small-note{
    color: var(--muted)!important;
    font-size: 0.88rem;
    line-height: 1.5;
}

.top-shell{
    background: linear-gradient(180deg, rgba(10,25,48,0.88), rgba(8,18,34,0.88));
    border: 1px solid rgba(122,161,220,0.12);
    border-radius: 26px;
    padding: 18px 22px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.28);
}

.kpi-card{
    background: linear-gradient(180deg, rgba(11,25,47,0.97), rgba(8,17,32,0.98));
    border: 1px solid rgba(112,156,212,0.15);
    border-radius: 24px;
    padding: 18px 18px 16px 18px;
    min-height: 138px;
    box-shadow: 0 16px 32px rgba(0,0,0,0.22);
}

.kpi-card-glow-green{ box-shadow: 0 12px 28px rgba(53,212,138,0.08);}
.kpi-card-glow-blue{ box-shadow: 0 12px 28px rgba(72,167,255,0.08);}
.kpi-card-glow-orange{ box-shadow: 0 12px 28px rgba(255,180,74,0.08);}
.kpi-card-glow-red{ box-shadow: 0 12px 28px rgba(255,99,99,0.08);}

.kpi-label{
    color: #b4c6e3 !important;
    font-size: 0.88rem;
    letter-spacing: 0.2px;
    margin-bottom: 10px;
}

.kpi-value{
    font-size: 2.1rem;
    font-weight: 800;
    line-height: 1.1;
}

.kpi-sub{
    color: #95a8c7 !important;
    font-size: 0.90rem;
    margin-top: 8px;
}

.panel{
    background: linear-gradient(180deg, rgba(11,25,47,0.97), rgba(8,17,32,0.98));
    border: 1px solid rgba(112,156,212,0.14);
    border-radius: 26px;
    padding: 16px 18px 12px 18px;
    box-shadow: 0 16px 34px rgba(0,0,0,0.22);
    margin-top: 10px;
}

.panel-title{
    font-size: 1.12rem;
    font-weight: 800;
    margin-bottom: 10px;
}

.status-card{
    border-radius: 22px;
    padding: 16px;
    min-height: 145px;
    border: 1px solid rgba(255,255,255,0.08);
}
.status-green{
    background: linear-gradient(180deg, rgba(8,56,41,0.95), rgba(6,34,26,0.96));
}
.status-orange{
    background: linear-gradient(180deg, rgba(72,46,4,0.95), rgba(45,27,4,0.96));
}
.status-red{
    background: linear-gradient(180deg, rgba(68,17,18,0.95), rgba(40,9,10,0.96));
}
.status-title{
    font-size: 1.05rem;
    font-weight: 800;
    margin-bottom: 10px;
}
.status-text{
    color:#dce7f7 !important;
    font-size: 0.96rem;
    line-height: 1.6;
}

.summary-card{
    background: linear-gradient(180deg, rgba(12,25,45,0.98), rgba(9,18,34,0.98));
    border: 1px solid rgba(110,150,208,0.16);
    border-radius: 26px;
    padding: 22px;
    min-height: 340px;
    box-shadow: 0 16px 36px rgba(0,0,0,0.25);
}

.metric-pill{
    display:inline-block;
    padding:6px 12px;
    border-radius:999px;
    margin: 4px 6px 0 0;
    font-size:0.82rem;
    border:1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.05);
}

.green{color:var(--green)!important;}
.orange{color:var(--orange)!important;}
.red{color:var(--red)!important;}
.blue{color:var(--blue)!important;}
.cyan{color:var(--cyan)!important;}

div[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #07111f 0%, #091524 100%);
    border-right: 1px solid rgba(118,154,210,0.12);
}
div[data-testid="stSidebar"] *{
    color:#eff5ff !important;
}
div[data-testid="stSidebar"] [data-baseweb="select"] > div,
div[data-testid="stSidebar"] [data-baseweb="tag"]{
    background: rgba(255,255,255,0.08) !important;
    color:#ffffff !important;
}
div[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div{
    color:#eff5ff !important;
}
.stDataFrame{
    border-radius: 20px;
    overflow: hidden;
}

div[data-testid="stMetric"]{
    background: transparent;
}

hr{
    border-color: rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ------------------------- HELPERS -------------------------
def money(v):
    return f"{v:,.1f}M"

def calc_scenario(revenue, current_margin, discount, op_impact):
    expected_margin = current_margin - discount
    real_margin = expected_margin - op_impact
    net_profit = revenue * real_margin / 100
    return round(expected_margin, 2), round(real_margin, 2), round(net_profit, 2)

def break_even_margin(current_profit, revenue):
    return round((current_profit / revenue) * 100, 2)

def zone_for(real_margin, be_margin):
    if real_margin >= be_margin + 1:
        return "Accept"
    elif real_margin >= be_margin:
        return "Risk"
    return "Reject"

def zone_label(zone, lang):
    if lang == "العربية":
        return {"Accept":"موافقة مشروطة", "Risk":"مراجعة مشروطة", "Reject":"غير موصى به"}[zone]
    return {"Accept":"Conditional Approval", "Risk":"Conditional Review", "Reject":"Not Recommended"}[zone]

def zone_color(zone):
    return {"Accept":"#35d48a", "Risk":"#ffb44a", "Reject":"#ff6363"}[zone]

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
                {'range': [min_v, (min_v+max_v)*0.45], 'color': 'rgba(255,99,99,0.16)'},
                {'range': [(min_v+max_v)*0.45, (min_v+max_v)*0.7], 'color': 'rgba(255,180,74,0.16)'},
                {'range': [(min_v+max_v)*0.7, max_v], 'color': 'rgba(53,212,138,0.16)'}
            ],
            'threshold': {
                'line': {'color': '#ffffff', 'width': 4},
                'thickness': 0.8,
                'value': threshold if threshold is not None else value
            }
        }
    ))
    fig.update_layout(
        height=255,
        margin=dict(l=12, r=12, t=55, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#edf5ff")
    )
    return fig

# ------------------------- SIDEBAR -------------------------
st.sidebar.markdown("## ⚙️ إعدادات اللوحة")
language = st.sidebar.radio("اللغة / Language", ["العربية", "English"], index=0)

ar = language == "العربية"

text = {
    "title": "لوحة القرار التنفيذي الذكية" if ar else "Executive Decision Intelligence Dashboard",
    "sub": "تحليل الخصم مقابل زيادة حجم الأعمال" if ar else "Discount vs Volume Increase Analysis",
    "menu": "العرض التنفيذي" if ar else "Executive View",
    "cur_rev": "الإيراد الحالي" if ar else "Current Revenue",
    "cur_margin": "هامش الربح الحالي %" if ar else "Current Net Margin %",
    "discount": "الخصم المقترح %" if ar else "Proposed Discount %",
    "impact": "الأثر التشغيلي المتوقع %" if ar else "Expected Operational Impact %",
    "revenues": "الإيرادات المقترحة" if ar else "Proposed Revenues",
    "summary": "الملخص التنفيذي" if ar else "Executive Summary",
    "scenario": "تحليل السيناريوهات" if ar else "Scenario Analysis",
    "margin": "تحليل الهامش" if ar else "Margin Analysis",
    "zones": "مناطق القرار" if ar else "Decision Zones",
    "risks": "مؤشرات المخاطر" if ar else "Risk Indicators",
    "recommendation": "التوصية النهائية" if ar else "Final Recommendation",
    "strengths": "نقاط القوة" if ar else "Strengths",
    "weaknesses": "نقاط الضعف والمخاطر" if ar else "Weaknesses & Risks",
    "table": "جدول المقارنة" if ar else "Comparison Table",
}

current_revenue = st.sidebar.slider(text["cur_rev"], 50, 500, 150, 10)
current_margin = st.sidebar.slider(text["cur_margin"], 5.0, 35.0, 20.0, 0.5)
discount = st.sidebar.slider(text["discount"], 0.0, 12.0, 5.0, 0.5)
op_impact = st.sidebar.slider(text["impact"], 0.0, 8.0, 3.0, 0.5)
proposed_revenues = st.sidebar.multiselect(text["revenues"], [180, 200, 220, 230, 250, 275, 300], default=[200, 230, 250])
show_notes = st.sidebar.checkbox("إظهار ملاحظات الإدارة" if ar else "Show management notes", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div class="small-note">
    • اختر الإيرادات المقترحة والخصم والأثر التشغيلي. <br>
    • اللوحة تقارن الربحية الحالية مع الربحية الفعلية بعد الخصم والتشغيل.
    </div>
    """ if ar else """
    <div class="small-note">
    • Select proposed revenues, discount, and operating impact. <br>
    • Dashboard compares current profitability with real post-offer profitability.
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------- DATA -------------------------
current_profit = round(current_revenue * current_margin / 100, 2)

rows = []
for rev in proposed_revenues:
    expected_margin, real_margin, net_profit = calc_scenario(rev, current_margin, discount, op_impact)
    be_margin = break_even_margin(current_profit, rev)
    zone = zone_for(real_margin, be_margin)
    rows.append({
        "Revenue": rev,
        "Expected Margin %": expected_margin,
        "Real Margin %": real_margin,
        "Break-even Margin %": be_margin,
        "Net Profit": net_profit,
        "Delta Profit": round(net_profit - current_profit, 2),
        "Decision Zone": zone
    })

df = pd.DataFrame(rows)
if not df.empty:
    df = df.sort_values(["Net Profit", "Real Margin %"], ascending=[False, False]).reset_index(drop=True)
    best = df.iloc[0]
else:
    best = None

# ------------------------- HEADER -------------------------
left_h, right_h = st.columns([4.8, 1.3])
with left_h:
    st.markdown(f"""
    <div class="top-shell">
        <div style="font-size:2.15rem;font-weight:800;line-height:1.1;">{text["title"]}</div>
        <div class="small-note" style="margin-top:8px;">{text["sub"]}</div>
        <div style="margin-top:12px;">
            <span class="metric-pill">Revenue Baseline: {money(current_revenue)}</span>
            <span class="metric-pill">Net Margin: {current_margin:.1f}%</span>
            <span class="metric-pill">Discount: {discount:.1f}%</span>
            <span class="metric-pill">Operational Impact: {op_impact:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with right_h:
    status = zone_label(best["Decision Zone"], language) if best is not None else "-"
    status_cls = "green" if best is not None and best["Decision Zone"]=="Accept" else "orange" if best is not None and best["Decision Zone"]=="Risk" else "red"
    st.markdown(f"""
    <div class="summary-card">
        <div class="small-note">{text["recommendation"]}</div>
        <div class="kpi-value {status_cls}" style="margin-top:8px;">{status}</div>
        <div class="kpi-sub">{'أفضل مخرجات النموذج الحالي' if ar else 'Best current modeled output'}</div>
        <hr>
        <div class="small-note">{'أفضل إيراد' if ar else 'Best Revenue'}</div>
        <div style="font-size:1.45rem;font-weight:800;">{money(best['Revenue']) if best is not None else '-'}</div>
        <div class="small-note" style="margin-top:8px;">{'الهامش الفعلي' if ar else 'Real Margin'}</div>
        <div style="font-size:1.2rem;font-weight:700;" class="cyan">{best['Real Margin %']:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------- KPI CARDS -------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card kpi-card-glow-blue">
        <div class="kpi-label">{'الإيراد الحالي' if ar else 'Current Revenue'}</div>
        <div class="kpi-value blue">{money(current_revenue)}</div>
        <div class="kpi-sub">{'خط الأساس للمقارنة' if ar else 'Baseline reference point'}</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card kpi-card-glow-green">
        <div class="kpi-label">{'صافي الربح الحالي' if ar else 'Current Net Profit'}</div>
        <div class="kpi-value green">{money(current_profit)}</div>
        <div class="kpi-sub">{'الربح قبل العرض الجديد' if ar else 'Profit before the new offer'}</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    best_profit = best["Net Profit"] if best is not None else 0
    delta = best["Delta Profit"] if best is not None else 0
    delta_cls = "green" if delta >= 0 else "red"
    st.markdown(f"""
    <div class="kpi-card kpi-card-glow-orange">
        <div class="kpi-label">{'أفضل صافي ربح متوقع' if ar else 'Best Expected Net Profit'}</div>
        <div class="kpi-value orange">{money(best_profit)}</div>
        <div class="kpi-sub">{'فرق الربح عن الوضع الحالي' if ar else 'Profit delta vs current'}: <span class="{delta_cls}">{delta:+.1f}M</span></div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    safe_margin = best["Break-even Margin %"] + 1 if best is not None else 0
    st.markdown(f"""
    <div class="kpi-card kpi-card-glow-red">
        <div class="kpi-label">{'الهامش الآمن المطلوب' if ar else 'Safe Margin Needed'}</div>
        <div class="kpi-value">{safe_margin:.1f}%</div>
        <div class="kpi-sub">{'نقطة الربح المقبول بعد هامش أمان' if ar else 'Break-even plus safety buffer'}</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------- MAIN VISUALS -------------------------
l1, l2, l3 = st.columns([1.35, 1.0, 1.0])

with l1:
    st.markdown(f'<div class="panel"><div class="panel-title">{text["scenario"]}</div>', unsafe_allow_html=True)
    fig_profit = go.Figure()
    fig_profit.add_bar(
        x=[f"{int(v)}M" for v in df["Revenue"]],
        y=df["Net Profit"],
        text=[f"{v:.1f}M" for v in df["Net Profit"]],
        textposition="outside",
        marker=dict(
            color=[zone_color(z) for z in df["Decision Zone"]],
            line=dict(color="rgba(255,255,255,0.18)", width=1.0)
        ),
        hovertemplate="%{x}<br>Profit: %{y:.1f}M<extra></extra>"
    )
    fig_profit.add_hline(
        y=current_profit,
        line_color="#48a7ff",
        line_dash="dash",
        annotation_text=("الربح الحالي" if ar else "Current Profit"),
        annotation_position="top left"
    )
    fig_profit.update_layout(
        height=350,
        margin=dict(l=10,r=10,t=10,b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#edf5ff"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="M SAR"),
        showlegend=False
    )
    st.plotly_chart(fig_profit, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with l2:
    title = "الهامش الفعلي" if ar else "Real Margin"
    fig_g1 = gauge(best["Real Margin %"] if best is not None else 0, title, 0, 25, "#32e0ff", "%", threshold=safe_margin)
    st.markdown(f'<div class="panel"><div class="panel-title">{text["margin"]}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_g1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with l3:
    title = "قوة القرار" if ar else "Decision Strength"
    strength_score = 0
    if best is not None:
        if best["Decision Zone"] == "Accept":
            strength_score = 82
        elif best["Decision Zone"] == "Risk":
            strength_score = 58
        else:
            strength_score = 28
    fig_g2 = gauge(strength_score, title, 0, 100, zone_color(best["Decision Zone"]) if best is not None else "#ff6363", "%", threshold=75)
    st.markdown(f'<div class="panel"><div class="panel-title">{text["zones"]}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_g2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- SECOND ROW -------------------------
m1, m2, m3 = st.columns([1.35, 1.0, 1.0])

with m1:
    st.markdown(f'<div class="panel"><div class="panel-title">{text["table"]}</div>', unsafe_allow_html=True)
    show_df = df.copy()
    if ar:
        show_df = show_df.rename(columns={
            "Revenue":"الإيراد",
            "Expected Margin %":"الهامش المتوقع %",
            "Real Margin %":"الهامش الفعلي %",
            "Break-even Margin %":"هامش التعادل %",
            "Net Profit":"صافي الربح",
            "Delta Profit":"فرق الربح",
            "Decision Zone":"منطقة القرار",
        })
        show_df["منطقة القرار"] = show_df["منطقة القرار"].replace({"Accept":"موافقة","Risk":"مخاطرة","Reject":"رفض"})
    st.dataframe(show_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with m2:
    st.markdown(f'<div class="panel"><div class="panel-title">{text["zones"]}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="status-card status-green">
            <div class="status-title">🟢 {'موافقة' if ar else 'Accept'}</div>
            <div class="status-text">{'ربحية أعلى من الوضع الحالي مع هامش آمن' if ar else 'Higher profit than baseline with safe margin'}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="status-card status-orange">
            <div class="status-title">🟡 {'مخاطرة' if ar else 'Risk'}</div>
            <div class="status-text">{'ربح مقبول لكن الهامش قريب من نقطة التعادل' if ar else 'Acceptable profit but margin is close to break-even'}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="status-card status-red">
            <div class="status-title">🔴 {'رفض' if ar else 'Reject'}</div>
            <div class="status-text">{'الربحية لا تبرر مستوى المخاطر' if ar else 'Profitability does not justify the risk level'}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with m3:
    st.markdown(f'<div class="panel"><div class="panel-title">{text["risks"]}</div>', unsafe_allow_html=True)
    risk_names = (
        ["الضغط التشغيلي", "الانحرافات", "الغرامات", "المواد/الوقود"]
        if ar else
        ["Operational", "Deviations", "Penalties", "Materials/Fuel"]
    )
    risk_values = [
        2 if op_impact <= 2 else 3 if op_impact <= 4 else 4,
        2 if discount <= 3 else 3 if discount <= 5 else 4,
        2 if discount <= 4 else 3 if discount <= 6 else 4,
        4
    ]
    risk_fig = go.Figure()
    risk_fig.add_bar(
        x=risk_names,
        y=risk_values,
        text=["L" if v==1 else "M" if v==2 else "H" if v==3 else "C" for v in risk_values],
        textposition="inside",
        marker=dict(color=["#35d48a" if v<=2 else "#ffb44a" if v==3 else "#ff6363" for v in risk_values]),
        hovertemplate="%{x}<extra></extra>"
    )
    risk_fig.update_layout(
        height=310,
        margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#edf5ff"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", tickvals=[1,2,3,4],
                   ticktext=(["Low","Med","High","Critical"] if not ar else ["منخفض","متوسط","مرتفع","حرج"]),
                   range=[0,4.5]),
        showlegend=False
    )
    st.plotly_chart(risk_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- BOTTOM ROW -------------------------
b1, b2, b3 = st.columns([1,1,1])

with b1:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{text["strengths"]}</div>
        <div class="small-note">
        {'• ضمان حجم عمل من بداية العام<br>• تحسين التوريد وشراء المواد مبكرًا<br>• ترتيب الموارد واللوجستيات بوقت كافٍ<br>• وضوح أعلى للخطة المالية السنوية' if ar else '• Secured work volume from the start of the year<br>• Better early procurement and material planning<br>• More time to arrange resources and logistics<br>• Stronger annual financial visibility'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with b2:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{text["weaknesses"]}</div>
        <div class="small-note">
        {'• الخصم يقلل الربح مباشرة<br>• ضغط أعلى على الجودة والتنفيذ<br>• احتمالية زيادة deviations و penalties<br>• خطر ارتفاع أسعار المواد والمحروقات' if ar else '• Discount directly reduces profit<br>• Higher pressure on execution and quality<br>• Higher probability of deviations and penalties<br>• Risk of fuel and material price escalation'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with b3:
    final_zone = best["Decision Zone"] if best is not None else "Reject"
    final_cls = "green" if final_zone=="Accept" else "orange" if final_zone=="Risk" else "red"
    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{text["summary"]}</div>
        <div class="small-note">
        {'القرار الأفضل حاليًا هو' if ar else 'The best current decision is'}:
        </div>
        <div style="font-size:1.4rem;font-weight:800;margin-top:8px;" class="{final_cls}">
            {zone_label(final_zone, language)}
        </div>
        <div class="small-note" style="margin-top:10px;">
        {'يوصى بالموافقة المشروطة فقط إذا بقي الهامش الفعلي أعلى من هامش التعادل مع إضافة هامش أمان، مع متابعة شهرية للغرامات والانحرافات.' if ar else 'Conditional approval is recommended only if real margin stays above break-even with safety buffer, with monthly monitoring of deviations and penalties.'}
        </div>
        {'<hr><div class="small-note"><b>ملاحظة:</b> في حال الرفض الكامل قد يتم توزيع الأعمال على مقاولين آخرين مما يؤثر على حصة العام القادم.</div>' if ar and show_notes else ''}
        {'<hr><div class="small-note"><b>Note:</b> A full rejection may lead to future work redistribution to other contractors.</div>' if (not ar) and show_notes else ''}
    </div>
    """, unsafe_allow_html=True)

st.caption("تم إعداد هذه اللوحة كنسخة تنفيذية أقرب للستايل الاستشاري الحديث." if ar else "Prepared as a modern consulting-style executive dashboard.")
