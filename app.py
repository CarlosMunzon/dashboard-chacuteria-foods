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

# -------------------------------------------------------
# ESTILOS
# -------------------------------------------------------

st.markdown("""
<style>

.stApp{
background:linear-gradient(180deg,#eef3f8 0%,#f7f9fc 100%);
}

.block-container{
max-width:1400px;
padding-top:1rem;
}

[data-testid="stSidebar"]{
background:linear-gradient(180deg,#163a63 0%,#0f2d4d 100%);
}

[data-testid="stSidebar"] *{
color:white !important;
}

.hero{
background:linear-gradient(90deg,#163a63 0%,#1f5d99 60%,#2873bf 100%);
border-radius:24px;
padding:28px;
color:white;
margin-bottom:18px;
box-shadow:0 10px 25px rgba(0,0,0,0.15);
}

.hero-title{
font-size:44px;
font-weight:800;
}

.hero-subtitle{
font-size:20px;
margin-top:4px;
}

.section-title{
font-size:30px;
font-weight:800;
color:#17324d;
margin-top:18px;
}

.insight-box{
background:white;
border-left:6px solid #1f5d99;
border-radius:16px;
padding:16px;
margin-top:10px;
margin-bottom:12px;
box-shadow:0 6px 16px rgba(0,0,0,0.05);
}

.mini-card{
background:white;
border-radius:16px;
padding:16px;
border:1px solid #e4ebf3;
box-shadow:0 6px 16px rgba(0,0,0,0.05);
}

.mini-card-title{
font-size:14px;
color:#6b7f93;
font-weight:700;
}

.mini-card-value{
font-size:28px;
font-weight:800;
color:#163a63;
}

.mini-card-sub{
font-size:14px;
color:#6b7f93;
}

.stPlotlyChart{
background:white;
border-radius:18px;
padding:8px;
border:1px solid #e4ebf3;
}

</style>
""",unsafe_allow_html=True)

# -------------------------------------------------------
# UTILIDADES
# -------------------------------------------------------

def format_cop(x):

    if abs(x)>=1e9:
        return f"${x/1e9:,.2f} B"

    if abs(x)>=1e6:
        return f"${x/1e6:,.1f} MM"

    return f"${x:,.0f}"

def format_ton(x):

    return f"{x/1000:,.1f} ton"

# -------------------------------------------------------
# DATA
# -------------------------------------------------------

base=Path(__file__).parent

si=pd.read_csv(base/"sell_in_limpio.csv",parse_dates=["fecha"])
so=pd.read_csv(base/"sell_out_limpio.csv",parse_dates=["fecha"])
summary=pd.read_csv(base/"resumen_mensual.csv",parse_dates=["mes"])
inv=pd.read_csv(base/"inventario_mensual_cierre.csv",parse_dates=["mes","fecha"])
alerts_inv=pd.read_csv(base/"alertas_inventario_dic.csv")
alerts_beh=pd.read_csv(base/"alertas_comportamiento.csv",parse_dates=["mes"])
market_sum=pd.read_csv(base/"mercado_resumen_mensual.csv",parse_dates=["mes"])

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

st.sidebar.markdown("## 🎛️ Filtros gerenciales")

canales=st.sidebar.multiselect("Canal",sorted(si["canal"].dropna().unique()))
clientes=st.sidebar.multiselect("Cliente",sorted(si["cliente"].dropna().unique()))
categorias=st.sidebar.multiselect("Categoría",sorted(si["categoria"].dropna().unique()))
regionales=st.sidebar.multiselect("Regional",sorted(si["regional"].dropna().unique()))

def apply_filters(df):

    out=df.copy()

    if canales:
        out=out[out["canal"].isin(canales)]

    if clientes:
        out=out[out["cliente"].isin(clientes)]

    if categorias:
        out=out[out["categoria"].isin(categorias)]

    if regionales:
        out=out[out["regional"].isin(regionales)]

    return out

si_f=apply_filters(si)
so_f=apply_filters(so)

si_valid=si_f[si_f["sku_valido"]==True]
so_valid=so_f[so_f["sku_valido"]==True]

# -------------------------------------------------------
# HERO
# -------------------------------------------------------

fecha_actualizacion=pd.Timestamp.today().strftime("%d/%m/%Y")

st.markdown(f"""
<div class="hero">
<div class="hero-title">Chacutería Foods</div>
<div class="hero-subtitle">
Dashboard gerencial 2025 • Seguimiento comercial y participación de mercado
</div>
<div style="margin-top:8px;font-size:14px;">
Actualizado al {fecha_actualizacion}
</div>
</div>
""",unsafe_allow_html=True)

# -------------------------------------------------------
# KPIS
# -------------------------------------------------------

k1=si_valid["valor"].sum()
k2=so_valid["valor"].sum()
k3=si_valid["kilos"].sum()
k4=so_valid["kilos"].sum()

delta_valor=k1-k2
delta_vol=k3-k4
gap_pct=(delta_valor/k1)*100 if k1>0 else 0

st.markdown('<div class="section-title">Resumen del negocio</div>',unsafe_allow_html=True)

c1,c2,c3,c4=st.columns(4)

c1.metric("💰 Sell-in valor",format_cop(k1))
c2.metric("🛒 Sell-out valor",format_cop(k2),delta=format_cop(delta_valor))
c3.metric("📦 Sell-in volumen",format_ton(k3))
c4.metric("🚚 Sell-out volumen",format_ton(k4),delta=format_ton(delta_vol))

# -------------------------------------------------------
# KPIS ESTRATEGICOS
# -------------------------------------------------------

extra1,extra2,extra3=st.columns(3)

share_company = market_sum["share_compania_prom"].mean()*100 if "share_compania_prom" in market_sum.columns else 0

budget_cols = [c for c in summary.columns if "presupuesto" in c.lower()]
budget_total = summary[budget_cols[0]].sum() if budget_cols else 0
budget_pct = (k1/budget_total)*100 if budget_total>0 else 0

with extra1:

    st.markdown(f"""
    <div class="mini-card">
    <div class="mini-card-title">Cumplimiento presupuesto</div>
    <div class="mini-card-value">{budget_pct:.1f}%</div>
    <div class="mini-card-sub">Objetivo anual</div>
    </div>
    """,unsafe_allow_html=True)

with extra2:

    st.markdown(f"""
    <div class="mini-card">
    <div class="mini-card-title">Share compañía</div>
    <div class="mini-card-value">{share_company:.1f}%</div>
    <div class="mini-card-sub">Promedio retail</div>
    </div>
    """,unsafe_allow_html=True)

with extra3:

    st.markdown(f"""
    <div class="mini-card">
    <div class="mini-card-title">Brecha comercial</div>
    <div class="mini-card-value">{gap_pct:.1f}%</div>
    <div class="mini-card-sub">Sell-in vs Sell-out</div>
    </div>
    """,unsafe_allow_html=True)

# -------------------------------------------------------
# INSIGHT AUTOMATICO
# -------------------------------------------------------

st.markdown(f"""
<div class="insight-box">
📌 El negocio registra <b>{format_cop(k1)}</b> en sell-in y <b>{format_cop(k2)}</b> en sell-out.
La brecha actual es <b>{format_cop(delta_valor)}</b> ({gap_pct:.1f}%).
</div>
""",unsafe_allow_html=True)

# -------------------------------------------------------
# EVOLUCION
# -------------------------------------------------------

si_m=si_valid.assign(mes=lambda d:d["fecha"].values.astype("datetime64[M]")).groupby("mes",as_index=False).agg(valor=("valor","sum"))
so_m=so_valid.assign(mes=lambda d:d["fecha"].values.astype("datetime64[M]")).groupby("mes",as_index=False).agg(valor=("valor","sum"))

trend=pd.merge(si_m,so_m,on="mes",how="outer").fillna(0)

fig=go.Figure()

fig.add_trace(go.Scatter(x=trend["mes"],y=trend["valor_x"]/1e9,mode="lines+markers",name="Sell-in"))
fig.add_trace(go.Scatter(x=trend["mes"],y=trend["valor_y"]/1e9,mode="lines+markers",name="Sell-out"))

fig.update_layout(
height=420,
template="plotly_white",
title="Valor mensual del negocio",
xaxis_title="Mes",
yaxis_title="COP Billones"
)

st.plotly_chart(fig,use_container_width=True)

# -------------------------------------------------------
# COMPOSICION COMERCIAL
# -------------------------------------------------------

st.markdown('<div class="section-title">Composición comercial</div>',unsafe_allow_html=True)

left,right=st.columns(2)

with left:

    mix=si_valid.groupby("canal",as_index=False).agg(valor=("valor","sum")).sort_values("valor",ascending=False)

    fig_mix=px.bar(mix,x="canal",y="valor",title="Mix sell-in por canal")

    st.plotly_chart(fig_mix,use_container_width=True)

with right:

    cat=so_valid.groupby("categoria",as_index=False).agg(valor=("valor","sum")).sort_values("valor",ascending=False)

    fig_cat=px.bar(cat,x="categoria",y="valor",title="Sell-out por categoría")

    st.plotly_chart(fig_cat,use_container_width=True)

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------

st.markdown("""
<div style="
margin-top:25px;
padding:18px;
background:white;
border-radius:16px;
border:1px solid #e4ebf3;
font-size:14px;
">

<b>Nota ejecutiva:</b> Este dashboard consolida indicadores de sell-in, sell-out,
inventario y mercado para facilitar el seguimiento comercial y priorizar acciones.

</div>
""",unsafe_allow_html=True)
