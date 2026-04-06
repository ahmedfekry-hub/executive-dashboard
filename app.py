
import io
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
    background: rgba(255,255,255,0.10) !important;
    color:#ffffff !important;
    border-radius: 12px !important;
    -webkit-text-fill-color:#ffffff !important;
    opacity:1 !important;
}
[data-testid="stSidebar"] input[type="number"]{
    color:#ffffff !important;
    -webkit-text-fill-color:#ffffff !important;
    font-weight:700 !important;
}
[data-testid="stSidebar"] button[title="Increment value"],
[data-testid="stSidebar"] button[title="Decrement value"]{
    color:#ffffff !important;
    opacity:1 !important;
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
        return "موافقة"
    elif real_margin >= be_margin:
        return "Risk"
    return "رفض"

def zone_ar(z):
    return {"موافقة":"موافقة مشروطة", "Risk":"مراجعة مشروطة", "رفض":"غير موصى به"}[z]

def zone_color(z):
    return {"موافقة":"#35d48a", "Risk":"#ffb44a", "رفض":"#ff6363"}[z]

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

    # Try Arabic-capable font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        pdfmetrics.registerFont(TTFont("ArabicFontBold", bold_path))
        font_regular = "ArabicFont"
        font_bold = "ArabicFontBold"
    except Exception:
        font_regular = "Helvetica"
        font_bold = "Helvetica-Bold"

    def rtl_text(s):
        # Light fallback for Arabic rendering direction in PDF
        try:
            return str(s)[::-1]
        except Exception:
            return str(s)

    def draw_rtl(x_right, y, text, font_name=font_regular, size=10, color=colors.white):
        c.setFont(font_name, size)
        c.setFillColor(color)
        t = rtl_text(text)
        c.drawRightString(x_right, y, t)

    # Background
    c.setFillColorRGB(0.02, 0.07, 0.14)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Header
    c.setFillColorRGB(0.04, 0.12, 0.24)
    c.roundRect(14*mm, height-50*mm, width-28*mm, 32*mm, 8*mm, fill=1, stroke=0)
    draw_rtl(width-20*mm, height-28*mm, "لوحة القرار التنفيذي - الملخص الاستشاري", font_bold, 16)
    draw_rtl(width-20*mm, height-36*mm, "تحليل الخصم مقابل زيادة حجم الأعمال", font_regular, 10, colors.HexColor("#bfd0e8"))

    y = height - 62*mm
    draw_rtl(width-18*mm, y, "المؤشرات الرئيسية", font_bold, 12)
    y -= 8*mm

    lines = [
        f"الإيراد الحالي: {summary['current_revenue']}",
        f"هامش الربح الحالي: {summary['current_margin']}",
        f"صافي الربح الحالي: {summary['current_profit']}",
        f"الخصم المقترح: {summary['discount']} | الأثر التشغيلي: {summary['op_impact']}",
        f"أفضل سيناريو إيراد: {summary['best_revenue']}",
        f"الهامش الفعلي الأفضل: {summary['best_real_margin']}",
        f"أفضل صافي ربح: {summary['best_net_profit']}",
        f"التوصية: {summary['recommendation']}",
    ]
    for line in lines:
        draw_rtl(width-20*mm, y, line, font_regular, 10)
        y -= 6.6*mm

    # Profit comparison chart
    y_chart_top = y - 6*mm
    draw_rtl(width-18*mm, y_chart_top, "مقارنة صافي الربح للسيناريوهات", font_bold, 12)
    chart_x = 18*mm
    chart_y = y_chart_top - 48*mm
    chart_w = 84*mm
    chart_h = 38*mm
    c.setStrokeColorRGB(0.45, 0.55, 0.7)
    c.rect(chart_x, chart_y, chart_w, chart_h, fill=0, stroke=1)

    if len(df) > 0:
        max_profit = max(float(df["Net Profit"].max()), 1)
        bar_gap = 5*mm
        bar_w = (chart_w - (len(df)+1)*bar_gap) / max(len(df),1)
        for i, row in enumerate(df.to_dict(orient="records")):
            bx = chart_x + bar_gap + i*(bar_w + bar_gap)
            profit_val = float(row.get("Net Profit", 0))
            bh = (profit_val / max_profit) * (chart_h - 8*mm)
            by = chart_y + 4*mm
            color = row.get("Decision Zone", "رفض")
            if color == "موافقة":
                c.setFillColorRGB(0.21, 0.83, 0.54)
            elif color == "Risk":
                c.setFillColorRGB(1.0, 0.71, 0.29)
            else:
                c.setFillColorRGB(1.0, 0.39, 0.39)
            c.rect(bx, by, bar_w, bh, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont(font_regular, 8)
            c.drawCentredString(bx + bar_w/2, chart_y - 4*mm, f"{int(row.get('Revenue', 0))}")
            c.drawCentredString(bx + bar_w/2, by + bh + 2*mm, f"{profit_val:.1f}")

    # Margin trend
    mx = 112*mm
    my = chart_y
    mw = 80*mm
    mh = chart_h
    c.setStrokeColorRGB(0.45, 0.55, 0.7)
    c.rect(mx, my, mw, mh, fill=0, stroke=1)
    draw_rtl(width-18*mm, y_chart_top, "اتجاه الهامش الفعلي", font_bold, 12)
    if len(df) > 1:
        max_m = max(float(df["Real Margin %"].max()), 1)
        min_m = min(float(df["Real Margin %"].min()), 0)
        rng = max(max_m - min_m, 1)
        points = []
        for i, row in enumerate(df.to_dict(orient="records")):
            px = mx + 7*mm + i*((mw-14*mm)/(len(df)-1))
            py = my + 6*mm + ((float(row.get("Real Margin %", 0)) - min_m)/rng)*(mh-12*mm)
            points.append((px, py))
        c.setStrokeColorRGB(0.22, 0.87, 1.0)
        c.setLineWidth(2)
        for i in range(len(points)-1):
            c.line(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        for i, pt in enumerate(points):
            c.setFillColorRGB(0.29, 0.65, 1.0)
            c.circle(pt[0], pt[1], 2.3, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont(font_regular, 8)
            c.drawCentredString(pt[0], my - 4*mm, f"{int(df.iloc[i]['Revenue'])}")

    y2 = chart_y - 18*mm
    draw_rtl(width-18*mm, y2, "ملاحظات الإدارة", font_bold, 12)
    y2 -= 8*mm
    notes = [
        "١. يوصى بالموافقة المشروطة فقط إذا بقي الهامش الفعلي أعلى من هامش التعادل مع هامش أمان مناسب.",
        "٢. نقاط القوة: ضمان حجم أعمال مبكر، تحسين التوريد، جاهزية الموارد، ووضوح الخطة المالية.",
        "٣. أهم المخاطر: تآكل الربحية بسبب الخصم، ضغط التشغيل، الغرامات، وارتفاع أسعار المواد والمحروقات.",
        "٤. الرفض الكامل قد يؤدي إلى انخفاض حصة العام القادم إذا تم توزيع الأعمال على مقاولين آخرين."
    ]
    for note in notes:
        draw_rtl(width-20*mm, y2, note, font_regular, 9.5)
        y2 -= 6.7*mm

    c.setFillColorRGB(0.7, 0.78, 0.9)
    c.setFont(font_regular, 8.5)
    c.drawString(18*mm, 10*mm, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    buffer.seek(0)
    return buffer

# ------------------------- SIDEBAR -------------------------
st.sidebar.image("brand_logo.png", use_container_width=True)

st.sidebar.markdown("### التنقل")
menu = st.sidebar.radio(
    "",
    ["🏠 النظرة التنفيذية", "🎯 محاكي الخصم", "⚠️ مركز المخاطر"],
    index=0
)

st.sidebar.markdown("### المدخلات التجارية النهائية")
current_revenue = st.sidebar.number_input("الإيراد الحالي (مليون ريال)", min_value=0.0, value=150.0, step=10.0, format="%.1f")
current_margin = st.sidebar.number_input("هامش الربح الحالي %", min_value=0.0, value=20.0, step=0.5, format="%.1f")
discount = st.sidebar.number_input("الخصم %", min_value=0.0, value=5.0, step=0.5, format="%.1f")
op_impact = st.sidebar.number_input("الأثر التشغيلي %", min_value=0.0, value=3.0, step=0.5, format="%.1f")
proposed_revenues = st.sidebar.multiselect("الإيرادات المقترحة (مليون ريال)", [180,200,220,230,250,275,300], default=[200,230,250])

st.sidebar.markdown("### الهوية والعلامة")
dashboard_title = st.sidebar.text_input("عنوان اللوحة", value="MST Executive")
dashboard_subtitle = st.sidebar.text_input("العنوان الفرعي", value="Commercial Decision Dashboard")
show_management_notes = st.sidebar.checkbox("إظهار الملاحظات الإدارية", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="small">
استخدم المدخلات التجارية النهائية لتحديث جميع المؤشرات والرسوم ونتائج المحاكاة والمخاطر وملف PDF تلقائياً.
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
            <span class="pill">الإيراد الحالي: {money(current_revenue)}</span>
            <span class="pill">هامش الربح الحالي: {current_margin:.1f}%</span>
            <span class="pill">Discount: {discount:.1f}%</span>
            <span class="pill">الأثر التشغيلي: {op_impact:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.download_button(
        "📄 تحميل التقرير الاستشاري PDF",
        data=pdf_buffer,
        file_name="mst_executive_dashboard_summary.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown(f"""
    <div class="small" style="margin-top:10px;">
    أفضل سيناريو حالي:<br>
    <b>{money(best["Revenue"]) if best is not None else "-"}</b><br>
    الهامش الفعلي: <b>{best["Real Margin %"]:.1f}%</b><br>
    التوصية: <b>{zone_ar(best["Decision Zone"]) if best is not None else "-"}</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- PAGES -------------------------
if menu == "🏠 النظرة التنفيذية":
    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi"><div class="label">الإيراد الحالي</div><div class="value blue">{money(current_revenue)}</div><div class="small">خط الأساس الرئيسي للنقاش</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi"><div class="label">صافي الربح الحالي</div><div class="value green">{money(current_profit)}</div><div class="small">قبل تطبيق العرض الجديد</div></div>""", unsafe_allow_html=True)
    with k3:
        delta = best["Delta Profit"] if best is not None else 0
        delta_cls = "green" if delta >= 0 else "red"
        st.markdown(f"""<div class="kpi"><div class="label">أفضل صافي ربح متوقع</div><div class="value orange">{money(best["Net Profit"]) if best is not None else "-"}</div><div class="small">فرق الربح: <span class="{delta_cls}">{delta:+.1f}M</span></div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi"><div class="label">الهامش الآمن المطلوب</div><div class="value">{safe_margin:.1f}%</div><div class="small">هامش التعادل + هامش أمان</div></div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.5,1,1])
    with c1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">مقارنة صافي الربح للسيناريوهات</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(
            x=[f"{int(v)}M" for v in df["Revenue"]],
            y=df["Net Profit"],
            text=[f"{v:.1f}M" for v in df["Net Profit"]],
            textposition="outside",
            marker=dict(color=[zone_color(z) for z in df["Decision Zone"]], line=dict(color="rgba(255,255,255,0.18)", width=1)),
            hovertemplate="%{x}<br>Net Profit %{y:.1f}M<extra></extra>"
        )
        fig.add_hline(y=current_profit, line_dash="dash", line_color="#48a7ff", annotation_text="الربح الحالي", annotation_position="top left")
        fig.update_layout(height=365, margin=dict(l=10,r=10,t=10,b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="M SAR"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">مؤشر الهامش الفعلي</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge(best["Real Margin %"] if best is not None else 0, "Real Margin", 0, 25, "#37ddff", "%", threshold=safe_margin), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        score = 82 if best is not None and best["Decision Zone"]=="موافقة" else 58 if best is not None and best["Decision Zone"]=="Risk" else 28
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">قوة القرار</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge(score, "قوة القرار", 0, 100, zone_color(best["Decision Zone"]) if best is not None else "#ff6363", "%", threshold=75), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    m1,m2,m3 = st.columns([1.45,1,1])
    with m1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">جدول المقارنة</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="panel"><div class="label" style="font-size:1.02rem;">مناطق القرار</div>
            <div class="state accept"><b>🟢 موافقة</b><br><span class="small">ربحية أعلى من الوضع الحالي مع هامش فعلي آمن.</span></div><br>
            <div class="state risk"><b>🟡 مراجعة</b><br><span class="small">موافقةable result, but margin is close to break-even.</span></div><br>
            <div class="state reject"><b>🔴 رفض</b><br><span class="small">الربحية لا تبرر مستوى المخاطر.</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        final_cls = "green" if best is not None and best["Decision Zone"]=="موافقة" else "orange" if best is not None and best["Decision Zone"]=="Risk" else "red"
        notes_html = """
        <hr><div class="small"><b>ملاحظة إدارية:</b> الرفض الكامل قد يقلل حصة العام القادم إذا أعيد توزيع الأعمال على مقاولين آخرين.</div>
        """ if show_management_notes else ""
        st.markdown(f"""
        <div class="panel">
            <div class="label" style="font-size:1.02rem;">الملخص التنفيذي</div>
            <div class="small">التوصية الحالية:</div>
            <div class="value {final_cls}" style="margin-top:8px;">{zone_ar(best["Decision Zone"]) if best is not None else "-"}</div>
            <div class="small" style="margin-top:10px;">
            يوصى بالموافقة المشروطة فقط إذا بقي الهامش الفعلي أعلى من هامش التعادل مع هامش أمان، مع القدرة على ضبط الانحرافات والغرامات وتقلبات التوريد.
            </div>
            {notes_html}
        </div>
        """, unsafe_allow_html=True)

elif menu == "🎯 محاكي الخصم":
    d_min, d_max = st.slider("نطاق الخصم للمحاكاة %", 0.0, 12.0, (0.0, 10.0), 0.5)
    selected_revenue = st.selectbox("الإيراد المراد محاكاته", [180,200,220,230,250,275,300], index=4)
    step = st.selectbox("درجة الحركة", [0.5, 1.0], index=0)
    active_discount = st.slider("الخصم الجاري تحليله %", d_min, d_max, min(discount, d_max), step)

    discount_values = []
    x = d_min
    while x <= d_max + 1e-9:
        discount_values.append(round(x,2))
        x += step
    sim_df = pd.DataFrame([calc_row(selected_revenue, current_margin, d, op_impact, current_profit) | {"Discount %": d} for d in discount_values])
    current_row = sim_df[sim_df["Discount %"] == round(active_discount,2)]
    current_row = current_row.iloc[0] if not current_row.empty else sim_df.iloc[0]
    safe_df = sim_df[sim_df["Decision Zone"]=="موافقة"]
    best_safe_discount = safe_df["Discount %"].max() if not safe_df.empty else None

    s1,s2,s3,s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="kpi"><div class="label">الخصم المختار</div><div class="value orange">{current_row['Discount %']:.1f}%</div><div class="small">الخصم الجاري تقييمه الآن</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="kpi"><div class="label">Real Margin</div><div class="value cyan">{current_row['Real Margin %']:.1f}%</div><div class="small">بعد الخصم والأثر التشغيلي</div></div>""", unsafe_allow_html=True)
    with s3:
        cls = "green" if current_row["Delta Profit"] >= 0 else "red"
        st.markdown(f"""<div class="kpi"><div class="label">صافي الربح المتوقع</div><div class="value {cls}">{money(current_row['Net Profit'])}</div><div class="small">فرق الربح: <span class="{cls}">{current_row['Delta Profit']:+.1f}M</span></div></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="kpi"><div class="label">Best موافقةable Discount</div><div class="value green">{f"{best_safe_discount:.1f}%" if best_safe_discount is not None else "None"}</div><div class="small">أعلى خصم ما زال داخل منطقة الموافقة</div></div>""", unsafe_allow_html=True)

    p1,p2 = st.columns([1.4,1])
    with p1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">الخصم مقابل صافي الربح</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_scatter(x=sim_df["Discount %"], y=sim_df["Net Profit"], mode="lines+markers", line=dict(color="#48a7ff", width=4), marker=dict(size=10, color=[zone_color(z) for z in sim_df["Decision Zone"]]), hovertemplate="Discount %{x:.1f}%<br>Profit %{y:.1f}M<extra></extra>")
        fig.add_hline(y=current_profit, line_dash="dash", line_color="#35d48a", annotation_text="الربح الحالي", annotation_position="top left")
        fig.update_layout(height=390, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(title="Discount %", showgrid=False), yaxis=dict(title="Net Profit (M SAR)", showgrid=True, gridcolor="rgba(255,255,255,0.08)"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">الخصم مقابل الهامش الفعلي</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_scatter(x=sim_df["Discount %"], y=sim_df["Real Margin %"], mode="lines+markers", line=dict(color="#37ddff", width=4), marker=dict(size=10, color=[zone_color(z) for z in sim_df["Decision Zone"]]), hovertemplate="Discount %{x:.1f}%<br>Real Margin %{y:.1f}%<extra></extra>")
        fig2.add_hline(y=current_row["Break-even Margin %"], line_dash="dash", line_color="#ffb44a", annotation_text=f"Break-even {current_row['Break-even Margin %']:.1f}%", annotation_position="top left")
        fig2.update_layout(height=390, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(title="Discount %", showgrid=False), yaxis=dict(title="Real Margin %", showgrid=True, gridcolor="rgba(255,255,255,0.08)"))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">جدول المحاكاة</div>', unsafe_allow_html=True)
    st.dataframe(sim_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    risk_names = ["الضغط التشغيلي", "Deviations", "Penalties", "Materials/Fuel"]
    risk_values = [
        2 if op_impact <= 2 else 3 if op_impact <= 4 else 4,
        2 if discount <= 3 else 3 if discount <= 5 else 4,
        2 if discount <= 4 else 3 if discount <= 6 else 4,
        4
    ]
    risk_colors = ["#35d48a" if v<=2 else "#ffb44a" if v==3 else "#ff6363" for v in risk_values]

    r1,r2,r3 = st.columns(3)
    with r1:
        st.markdown(f"""<div class="kpi"><div class="label">الضغط التشغيلي</div><div class="value {'green' if risk_values[0]<=2 else 'orange' if risk_values[0]==3 else 'red'}">{['-','Low','Medium','High','Critical'][risk_values[0]]}</div><div class="small">مرتبط بالأثر التشغيلي المدخل</div></div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""<div class="kpi"><div class="label">مخاطر الربحية</div><div class="value {'green' if best is not None and best['Decision Zone']=='موافقة' else 'orange' if best is not None and best['Decision Zone']=='Risk' else 'red'}">{zone_ar(best['Decision Zone']) if best is not None else '-'}</div><div class="small">مبنية على الهامش الفعلي مقابل التعادل</div></div>""", unsafe_allow_html=True)
    with r3:
        st.markdown(f"""<div class="kpi"><div class="label">مخاطر المواد والوقود</div><div class="value red">High</div><div class="small">خطر خارجي قد يحتاج بند مراجعة أسعار</div></div>""", unsafe_allow_html=True)

    rc1,rc2 = st.columns([1.15,1])
    with rc1:
        st.markdown('<div class="panel"><div class="label" style="font-size:1.02rem;">مصفوفة المخاطر</div>', unsafe_allow_html=True)
        risk_fig = go.Figure()
        risk_fig.add_bar(x=risk_names, y=risk_values, text=["L" if v==1 else "M" if v==2 else "H" if v==3 else "C" for v in risk_values], textposition="inside", marker=dict(color=risk_colors), hovertemplate="%{x}<extra></extra>")
        risk_fig.update_layout(height=370, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#edf5ff"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", tickvals=[1,2,3,4], ticktext=["Low","Medium","High","Critical"], range=[0,4.5]), showlegend=False)
        st.plotly_chart(risk_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with rc2:
        st.markdown("""
        <div class="panel">
            <div class="label" style="font-size:1.02rem;">خطة التعامل مع المخاطر</div>
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
        <div class="label" style="font-size:1.02rem;">القراءة التنفيذية</div>
        <div class="small">
        The key issue is not only the discount itself, but the combined impact of discount plus operating pressure on real margin. 
        If the offer is accepted without commercial protections, the company could gain volume but lose profitability quality. 
        If the offer is rejected entirely, part of next year's workload may shift to other contractors. 
        Therefore, the best path is typically conditional approval with a clear discount cap, scenario tracking, and monthly risk review.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.caption("Consulting-style executive dashboard with integrated simulator, risk center, branding, and PDF export.")
