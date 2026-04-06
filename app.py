
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
    page_title="Executive Decision Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- THEME -------------------------
st.markdown("""
<style>
:root{
    --bg1:#030916; --bg2:#071326; --panel:#0a1a31; --panel2:#0d223f; --text:#edf5ff; --muted:#a7b8d3;
    --blue:#48a7ff; --cyan:#32e0ff; --green:#35d48a; --orange:#ffb44a; --red:#ff6363; --line:rgba(112,156,212,0.14);
}
.stApp{
    background:
        radial-gradient(circle at 15% 5%, rgba(72,167,255,0.20), transparent 18%),
        radial-gradient(circle at 85% 10%, rgba(50,224,255,0.11), transparent 16%),
        radial-gradient(circle at 70% 85%, rgba(255,180,74,0.12), transparent 20%),
        linear-gradient(180deg, var(--bg1) 0%, #061121 44%, #040b17 100%);
    color: var(--text);
}
.block-container{max-width:1550px;padding-top:0.8rem;padding-bottom:1rem;}
h1,h2,h3,h4,h5,h6,p,div,span,label{color:var(--text)!important;}
.small{color:var(--muted)!important;font-size:.88rem;line-height:1.6;}
.brand{
    background: linear-gradient(180deg, rgba(10,25,48,0.90), rgba(8,18,34,0.90));
    border: 1px solid rgba(122,161,220,0.12);
    border-radius: 26px;
    padding: 18px 22px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.28);
}
.kpi{
    background: linear-gradient(180deg, rgba(11,25,47,0.97), rgba(8,17,32,0.98));
    border: 1px solid rgba(112,156,212,0.15);
    border-radius: 24px;
    padding: 18px;
    min-height: 132px;
    box-shadow: 0 16px 32px rgba(0,0,0,0.22);
}
.panel{
    background: linear-gradient(180deg, rgba(11,25,47,0.97), rgba(8,17,32,0.98));
    border: 1px solid rgba(112,156,212,0.14);
    border-radius: 26px;
    padding: 16px 18px 12px 18px;
    box-shadow: 0 16px 34px rgba(0,0,0,0.22);
    margin-top: 10px;
}
.label{color:#b4c6e3!important;font-size:.88rem;margin-bottom:8px;}
.title{font-size:2.15rem;font-weight:800;line-height:1.1;}
.value{font-size:2rem;font-weight:800;line-height:1.1;}
.blue{color:var(--blue)!important;} .green{color:var(--green)!important;} .orange{color:var(--orange)!important;}
.red{color:var(--red)!important;} .cyan{color:var(--cyan)!important;}
.pill{
    display:inline-block;padding:6px 12px;border-radius:999px;margin:4px 6px 0 0;
    font-size:.82rem;border:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.05);
}
.menu-item{
    padding:10px 14px;border-radius:14px;margin:6px 0;background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.06);font-weight:600;
}
.state{
    border-radius:20px;padding:16px;min-height:140px;border:1px solid rgba(255,255,255,0.08);
}
.accept{background: linear-gradient(180deg, rgba(8,56,41,0.95), rgba(6,34,26,0.96));}
.risk{background: linear-gradient(180deg, rgba(72,46,4,0.95), rgba(45,27,4,0.96));}
.reject{background: linear-gradient(180deg, rgba(68,17,18,0.95), rgba(40,9,10,0.96));}
div[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #07111f 0%, #091524 100%);
    border-right: 1px solid rgba(118,154,210,0.12);
}
div[data-testid="stSidebar"] *{color:#eff5ff !important;}
div[data-testid="stSidebar"] [data-baseweb="select"] > div,
div[data-testid="stSidebar"] [data-baseweb="tag"]{
    background: rgba(255,255,255,0.08) !important;
    color:#ffffff !important;
}
.stDataFrame{border-radius:20px;overflow:hidden;}
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

def build_pdf(summary):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Background
    c.setFillColorRGB(0.03, 0.07, 0.14)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Header block
    c.setFillColorRGB(0.05, 0.12, 0.24)
    c.roundRect(15*mm, height-55*mm, width-30*mm, 35*mm, 8*mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(22*mm, height-32*mm, "Executive Decision Dashboard")
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.75, 0.82, 0.92)
    c.drawString(22*mm, height-39*mm, "Discount vs Volume Increase - Executive Summary")

    y = height - 72*mm
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20*mm, y, "Key Metrics")
    y -= 8*mm

    c.setFont("Helvetica", 11)
    lines = [
        f"Current Revenue: {summary['current_revenue']}",
        f"Current Net Margin: {summary['current_margin']}",
        f"Current Net Profit: {summary['current_profit']}",
        f"Selected Discount: {summary['discount']}",
        f"Operational Impact: {summary['op_impact']}",
        f"Best Scenario Revenue: {summary['best_revenue']}",
        f"Best Real Margin: {summary['best_real_margin']}",
        f"Best Net Profit: {summary['best_net_profit']}",
        f"Recommendation: {summary['recommendation']}",
    ]
    for line in lines:
        c.drawString(22*mm, y, line)
        y -= 7*mm

    y -= 4*mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20*mm, y, "Management Notes")
    y -= 8*mm
    c.setFont("Helvetica", 11)
    notes = [
        "1. Conditional approval is preferred only when real margin remains above break-even with safety buffer.",
        "2. Main strengths: secured pipeline, early procurement planning, resource readiness, cash-flow clarity.",
        "3. Main risks: discount erosion, operating pressure, penalties, and material/fuel escalation.",
        "4. Full rejection may reduce next year's market share if work is redistributed to other contractors."
    ]
    for note in notes:
        c.drawString(22*mm, y, note[:110])
        y -= 7*mm

    c.setFillColorRGB(0.65, 0.75, 0.88)
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, 12*mm, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    buffer.seek(0)
    return buffer

# ------------------------- SIDEBAR -------------------------
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("### التنقل")
menu = st.sidebar.radio(
    "",
    ["🏠 Executive Overview", "🎯 Discount Simulator", "⚠️ Risk Center"],
    index=0
)

st.sidebar.markdown("### المدخلات الأساسية")
current_revenue = st.sidebar.slider("الإيراد الحالي", 50, 500, 150, 10)
current_margin = st.sidebar.slider("هامش الربح الحالي %", 5.0, 35.0, 20.0, 0.5)
discount = st.sidebar.slider("الخصم الحالي %", 0.0, 12.0, 5.0, 0.5)
op_impact = st.sidebar.slider("الأثر التشغيلي المتوقع %", 0.0, 8.0, 3.0, 0.5)
proposed_revenues = st.sidebar.multiselect("الإيرادات المقترحة", [180,200,220,230,250,275,300], default=[200,230,250])

st.sidebar.markdown("### الهوية والعلامة")
company_name = st.sidebar.text_input("اسم الشركة", value="MST Executive")
brand_line = st.sidebar.text_input("وصف مختصر", value="Commercial Decision Dashboard")
show_brand_notes = st.sidebar.checkbox("إظهار الملاحظات الإدارية", value=True)

current_profit = round(current_revenue * current_margin / 100.0, 2)
rows = [calc_row(r, current_margin, discount, op_impact, current_profit) for r in proposed_revenues]
df = pd.DataFrame(rows)
if not df.empty:
    df = df.sort_values(["Net Profit", "Real Margin %"], ascending=[False, False]).reset_index(drop=True)
    best = df.iloc[0]
else:
    best = None

safe_margin = round((best["Break-even Margin %"] + 1), 2) if best is not None else 0

# PDF export
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
pdf_buffer = build_pdf(summary)

# ------------------------- HEADER -------------------------
top1, top2 = st.columns([4.7, 1.5])
with top1:
    st.markdown(f"""
    <div class="brand">
        <div class="title">{company_name}</div>
        <div class="small">{brand_line}</div>
        <div style="margin-top:10px;">
            <span class="pill">Baseline Revenue: {money(current_revenue)}</span>
            <span class="pill">Net Margin: {current_margin:.1f}%</span>
            <span class="pill">Discount: {discount:.1f}%</span>
            <span class="pill">Operational Impact: {op_impact:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.download_button(
        "📄 Download PDF Summary",
        data=pdf_buffer,
        file_name="executive_decision_summary.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown(f"""
    <div class="small" style="margin-top:12px;">
    أفضل مخرجات النموذج الحالي:<br>
    <b>{money(best["Revenue"]) if best is not None else "-"}</b><br>
    الهامش الفعلي: <b>{best["Real Margin %"]:.1f}%</b><br>
    القرار: <b>{zone_ar(best["Decision Zone"]) if best is not None else "-"}</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- PAGE 1 -------------------------
if menu == "🏠 Executive Overview":
    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi"><div class="label">الإيراد الحالي</div><div class="value blue">{money(current_revenue)}</div><div class="small">خط الأساس للمقارنة</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi"><div class="label">صافي الربح الحالي</div><div class="value green">{money(current_profit)}</div><div class="small">الربح قبل العرض الجديد</div></div>""", unsafe_allow_html=True)
    with k3:
        delta = best["Delta Profit"] if best is not None else 0
        delta_cls = "green" if delta >= 0 else "red"
        st.markdown(f"""<div class="kpi"><div class="label">أفضل صافي ربح متوقع</div><div class="value orange">{money(best["Net Profit"]) if best is not None else "-"}</div><div class="small">فرق الربح: <span class="{delta_cls}">{delta:+.1f}M</span></div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi"><div class="label">الهامش الآمن المطلوب</div><div class="value">{safe_margin:.1f}%</div><div class="small">هامش التعادل + أمان</div></div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.35,1,1])
    with c1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">تحليل السيناريوهات</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(
            x=[f"{int(v)}M" for v in df["Revenue"]],
            y=df["Net Profit"],
            text=[f"{v:.1f}M" for v in df["Net Profit"]],
            textposition="outside",
            marker=dict(color=[zone_color(z) for z in df["Decision Zone"]], line=dict(color="rgba(255,255,255,0.18)", width=1)),
            hovertemplate="%{x}<br>Profit %{y:.1f}M<extra></extra>"
        )
        fig.add_hline(y=current_profit, line_dash="dash", line_color="#48a7ff", annotation_text="Current Profit", annotation_position="top left")
        fig.update_layout(height=350, margin=dict(l=10,r=10,t=10,b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="M SAR"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">تحليل الهامش</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge(best["Real Margin %"] if best is not None else 0, "الهامش الفعلي", 0, 25, "#32e0ff", "%", threshold=safe_margin), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        score = 82 if best is not None and best["Decision Zone"]=="Accept" else 58 if best is not None and best["Decision Zone"]=="Risk" else 28
        st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">قوة القرار</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge(score, "Decision Strength", 0, 100, zone_color(best["Decision Zone"]) if best is not None else "#ff6363", "%", threshold=75), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    m1,m2,m3 = st.columns([1.35,1,1])
    with m1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">جدول المقارنة</div>', unsafe_allow_html=True)
        show_df = df.rename(columns={
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
        st.markdown("""
        <div class="panel"><div class="label" style="font-size:1.05rem;">مناطق القرار</div>
            <div class="state accept"><b>🟢 موافقة</b><br><span class="small">ربحية أعلى من الوضع الحالي مع هامش آمن</span></div><br>
            <div class="state risk"><b>🟡 مخاطرة</b><br><span class="small">ربح مقبول لكن الهامش قريب من نقطة التعادل</span></div><br>
            <div class="state reject"><b>🔴 رفض</b><br><span class="small">الربحية لا تبرر مستوى المخاطر</span></div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        final_cls = "green" if best is not None and best["Decision Zone"]=="Accept" else "orange" if best is not None and best["Decision Zone"]=="Risk" else "red"
        st.markdown(f"""
        <div class="panel">
            <div class="label" style="font-size:1.05rem;">الملخص التنفيذي</div>
            <div class="small">القرار الأفضل حاليًا هو:</div>
            <div class="value {final_cls}" style="margin-top:8px;">{zone_ar(best["Decision Zone"]) if best is not None else "-"}</div>
            <div class="small" style="margin-top:10px;">
            يوصى بالموافقة المشروطة فقط إذا بقي الهامش الفعلي أعلى من هامش التعادل مع إضافة هامش أمان، مع متابعة شهرية للغرامات والانحرافات.
            </div>
            {'<hr><div class="small"><b>ملاحظة:</b> في حال الرفض الكامل قد يتم توزيع الأعمال على مقاولين آخرين مما يؤثر على حصة العام القادم.</div>' if show_brand_notes else ''}
        </div>
        """, unsafe_allow_html=True)

# ------------------------- PAGE 2 -------------------------
elif menu == "🎯 Discount Simulator":
    st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">Discount Simulator</div></div>', unsafe_allow_html=True)
    d_min, d_max = st.slider("نطاق الخصم للمحاكاة %", 0.0, 12.0, (0.0, 10.0), 0.5)
    selected_revenue = st.selectbox("الإيراد المراد محاكاته", [180,200,220,230,250,275,300], index=4)
    step = st.selectbox("درجة الحركة", [0.5, 1.0], index=0)
    active_discount = st.slider("الخصم المراد تحليله %", d_min, d_max, min(discount, d_max), step)

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
        st.markdown(f"""<div class="kpi"><div class="label">الخصم الحالي المختار</div><div class="value orange">{current_row['Discount %']:.1f}%</div><div class="small">الخصم الذي يتم تحليله الآن</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="kpi"><div class="label">الهامش الفعلي</div><div class="value cyan">{current_row['Real Margin %']:.1f}%</div><div class="small">بعد الخصم والأثر التشغيلي</div></div>""", unsafe_allow_html=True)
    with s3:
        cls = "green" if current_row["Delta Profit"] >= 0 else "red"
        st.markdown(f"""<div class="kpi"><div class="label">صافي الربح المتوقع</div><div class="value {cls}">{money(current_row['Net Profit'])}</div><div class="small">فرق الربح: <span class="{cls}">{current_row['Delta Profit']:+.1f}M</span></div></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="kpi"><div class="label">أفضل خصم مقبول</div><div class="value green">{f"{best_safe_discount:.1f}%" if best_safe_discount is not None else "لا يوجد"}</div><div class="small">أعلى خصم ما زال داخل الموافقة</div></div>""", unsafe_allow_html=True)

    p1,p2 = st.columns([1.4,1])
    with p1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">منحنى الخصم مقابل صافي الربح</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_scatter(
            x=sim_df["Discount %"], y=sim_df["Net Profit"], mode="lines+markers",
            line=dict(color="#48a7ff", width=4),
            marker=dict(size=10, color=[zone_color(z) for z in sim_df["Decision Zone"]]),
            hovertemplate="Discount %{x:.1f}%<br>Profit %{y:.1f}M<extra></extra>"
        )
        fig.add_hline(y=current_profit, line_dash="dash", line_color="#35d48a", annotation_text="Current Profit", annotation_position="top left")
        fig.update_layout(height=380, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(title="Discount %", showgrid=False), yaxis=dict(title="Net Profit (M SAR)", showgrid=True, gridcolor="rgba(255,255,255,0.08)"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">منحنى الخصم مقابل الهامش الفعلي</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_scatter(
            x=sim_df["Discount %"], y=sim_df["Real Margin %"], mode="lines+markers",
            line=dict(color="#32e0ff", width=4),
            marker=dict(size=10, color=[zone_color(z) for z in sim_df["Decision Zone"]]),
            hovertemplate="Discount %{x:.1f}%<br>Real Margin %{y:.1f}%<extra></extra>"
        )
        fig2.add_hline(y=current_row["Break-even Margin %"], line_dash="dash", line_color="#ffb44a", annotation_text=f"Break-even {current_row['Break-even Margin %']:.1f}%", annotation_position="top left")
        fig2.update_layout(height=380, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(title="Discount %", showgrid=False), yaxis=dict(title="Real Margin %", showgrid=True, gridcolor="rgba(255,255,255,0.08)"))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">جدول المحاكاة</div>', unsafe_allow_html=True)
    show_sim = sim_df.rename(columns={
        "Discount %":"الخصم %","Expected Margin %":"الهامش المتوقع %","Real Margin %":"الهامش الفعلي %","Net Profit":"صافي الربح","Break-even Margin %":"هامش التعادل %","Decision Zone":"منطقة القرار","Delta Profit":"فرق الربح"
    })
    show_sim["منطقة القرار"] = show_sim["منطقة القرار"].replace({"Accept":"موافقة","Risk":"مخاطرة","Reject":"رفض"})
    st.dataframe(show_sim, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- PAGE 3 -------------------------
else:
    st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">Risk Center</div></div>', unsafe_allow_html=True)

    risk_names = ["الضغط التشغيلي", "الانحرافات", "الغرامات", "المواد/الوقود"]
    risk_values = [
        2 if op_impact <= 2 else 3 if op_impact <= 4 else 4,
        2 if discount <= 3 else 3 if discount <= 5 else 4,
        2 if discount <= 4 else 3 if discount <= 6 else 4,
        4
    ]
    risk_colors = ["#35d48a" if v<=2 else "#ffb44a" if v==3 else "#ff6363" for v in risk_values]

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""<div class="kpi"><div class="label">مستوى الضغط التشغيلي</div><div class="value {'green' if risk_values[0]<=2 else 'orange' if risk_values[0]==3 else 'red'}">{['-','منخفض','متوسط','مرتفع','حرج'][risk_values[0]]}</div><div class="small">مرتبط بالأثر التشغيلي المدخل</div></div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""<div class="kpi"><div class="label">مخاطر الربحية</div><div class="value {'green' if best is not None and best['Decision Zone']=='Accept' else 'orange' if best is not None and best['Decision Zone']=='Risk' else 'red'}">{zone_ar(best['Decision Zone']) if best is not None else '-'}</div><div class="small">تعتمد على الهامش الفعلي مقابل هامش التعادل</div></div>""", unsafe_allow_html=True)
    with r3:
        st.markdown(f"""<div class="kpi"><div class="label">أثر المواد والوقود</div><div class="value red">مرتفع</div><div class="small">خطر خارجي يحتاج بند مراجعة أسعار</div></div>""", unsafe_allow_html=True)

    rc1, rc2 = st.columns([1.1, 1])
    with rc1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.05rem;">مصفوفة المخاطر</div>', unsafe_allow_html=True)
        risk_fig = go.Figure()
        risk_fig.add_bar(
            x=risk_names, y=risk_values,
            text=["L" if v==1 else "M" if v==2 else "H" if v==3 else "C" for v in risk_values],
            textposition="inside",
            marker=dict(color=risk_colors),
            hovertemplate="%{x}<extra></extra>"
        )
        risk_fig.update_layout(height=350, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", tickvals=[1,2,3,4], ticktext=["منخفض","متوسط","مرتفع","حرج"], range=[0,4.5]), showlegend=False)
        st.plotly_chart(risk_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rc2:
        st.markdown("""
        <div class="panel">
            <div class="label" style="font-size:1.05rem;">خطة التعامل مع المخاطر</div>
            <div class="small">
            • تحديد سقف خصم واضح وربطه بحجم أعمال مضمون.<br>
            • إدراج بند مراجعة أسعار للمواد والمحروقات إن أمكن.<br>
            • متابعة شهرية للانحرافات والغرامات والتكلفة الإضافية.<br>
            • تجهيز خطة موارد وتوريد من بداية السنة لتقليل الارتباك التشغيلي.<br>
            • عدم اتخاذ قرار نهائي بناءً على الإيراد فقط؛ بل على الربحية الفعلية.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
        <div class="label" style="font-size:1.05rem;">قراءة تنفيذية سريعة</div>
        <div class="small">
        في حال قبول العرض مع خصم مرتفع دون حماية تعاقدية، فإن الخطر الأكبر لن يكون فقط انخفاض هامش الربح، بل أيضًا ارتفاع الانحرافات والغرامات وتكاليف التشغيل. 
        وفي حال الرفض الكامل، قد يتم توزيع جزء من الأعمال على مقاولين آخرين مما يضغط على حصة العام القادم. لذلك فإن الاتجاه الأفضل غالبًا هو الموافقة المشروطة مع حدود خصم وآلية متابعة واضحة.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.caption("نسخة تنفيذية متكاملة: Executive Overview + Discount Simulator + Risk Center + PDF Export.")
