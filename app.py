import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Chacutería Foods | Dashboard Comercial 2025",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Utilidades
# -----------------------------
def format_cop(value: float) -> str:
    if pd.isna(value):
        return "$0 COP"
    abs_value = abs(value)
    if abs_value >= 1e9:
        return f"${value/1e9:,.2f} billones COP"
    if abs_value >= 1e6:
        return f"${value/1e6:,.1f} millones COP"
    return f"${value:,.0f} COP"

def format_ton(value: float) -> str:
    if pd.isna(value):
        return "0.0 ton"
    return f"{value/1000:,.1f} ton"

@st.cache_data
def load_data(base_path: Path):
    si = pd.read_csv(base_path / "sell_in_limpio.csv", parse_dates=["fecha"])
    so = pd.read_csv(base_path / "sell_out_limpio.csv", parse_dates=["fecha"])
    summary = pd.read_csv(base_path / "resumen_mensual.csv", parse_dates=["mes"])
    inv = pd.read_csv(base_path / "inventario_mensual_cierre.csv", parse_dates=["mes", "fecha"])
    alerts_inv = pd.read_csv(base_path / "alertas_inventario_dic.csv")
    alerts_beh = pd.read_csv(base_path / "alertas_comportamiento.csv", parse_dates=["mes"])
    market_sum = pd.read_csv(base_path / "mercado_resumen_mensual.csv", parse_dates=["mes"])
    return si, so, summary, inv, alerts_inv, alerts_beh, market_sum

def apply_filters(df, canales, clientes, categorias, regionales):
    out = df.copy()
    if canales and "canal" in out.columns:
        out = out[out["canal"].isin(canales)]
    if clientes and "cliente" in out.columns:
        out = out[out["cliente"].isin(clientes)]
    if categorias and "categoria" in out.columns:
        out = out[out["categoria"].isin(categorias)]
    if regionales and "regional" in out.columns:
        out = out[out["regional"].isin(regionales)]
    return out

# -----------------------------
# Carga de datos
# -----------------------------
base = Path(__file__).parent
si, so, summary, inv, alerts_inv, alerts_beh, market_sum = load_data(base)

# -----------------------------
# Header
# -----------------------------
st.title("Chacutería Foods – Dashboard comercial 2025")
st.caption("Versión mejorada del dashboard para seguimiento comercial, inventario y mercado.")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Filtros")

canales = st.sidebar.multiselect(
    "Canal",
    sorted(x for x in si["canal"].dropna().unique())
)

clientes = st.sidebar.multiselect(
    "Cliente",
    sorted(x for x in si["cliente"].dropna().unique())
)

categorias = st.sidebar.multiselect(
    "Categoría",
    sorted(x for x in si["categoria"].dropna().unique())
)

regionales = st.sidebar.multiselect(
    "Regional",
    sorted(x for x in si["regional"].dropna().unique())
)

# -----------------------------
# Aplicación de filtros
# -----------------------------
si_f = apply_filters(si, canales, clientes, categorias, regionales)
so_f = apply_filters(so, canales, clientes, categorias, regionales)

if si_f.empty and so_f.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

si_valid = si_f[si_f["sku_valido"] == True].copy()
so_valid = so_f[so_f["sku_valido"] == True].copy()

# -----------------------------
# KPIs
# -----------------------------
k1 = si_valid["valor"].sum()
k2 = so_valid["valor"].sum()
k3 = si_valid["kilos"].sum()
k4 = so_valid["kilos"].sum()

delta_valor = k1 - k2
delta_vol = k3 - k4

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sell-in valor", format_cop(k1))
c2.metric("Sell-out valor", format_cop(k2), delta=format_cop(delta_valor))
c3.metric("Sell-in volumen", format_ton(k3))
c4.metric("Sell-out volumen", format_ton(k4), delta=format_ton(delta_vol))

# -----------------------------
# Evolución mensual
# -----------------------------
si_m = (
    si_valid.assign(mes=lambda d: d["fecha"].values.astype("datetime64[M]"))
    .groupby("mes", as_index=False)
    .agg(sell_in_valor=("valor", "sum"), sell_in_kilos=("kilos", "sum"))
)

so_m = (
    so_valid.assign(mes=lambda d: d["fecha"].values.astype("datetime64[M]"))
    .groupby("mes", as_index=False)
    .agg(sell_out_valor=("valor", "sum"), sell_out_kilos=("kilos", "sum"))
)

trend = pd.merge(si_m, so_m, on="mes", how="outer").fillna(0).sort_values("mes")

st.subheader("Evolución mensual")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=trend["mes"],
    y=trend["sell_in_valor"] / 1e9,
    mode="lines+markers",
    name="Sell-in"
))
fig.add_trace(go.Scatter(
    x=trend["mes"],
    y=trend["sell_out_valor"] / 1e9,
    mode="lines+markers",
    name="Sell-out"
))
fig.update_layout(
    height=380,
    template="plotly_white",
    title="Valor mensual (billones COP)",
    xaxis_title="Mes",
    yaxis_title="Billones COP",
    legend_title=""
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Visualizaciones
# -----------------------------
left, right = st.columns(2)

with left:
    mix = (
        si_valid.groupby("canal", as_index=False)
        .agg(valor=("valor", "sum"))
        .sort_values("valor", ascending=False)
    )
    fig_mix = px.bar(
        mix,
        x="canal",
        y="valor",
        title="Mix sell-in por canal",
        labels={"valor": "Valor (COP)", "canal": "Canal"},
        text_auto=".2s"
    )
    fig_mix.update_layout(template="plotly_white", height=360)
    st.plotly_chart(fig_mix, use_container_width=True)

with right:
    cat = (
        so_valid.groupby("categoria", as_index=False)
        .agg(valor=("valor", "sum"))
        .sort_values("valor", ascending=False)
    )
    fig_cat = px.bar(
        cat,
        x="categoria",
        y="valor",
        title="Sell-out por categoría",
        labels={"valor": "Valor (COP)", "categoria": "Categoría"},
        text_auto=".2s"
    )
    fig_cat.update_layout(template="plotly_white", height=360)
    st.plotly_chart(fig_cat, use_container_width=True)

# -----------------------------
# Inventario y alertas
# -----------------------------
st.subheader("Inventario y alertas")
if {"cliente", "descripcion_producto", "riesgo", "inv_kilos_cierre", "doh_30d"}.issubset(alerts_inv.columns):
    st.dataframe(
        alerts_inv[["cliente", "descripcion_producto", "riesgo", "inv_kilos_cierre", "doh_30d"]]
        .sort_values(["riesgo", "doh_30d"])
        .head(50),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No se encontraron las columnas esperadas en alertas de inventario.")

# -----------------------------
# Mercado
# -----------------------------
st.subheader("Mercado")
figm = go.Figure()
figm.add_trace(go.Scatter(
    x=market_sum["mes"],
    y=market_sum["share_compania_prom"] * 100,
    mode="lines+markers",
    name="Compañía"
))
figm.add_trace(go.Scatter(
    x=market_sum["mes"],
    y=market_sum["share_competidor_1_prom"] * 100,
    mode="lines+markers",
    name="Competidor 1"
))
figm.add_trace(go.Scatter(
    x=market_sum["mes"],
    y=market_sum["share_competidor_2_prom"] * 100,
    mode="lines+markers",
    name="Competidor 2"
))
figm.update_layout(
    height=360,
    template="plotly_white",
    title="Share promedio mensual (%)",
    xaxis_title="Mes",
    yaxis_title="Participación (%)",
    legend_title=""
)
st.plotly_chart(figm, use_container_width=True)

# -----------------------------
# Alertas atípicas
# -----------------------------
st.subheader("Alertas atípicas")
if {"anio_mes", "cliente", "categoria", "valor", "base_3m", "var_vs_base_pct", "alerta"}.issubset(alerts_beh.columns):
    st.dataframe(
        alerts_beh[["anio_mes", "cliente", "categoria", "valor", "base_3m", "var_vs_base_pct", "alerta"]]
        .sort_values("var_vs_base_pct")
        .head(50),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No se encontraron las columnas esperadas en alertas de comportamiento.")
