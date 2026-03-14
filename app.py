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

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: white !important;
    }

    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 12px !important;
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
        line-height: 1.05;
        margin: 0 0 8px 0;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 20px;
        line-height: 1.35;
        opacity: 0.96;
        margin: 0;
    }

    .section-title {
        font-size: 30px;
        font-weight: 800;
        color: #13314f;
        margin-top: 12px;
        margin-bottom: 8px;
        letter-spacing: -0.3px;
    }

    .small-note {
        color: #50677e;
        font-size: 15px;
        margin-top: -6px;
        margin-bottom: 10px;
    }

    .insight-box {
        background: white;
        border-left: 6px solid #1f5d99;
        border-radius: 16px;
        padding: 14px 18px;
        margin-bottom: 16px;
        box-shadow: 0 6px 18px rgba(23, 45, 77, 0.06);
        color: #15314f;
        font-size: 17px;
    }

    .mini-card {
        background: white;
        border-radius: 18px;
        padding: 16px 18px;
        border: 1px solid #e4ebf3;
        box-shadow: 0 8px 24px rgba(23, 45, 77, 0.06);
        margin-bottom: 10px;
    }

    .mini-card-title {
        font-size: 15px;
        color: #5b7086;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .mini-card-value {
        font-size: 28px;
        color: #163a63;
        font-weight: 800;
        line-height: 1.05;
    }

    .mini-card-sub {
        font-size: 14px;
        color: #5b7086;
        margin-top: 6px;
    }

    .traffic-card {
        background: white;
        border-radius: 18px;
        padding: 16px 18px;
        border: 1px solid #e4ebf3;
        box-shadow: 0 8px 24px rgba(23, 45, 77, 0.06);
        margin-bottom: 12px;
    }

    .traffic-title {
        font-size: 15px;
        color: #5b7086;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .traffic-value {
        font-size: 26px;
        font-weight: 800;
        color: #17324d;
    }

    .traffic-pill {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 800;
        margin-top: 8px;
    }

    .pill-green {
        background: #dff5e8;
        color: #137a43;
    }

    .pill-yellow {
        background: #fff4d6;
        color: #9a6a00;
    }

    .pill-red {
        background: #fde1df;
        color: #b42318;
    }

    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #dde6f0;
        padding: 18px 18px 16px 18px;
        border-radius: 20px;
        box-shadow: 0 6px 18px rgba(23, 45, 77, 0.07);
    }

    div[data-testid="metric-container"] label {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #27496b !important;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #102a43 !important;
    }

    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 14px !important;
        font-weight: 700 !important;
    }

    .stPlotlyChart {
        background: white;
        border-radius: 22px;
        padding: 10px 12px 4px 12px;
        box-shadow: 0 8px 24px rgba(23, 45, 77, 0.07);
        border: 1px solid #e4ebf3;
    }

    [data-testid="stDataFrame"] {
        background: white;
        border-radius: 18px;
        padding: 6px;
        border: 1px solid #e4ebf3;
        box-shadow: 0 8px 24px rgba(23, 45, 77, 0.06);
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# UTILIDADES
# =========================================================
def format_cop(value: float) -> str:
    if pd.isna(value):
        return "$0 COP"
    abs_value = abs(value)
    if abs_value >= 1e9:
        return f"${value/1e9:,.2f} B"
    if abs_value >= 1e6:
        return f"${value/1e6:,.1f} MM"
    return f"${value:,.0f}"

def format_ton(value: float) -> str:
    if pd.isna(value):
        return "0.0 ton"
    return f"{value/1000:,.1f} ton"

def format_units(value: float) -> str:
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"

def traffic_light(value, good_threshold, warn_threshold, reverse=False):
    if pd.isna(value):
        return ("Sin dato", "pill-yellow")
    if reverse:
        if value <= good_threshold:
            return ("Verde", "pill-green")
        elif value <= warn_threshold:
            return ("Amarillo", "pill-yellow")
        return ("Rojo", "pill-red")
    else:
        if value >= good_threshold:
            return ("Verde", "pill-green")
        elif value >= warn_threshold:
            return ("Amarillo", "pill-yellow")
        return ("Rojo", "pill-red")

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

def apply_filters(df, canales, clientes, categorias, regionales, skus, tipos_producto):
    out = df.copy()
    if canales and "canal" in out.columns:
        out = out[out["canal"].isin(canales)]
    if clientes and "cliente" in out.columns:
        out = out[out["cliente"].isin(clientes)]
    if categorias and "categoria" in out.columns:
        out = out[out["categoria"].isin(categorias)]
    if regionales and "regional" in out.columns:
        out = out[out["regional"].isin(regionales)]
    if skus and "sku" in out.columns:
        out = out[out["sku"].astype(str).isin(skus)]
    if tipos_producto and "tipo_producto" in out.columns:
        out = out[out["tipo_producto"].isin(tipos_producto)]
    return out

# =========================================================
# CARGA DE DATOS
# =========================================================
base = Path(__file__).parent
si, so, summary, inv, alerts_inv, alerts_beh, market_sum = load_data(base)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 🎛️ Filtros gerenciales")
st.sidebar.markdown("Refina la lectura comercial por segmento.")

canales = st.sidebar.multiselect("Canal", sorted(x for x in si["canal"].dropna().unique()))
clientes = st.sidebar.multiselect("Cliente", sorted(x for x in si["cliente"].dropna().unique()))
categorias = st.sidebar.multiselect("Categoría", sorted(x for x in si["categoria"].dropna().unique()))
regionales = st.sidebar.multiselect("Regional", sorted(x for x in si["regional"].dropna().unique()))
skus = st.sidebar.multiselect("SKU", sorted(si["sku"].dropna().astype(str).unique())) if "sku" in si.columns else []
tipos_producto = st.sidebar.multiselect("Tipo de producto", sorted(si["tipo_producto"].dropna().unique())) if "tipo_producto" in si.columns else []

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Guía rápida")
st.sidebar.markdown(
    "- KPIs: visión total del negocio\n"
    "- Semáforos: foco ejecutivo inmediato\n"
    "- Evolución mensual: tendencia de valor\n"
    "- Composición comercial: foco de crecimiento\n"
    "- Alertas: intervención operativa"
)

# =========================================================
# FILTROS
# =========================================================
si_f = apply_filters(si, canales, clientes, categorias, regionales, skus, tipos_producto)
so_f = apply_filters(so, canales, clientes, categorias, regionales, skus, tipos_producto)

if si_f.empty and so_f.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

si_valid = si_f[si_f["sku_valido"] == True].copy() if "sku_valido" in si_f.columns else si_f.copy()
so_valid = so_f[so_f["sku_valido"] == True].copy() if "sku_valido" in so_f.columns else so_f.copy()

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">Chacutería Foods</div>
    <div class="hero-subtitle">Dashboard gerencial 2025 • Seguimiento comercial, inventarios y participación de mercado para comités de dirección y toma de decisiones.</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# KPIS
# =========================================================
k1 = si_valid["valor"].sum() if "valor" in si_valid.columns else 0
k2 = so_valid["valor"].sum() if "valor" in so_valid.columns else 0
k3 = si_valid["kilos"].sum() if "kilos" in si_valid.columns else 0
k4 = so_valid["kilos"].sum() if "kilos" in so_valid.columns else 0
u1 = si_valid["unidades"].sum() if "unidades" in si_valid.columns else 0
u2 = so_valid["unidades"].sum() if "unidades" in so_valid.columns else 0

delta_valor = k1 - k2
delta_vol = k3 - k4
delta_u = u1 - u2
gap_pct = (delta_valor / k1) * 100 if k1 != 0 else 0

# Presupuesto ajustado por escala
budget_total = None
budget_pct = None
if summary is not None and not summary.empty:
    budget_candidates = [c for c in summary.columns if "presupuesto" in c.lower()]
    if budget_candidates:
        budget_total = summary[budget_candidates[0]].sum()

        if budget_total < 1e6:
            budget_total = budget_total * 1000
        elif budget_total < 1e9:
            budget_total = budget_total * 1_000_000

        if budget_total != 0:
            budget_pct = (k1 / budget_total) * 100

# Inventario / DOH
inv_total_kg = None
doh_avg = None
if inv is not None and not inv.empty:
    kilos_candidates = [c for c in inv.columns if "kilo" in c.lower()]
    doh_candidates = [c for c in inv.columns if "doh" in c.lower()]
    if kilos_candidates:
        inv_total_kg = inv[kilos_candidates[0]].sum()
    if doh_candidates:
        doh_avg = inv[doh_candidates[0]].mean()

# Market share
share_company = None
if market_sum is not None and not market_sum.empty:
    share_candidates = [c for c in market_sum.columns if "share_compania" in c.lower()]
    if share_candidates:
        share_company = market_sum[share_candidates[0]].mean() * 100

# Tops
top_client = None
top_cat = None
if not so_valid.empty:
    if "cliente" in so_valid.columns:
        top_client = so_valid.groupby("cliente")["valor"].sum().sort_values(ascending=False).index[0]
    if "categoria" in so_valid.columns:
        top_cat = so_valid.groupby("categoria")["valor"].sum().sort_values(ascending=False).index[0]

# Sobreinventario
sobreinventario_msg = ""
if "doh_30d" in alerts_inv.columns:
    sobre = alerts_inv[alerts_inv["doh_30d"] > 30]
    if len(sobre) > 0:
        sobreinventario_msg = f"<br><br>⚠️ <b>Sobreinventario:</b> se identifican {len(sobre)} registros con DOH superior a 30 días."

insight_text = (
    f"El negocio registra un sell-in de <b>{format_cop(k1)}</b> y un sell-out de "
    f"<b>{format_cop(k2)}</b>. La brecha comercial asciende a <b>{format_cop(delta_valor)}</b> "
    f"({gap_pct:.1f}%). Esta diferencia sugiere acumulación de inventario en clientes, por lo que "
    f"se recomienda priorizar revisión de rotación en cuentas clave y ajustar despachos para "
    f"evitar sobreinventario en el canal."
)

st.markdown(f'<div class="insight-box">📌 {insight_text}{sobreinventario_msg}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Resumen ejecutivo</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Sell-in valor", format_cop(k1))
c2.metric("🛒 Sell-out valor", format_cop(k2), delta=format_cop(delta_valor))
c3.metric("📦 Sell-in volumen", format_ton(k3))
c4.metric("🚚 Sell-out volumen", format_ton(k4), delta=format_ton(delta_vol))

c5, c6 = st.columns(2)
c5.metric("🧮 Sell-in unidades", format_units(u1))
c6.metric("🏪 Sell-out unidades", format_units(u2), delta=format_units(delta_u))

# =========================================================
# TARJETAS GERENCIALES
# =========================================================
st.markdown('<div class="section-title">Semáforos gerenciales</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Indicadores de control para seguimiento ejecutivo y priorización de acciones.</div>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)

budget_label, budget_class = traffic_light(budget_pct if budget_pct is not None else float("nan"), 100, 95)
with s1:
    st.markdown(f"""
    <div class="traffic-card">
        <div class="traffic-title">Cumplimiento vs presupuesto</div>
        <div class="traffic-value">{f"{budget_pct:.1f}%" if budget_pct is not None else "N/D"}</div>
        <div class="mini-card-sub">Presupuesto: {format_cop(budget_total) if budget_total is not None else "N/D"}</div>
        <div class="traffic-pill {budget_class}">{budget_label}</div>
    </div>
    """, unsafe_allow_html=True)

doh_label, doh_class = traffic_light(doh_avg if doh_avg is not None else float("nan"), 15, 25, reverse=True)
with s2:
    st.markdown(f"""
    <div class="traffic-card">
        <div class="traffic-title">Inventario y DOH</div>
        <div class="traffic-value">{f"{inv_total_kg/1000:,.1f}k kg" if inv_total_kg is not None else "N/D"}</div>
        <div class="mini-card-sub">DOH promedio: {f"{doh_avg:.1f} días" if doh_avg is not None else "N/D"}</div>
        <div class="traffic-pill {doh_class}">{doh_label}</div>
    </div>
    """, unsafe_allow_html=True)

share_label, share_class = traffic_light(share_company if share_company is not None else float("nan"), 12, 10)
with s3:
    st.markdown(f"""
    <div class="traffic-card">
        <div class="traffic-title">Share compañía</div>
        <div class="traffic-value">{f"{share_company:.1f}%" if share_company is not None else "N/D"}</div>
        <div class="mini-card-sub">Promedio mensual retail</div>
        <div class="traffic-pill {share_class}">{share_label}</div>
    </div>
    """, unsafe_allow_html=True)

gap_label, gap_class = traffic_light(gap_pct, 5, 10, reverse=True)
with s4:
    st.markdown(f"""
    <div class="traffic-card">
        <div class="traffic-title">Brecha sell-in vs sell-out</div>
        <div class="traffic-value">{gap_pct:.1f}%</div>
        <div class="mini-card-sub">Diferencia: {format_cop(delta_valor)}</div>
        <div class="traffic-pill {gap_class}">{gap_label}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# INSIGHTS ESTRATEGICOS
# =========================================================
st.markdown('<div class="section-title">Insights estratégicos</div>', unsafe_allow_html=True)

i1, i2, i3 = st.columns(3)

with i1:
    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-card-title">Cliente líder</div>
        <div class="mini-card-value">{top_client if top_client is not None else "N/D"}</div>
        <div class="mini-card-sub">Mayor sell-out acumulado en el periodo.</div>
    </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-card-title">Categoría líder</div>
        <div class="mini-card-value">{top_cat if top_cat is not None else "N/D"}</div>
        <div class="mini-card-sub">Mayor contribución en valor sell-out.</div>
    </div>
    """, unsafe_allow_html=True)

with i3:
    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-card-title">Lectura ejecutiva</div>
        <div class="mini-card-value">{'Escalar' if gap_pct <= 5 else 'Revisar' if gap_pct <= 10 else 'Intervenir'}</div>
        <div class="mini-card-sub">Prioridad sugerida según brecha comercial e inventario.</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TENDENCIA
# =========================================================
si_m = (
    si_valid.assign(mes=lambda d: d["fecha"].values.astype("datetime64[M]"))
    .groupby("mes", as_index=False)
    .agg(
        sell_in_valor=("valor", "sum"),
        sell_in_kilos=("kilos", "sum"),
        sell_in_unidades=("unidades", "sum") if "unidades" in si_valid.columns else ("valor", "count")
    )
)

so_m = (
    so_valid.assign(mes=lambda d: d["fecha"].values.astype("datetime64[M]"))
    .groupby("mes", as_index=False)
    .agg(
        sell_out_valor=("valor", "sum"),
        sell_out_kilos=("kilos", "sum"),
        sell_out_unidades=("unidades", "sum") if "unidades" in so_valid.columns else ("valor", "count")
    )
)

trend = pd.merge(si_m, so_m, on="mes", how="outer").fillna(0).sort_values("mes")

if summary is not None and not summary.empty:
    sum_copy = summary.copy()
    budget_candidates = [c for c in sum_copy.columns if "presupuesto" in c.lower()]
    if "mes" in sum_copy.columns and budget_candidates:
        sum_copy = sum_copy[["mes", budget_candidates[0]]].rename(columns={budget_candidates[0]: "presupuesto"})

        if sum_copy["presupuesto"].sum() < 1e6:
            sum_copy["presupuesto"] = sum_copy["presupuesto"] * 1000
        elif sum_copy["presupuesto"].sum() < 1e9:
            sum_copy["presupuesto"] = sum_copy["presupuesto"] * 1_000_000

        trend = trend.merge(sum_copy, on="mes", how="left")

st.markdown('<div class="section-title">Evolución mensual del negocio</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Comparativo mensual de sell-in, sell-out y presupuesto para seguimiento comercial.</div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=trend["mes"], y=trend["sell_in_valor"] / 1e9,
    mode="lines+markers", name="Sell-in",
    line=dict(width=5, color="#4F6BED"), marker=dict(size=8)
))
fig.add_trace(go.Scatter(
    x=trend["mes"], y=trend["sell_out_valor"] / 1e9,
    mode="lines+markers", name="Sell-out",
    line=dict(width=5, color="#F05A3A"), marker=dict(size=8)
))
if "presupuesto" in trend.columns:
    fig.add_trace(go.Scatter(
        x=trend["mes"], y=trend["presupuesto"] / 1e9,
        mode="lines+markers", name="Presupuesto",
        line=dict(width=4, color="#13B58C", dash="dash"), marker=dict(size=7)
    ))
fig.update_layout(
    height=450,
    template="plotly_white",
    title="Valor mensual del negocio",
    xaxis_title="Mes",
    yaxis_title="COP Billones",
    legend_title="",
    title_font=dict(size=22),
    font=dict(size=14, color="#17324d"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    title_x=0.01,
    margin=dict(l=20, r=20, t=60, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# =========================================================
# COMPOSICION COMERCIAL
# =========================================================
st.markdown('<div class="section-title">Composición comercial</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Apertura por canal y categoría para identificar focos de crecimiento.</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    mix = (
        si_valid.groupby("canal", as_index=False)
        .agg(valor=("valor", "sum"))
        .sort_values("valor", ascending=False)
    )
    fig_mix = px.bar(
        mix, x="canal", y="valor",
        title="Mix sell-in por canal",
        labels={"valor": "Valor (COP)", "canal": "Canal"},
        text_auto=".2s"
    )
    fig_mix.update_traces(marker_color="#2C7BE5")
    fig_mix.update_layout(
        template="plotly_white",
        height=390,
        title_x=0.03,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=13, color="#17324d")
    )
    st.plotly_chart(fig_mix, use_container_width=True)

with right:
    cat = (
        so_valid.groupby("categoria", as_index=False)
        .agg(valor=("valor", "sum"))
        .sort_values("valor", ascending=False)
    )
    fig_cat = px.bar(
        cat, x="categoria", y="valor",
        title="Sell-out por categoría",
        labels={"valor": "Valor (COP)", "categoria": "Categoría"},
        text_auto=".2s"
    )
    fig_cat.update_traces(marker_color="#13B58C")
    fig_cat.update_layout(
        template="plotly_white",
        height=390,
        title_x=0.03,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=13, color="#17324d")
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# =========================================================
# DETALLE POR SKU / TIPO DE PRODUCTO
# =========================================================
st.markdown('<div class="section-title">Detalle por SKU y tipo de producto</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Profundización del desempeño comercial a nivel de producto.</div>', unsafe_allow_html=True)

d1, d2 = st.columns(2)

with d1:
    if "sku" in so_valid.columns:
        sku_rank = (
            so_valid.groupby("sku", as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("valor", ascending=False)
            .head(10)
        )
        fig_sku = px.bar(
            sku_rank,
            x="sku",
            y="valor",
            title="Top 10 SKU por sell-out",
            labels={"valor": "Valor (COP)", "sku": "SKU"},
            text_auto=".2s"
        )
        fig_sku.update_traces(marker_color="#6C63FF")
        fig_sku.update_layout(
            template="plotly_white",
            height=390,
            title_x=0.03,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(size=13, color="#17324d")
        )
        st.plotly_chart(fig_sku, use_container_width=True)
    else:
        st.info("No se encontró la columna SKU en la base filtrada.")

with d2:
    if "tipo_producto" in so_valid.columns:
        tipo_rank = (
            so_valid.groupby("tipo_producto", as_index=False)
            .agg(valor=("valor", "sum"))
            .sort_values("valor", ascending=False)
        )
        fig_tipo = px.bar(
            tipo_rank,
            x="tipo_producto",
            y="valor",
            title="Sell-out por tipo de producto",
            labels={"valor": "Valor (COP)", "tipo_producto": "Tipo de producto"},
            text_auto=".2s"
        )
        fig_tipo.update_traces(marker_color="#FF9F1C")
        fig_tipo.update_layout(
            template="plotly_white",
            height=390,
            title_x=0.03,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(size=13, color="#17324d")
        )
        st.plotly_chart(fig_tipo, use_container_width=True)
    else:
        st.info("No se encontró la columna tipo de producto en la base filtrada.")

# =========================================================
# RANKING CLIENTES
# =========================================================
st.markdown('<div class="section-title">Ranking comercial</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Top clientes por valor sell-out para priorización comercial.</div>', unsafe_allow_html=True)

if "cliente" in so_valid.columns and not so_valid.empty:
    rank_client = (
        so_valid.groupby("cliente", as_index=False)
        .agg(valor=("valor", "sum"))
        .sort_values("valor", ascending=False)
        .head(10)
    )
    fig_rank = px.bar(
        rank_client.sort_values("valor", ascending=True),
        x="valor", y="cliente",
        orientation="h",
        title="Top 10 clientes por sell-out",
        labels={"valor": "Valor (COP)", "cliente": "Cliente"},
        text_auto=".2s"
    )
    fig_rank.update_traces(marker_color="#1f5d99")
    fig_rank.update_layout(
        template="plotly_white",
        height=420,
        title_x=0.03,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=13, color="#17324d")
    )
    st.plotly_chart(fig_rank, use_container_width=True)

# =========================================================
# INVENTARIO + MERCADO
# =========================================================
left2, right2 = st.columns([1.15, 1])

with left2:
    st.markdown('<div class="section-title">Inventario y alertas críticas</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-note">Productos y clientes con mayor prioridad operativa.</div>', unsafe_allow_html=True)
    expected_cols = {"cliente", "descripcion_producto", "riesgo", "inv_kilos_cierre", "doh_30d"}
    if expected_cols.issubset(alerts_inv.columns):
        st.dataframe(
            alerts_inv[["cliente", "descripcion_producto", "riesgo", "inv_kilos_cierre", "doh_30d"]]
            .sort_values(["riesgo", "doh_30d"])
            .head(30),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No se encontraron las columnas esperadas en alertas de inventario.")

with right2:
    st.markdown('<div class="section-title">Share promedio mensual retail</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-note">Seguimiento comparativo frente a competidores relevantes.</div>', unsafe_allow_html=True)
    figm = go.Figure()
    figm.add_trace(go.Scatter(
        x=market_sum["mes"], y=market_sum["share_compania_prom"] * 100,
        mode="lines+markers", name="Compañía",
        line=dict(width=5, color="#4F6BED"), marker=dict(size=7)
    ))
    figm.add_trace(go.Scatter(
        x=market_sum["mes"], y=market_sum["share_competidor_1_prom"] * 100,
        mode="lines+markers", name="Competidor 1",
        line=dict(width=4, color="#F05A3A"), marker=dict(size=7)
    ))
    figm.add_trace(go.Scatter(
        x=market_sum["mes"], y=market_sum["share_competidor_2_prom"] * 100,
        mode="lines+markers", name="Competidor 2",
        line=dict(width=4, color="#13B58C"), marker=dict(size=7)
    ))
    figm.update_layout(
        height=430,
        template="plotly_white",
        title="Participación promedio mensual (%)",
        xaxis_title="Mes",
        yaxis_title="Share %",
        legend_title="",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=13, color="#17324d"),
        title_x=0.03
    )
    st.plotly_chart(figm, use_container_width=True)

# =========================================================
# ALERTAS ATIPICAS
# =========================================================
st.markdown('<div class="section-title">Alertas atípicas de comportamiento</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Cambios relevantes versus base histórica de 3 meses.</div>', unsafe_allow_html=True)

expected_alert_cols = {"anio_mes", "cliente", "categoria", "valor", "base_3m", "var_vs_base_pct", "alerta"}
if expected_alert_cols.issubset(alerts_beh.columns):
    st.dataframe(
        alerts_beh[["anio_mes", "cliente", "categoria", "valor", "base_3m", "var_vs_base_pct", "alerta"]]
        .sort_values("var_vs_base_pct")
        .head(40),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No se encontraron las columnas esperadas en alertas de comportamiento.")
