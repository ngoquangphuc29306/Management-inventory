# -*- coding: utf-8 -*-
"""
Giao diện người dùng Streamlit (Presentation Layer) cho Hệ thống quản lý tồn kho.
Thiết kế theo phong cách giao diện SaaS Warehouse Dashboard cao cấp.
"""

import io
import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

import db
import logic

ICON_DIR = Path("ionicons.designerpack")
APP_ICON_PATH = ICON_DIR / "cube-outline.svg"


def load_ionicon(filename):
    icon_path = ICON_DIR / filename
    if not icon_path.exists():
        raise FileNotFoundError(f"Không tìm thấy icon phù hợp trong thư mục ionicons.designerpack: {filename}")

    svg = icon_path.read_text(encoding="utf-8")
    svg = svg.replace("#000", "currentColor")
    svg = svg.replace('width="512" height="512"', 'width="1em" height="1em" aria-hidden="true" focusable="false"')
    return svg


ICONS = {
    "app": load_ionicon("cube-outline.svg"),
    "dashboard": load_ionicon("bar-chart-outline.svg"),
    "search": load_ionicon("search-outline.svg"),
    "transactions": load_ionicon("swap-horizontal-outline.svg"),
    "products": load_ionicon("clipboard-outline.svg"),
    "history": load_ionicon("document-text-outline.svg"),
    "reports": load_ionicon("folder-open-outline.svg"),
    "add": load_ionicon("add-circle-outline.svg"),
    "download": load_ionicon("download-outline.svg"),
    "alert": load_ionicon("alert-circle-outline.svg"),
}


def icon_html(name, class_name="app-icon"):
    return f'<span class="{class_name}">{ICONS[name]}</span>'


def title_html(icon_name, title, subtitle):
    return f"""
    <div class="title-banner">
        <h1>{icon_html(icon_name, "title-icon")}<span>{title}</span></h1>
        <p>{subtitle}</p>
    </div>
    """

# ==========================================
# CẤU HÌNH GIAO DIỆN STREAMLIT
# ==========================================

st.set_page_config(
    page_title="Warehouse Management System",
    page_icon=str(APP_ICON_PATH),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nhúng CSS tùy chỉnh cho giao diện warehouse dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink-950: #101820;
        --ink-900: #17212b;
        --ink-800: #23303d;
        --ink-700: #344354;
        --ink-500: #667085;
        --line: #d9e2ea;
        --paper: #fbfcf7;
        --panel: #ffffff;
        --mint: #00a884;
        --mint-soft: #e6f7f1;
        --amber: #f59e0b;
        --amber-soft: #fff4d8;
        --red: #df3b3b;
        --red-soft: #fff0ee;
        --blueprint: #22577a;
        --shadow: 0 18px 40px rgba(16, 24, 32, 0.09);
    }

    html, body, .stMarkdown, .stDataFrame, .stTextInput, .stSelectbox, .stNumberInput {
        font-family: 'Manrope', 'Segoe UI', sans-serif;
    }

    .stApp {
        background:
            linear-gradient(90deg, rgba(34, 87, 122, 0.055) 1px, transparent 1px),
            linear-gradient(0deg, rgba(34, 87, 122, 0.045) 1px, transparent 1px),
            #f4f7f4;
        background-size: 32px 32px;
        color: var(--ink-900);
    }

    .main .block-container {
        padding-top: 1.75rem;
        padding-bottom: 3rem;
        max-width: 1440px;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(0, 168, 132, 0.12), transparent 34%),
            #111923;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #d8e1e8 !important;
    }

    .sidebar-brand {
        padding: 0.25rem 0 1.25rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.25rem;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .brand-mark {
        width: 44px;
        height: 44px;
        border-radius: 8px;
        display: grid;
        place-items: center;
        color: #08120f;
        background: #b7f7df;
        box-shadow: inset 0 -5px 0 rgba(16, 24, 32, 0.14);
    }

    .brand-mark svg {
        width: 24px;
        height: 24px;
        display: block;
    }

    .brand-title {
        font-size: 1rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }

    .brand-subtitle {
        margin-top: 0.2rem;
        font-size: 0.76rem;
        color: #9fb0bf;
        font-weight: 600;
    }

    .sidebar-operator {
        margin-top: 1rem;
        padding: 0.85rem;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .operator-label {
        color: #91a4b7;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0;
        text-transform: uppercase;
    }

    .operator-name {
        margin-top: 0.25rem;
        color: #ffffff;
        font-size: 0.92rem;
        font-weight: 800;
    }

    .operator-role {
        margin-top: 0.1rem;
        color: #aab8c4;
        font-size: 0.72rem;
        font-weight: 600;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.35rem;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 0.7rem 0.75rem;
        border-radius: 8px;
        border: 1px solid transparent;
        background: transparent;
        transition: background 0.16s ease, border-color 0.16s ease, transform 0.16s ease;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(255, 255, 255, 0.09);
        transform: translateX(2px);
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: #f0f7f1;
        border-color: #bfe7d8;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
        color: #102018 !important;
        font-weight: 800;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) div {
        color: #102018 !important;
        font-weight: 800;
    }

    .sidebar-snapshot {
        margin-top: 1.25rem;
        padding: 1rem;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.09);
    }

    .snapshot-title {
        color: #91a4b7;
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
    }

    .snapshot-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.65rem;
        margin-top: 0.75rem;
    }

    .snapshot-item {
        padding: 0.65rem;
        border-radius: 8px;
        background: rgba(0, 0, 0, 0.16);
    }

    .snapshot-value {
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 800;
    }

    .snapshot-label {
        color: #aab8c4;
        font-size: 0.68rem;
        font-weight: 700;
    }

    .title-banner {
        position: relative;
        overflow: hidden;
        color: #fff;
        padding: 1.45rem 1.6rem;
        border-radius: 8px;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background:
            linear-gradient(135deg, rgba(0, 168, 132, 0.26), rgba(245, 158, 11, 0.08)),
            repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.05) 0 1px, transparent 1px 22px),
            #14202a;
        box-shadow: var(--shadow);
    }

    .title-banner:before {
        content: "WAREHOUSE OPS";
        position: absolute;
        right: 1.4rem;
        top: 1.05rem;
        color: rgba(255, 255, 255, 0.18);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0;
    }

    .title-banner h1 {
        display: flex;
        align-items: center;
        gap: 1.65rem;
        color: #ffffff !important;
        font-size: clamp(1.45rem, 1.4vw + 1rem, 2.1rem) !important;
        line-height: 1.1 !important;
        font-weight: 800 !important;
        margin: 0 0 0.45rem 0 !important;
        letter-spacing: 0 !important;
        max-width: 72%;
    }

    .app-icon,
    .title-icon,
    .section-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
        color: currentColor;
        flex: 0 0 auto;
    }

    .title-icon {
        width: 40px;
        height: 40px;
        min-width: 40px;
        border-radius: 8px;
        background: #b7f7df;
        color: #102018;
        box-shadow: inset 0 -5px 0 rgba(16, 24, 32, 0.14);
        margin-right: 0.35rem;
    }

    .title-icon svg {
        width: 24px;
        height: 24px;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin: 0.75rem 0 0.95rem;
        color: var(--ink-900);
        font-size: 1.25rem;
        font-weight: 800;
    }

    .section-icon {
        width: 28px;
        height: 28px;
        border-radius: 7px;
        background: var(--mint-soft);
        color: #0b7b63;
    }

    .section-icon svg {
        width: 18px;
        height: 18px;
    }

    .title-banner p {
        color: #cbd9df !important;
        margin: 0 !important;
        font-size: 0.94rem;
        font-weight: 600;
        max-width: 760px;
    }

    .custom-card {
        position: relative;
        overflow: hidden;
        background: var(--panel);
        border-radius: 8px;
        padding: 1.15rem 1.2rem 1.05rem;
        box-shadow: 0 10px 28px rgba(16, 24, 32, 0.07);
        border: 1px solid var(--line);
        margin-bottom: 1rem;
        border-top: 4px solid var(--blueprint);
    }

    .custom-card:after {
        content: "";
        position: absolute;
        right: 1rem;
        top: 1rem;
        width: 42px;
        height: 18px;
        border-top: 2px solid rgba(34, 87, 122, 0.18);
        border-bottom: 2px solid rgba(34, 87, 122, 0.18);
    }

    .custom-card.alert {
        border-top-color: var(--red);
        background: linear-gradient(180deg, #fff, var(--red-soft));
    }

    .custom-card.success {
        border-top-color: var(--mint);
        background: linear-gradient(180deg, #fff, var(--mint-soft));
    }

    .custom-card .card-title {
        color: var(--ink-500);
        font-size: 0.72rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0;
    }

    .custom-card .card-value {
        font-size: 2rem;
        line-height: 1;
        font-weight: 800;
        color: var(--ink-950);
        margin: 0;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--line);
        border-top: 4px solid var(--blueprint);
        border-radius: 8px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 28px rgba(16, 24, 32, 0.07);
    }

    [data-testid="stMetricLabel"] p {
        color: var(--ink-500) !important;
        font-size: 0.72rem !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        color: var(--ink-950) !important;
        font-weight: 800 !important;
    }

    .main label,
    .main [data-testid="stWidgetLabel"],
    .main [data-testid="stWidgetLabel"] p,
    .main .stCaptionContainer {
        color: var(--ink-800) !important;
    }

    .main [data-testid="stWidgetLabel"] p,
    .main label p {
        font-weight: 700 !important;
    }

    /* Streamlit không bọc widget bằng div HTML mở/đóng qua markdown, nên ẩn wrapper rỗng. */
    .panel-container {
        display: none !important;
    }

    .panel-container h4,
    .panel-container h3,
    .stMarkdown h3,
    .stMarkdown h4 {
        color: var(--ink-900);
        font-weight: 800;
        letter-spacing: 0 !important;
    }

    .stock-alert-row {
        background: #fff5f3;
        border: 1px solid #ffd0c7;
        border-left: 4px solid var(--red);
        border-radius: 8px;
        padding: 0.78rem 0.9rem;
        margin-bottom: 0.55rem;
    }

    .stock-alert-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.75rem;
    }

    .stock-alert-name {
        font-weight: 800;
        color: #8f1f1f;
        font-size: 0.9rem;
    }

    .stock-alert-badge {
        background-color: #ffd7cf;
        color: #8f1f1f;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 0.15rem 0.45rem;
        border-radius: 999px;
        white-space: nowrap;
    }

    .stock-alert-meta {
        font-size: 0.76rem;
        color: #a7392f;
        margin-top: 0.28rem;
        font-weight: 600;
    }

    div.stButton > button,
    div.stDownloadButton > button,
    [data-testid="stFormSubmitButton"] button {
        background: #14202a !important;
        color: #ffffff !important;
        border: 1px solid #14202a !important;
        border-radius: 6px !important;
        padding: 0.58rem 1.05rem !important;
        font-weight: 800 !important;
        transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease !important;
        box-shadow: 0 8px 18px rgba(16, 24, 32, 0.12) !important;
    }

    div.stButton > button p,
    div.stDownloadButton > button p,
    [data-testid="stFormSubmitButton"] button p {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: #00a884 !important;
        border-color: #00a884 !important;
        transform: translateY(-1px);
        box-shadow: 0 10px 22px rgba(0, 168, 132, 0.2) !important;
    }

    div.stButton > button:disabled {
        background: #d8e0e6 !important;
        border-color: #d8e0e6 !important;
        color: #7a8793 !important;
        box-shadow: none !important;
    }

    .delete-btn-container div.stButton > button,
    .delete-btn-container [data-testid="stFormSubmitButton"] button {
        background: var(--red) !important;
        border-color: var(--red) !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="select"] > div,
    textarea,
    [data-testid="stNumberInput"] input {
        border-radius: 6px !important;
        border-color: #cfd9e2 !important;
        background-color: #ffffff !important;
        color: var(--ink-900) !important;
        -webkit-text-fill-color: var(--ink-900) !important;
        opacity: 1 !important;
    }

    div[data-baseweb="input"] input::placeholder,
    textarea::placeholder {
        color: #7b8794 !important;
        -webkit-text-fill-color: #7b8794 !important;
        opacity: 1 !important;
    }

    input:disabled,
    textarea:disabled,
    [aria-disabled="true"] input {
        color: #5d6976 !important;
        -webkit-text-fill-color: #5d6976 !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: var(--ink-900) !important;
    }

    [data-testid="stForm"] {
        border: 1px solid #dbe4ea;
        border-radius: 8px;
        padding: 1rem;
        background: #fbfcf7;
    }

    [data-testid="stTabs"] button {
        font-weight: 800;
        color: var(--ink-700);
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #0b7b63;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(16, 24, 32, 0.05);
    }

    .stAlert {
        border-radius: 8px;
    }

    @media (max-width: 900px) {
        .title-banner h1 {
            max-width: 100%;
            font-size: 1.35rem !important;
        }

        .title-banner:before {
            display: none;
        }

        .stock-alert-head {
            align-items: flex-start;
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

def style_chart(fig, height=None):
    """Áp dụng cùng một theme trực quan cho các biểu đồ trong dashboard."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#fbfcf7',
        font=dict(family="Manrope, Segoe UI, sans-serif", color="#344354"),
        title_font=dict(color="#17212b", size=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#14202a", font_color="#ffffff", bordercolor="#14202a"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#d9e2ea")
    fig.update_yaxes(gridcolor="rgba(34, 87, 122, 0.12)", zeroline=False, linecolor="#d9e2ea")
    if height:
        fig.update_layout(height=height)
    return fig

# Tải dữ liệu ban đầu
try:
    df_sp, df_gd = db.load_data()
    df_summary = logic.get_inventory_summary(df_sp, df_gd)
except Exception as e:
    st.error(f"Lỗi khởi động ứng dụng: {str(e)}")
    st.stop()

# ==========================================
# THIẾT KẾ SIDEBAR ĐIỀU HƯỚNG SAAS
# ==========================================

st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="brand-lockup">
        <div class="brand-mark">""" + ICONS["app"] + """</div>
        <div>
            <div class="brand-title">Warehouse<br/>Control</div>
            <div class="brand-subtitle">Inventory operations</div>
        </div>
    </div>
    <div class="sidebar-operator">
        <div class="operator-label">Đang đăng nhập</div>
        <div class="operator-name">Admin Kho</div>
        <div class="operator-role">Quản lý kho chính</div>
    </div>
</div>
""", unsafe_allow_html=True)

menu_options = [
    "Bảng điều khiển",
    "Tra cứu Tồn kho",
    "Nhập / Xuất kho",
    "Danh mục Sản phẩm",
    "Nhật ký Giao dịch",
    "Xuất Bản Báo cáo"
]

selected_menu = st.sidebar.radio("ĐIỀU HƯỚNG MENU", menu_options, label_visibility="collapsed")

# ==========================================
# PHẦN THỐNG KÊ NHANH (METRICS SUMMARY)
# ==========================================
total_products = len(df_sp)
low_stock_count = len(df_summary[df_summary['ton_hien_tai'] < df_summary['ton_toi_thieu']])

# Tính số giao dịch diễn ra trong hôm nay
today = datetime.date.today()
if not df_gd.empty:
    today_transactions = df_gd[df_gd['ngay_gio'].dt.date == today]
    today_tx_count = len(today_transactions)
else:
    today_tx_count = 0

total_stock_units = int(df_summary['ton_hien_tai'].sum()) if not df_summary.empty else 0
safe_stock_count = max(total_products - low_stock_count, 0)

st.sidebar.markdown(f"""
<div class="sidebar-snapshot">
    <div class="snapshot-title">Tình trạng vận hành</div>
    <div class="snapshot-grid">
        <div class="snapshot-item">
            <div class="snapshot-value">{total_products}</div>
            <div class="snapshot-label">Mặt hàng</div>
        </div>
        <div class="snapshot-item">
            <div class="snapshot-value">{total_stock_units}</div>
            <div class="snapshot-label">Tổng tồn</div>
        </div>
        <div class="snapshot-item">
            <div class="snapshot-value">{safe_stock_count}</div>
            <div class="snapshot-label">An toàn</div>
        </div>
        <div class="snapshot-item">
            <div class="snapshot-value">{low_stock_count}</div>
            <div class="snapshot-label">Cần nhập</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# TRANG 1: BẢNG ĐIỀU KHIỂN (DASHBOARD)
# ==========================================
if selected_menu == "Bảng điều khiển":
    st.markdown(title_html(
        "dashboard",
        "BẢNG ĐIỀU KHIỂN HỆ THỐNG",
        "Phân tích số liệu tổng quan, thống kê xuất nhập và cảnh báo tồn kho tức thời"
    ), unsafe_allow_html=True)
    
    # Hiển thị bộ Metrics ở trên cùng
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Tổng mặt hàng", total_products)
    with col_m2:
        st.metric("Dưới mức tối thiểu", low_stock_count)
    with col_m3:
        st.metric("Giao dịch hôm nay", today_tx_count)
        
    # Thống kê chi tiết
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown('<div class="panel-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{icon_html("download", "section-icon")}<span>Top 10 Sản phẩm Nhập nhiều nhất trong tháng</span></div>', unsafe_allow_html=True)
        df_nhap_all = df_gd[df_gd['loai'] == 'nhap']
        if df_nhap_all.empty:
            st.info("Chưa có dữ liệu nhập kho nào để thống kê.")
        else:
            this_month_nhap = df_nhap_all[
                (df_nhap_all['ngay_gio'].dt.year == today.year) & 
                (df_nhap_all['ngay_gio'].dt.month == today.month)
            ]
            if this_month_nhap.empty:
                df_bar_data = df_nhap_all.copy()
                title_bar = "Top 10 sản phẩm nhập nhiều nhất (Tổng quan)"
            else:
                df_bar_data = this_month_nhap.copy()
                title_bar = f"Top 10 sản phẩm nhập nhiều nhất tháng {today.month}/{today.year}"
                
            df_bar_merged = df_bar_data.merge(df_sp[['ma_sp', 'ten_sp']], on='ma_sp', how='left')
            df_bar_grouped = df_bar_merged.groupby(['ma_sp', 'ten_sp'])['so_luong'].sum().reset_index()
            df_bar_top = df_bar_grouped.sort_values(by='so_luong', ascending=False).head(10)
            
            fig_bar = px.bar(
                df_bar_top,
                x='ten_sp',
                y='so_luong',
                text='so_luong',
                color='so_luong',
                color_continuous_scale=['#dff7ec', '#00a884', '#14202a'],
                labels={'ten_sp': 'Tên sản phẩm', 'so_luong': 'Số lượng nhập'}
            )
            fig_bar.update_layout(title=title_bar, margin=dict(t=30, b=10, l=10, r=10), height=320)
            fig_bar = style_chart(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_right:
        st.markdown('<div class="panel-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{icon_html("alert", "section-icon")}<span>Cảnh báo Tồn kho tối thiểu</span></div>', unsafe_allow_html=True)
        df_low_stock = df_summary[df_summary['ton_hien_tai'] < df_summary['ton_toi_thieu']]
        if df_low_stock.empty:
            st.success("✅ Tuyệt vời! Tất cả sản phẩm đều có mức tồn kho an toàn.")
        else:
            # Render dạng các box cảnh báo SaaS đẹp mắt
            for _, row in df_low_stock.iterrows():
                st.markdown(f"""
                <div class="stock-alert-row">
                    <div class="stock-alert-head">
                        <span class="stock-alert-name">{row['ten_sp']} ({row['ma_sp']})</span>
                        <span class="stock-alert-badge">Hụt {row['ton_toi_thieu'] - row['ton_hien_tai']} {row['don_vi_tinh']}</span>
                    </div>
                    <div class="stock-alert-meta">
                        Tồn: <strong>{row['ton_hien_tai']}</strong> / Mức tối thiểu: {row['ton_toi_thieu']} (Nhóm: {row['nhom_hang']})
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Dòng 3: Đồ thị xu hướng tồn kho lũy kế của sản phẩm tùy chọn
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{icon_html("dashboard", "section-icon")}<span>Phân tích Xu hướng Tồn kho lũy kế</span></div>', unsafe_allow_html=True)
    if df_sp.empty:
        st.info("Chưa có sản phẩm nào.")
    else:
        sp_dashboard_choices = [f"{row['ma_sp']} - {row['ten_sp']}" for _, row in df_sp.iterrows()]
        selected_dashboard_choice = st.selectbox("Chọn sản phẩm để xem dòng thời gian tồn kho:", sp_dashboard_choices, key="dashboard_sp_select")
        selected_dashboard_ma = selected_dashboard_choice.split(" - ")[0]
        selected_dashboard_name = selected_dashboard_choice.split(" - ")[1]
        
        df_dashboard_gd = df_gd[df_gd['ma_sp'] == selected_dashboard_ma].sort_values(by='ngay_gio')
        if df_dashboard_gd.empty:
            st.info("Chưa có giao dịch nào phát sinh đối với sản phẩm này.")
        else:
            df_dashboard_trend = df_dashboard_gd.copy()
            df_dashboard_trend['change'] = df_dashboard_trend.apply(lambda r: r['so_luong'] if r['loai'] == 'nhap' else -r['so_luong'], axis=1)
            df_dashboard_trend['ton_kho_luy_ke'] = df_dashboard_trend['change'].cumsum()
            
            fig_line = px.line(
                df_dashboard_trend,
                x='ngay_gio',
                y='ton_kho_luy_ke',
                markers=True,
                labels={'ngay_gio': 'Thời điểm', 'ton_kho_luy_ke': 'Mức tồn hiện có'},
                color_discrete_sequence=['#00a884']
            )
            fig_line.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
            fig_line = style_chart(fig_line)
            st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TRANG 2: TRA CỨU TỒN KHO
# ==========================================
elif selected_menu == "Tra cứu Tồn kho":
    st.markdown(title_html(
        "search",
        "TRA CỨU TỒN KHO CHI TIẾT",
        "Tìm kiếm sản phẩm, lọc theo nhóm hàng và click chọn để phân tích chi tiết"
    ), unsafe_allow_html=True)
    
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    # Bộ lọc tìm kiếm sản phẩm, lọc theo trạng thái và lọc theo nhóm hàng
    col_search, col_grp, col_filter = st.columns([2, 1, 1])
    with col_search:
        search_query = st.text_input("Tìm kiếm theo Mã hoặc Tên sản phẩm", "", key="search_inv")
    with col_grp:
        unique_groups = ["Tất cả"] + list(df_sp['nhom_hang'].unique())
        selected_grp = st.selectbox("Lọc theo nhóm hàng", unique_groups, key="filter_group")
    with col_filter:
        status_filter = st.selectbox("Lọc theo trạng thái cảnh báo", ["Tất cả", "Bình thường", "Cần nhập hàng"], key="filter_status")
        
    df_filtered = df_summary.copy()
    
    # Thực hiện lọc dữ liệu
    if search_query:
        df_filtered = df_filtered[
            df_filtered['ma_sp'].str.contains(search_query, case=False) | 
            df_filtered['ten_sp'].str.contains(search_query, case=False)
        ]
        
    if selected_grp != "Tất cả":
        df_filtered = df_filtered[df_filtered['nhom_hang'] == selected_grp]
        
    if status_filter != "Tất cả":
        df_filtered = df_filtered[df_filtered['trang_thai'] == status_filter]
        
    if df_filtered.empty:
        st.info("Không tìm thấy sản phẩm nào phù hợp với bộ lọc.")
    else:
        # Chuẩn bị bảng dữ liệu hiển thị
        df_display = df_filtered[['ma_sp', 'ten_sp', 'nhom_hang', 'don_vi_tinh', 'ton_hien_tai', 'ton_toi_thieu', 'trang_thai']].copy()
        df_display.columns = ['Mã sản phẩm', 'Tên sản phẩm', 'Nhóm hàng', 'Đơn vị tính', 'Tồn hiện tại', 'Tồn tối thiểu', 'Trạng thái']
        
        # Định nghĩa hàm tô màu đỏ cho dòng có lượng tồn dưới mức tồn tối thiểu
        def color_low_stock(row):
            is_low = row['Tồn hiện tại'] < row['Tồn tối thiểu']
            return ['background-color: #fef2f2; color: #b91c1c; font-weight: bold; border-left: 4px solid #ef4444;' if is_low else '' for _ in row]
            
        styled_df = df_display.style.apply(color_low_stock, axis=1)
        
        st.caption("💡 Mẹo: Nhấp chọn một dòng sản phẩm trên bảng để xem chi tiết lịch sử biến động tồn kho.")
        
        # Cho phép người dùng chọn dòng trên bảng (Streamlit on_select)
        selection = st.dataframe(
            styled_df, 
            use_container_width=True, 
            height=300,
            on_select="rerun",
            selection_mode="single-row",
            key="df_inv_selection"
        )
        
        # In ra các cảnh báo bằng alert widget của Streamlit
        low_stock_items = df_filtered[df_filtered['ton_hien_tai'] < df_filtered['ton_toi_thieu']]
        if not low_stock_items.empty:
            st.warning(f"⚠️ Cảnh báo: Có **{len(low_stock_items)}** sản phẩm đang dưới mức tồn kho tối thiểu!")
            
        # Xử lý khi người dùng chọn dòng sản phẩm
        selected_rows = selection.get("selection", {}).get("rows", [])
        if selected_rows:
            row_idx = selected_rows[0]
            selected_ma_sp = df_display.iloc[row_idx]['Mã sản phẩm']
            selected_ten_sp = df_display.iloc[row_idx]['Tên sản phẩm']
            
            st.markdown("---")
            st.markdown(f'<div class="section-title">{icon_html("search", "section-icon")}<span>Chi tiết biến động: {selected_ten_sp} ({selected_ma_sp})</span></div>', unsafe_allow_html=True)
            
            # Vẽ biểu đồ xu hướng tồn kho cho sản phẩm được chọn
            df_prod_gd = df_gd[df_gd['ma_sp'] == selected_ma_sp].sort_values(by='ngay_gio')
            
            col_detail_chart, col_detail_list = st.columns([3, 2])
            
            with col_detail_chart:
                if df_prod_gd.empty:
                    st.info("Chưa có giao dịch nào cho sản phẩm này.")
                else:
                    df_trend = df_prod_gd.copy()
                    df_trend['change'] = df_trend.apply(lambda r: r['so_luong'] if r['loai'] == 'nhap' else -r['so_luong'], axis=1)
                    df_trend['ton_kho_luy_ke'] = df_trend['change'].cumsum()
                    
                    fig_line_detail = px.line(
                        df_trend, 
                        x='ngay_gio', 
                        y='ton_kho_luy_ke',
                        markers=True,
                        title=f"Đồ thị lịch sử tồn lũy kế",
                        labels={'ngay_gio': 'Thời điểm', 'ton_kho_luy_ke': 'Mức tồn'},
                        color_discrete_sequence=['#00a884']
                    )
                    fig_line_detail.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=220)
                    fig_line_detail = style_chart(fig_line_detail)
                    st.plotly_chart(fig_line_detail, use_container_width=True)
                    
            with col_detail_list:
                st.markdown("**Nhật ký giao dịch gần đây:**")
                if df_prod_gd.empty:
                    st.caption("Không có giao dịch.")
                else:
                    df_prod_gd_show = df_prod_gd.sort_values(by='ngay_gio', ascending=False).copy()
                    df_prod_gd_show['loai'] = df_prod_gd_show['loai'].map({'nhap': 'Nhập kho', 'xuat': 'Xuất kho'})
                    df_prod_gd_show['ngay_gio'] = df_prod_gd_show['ngay_gio'].dt.strftime('%H:%M:%S %d/%m/%Y')
                    df_prod_gd_show = df_prod_gd_show[['ngay_gio', 'loai', 'so_luong']]
                    df_prod_gd_show.columns = ['Thời gian', 'Loại', 'Số lượng']
                    st.dataframe(df_prod_gd_show, use_container_width=True, height=220)
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TRANG 3: NHẬP / XUẤT KHO
# ==========================================
elif selected_menu == "Nhập / Xuất kho":
    st.markdown(title_html(
        "transactions",
        "GIAO DỊCH NHẬP / XUẤT KHO",
        "Ghi nhận nhật ký nhập xuất hàng hóa thủ công hoặc tải lên hàng loạt từ tệp Excel"
    ), unsafe_allow_html=True)
    
    if df_sp.empty:
        st.info("Chưa có sản phẩm nào trong danh mục. Vui lòng thêm sản phẩm trước.")
    else:
        col_form, col_recent = st.columns([1, 1])
        
        with col_form:
            st.markdown('<div class="panel-container">', unsafe_allow_html=True)
            sub_tab_manual_tx, sub_tab_excel_tx = st.tabs(["Ghi nhận thủ công", "Nhập giao dịch từ Excel"])
            
            with sub_tab_manual_tx:
                with st.form("form_transaction_entry"):
                    sp_choices = [f"{row['ma_sp']} - {row['ten_sp']} ({row['don_vi_tinh']})" for _, row in df_sp.iterrows()]
                    selected_sp_choice = st.selectbox("Chọn sản phẩm*", sp_choices)
                    selected_ma_sp = selected_sp_choice.split(" - ")[0]
                    selected_sp_data = df_sp[df_sp['ma_sp'] == selected_ma_sp].iloc[0]
                    selected_ma_kho = str(selected_sp_data.get('ma_kho', '') if pd.notna(selected_sp_data.get('ma_kho', '')) else '')
                    st.caption(f"Mã kho: {selected_ma_kho or 'Chưa khai báo'}")
                    
                    tx_type = st.radio("Loại giao dịch*", ["Nhập kho (Nhập hàng về)", "Xuất kho (Xuất kho sử dụng)"], horizontal=True)
                    loai_val = "nhap" if "Nhập" in tx_type else "xuat"
                    
                    so_luong = st.number_input("Số lượng*", min_value=1, step=1, value=1)
                    ghi_chu_tx = st.text_input("Ghi chú", value="")
                    
                    submit_tx = st.form_submit_button("Ghi nhận giao dịch")
                    
                    if submit_tx:
                        try:
                            # Thực hiện ghi giao dịch
                            logic.record_transaction(selected_ma_sp, loai_val, so_luong, ghi_chu_tx)
                            st.success("🎉 Giao dịch đã được ghi nhận thành công!")
                            
                            # Cảnh báo động (st.toast) nếu sau khi xuất kho, sản phẩm hụt tồn dưới mức tối thiểu
                            if loai_val == 'xuat':
                                df_sp_new, df_gd_new = db.load_data()
                                df_sum_new = logic.get_inventory_summary(df_sp_new, df_gd_new)
                                p_info = df_sum_new[df_sum_new['ma_sp'] == selected_ma_sp].iloc[0]
                                
                                if p_info['ton_hien_tai'] < p_info['ton_toi_thieu']:
                                    st.toast(f"⚠️ CẢNH BÁO: Tồn kho '{p_info['ten_sp']}' đã xuống dưới mức tối thiểu ({p_info['ton_hien_tai']}/{p_info['ton_toi_thieu']})!", icon="🚨")
                                    
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Không thể thực hiện giao dịch: {str(e)}")
                            
            with sub_tab_excel_tx:
                st.write("File Excel nhập/xuất kho cần Mã sản phẩm và Số lượng. Có thể thêm Mã kho, Ghi chú, Ngày giờ. Nếu điền Mã kho thì phải khớp với mã kho trong danh mục sản phẩm.")
                tx_excel_type = st.radio(
                    "Loại giao dịch áp dụng cho file*",
                    ["Nhập kho", "Xuất kho"],
                    horizontal=True,
                    key="tx_excel_type"
                )
                tx_excel_loai = "nhap" if tx_excel_type == "Nhập kho" else "xuat"
                
                # Sinh và cho tải file mẫu giao dịch
                tx_template_bytes = logic.generate_transaction_template_excel()
                st.download_button(
                    label="Tải file Excel mẫu giao dịch (.xlsx)",
                    data=tx_template_bytes,
                    file_name="mau_nhap_giao_dich.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_tx_template_btn"
                )
                
                st.markdown("---")
                # Tải tệp lên
                uploaded_tx_file = st.file_uploader("Chọn file Excel giao dịch*", type=["xlsx", "xls"], key="tx_excel_uploader")
                if uploaded_tx_file is not None:
                    if st.button("Tiến hành nhập giao dịch", key="btn_import_tx_excel"):
                        try:
                            file_bytes = uploaded_tx_file.read()
                            added, errs = logic.import_transactions_from_excel(file_bytes, tx_excel_loai)
                            if added > 0:
                                st.success(f"🎉 Đã thêm thành công {added} giao dịch mới từ file Excel!")
                                df_sp_new, df_gd_new = db.load_data()
                                df_sum_new = logic.get_inventory_summary(df_sp_new, df_gd_new)
                                low_items = df_sum_new[df_sum_new['ton_hien_tai'] < df_sum_new['ton_toi_thieu']]
                                if not low_items.empty:
                                    st.toast(f"⚠️ Phát hiện {len(low_items)} sản phẩm dưới mức tồn tối thiểu sau khi import!", icon="🚨")
                                st.rerun()
                            if errs:
                                st.error("❌ Phát hiện lỗi trên các dòng sau (giao dịch không được ghi nhận):")
                                for err in errs:
                                    st.write(f"- {err}")
                        except Exception as e:
                            st.error(f"❌ Lỗi xử lý: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_recent:
            st.markdown('<div class="panel-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">{icon_html("history", "section-icon")}<span>10 Giao dịch gần nhất</span></div>', unsafe_allow_html=True)
            if df_gd.empty:
                st.info("Chưa có giao dịch nào được ghi nhận.")
            else:
                df_gd_sorted = df_gd.sort_values(by='ngay_gio', ascending=False).head(10).copy()
                df_history = df_gd_sorted.merge(df_sp[['ma_sp', 'ten_sp', 'don_vi_tinh']], on='ma_sp', how='left')
                df_history['loai'] = df_history['loai'].map({'nhap': 'Nhập kho', 'xuat': 'Xuất kho'})
                df_history['ngay_gio'] = df_history['ngay_gio'].dt.strftime('%H:%M:%S %d/%m/%Y')
                history_cols = ['ngay_gio', 'ma_sp', 'ten_sp', 'loai', 'so_luong', 'don_vi_tinh']
                history_rename = {
                    'ngay_gio': 'Thời điểm',
                    'ma_sp': 'Mã SP',
                    'ten_sp': 'Tên sản phẩm',
                    'loai': 'Loại',
                    'so_luong': 'Số lượng',
                    'don_vi_tinh': 'Đơn vị',
                    'ma_kho': 'Mã kho',
                    'ghi_chu': 'Ghi chú'
                }
                for optional_col in ['ma_kho', 'ghi_chu']:
                    if optional_col in df_history.columns:
                        history_cols.append(optional_col)
                df_history = df_history[history_cols].rename(columns=history_rename)
                st.dataframe(df_history, use_container_width=True, height=350)
            st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TRANG 4: DANH MỤC SẢN PHẨM
# ==========================================
elif selected_menu == "Danh mục Sản phẩm":
    st.markdown(title_html(
        "products",
        "QUẢN LÝ DANH MỤC SẢN PHẨM",
        "Khai báo mặt hàng mới, tự sinh mã sản phẩm và quản lý thông tin nền của danh mục hàng hóa"
    ), unsafe_allow_html=True)
    
    col_left_sp, col_right_sp = st.columns([1, 1])
    
    # Thêm sản phẩm mới
    with col_left_sp:
        st.markdown('<div class="panel-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{icon_html("add", "section-icon")}<span>Thêm sản phẩm</span></div>', unsafe_allow_html=True)
        sub_tab_manual, sub_tab_excel = st.tabs(["Thêm thủ công", "Nhập từ file Excel"])
        
        with sub_tab_manual:
            with st.form("form_add_new_product", clear_on_submit=True):
                st.caption("Mã sản phẩm sẽ tự sinh theo format SP + số thứ tự tăng dần, ví dụ SP005.")
                new_ten = st.text_input("Tên sản phẩm*")
                new_dvt = st.text_input("Đơn vị tính*")
                new_min = st.number_input("Mức tồn tối thiểu*", min_value=0, step=1, value=5)
                new_nhom = st.text_input("Nhóm hàng", value="Văn phòng phẩm")
                new_ma_kho = st.text_input("Mã kho", value="")
                
                submit_add = st.form_submit_button("Thêm sản phẩm")
                
                if submit_add:
                    try:
                        created_ma = logic.add_product(new_ten, new_dvt, new_min, new_nhom, new_ma_kho)
                        st.success(f"🎉 Đã thêm thành công sản phẩm '{new_ten}' với mã {created_ma}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
                        
        with sub_tab_excel:
            st.write("File sản phẩm không cần mã. Hệ thống tự sinh mã theo format SP### và sẽ báo lỗi nếu tên sản phẩm bị trùng.")
            
            # Sinh và cho tải file mẫu sản phẩm
            template_bytes = logic.generate_template_excel()
            st.download_button(
                label="Tải file Excel mẫu sản phẩm (.xlsx)",
                data=template_bytes,
                file_name="mau_nhap_san_pham.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_template_btn"
            )
            
            st.markdown("---")
            # Tải tệp lên
            uploaded_file = st.file_uploader("Chọn file Excel danh sách sản phẩm*", type=["xlsx", "xls"], key="excel_uploader")
            if uploaded_file is not None:
                if st.button("Tiến hành nhập dữ liệu", key="btn_import_excel"):
                    try:
                        file_bytes = uploaded_file.read()
                        added, skipped = logic.import_products_from_excel(file_bytes)
                        if added > 0:
                            st.success(f"🎉 Đã thêm thành công {added} sản phẩm mới từ file Excel!")
                            st.rerun()
                        if skipped:
                            st.error("❌ Phát hiện lỗi trong file sản phẩm, dữ liệu chưa được nhập:")
                            for err in skipped:
                                st.write(f"- {err}")
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Chỉnh sửa sản phẩm hiện có
    with col_right_sp:
        st.markdown('<div class="panel-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{icon_html("products", "section-icon")}<span>Chỉnh sửa / Xóa sản phẩm</span></div>', unsafe_allow_html=True)
        if df_sp.empty:
            st.info("Chưa có sản phẩm nào để chỉnh sửa hoặc xóa.")
        else:
            sp_edit_choices = [f"{row['ma_sp']} - {row['ten_sp']}" for _, row in df_sp.iterrows()]
            selected_edit_choice = st.selectbox("Chọn sản phẩm cần xử lý*", sp_edit_choices)
            selected_edit_ma = selected_edit_choice.split(" - ")[0]
            
            sp_data = df_sp[df_sp['ma_sp'] == selected_edit_ma].iloc[0]
            
            with st.form("form_edit_product"):
                st.text_input("Mã sản phẩm (Không thể chỉnh sửa)", value=sp_data['ma_sp'], disabled=True)
                edit_ten = st.text_input("Tên sản phẩm*", value=sp_data['ten_sp'])
                edit_dvt = st.text_input("Đơn vị tính*", value=sp_data['don_vi_tinh'])
                edit_min = st.number_input("Mức tồn tối thiểu*", min_value=0, step=1, value=int(sp_data['ton_toi_thieu']))
                edit_nhom = st.text_input("Nhóm hàng", value=str(sp_data.get('nhom_hang', 'Văn phòng phẩm')))
                edit_ma_kho = st.text_input("Mã kho", value=str(sp_data.get('ma_kho', '') if pd.notna(sp_data.get('ma_kho', '')) else ''))
                
                col_btn_edit, col_btn_del = st.columns(2)
                with col_btn_edit:
                    submit_update = st.form_submit_button("Cập nhật thông tin")
                with col_btn_del:
                    st.markdown('<div class="delete-btn-container">', unsafe_allow_html=True)
                    submit_delete = st.form_submit_button("Xóa sản phẩm này")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                confirm_del = st.checkbox("Xác nhận xóa (Thao tác này cũng sẽ xóa sạch các giao dịch liên quan)", value=False)
                
                if submit_update:
                    try:
                        logic.update_product(selected_edit_ma, edit_ten, edit_dvt, edit_min, edit_nhom, edit_ma_kho)
                        st.success(f"🎉 Đã cập nhật sản phẩm '{edit_ten}' thành công!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
                        
                if submit_delete:
                    if not confirm_del:
                        st.error("⚠️ Bạn phải tích chọn ô 'Xác nhận xóa' ở trên để tiến hành xóa sản phẩm.")
                    else:
                        try:
                            logic.delete_product(selected_edit_ma)
                            st.success(f"🗑️ Đã xóa sản phẩm {selected_edit_ma} và các dữ liệu liên quan thành công!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Lỗi: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Danh sách toàn bộ sản phẩm hiện có
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{icon_html("app", "section-icon")}<span>Danh sách Sản phẩm Hiện có</span></div>', unsafe_allow_html=True)
    if df_sp.empty:
        st.caption("Chưa có sản phẩm nào.")
    else:
        display_columns = ['ma_sp', 'ten_sp', 'don_vi_tinh', 'ton_toi_thieu', 'nhom_hang']
        if 'ma_kho' in df_sp.columns:
            display_columns.append('ma_kho')

        df_sp_display = df_sp[[col for col in display_columns if col in df_sp.columns]].copy()
        df_sp_display = df_sp_display.rename(columns={
            'ma_sp': 'Mã sản phẩm',
            'ten_sp': 'Tên sản phẩm',
            'don_vi_tinh': 'Đơn vị tính',
            'ton_toi_thieu': 'Tồn tối thiểu',
            'nhom_hang': 'Nhóm hàng',
            'ma_kho': 'Mã kho'
        })
        st.dataframe(df_sp_display, use_container_width=True, height=250)
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TRANG 5: NHẬT KÝ GIAO DỊCH
# ==========================================
elif selected_menu == "Nhật ký Giao dịch":
    st.markdown(title_html(
        "history",
        "NHẬT KÝ GIAO DỊCH CHI TIẾT",
        "Tra cứu mọi lịch sử nhập xuất, hỗ trợ lọc thông minh và phân trang tối ưu"
    ), unsafe_allow_html=True)
    
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    if df_gd.empty:
        st.info("Chưa có giao dịch nào được ghi nhận.")
    else:
        # Bộ lọc tìm kiếm & đối soát lịch sử
        col_h_filter1, col_h_filter2, col_h_filter3 = st.columns([1.5, 1.5, 1])
        with col_h_filter1:
            sp_hist_options = ["Tất cả"] + [f"{row['ma_sp']} - {row['ten_sp']}" for _, row in df_sp.iterrows()]
            selected_sp_hist = st.selectbox("Lọc theo sản phẩm:", sp_hist_options, key="hist_sp_filter")
        with col_h_filter2:
            min_date = df_gd['ngay_gio'].min().date()
            max_date = df_gd['ngay_gio'].max().date()
            if min_date == max_date:
                date_range_selection = st.date_input("Lọc theo ngày:", value=min_date, key="hist_date_filter")
            else:
                date_range_selection = st.date_input("Lọc theo khoảng thời gian:", value=(min_date, max_date), key="hist_date_filter")
        with col_h_filter3:
            selected_type_hist = st.selectbox("Lọc theo loại giao dịch:", ["Tất cả", "Nhập kho", "Xuất kho"], key="hist_type_filter")
            
        # Áp dụng các bộ lọc
        df_h_filtered = df_gd.copy()
        
        if selected_sp_hist != "Tất cả":
            ma_hist_filter = selected_sp_hist.split(" - ")[0]
            df_h_filtered = df_h_filtered[df_h_filtered['ma_sp'] == ma_hist_filter]
            
        if isinstance(date_range_selection, tuple) and len(date_range_selection) == 2:
            start_date, end_date = date_range_selection
            start_dt = datetime.datetime.combine(start_date, datetime.time.min)
            end_dt = datetime.datetime.combine(end_date, datetime.time.max)
            df_h_filtered = df_h_filtered[(df_h_filtered['ngay_gio'] >= start_dt) & (df_h_filtered['ngay_gio'] <= end_dt)]
        elif isinstance(date_range_selection, datetime.date):
            start_dt = datetime.datetime.combine(date_range_selection, datetime.time.min)
            end_dt = datetime.datetime.combine(date_range_selection, datetime.time.max)
            df_h_filtered = df_h_filtered[(df_h_filtered['ngay_gio'] >= start_dt) & (df_h_filtered['ngay_gio'] <= end_dt)]
            
        if selected_type_hist != "Tất cả":
            type_val = "nhap" if selected_type_hist == "Nhập kho" else "xuat"
            df_h_filtered = df_h_filtered[df_h_filtered['loai'] == type_val]
            
        if df_h_filtered.empty:
            st.info("Không tìm thấy giao dịch nào phù hợp với bộ lọc.")
        else:
            df_h_display = df_h_filtered.merge(df_sp[['ma_sp', 'ten_sp', 'don_vi_tinh']], on='ma_sp', how='left')
            df_h_display = df_h_display.sort_values(by='ngay_gio', ascending=False)
            
            df_h_display['loai'] = df_h_display['loai'].map({'nhap': 'Nhập kho', 'xuat': 'Xuất kho'})
            df_h_display['ngay_gio'] = df_h_display['ngay_gio'].dt.strftime('%H:%M:%S %d/%m/%Y')
            history_detail_cols = ['ngay_gio', 'ma_sp', 'ten_sp', 'loai', 'so_luong', 'don_vi_tinh']
            history_detail_rename = {
                'ngay_gio': 'Thời điểm giao dịch',
                'ma_sp': 'Mã sản phẩm',
                'ten_sp': 'Tên sản phẩm',
                'loai': 'Loại giao dịch',
                'so_luong': 'Số lượng',
                'don_vi_tinh': 'Đơn vị tính',
                'ma_kho': 'Mã kho',
                'ghi_chu': 'Ghi chú'
            }
            for optional_col in ['ma_kho', 'ghi_chu']:
                if optional_col in df_h_display.columns:
                    history_detail_cols.append(optional_col)
            df_h_display = df_h_display[history_detail_cols].rename(columns=history_detail_rename)
            
            # Phân trang (Pagination)
            rows_per_page = 10
            total_records = len(df_h_display)
            total_pages = max(1, (total_records - 1) // rows_per_page + 1)
            
            if 'hist_page_num' not in st.session_state:
                st.session_state.hist_page_num = 1
                
            if st.session_state.hist_page_num > total_pages:
                st.session_state.hist_page_num = total_pages
                
            col_page_prev, col_page_text, col_page_next = st.columns([1, 2, 1])
            with col_page_prev:
                if st.button("⮜ Trang trước", disabled=(st.session_state.hist_page_num == 1), key="btn_prev_page"):
                    st.session_state.hist_page_num -= 1
                    st.rerun()
            with col_page_text:
                st.markdown(f"<div style='text-align: center; line-height: 2.4rem; font-weight: bold;'>Trang {st.session_state.hist_page_num} / {total_pages} (Tổng số {total_records} giao dịch)</div>", unsafe_allow_html=True)
            with col_page_next:
                if st.button("Trang sau ⮞", disabled=(st.session_state.hist_page_num == total_pages), key="btn_next_page"):
                    st.session_state.hist_page_num += 1
                    st.rerun()
                    
            start_row = (st.session_state.hist_page_num - 1) * rows_per_page
            end_row = start_row + rows_per_page
            
            st.dataframe(df_h_display.iloc[start_row:end_row], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# TRANG 6: XUẤT BẢN BÁO CÁO
# ==========================================
elif selected_menu == "Xuất Bản Báo cáo":
    st.markdown(title_html(
        "reports",
        "XUẤT BẢN BÁO CÁO KHO",
        "Kết xuất dữ liệu tồn kho hiện tại ra tệp Excel (.xlsx) hoặc tệp PDF chuyên nghiệp (.pdf)"
    ), unsafe_allow_html=True)
    
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    if df_sp.empty:
        st.info("Chưa có dữ liệu sản phẩm để xuất báo cáo.")
    else:
        df_rep = df_summary[['ma_sp', 'ten_sp', 'nhom_hang', 'ton_hien_tai', 'ton_toi_thieu', 'trang_thai']].copy()
        df_rep.columns = ['Mã sản phẩm', 'Tên sản phẩm', 'Nhóm hàng', 'Tồn hiện tại', 'Tồn tối thiểu', 'Trạng thái']
        
        st.markdown("#### Xem trước dữ liệu báo cáo:")
        st.dataframe(df_rep, use_container_width=True)
        
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_excel_filename = f"bao_cao_ton_kho_{now_str}.xlsx"
        report_signature = pd.util.hash_pandas_object(df_summary.fillna(""), index=True).sum()
        if st.session_state.get("report_pdf_signature") != report_signature:
            st.session_state.pop("report_pdf_bytes", None)
            st.session_state.pop("report_pdf_filename", None)
            st.session_state.report_pdf_signature = report_signature
        
        st.markdown("---")
        st.write("Nhấp vào nút bên dưới để tải tệp tương ứng:")
        
        col_down_excel, col_down_pdf = st.columns(2)
        
        # 1. Nút tải Excel
        with col_down_excel:
            excel_buffer = io.BytesIO()
            try:
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_rep.to_excel(writer, sheet_name='Báo cáo tồn kho', index=False)
                excel_bytes = excel_buffer.getvalue()
                
                st.download_button(
                    label="📥 Tải file Excel Báo cáo (.xlsx)",
                    data=excel_bytes,
                    file_name=report_excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="btn_download_excel"
                )
            except Exception as e:
                st.error(f"Lỗi chuẩn bị Excel: {str(e)}")
                
        # 2. Nút tải PDF
        with col_down_pdf:
            if st.button("Tạo file PDF Báo cáo (.pdf)", key="btn_prepare_pdf"):
                try:
                    with st.spinner("Đang tạo file PDF..."):
                        st.session_state.report_pdf_bytes = logic.generate_report_pdf(df_summary)
                        st.session_state.report_pdf_filename = f"bao_cao_ton_kho_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                except Exception as e:
                    st.error(f"Lỗi chuẩn bị PDF: {str(e)}")

            if st.session_state.get("report_pdf_bytes"):
                st.download_button(
                    label="📥 Tải file PDF Báo cáo (.pdf)",
                    data=st.session_state.report_pdf_bytes,
                    file_name=st.session_state.report_pdf_filename,
                    mime="application/pdf",
                    key="btn_download_pdf"
                )
            else:
                st.caption("PDF sẽ được tạo khi bạn bấm nút phía trên.")
    st.markdown('</div>', unsafe_allow_html=True)
