
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Chacutería Foods | Dashboard Gerencial 2025",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# ESTILOS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #eef3f8 0%, #f7f9fc 100%);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1420px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #163a63 0%, #0f2d4d 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    .hero {
        background: linear-gradient(90deg, #163a63 0%, #1f5d99 55%, #2873bf 100%);
        border-radius: 24px;
        padding: 30px 34px 26px 34px;
        color: white;
        box-shadow: 0 12px 30px rgba(17, 45, 79, 0.18);
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 44px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 20px;
        opacity: 0.96;
    }

    .section-title {
        font-size: 30px;
        font-weight: 800;
        color: #13314f;
        margin-top: 12px;
        margin-bottom: 8px;
    }

</style>
""", unsafe_allow_html=True)

# =========================================================
# UTILIDADES
# =========================================================
def format_cop(value):
    if pd.isna(value):
        return "$0"
    if abs(value) >= 1e9:
        return f"${value/1e9:,.2f} B"
    if abs(value) >= 1e6:
        return f"${value/1e6:,.1f} MM"
    return f"${value:,.0f}"

def format_ton(value):
    if pd.isna(value):
        return "0 ton"
    return f"{value/1000:,.1f} ton"

def traffic_light(value, good, warn, reverse=False):
    if pd.isna(value):
        return ("Sin dato","pill-yellow")
    if reverse:
        if value <= good:
            return ("Verde","pill-green")
        elif value <= warn:
            return ("Amarillo","pill-yellow")
        else:
            return ("Rojo","pill-red")
    else:
        if value >= good:
            return ("Verde","pill-green")
        elif value >= warn:
            return ("Amarillo","pill-yellow")
        else:
            return ("Rojo","pill-red")

@st.cache_data
def load_data(base):
    si = pd.read_csv(base/"sell_in_limpio.csv", parse_dates=["fecha"])
    so = pd.read_csv(base/"sell_out_limpio.csv", parse_dates=["fecha"])
    summary = pd.read_csv(base/"resumen_mensual.csv", parse_dates=["mes"])
    inv = pd.read_csv(base/"inventario_mensual_cierre.csv", parse_dates=["mes","fecha"])
    alerts_inv = pd.read_csv(base/"alertas_inventario_dic.csv")
    alerts_beh = pd.read_csv(base/"alertas_comportamiento.csv")
    market_sum = pd.read_csv(base/"mercado_resumen_mensual.csv", parse_dates=["mes"])
    return si,so,summary,inv,alerts_inv,alerts_beh,market_sum

# =========================================================
# CARGA
# =========================================================
base = Path(__file__).parent
si,so,summary,inv,alerts_inv,alerts_beh,market_sum = load_data(base)

# =========================================================
# KPIS
# =========================================================
k1 = si["valor"].sum()
k2 = so["valor"].sum()

delta_valor = k1 - k2
gap_pct = (delta_valor/k1)*100 if k1!=0 else 0

# =========================================================
# PRESUPUESTO CORREGIDO
# =========================================================
budget_total = None
budget_pct = None

if "valor_presupuesto" in summary.columns:
    budget_total = summary["valor_presupuesto"].sum()

if budget_total and budget_total>0:
    budget_pct = (k1/budget_total)*100

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">
<div class="hero-title">Chacutería Foods</div>
<div class="hero-subtitle">Dashboard gerencial 2025</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# KPIS DISPLAY
# =========================================================
c1,c2,c3 = st.columns(3)

c1.metric("Sell-in valor", format_cop(k1))
c2.metric("Sell-out valor", format_cop(k2), delta=format_cop(delta_valor))

if budget_pct:
    c3.metric("Cumplimiento presupuesto", f"{budget_pct:.1f}%")
else:
    c3.metric("Cumplimiento presupuesto","N/D")

# =========================================================
# TENDENCIA
# =========================================================
si_m = (
    si.assign(mes=lambda d:d["fecha"].values.astype("datetime64[M]"))
    .groupby("mes",as_index=False)
    .agg(sell_in_valor=("valor","sum"))
)

so_m = (
    so.assign(mes=lambda d:d["fecha"].values.astype("datetime64[M]"))
    .groupby("mes",as_index=False)
    .agg(sell_out_valor=("valor","sum"))
)

trend = pd.merge(si_m,so_m,on="mes",how="outer").fillna(0)

# PRESUPUESTO MENSUAL CORREGIDO
if "valor_presupuesto" in summary.columns:
    pres = summary[["mes","valor_presupuesto"]].rename(columns={"valor_presupuesto":"presupuesto"})
    trend = trend.merge(pres,on="mes",how="left")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=trend["mes"],
    y=trend["sell_in_valor"]/1e9,
    name="Sell-in",
    mode="lines+markers"
))

fig.add_trace(go.Scatter(
    x=trend["mes"],
    y=trend["sell_out_valor"]/1e9,
    name="Sell-out",
    mode="lines+markers"
))

if "presupuesto" in trend.columns:
    fig.add_trace(go.Scatter(
        x=trend["mes"],
        y=trend["presupuesto"]/1e9,
        name="Presupuesto",
        mode="lines+markers",
        line=dict(dash="dash")
))

fig.update_layout(
    template="plotly_white",
    title="Evolución mensual",
    yaxis_title="COP Billones"
)

st.plotly_chart(fig,use_container_width=True)

# =========================================================
# DOH
# =========================================================
if "doh_30d" in inv.columns:

    doh = inv.groupby("mes",as_index=False).agg(doh=("doh_30d","mean"))

    fig2 = px.line(
        doh,
        x="mes",
        y="doh",
        title="DOH promedio"
    )

    st.plotly_chart(fig2,use_container_width=True)
