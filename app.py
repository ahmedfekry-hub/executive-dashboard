
import math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Executive Decision Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- THEME / CSS ----------
st.markdown("""
<style>
:root{
    --bg:#07111f;
    --panel:#0d1b2e;
    --panel2:#10223a;
    --line:#1b3353;
    --text:#eaf2ff;
    --muted:#9eb0c8;
    --blue:#2f8cff;
    --cyan:#2de2e6;
    --green:#32d583;
    --orange:#ff9f43;
    --red:#ff5d5d;
    --purple:#8b5cf6;
}
.stApp {
    background:
        radial-gradient(circle at top left, rgba(47,140,255,0.14), transparent 28%),
        radial-gradient(circle at bottom right, rgba(255,159,67,0.12), transparent 24%),
        linear-gradient(180deg, #060d18 0%, #08111f 100%);
    color: var(--text);
}
.block-container{
    padding-top: 1.2rem;
    padding-bottom: 1.2rem;
    max-width: 1500px;
}
h1,h2,h3,h4,h5,p,span,div,label{
    color: var(--text) !important;
}
.small-muted{
    color: var(--muted) !important;
    font-size: 0.84rem;
}
.kpi-card{
    background: linear-gradient(180deg, rgba(17,33,57,0.98), rgba(10,22,39,0.98));
    border: 1px solid rgba(87,125,185,0.22);
    border-radius: 22px;
    padding: 18px 18px 14px 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.28);
    min-height: 132px;
}
.kpi-title{
    color: #b9cae3 !important;
    font-size: 0.88rem;
    letter-spacing: .4px;
    margin-bottom: 8px;
}
.kpi-value{
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
}
.kpi-sub{
    color:#9db2cf !important;
    font-size: 0.9rem;
}
.green{color:#32d583 !important;}
.orange{color:#ffb54a !important;}
.red{color:#ff6b6b !important;}
.blue{color:#5aa7ff !important;}
.section-card{
    background: linear-gradient(180deg, rgba(14,27,47,0.98), rgba(9,19,33,0.98));
    border: 1px solid rgba(87,125,185,0.18);
    border-radius: 24px;
    padding: 16px 18px 10px 18px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.22);
    margin-top: 10px;
}
.section-title{
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.decision-box{
    border-radius:20px;
    padding:18px;
    border:1px solid rgba(255,255,255,0.08);
    min-height: 160px;
}
.accept{
    background: linear-gradient(180deg, rgba(10,52,37,0.95), rgba(9,34,26,0.95));
}
.risk{
    background: linear-gradient(180deg, rgba(70,48,12,0.95), rgba(43,28,7,0.95));
}
.reject{
    background: linear-gradient(180deg, rgba(62,19,19,0.95), rgba(39,12,12,0.95));
}
.summary-box{
    background: linear-gradient(180deg, rgba(14,27,47,0.95), rgba(8,18,32,0.95));
    border: 1px solid rgba(110,140,180,0.18);
    border-radius: 24px;
    padding: 22px;
}
div[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #07111f 0%, #0a1524 100%);
    border-right: 1px solid rgba(125,152,190,0.12);
}
div[data-testid="stSidebar"] *{
    color: #eef4ff !important;
}
div[data-testid="stSidebar"] label,
div[data-testid="stSidebar"] p,
div[data-testid="stSidebar"] span,
div[data-testid="stSidebar"] div{
    color: #eef4ff !important;
}
div[data-testid="stSidebar"] [data-baseweb="select"] > div,
div[data-testid="stSidebar"] [data-baseweb="tag"]{
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
}
.stDataFrame, .stTable{
    border-radius: 18px;
    overflow: hidden;
}
hr{
    border-color: rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------
def money(x):
    return f"{x:,.1f}M"

def calc_real_margin(revenue, net_margin, discount, op_impact):
    expected_margin = net_margin - discount
    real_margin = expected_margin - op_impact
    profit = revenue * real_margin / 100.0
    return expected_margin, real_margin, profit

def break_even_margin(current_profit, revenue):
    return current_profit / revenue * 100

# ---------- SIDEBAR ----------
st.sidebar.markdown("## ⚙️ إعدادات التحليل")
language = st.sidebar.radio("اللغة", ["العربية", "English"], index=0)

if language == "العربية":
    ui = {
        "title":"لوحة القرار التنفيذي",
        "subtitle":"تحليل الخصم مقابل زيادة حجم الأعمال",
        "current_revenue":"الإيراد الحالي",
        "current_margin":"هامش الربح الحالي",
        "current_profit":"صافي الربح الحالي",
        "proposed_revenue":"الإيراد المقترح",
        "discount":"نسبة الخصم المقترحة",
        "op_impact":"الأثر التشغيلي المتوقع",
        "best_case":"أفضل سيناريو",
        "decision":"القرار الموصى به",
        "summary":"الملخص التنفيذي",
        "strengths":"نقاط القوة",
        "weaknesses":"نقاط الضعف والمخاطر",
        "recommendation":"التوصية",
        "scenario_analysis":"تحليل السيناريوهات",
        "margin_analysis":"تحليل الهامش",
        "decision_zone":"مناطق القرار",
        "risk_matrix":"مؤشرات المخاطر",
        "table_title":"جدول المقارنة",
    }
else:
    ui = {
        "title":"Executive Decision Dashboard",
        "subtitle":"Discount vs Volume Increase Analysis",
        "current_revenue":"Current Revenue",
        "current_margin":"Current Net Margin",
        "current_profit":"Current Net Profit",
        "proposed_revenue":"Proposed Revenue",
        "discount":"Proposed Discount",
        "op_impact":"Expected Operational Impact",
        "best_case":"Best Scenario",
        "decision":"Recommended Decision",
        "summary":"Executive Summary",
        "strengths":"Strengths",
        "weaknesses":"Weaknesses & Risks",
        "recommendation":"Recommendation",
        "scenario_analysis":"Scenario Analysis",
        "margin_analysis":"Margin Analysis",
        "decision_zone":"Decision Zones",
        "risk_matrix":"Risk Indicators",
        "table_title":"Comparison Table",
    }

current_revenue = st.sidebar.slider(ui["current_revenue"], 50, 500, 150, 10)
current_margin = st.sidebar.slider(ui["current_margin"], 5.0, 35.0, 20.0, 0.5)
proposed_revenues = st.sidebar.multiselect(
    ui["proposed_revenue"],
    [200, 230, 250, 275, 300],
    default=[200, 230, 250]
)
discount = st.sidebar.slider(ui["discount"], 0.0, 12.0, 5.0, 0.5)
op_impact = st.sidebar.slider(ui["op_impact"], 0.0, 8.0, 3.0, 0.5)

st.sidebar.markdown("---")
show_notes = st.sidebar.checkbox("إظهار ملاحظات إدارية" if language=="العربية" else "Show management notes", value=True)

# ---------- DATA ----------
current_profit = current_revenue * current_margin / 100.0

rows = []
for rev in proposed_revenues:
    expected_margin, real_margin, profit = calc_real_margin(rev, current_margin, discount, op_impact)
    be_margin = break_even_margin(current_profit, rev)
    delta_profit = profit - current_profit
    if real_margin >= be_margin + 1:
        zone = "Accept"
    elif real_margin >= be_margin:
        zone = "Risk"
    else:
        zone = "Reject"
    rows.append({
        "Revenue": rev,
        "Expected Margin %": round(expected_margin,2),
        "Real Margin %": round(real_margin,2),
        "Break-even Margin %": round(be_margin,2),
        "Net Profit": round(profit,2),
        "Δ Profit": round(delta_profit,2),
        "Decision Zone": zone
    })

df = pd.DataFrame(rows).sort_values("Net Profit", ascending=False)
best = df.iloc[0] if not df.empty else None

# ---------- HEADER ----------
c1, c2 = st.columns([4,1])
with c1:
    st.markdown(f"""
    <div style="padding: 6px 4px 14px 4px;">
        <div style="font-size:2.1rem;font-weight:800;letter-spacing:0.3px;">{ui["title"]}</div>
        <div class="small-muted">{ui["subtitle"]}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="summary-box" style="padding:14px;text-align:center;">
        <div class="small-muted">Executive View</div>
        <div style="font-size:1.65rem;font-weight:800;" class="blue">2026</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- KPI ROW ----------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{ui["current_revenue"]}</div>
        <div class="kpi-value blue">{money(current_revenue)}</div>
        <div class="kpi-sub">{'Baseline business volume' if language=='English' else 'خط الأساس الحالي'}</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{ui["current_margin"]}</div>
        <div class="kpi-value green">{current_margin:.1f}%</div>
        <div class="kpi-sub">{'Net profitability before new offer' if language=='English' else 'الربحية الحالية قبل العرض الجديد'}</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{ui["current_profit"]}</div>
        <div class="kpi-value">{money(current_profit)}</div>
        <div class="kpi-sub">{'Reference point for all scenarios' if language=='English' else 'النقطة المرجعية لجميع السيناريوهات'}</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    best_text = f"{int(best['Revenue'])}M / {best['Real Margin %']:.1f}%" if best is not None else "-"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{ui["best_case"]}</div>
        <div class="kpi-value orange">{best_text}</div>
        <div class="kpi-sub">{'Highest modeled profit' if language=='English' else 'أعلى ربح متوقع في النموذج'}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- CHARTS ----------
left, right = st.columns([1.2,1])
with left:
    st.markdown(f'<div class="section-card"><div class="section-title">{ui["scenario_analysis"]}</div>', unsafe_allow_html=True)
    fig_profit = go.Figure()
    fig_profit.add_bar(
        x=[f"{r}M" for r in df["Revenue"]],
        y=df["Net Profit"],
        text=[f"{v:.1f}M" for v in df["Net Profit"]],
        textposition="outside",
        marker=dict(
            color=df["Decision Zone"].map({"Accept":"#32d583","Risk":"#ffb54a","Reject":"#ff6b6b"}),
            line=dict(color="rgba(255,255,255,0.2)", width=1)
        ),
        name="Net Profit"
    )
    fig_profit.add_hline(
        y=current_profit, line_dash="dash", line_color="#5aa7ff",
        annotation_text=("Current Profit" if language=="English" else "الربح الحالي"),
        annotation_position="top left"
    )
    fig_profit.update_layout(
        height=360,
        margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eaf2ff"),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="M SAR"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig_profit, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown(f'<div class="section-card"><div class="section-title">{ui["margin_analysis"]}</div>', unsafe_allow_html=True)
    fig_margin = go.Figure()
    fig_margin.add_scatter(
        x=[f"{r}M" for r in df["Revenue"]],
        y=df["Real Margin %"],
        mode="lines+markers+text",
        text=[f"{v:.1f}%" for v in df["Real Margin %"]],
        textposition="top center",
        line=dict(color="#2de2e6", width=4),
        marker=dict(size=12, color="#2f8cff"),
        name="Real Margin"
    )
    fig_margin.add_scatter(
        x=[f"{r}M" for r in df["Revenue"]],
        y=df["Break-even Margin %"],
        mode="lines+markers",
        line=dict(color="#ffb54a", width=3, dash="dash"),
        marker=dict(size=10),
        name="Break-even"
    )
    fig_margin.update_layout(
        height=360,
        margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eaf2ff"),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig_margin, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- MID ROW ----------
left2, center2, right2 = st.columns([1.15,1.15,0.9])

with left2:
    st.markdown(f'<div class="section-card"><div class="section-title">{ui["table_title"]}</div>', unsafe_allow_html=True)
    display_df = df.copy()
    if language == "العربية":
        display_df = display_df.rename(columns={
            "Revenue":"الإيراد",
            "Expected Margin %":"الهامش المتوقع %",
            "Real Margin %":"الهامش الفعلي %",
            "Break-even Margin %":"هامش التعادل %",
            "Net Profit":"صافي الربح",
            "Δ Profit":"فرق الربح",
            "Decision Zone":"منطقة القرار"
        })
        display_df["منطقة القرار"] = display_df["منطقة القرار"].replace({"Accept":"موافقة","Risk":"مخاطرة","Reject":"رفض"})
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with center2:
    st.markdown(f'<div class="section-card"><div class="section-title">{ui["decision_zone"]}</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    with a:
        st.markdown(f"""
        <div class="decision-box accept">
            <div style="font-size:1rem;font-weight:700;">🟢 {'موافقة' if language=='العربية' else 'Accept'}</div>
            <div class="small-muted">{'ربحية أعلى من الوضع الحالي مع هامش آمن' if language=='العربية' else 'Higher than baseline profit with safe margin'}</div>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown(f"""
        <div class="decision-box risk">
            <div style="font-size:1rem;font-weight:700;">🟡 {'مخاطرة' if language=='العربية' else 'Risk'}</div>
            <div class="small-muted">{'ربحية مقبولة لكن الهامش قريب من التعادل' if language=='العربية' else 'Acceptable profit but margin close to break-even'}</div>
        </div>
        """, unsafe_allow_html=True)
    with c:
        st.markdown(f"""
        <div class="decision-box reject">
            <div style="font-size:1rem;font-weight:700;">🔴 {'رفض' if language=='العربية' else 'Reject'}</div>
            <div class="small-muted">{'الربح أقل أو المخاطر أعلى من العائد' if language=='العربية' else 'Lower profit or risk exceeds value'}</div>
        </div>
        """, unsafe_allow_html=True)

    risk_labels = ["OPS", "DEV", "PEN", "EXT"]
    risk_values = [
        2 if op_impact <= 3 else 3,
        2 if discount <= 4 else 3,
        2 if discount <= 5 else 3,
        3
    ]
    risk_names = [
        "Operational Pressure" if language=="English" else "الضغط التشغيلي",
        "Deviation Exposure" if language=="English" else "مخاطر الانحرافات",
        "Penalty Sensitivity" if language=="English" else "حساسية الغرامات",
        "External Risk" if language=="English" else "المخاطر الخارجية",
    ]
    risk_colors = ["#32d583" if v == 1 else "#ffb54a" if v == 2 else "#ff6b6b" for v in risk_values]
    fig_risk = go.Figure(
        data=[
            go.Bar(
                x=risk_names,
                y=risk_values,
                text=risk_labels,
                textposition="inside",
                marker=dict(color=risk_colors, line=dict(color="rgba(255,255,255,0.18)", width=1)),
                hovertemplate="%{x}<extra></extra>",
            )
        ]
    )
    fig_risk.update_layout(
        height=190,
        margin=dict(l=10,r=10,t=5,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eaf2ff"),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            tickmode="array",
            tickvals=[1,2,3],
            ticktext=["Low","Medium","High"] if language=="English" else ["منخفض","متوسط","مرتفع"],
            range=[0,3.4],
            title=""
        ),
        xaxis=dict(showgrid=False, title=""),
        showlegend=False,
    )
    st.plotly_chart(fig_risk, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right2:
    st.markdown(f'<div class="summary-box"><div class="section-title">{ui["decision"]}</div>', unsafe_allow_html=True)
    if best is not None:
        zone_map_ar = {"Accept":"موافقة مشروطة","Risk":"مراجعة مشروطة","Reject":"غير موصى به"}
        zone_map_en = {"Accept":"Conditional Approval","Risk":"Conditional Review","Reject":"Not Recommended"}
        zone = zone_map_ar[best["Decision Zone"]] if language=="العربية" else zone_map_en[best["Decision Zone"]]
        final_text = f"""
        <div class="kpi-value">{zone}</div>
        <div class="small-muted" style="margin-top:8px;">
        {'أفضل سيناريو حاليًا:' if language=='العربية' else 'Current best case:'}
        <b>{int(best['Revenue'])}M</b><br>
        {'الهامش الفعلي:' if language=='العربية' else 'Real margin:'} <b>{best['Real Margin %']:.1f}%</b><br>
        {'صافي الربح:' if language=='العربية' else 'Net profit:'} <b>{best['Net Profit']:.1f}M</b>
        </div>
        """
        st.markdown(final_text, unsafe_allow_html=True)
    if show_notes:
        st.markdown("<hr>", unsafe_allow_html=True)
        if language == "العربية":
            st.markdown("""
            **ملخص تنفيذي:**  
            - زيادة حجم الأعمال تمنح الشركة وضوحًا مبكرًا في التخطيط والتوريد والموارد.  
            - الخطر الأساسي هو انخفاض الهامش الحقيقي نتيجة الخصم + الضغط التشغيلي.  
            - في حال الرفض، قد يتم توزيع الأعمال على مقاولين آخرين مما يضغط على حصة العام القادم.  
            - يوصى بالموافقة المشروطة مع سقف خصم واضح ومراجعة أثر الأسعار والوقود والمواد.
            """)
        else:
            st.markdown("""
            **Executive Note:**  
            - Higher volume improves planning, procurement, and resource readiness.  
            - The key risk is real margin erosion caused by discount + operating pressure.  
            - Rejection may reduce next year's workshare if volume is redistributed to other contractors.  
            - Recommend conditional approval with a discount cap and review of fuel/material escalation.
            """)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- BOTTOM SUMMARY ----------
b1, b2, b3 = st.columns([1,1,1])

with b1:
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">{ui["strengths"]}</div>
        <div class="small-muted">
        {'• ضمان حجم عمل من بداية العام<br>• تحسين شراء المواد والدعم اللوجستي<br>• ترتيب الموارد والفرق مبكرًا<br>• وضوح أفضل للخطة المالية' if language=='العربية' else '• Secured pipeline from the start of the year<br>• Better procurement and logistics planning<br>• Earlier resource and team readiness<br>• Stronger financial planning visibility'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with b2:
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">{ui["weaknesses"]}</div>
        <div class="small-muted">
        {'• الخصم يخفض الربحية مباشرة<br>• زيادة احتمال deviations و penalties<br>• مخاطر تثبيت سعر منخفض مستقبلاً<br>• احتمالية ارتفاع أسعار المواد والمحروقات' if language=='العربية' else '• Discount directly reduces profitability<br>• Higher deviation and penalty exposure<br>• Risk of long-term low-price anchoring<br>• Possible increase in fuel and material prices'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with b3:
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">{ui["recommendation"]}</div>
        <div class="small-muted">
        {'• الموافقة المشروطة فقط<br>• الحفاظ على هامش فعلي آمن لا يقل عن 13%–16%<br>• إدراج بند مراجعة للأسعار إن أمكن<br>• مراقبة الجودة والانحرافات شهريًا' if language=='العربية' else '• Conditional approval only<br>• Keep safe real margin no lower than 13%–16%<br>• Add a price-adjustment clause where possible<br>• Monitor quality and deviations monthly'}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Prepared as an executive decision-support dashboard for commercial and operational review." if language=="English" else "تم إعداد هذه اللوحة كأداة دعم قرار للإدارة التجارية والتشغيلية.")
