import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Sistem Cerdas IKP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# SESSION STATE — default to Light Mode
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "☀️ Mode Siang (Light)"

# ─────────────────────────────────────────────
# DYNAMIC CSS — injected based on theme choice
# ─────────────────────────────────────────────
LIGHT_CSS = """
<style>
    /* ── global ── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], section.main {
        background-color: #F0F4F8 !important;
        color: #1A202C !important;
    }
    /* ── sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] * { color: #1A202C !important; }
    /* ── metric cards ── */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
    }
    /* ── dataframe ── */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    /* ── divider ── */
    hr { border-color: #CBD5E0; }
</style>
"""

DARK_CSS = """
<style>
    /* ── global ── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], section.main {
        background-color: #0D1117 !important;
        color: #E2E8F0 !important;
    }
    /* ── sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D;
    }
    [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    /* ── metric cards ── */
    [data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 16px 20px;
    }
    /* ── inputs / selects ── */
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] select,
    [data-testid="stFileUploader"] {
        background-color: #21262D !important;
        color: #E2E8F0 !important;
        border-color: #30363D !important;
    }
    /* ── dataframe ── */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    /* ── divider ── */
    hr { border-color: #30363D; }
</style>
"""

is_dark = st.session_state.theme == "🌙 Mode Malam (Dark)"
st.markdown(DARK_CSS if is_dark else LIGHT_CSS, unsafe_allow_html=True)

# Plotly template & color palette derived from theme
plotly_template = "plotly_dark" if is_dark else "plotly_white"
text_color      = "#E2E8F0"    if is_dark else "#1A202C"
grid_color      = "#30363D"    if is_dark else "#E2E8F0"
paper_bg        = "#161B22"    if is_dark else "#FFFFFF"
plot_bg         = "#0D1117"    if is_dark else "#F0F4F8"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏢 Sistem Cerdas IKP")
    st.markdown("**Indeks Kebutuhan Peredam**")
    st.markdown("---")

    # ── Theme toggle ──────────────────────────
    st.markdown("### 🎨 Tema Tampilan")
    selected_theme = st.radio(
        label="Pilih mode tampilan:",
        options=["☀️ Mode Siang (Light)", "🌙 Mode Malam (Dark)"],
        index=0 if st.session_state.theme == "☀️ Mode Siang (Light)" else 1,
        key="theme_radio",
        label_visibility="collapsed",
    )
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.markdown("---")

    # ── File uploader ─────────────────────────
    st.markdown("### 📂 Upload Data ETABS")
    uploaded_file = st.file_uploader(
        label="Unggah file hasil output ETABS (.csv)",
        type=["csv"],
        help="File CSV harus memiliki kolom: Lantai, Drift, DC_Ratio",
    )

    st.markdown("---")

    # ── Cara penggunaan ───────────────────────
    with st.expander("📖 Cara Penggunaan", expanded=False):
        st.markdown(
            """
1. Pilih tema tampilan sesuai preferensi.
2. Siapkan file `.csv` hasil export ETABS dengan kolom:
   - **Lantai** — nomor / nama lantai
   - **Drift** — simpangan antar-lantai (desimal)
   - **DC_Ratio** — rasio Demand/Capacity kolom
3. Klik *Browse files* dan unggah file Anda.
4. Dashboard akan otomatis memproses & menampilkan hasil evaluasi.
            """
        )

    st.markdown("---")
    st.markdown(
        """
        <small>
        👤 <b>Bagus Karunia Ananda</b><br>
        🎓 Magister Teknik Sipil<br>
        🏛️ Universitas Mercu Buana
        </small>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.markdown(
    f"""
    <h1 style='text-align:center; font-size:2.2rem; margin-bottom:0;'>
        🏢 Sistem Cerdas IKP
    </h1>
    <p style='text-align:center; color:{"#8B949E" if is_dark else "#718096"}; font-size:1rem; margin-top:4px;'>
        Evaluasi Kinerja Seismik Gedung Asimetris — Berbasis Output ETABS
    </p>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ─────────────────────────────────────────────
# LANDING STATE — no file uploaded yet
# ─────────────────────────────────────────────
if uploaded_file is None:
    st.info(
        "👈 **Mulai di sini:** Unggah file `.csv` melalui panel kiri untuk memulai evaluasi kinerja seismik.",
        icon="📂",
    )
    st.markdown(
        """
        #### Tentang Aplikasi
        **Sistem Cerdas IKP** (*Indeks Kebutuhan Peredam*) adalah *dashboard* interaktif yang dirancang
        untuk membantu insinyur struktur dalam mengevaluasi kebutuhan alat peredam gempa (*damper*)
        pada gedung asimetris berdasarkan data numerik hasil analisis ETABS.

        | Parameter | Ambang Batas | Keterangan |
        |---|---|---|
        | `Drift` | ≤ 0.020 | Simpangan antar-lantai maksimum izin |
        | `DC_Ratio` | ≤ 1.00 | Rasio Demand/Capacity kolom maksimum |
        | `DC_Ratio` | ≥ 0.50 | Batas minimum agar desain tidak *overkill* |
        """
    )
    st.stop()

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
try:
    df = pd.read_csv(uploaded_file)
    required_cols = {"Lantai", "Drift", "DC_Ratio"}
    missing = required_cols - set(df.columns)
    if missing:
        st.error(f"❌ Kolom berikut tidak ditemukan di file Anda: **{', '.join(missing)}**. Periksa kembali format CSV Anda.")
        st.stop()
    df["Drift"]    = pd.to_numeric(df["Drift"],    errors="coerce")
    df["DC_Ratio"] = pd.to_numeric(df["DC_Ratio"], errors="coerce")
    df.dropna(subset=["Drift", "DC_Ratio"], inplace=True)
except Exception as e:
    st.error(f"❌ Gagal membaca file: {e}")
    st.stop()

max_drift    = float(df["Drift"].max())
max_dc_ratio = float(df["DC_Ratio"].max())

# ─────────────────────────────────────────────
# LOGIC — status evaluation
# ─────────────────────────────────────────────
if max_drift > 0.020 or max_dc_ratio > 1.00:
    status_label = "🔴 TIDAK AMAN"
    status_color = "#FC8181"
    status_bg    = "#742A2A"
    alert_fn     = st.error
    alert_msg    = (
        "**⚠️ STRUKTUR TIDAK AMAN!** Nilai Drift atau D/C Ratio melebihi batas izin. "
        "Desain memerlukan perkuatan atau penambahan peredam segera."
    )
elif (df["Drift"].max() <= 0.010) and (df["DC_Ratio"].max() < 0.50):
    status_label = "🟡 OVERKILL / BOROS"
    status_color = "#F6E05E"
    status_bg    = "#744210"
    alert_fn     = st.warning
    alert_msg    = (
        "**⚠️ DESAIN TERLALU KONSERVATIF!** Semua nilai Drift ≤ 0.010 dan D/C Ratio < 0.50. "
        "Kapasitas peredam berlebih — pertimbangkan untuk mengoptimalkan dimensi agar lebih ekonomis."
    )
else:
    status_label = "🟢 OPTIMAL"
    status_color = "#68D391"
    status_bg    = "#1C4532"
    alert_fn     = st.success
    alert_msg    = (
        "**✅ DESAIN AMAN & EKONOMIS!** Semua parameter berada dalam rentang optimal. "
        "Struktur memenuhi persyaratan keselamatan seismik dengan peredam berukuran efisien."
    )

# ─────────────────────────────────────────────
# STATUS ALERT BANNER
# ─────────────────────────────────────────────
alert_fn(alert_msg)

# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────
st.markdown("#### 📊 Ringkasan Indikator Kinerja")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🏷️ Status Akhir",
        value=status_label,
        help="Hasil evaluasi keseluruhan berdasarkan semua parameter",
    )
with col2:
    drift_delta = f"{((max_drift / 0.020) * 100):.1f}% dari batas"
    st.metric(
        label="📐 Max Drift",
        value=f"{max_drift:.4f}",
        delta=drift_delta,
        delta_color="inverse",
        help="Simpangan antar-lantai maksimum (batas izin: 0.020)",
    )
with col3:
    dc_delta = f"{((max_dc_ratio / 1.00) * 100):.1f}% dari batas"
    st.metric(
        label="⚖️ Max D/C Ratio",
        value=f"{max_dc_ratio:.4f}",
        delta=dc_delta,
        delta_color="inverse",
        help="Rasio Demand/Capacity kolom maksimum (batas izin: 1.00)",
    )

st.markdown("---")

# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
st.markdown("#### 📈 Visualisasi Interaktif")
chart_col1, chart_col2 = st.columns(2)

# Shared layout base
def base_layout(title: str) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=15, color=text_color)),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=text_color),
        xaxis=dict(gridcolor=grid_color, linecolor=grid_color, zerolinecolor=grid_color),
        yaxis=dict(gridcolor=grid_color, linecolor=grid_color, zerolinecolor=grid_color),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(font=dict(color=text_color)),
    )

with chart_col1:
    fig_drift = go.Figure()
    fig_drift.add_trace(go.Scatter(
        x=df["Drift"],
        y=df["Lantai"].astype(str),
        mode="lines+markers",
        name="Drift",
        line=dict(color="#63B3ED", width=2.5),
        marker=dict(size=7, color="#63B3ED"),
    ))
    fig_drift.add_vline(
        x=0.020,
        line=dict(color="#FC8181", dash="dot", width=2),
        annotation_text="Batas 0.020",
        annotation_font_color="#FC8181",
        annotation_position="top right",
    )
    fig_drift.update_layout(
        **base_layout("Profil Simpangan (Drift) Tiap Lantai"),
        xaxis_title="Drift",
        yaxis_title="Lantai",
    )
    st.plotly_chart(fig_drift, use_container_width=True)

with chart_col2:
    bar_colors = [
        "#FC8181" if v > 1.00 else "#68D391" if v >= 0.50 else "#F6E05E"
        for v in df["DC_Ratio"]
    ]
    fig_dc = go.Figure()
    fig_dc.add_trace(go.Bar(
        x=df["Lantai"].astype(str),
        y=df["DC_Ratio"],
        name="D/C Ratio",
        marker_color=bar_colors,
        text=[f"{v:.3f}" for v in df["DC_Ratio"]],
        textposition="outside",
        textfont=dict(color=text_color, size=10),
    ))
    fig_dc.add_hline(
        y=1.00,
        line=dict(color="#FC8181", dash="dot", width=2),
        annotation_text="Batas 1.00",
        annotation_font_color="#FC8181",
        annotation_position="top right",
    )
    fig_dc.update_layout(
        **base_layout("Rasio Demand/Capacity (D/C) Kolom"),
        xaxis_title="Lantai",
        yaxis_title="D/C Ratio",
    )
    st.plotly_chart(fig_dc, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# RAW DATA TABLE
# ─────────────────────────────────────────────
st.markdown("#### 🗂️ Tabel Data Mentah")
st.dataframe(
    df,
    use_container_width=True,
    height=min(400, 35 * len(df) + 40)
)

st.markdown(
    f"<p style='text-align:right; color:{'#8B949E' if is_dark else '#718096'}; font-size:0.8rem;'>"
    f"Total {len(df)} lantai diproses · Sistem Cerdas IKP © 2025 · Bagus Karunia Ananda — Universitas Mercu Buana</p>",
    unsafe_allow_html=True,
)
