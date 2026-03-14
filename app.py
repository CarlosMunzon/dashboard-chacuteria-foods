import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Chacutería Foods Dashboard", layout="wide")

base = Path(__file__).parent

# Carga de datos
si = pd.read_csv(base / "sell_in_limpio.csv", parse_dates=["fecha"])
so = pd.read_csv(base / "sell_out_limpio.csv", parse_dates=["fecha"])
summary = pd.read_csv(base / "resumen_mensual.csv", parse_dates=["mes"])
inv = pd.read_csv(base / "inventario_mensual_cierre.csv", parse_dates=["mes","fecha"])
alerts_inv = pd.read_csv(base / "alertas_inventario_dic.csv")
alerts_beh = pd.read_csv(base / "alertas_comportamiento.csv", parse_dates=["mes"])
market_sum = pd.read_csv(base / "mercado_resumen_mensual.csv", parse_dates=["mes"])

st.title("Chacutería Foods – Dashboard comercial 2025")
st.caption("App Streamlit entregable. Reemplazando los archivos de la carpeta data se actualiza la lectura.")

# ==========================
# FILTROS SIDEBAR
# ==========================

canales = st.sidebar.multiselect("Canal", sorted(x for x in si["canal"].dropna().unique()))
clientes = st.sidebar.multiselect("Cliente", sorted(x for x in si["cliente"].dropna().unique()))
categorias = st.sidebar.multiselect("Categoría", sorted(x for x in si["categoria"].dropna().unique()))
regionales = st.sidebar.multiselect("Regional", sorted(x for x in si["regional"].dropna().unique()))

# ==========================
# FUNCIÓN DE FILTRO
# ==========================

def filter_df(df):
    out = df.copy()
    if canales:
        out = out[out["canal"].isin(canales)]
    if clientes:
        out = out[out["cliente"].isin(clientes)]
    if categorias:
        out = out[out["categoria"].isin(categorias)]
    if regionales:
        out = out[out["regional"].isin(regionales)]
    return out

si_f = filter_df(si)
so_f = filter_df(so)

if si_f.empty and so_f.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# ==========================
# KPIs
# ==========================

k1 = si_f[si_f["sku_valido"]==True]["valor"].sum()
k2 = so_f[so_f["sku_valido"]==True]["valor"].sum()
k3 = si_f[si_f["sku_valido"]==True]["kilos"].sum()
k4 = so_f[so_f["sku_valido"]==True]["kilos"].sum()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Sell-in valor", f"COP {k1/1e9:.2f} B")
c2.metric("Sell-out valor", f"COP {k2/1e9:.2f} B")
c3.metric("Sell-in volumen", f"{k3/1000:.1f} ton")
c4.metric("Sell-out volumen", f"{k4/1000:.1f} ton")

# ==========================
# EVOLUCIÓN MENSUAL
# ==========================

si_m = si_f[si_f["sku_valido"]==True].assign(mes=lambda d: d["fecha"].values.astype("datetime64[M]")).groupby("mes", as_index=False).agg(
    sell_in_valor=("valor","sum"),
    sell_in_kilos=("kilos","sum")
)

so_m = so_f[so_f["sku_valido"]==True].assign(mes=lambda d: d["fecha"].values.astype("datetime64[M]")).groupby("mes", as_index=False).agg(
    sell_out_valor=("valor","sum"),
    sell_out_kilos=("kilos","sum")
)

trend = pd.merge(si_m, so_m, on="mes", how="outer").fillna(0).sort_values("mes")

fig = go.Figure()
fig.add_trace(go.Scatter(x=trend["mes"], y=trend["sell_in_valor"]/1e9, mode="lines+markers", name="Sell-in"))
fig.add_trace(go.Scatter(x=trend["mes"], y=trend["sell_out_valor"]/1e9, mode="lines+markers", name="Sell-out"))
fig.update_layout(height=360, template="plotly_white", title="Evolución mensual valor (COP billones)")

st.plotly_chart(fig, use_container_width=True)

# ==========================
# GRÁFICOS
# ==========================

left,right = st.columns(2)

with left:
    mix = si_f[si_f["sku_valido"]==True].groupby("canal", as_index=False).agg(valor=("valor","sum")).sort_values("valor", ascending=False)
    st.plotly_chart(px.bar(mix, x="canal", y="valor", title="Mix sell-in por canal", labels={"valor":"Valor"}), use_container_width=True)

with right:
    cat = so_f[so_f["sku_valido"]==True].groupby("categoria", as_index=False).agg(valor=("valor","sum")).sort_values("valor", ascending=False)
    st.plotly_chart(px.bar(cat, x="categoria", y="valor", title="Sell-out por categoría", labels={"valor":"Valor"}), use_container_width=True)

# ==========================
# INVENTARIO
# ==========================

st.subheader("Inventario y alertas")
st.dataframe(
    alerts_inv[["cliente","descripcion_producto","riesgo","inv_kilos_cierre","doh_30d"]]
    .sort_values(["riesgo","doh_30d"])
    .head(50),
    use_container_width=True
)

# ==========================
# MERCADO
# ==========================

st.subheader("Mercado")

figm = go.Figure()
figm.add_trace(go.Scatter(x=market_sum["mes"], y=market_sum["share_compania_prom"]*100, mode="lines+markers", name="Compañía"))
figm.add_trace(go.Scatter(x=market_sum["mes"], y=market_sum["share_competidor_1_prom"]*100, mode="lines+markers", name="Competidor 1"))
figm.add_trace(go.Scatter(x=market_sum["mes"], y=market_sum["share_competidor_2_prom"]*100, mode="lines+markers", name="Competidor 2"))
figm.update_layout(height=340, template="plotly_white", title="Share promedio mensual (%)")

st.plotly_chart(figm, use_container_width=True)

# ==========================
# ALERTAS
# ==========================

st.subheader("Alertas atípicas")

st.dataframe(
    alerts_beh[["anio_mes","cliente","categoria","valor","base_3m","var_vs_base_pct","alerta"]]
    .sort_values("var_vs_base_pct")
    .head(50),
    use_container_width=True
)
