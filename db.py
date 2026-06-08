# -*- coding: utf-8 -*-
"""
Module truy cập dữ liệu cho Hệ thống quản lý tồn kho.
Dữ liệu chính được lưu trong SQLite; Excel chỉ dùng cho import/export.
"""

import datetime
import sqlite3

import pandas as pd

DB_FILE = "inventory.db"

PRODUCT_COLUMNS = ["ma_sp", "ten_sp", "don_vi_tinh", "ton_toi_thieu", "nhom_hang", "ma_kho"]
TRANSACTION_COLUMNS = ["ma_sp", "loai", "so_luong", "ngay_gio", "ma_kho", "ghi_chu"]

SAMPLE_PRODUCTS = [
    {"ma_sp": "SP001", "ten_sp": "Bút bi Thiên Long", "don_vi_tinh": "Cái", "ton_toi_thieu": 20, "nhom_hang": "Văn phòng phẩm", "ma_kho": "KHO-01"},
    {"ma_sp": "SP002", "ten_sp": "Giấy A4 Double A", "don_vi_tinh": "Ram", "ton_toi_thieu": 10, "nhom_hang": "Văn phòng phẩm", "ma_kho": "KHO-01"},
    {"ma_sp": "SP003", "ten_sp": "Băng keo trong", "don_vi_tinh": "Cuộn", "ton_toi_thieu": 15, "nhom_hang": "Vật tư đóng gói", "ma_kho": "KHO-02"},
    {"ma_sp": "SP004", "ten_sp": "Sổ lò xo A5", "don_vi_tinh": "Cuốn", "ton_toi_thieu": 12, "nhom_hang": "Văn phòng phẩm", "ma_kho": "KHO-01"},
    {"ma_sp": "SP005", "ten_sp": "Thùng carton 40x30x30", "don_vi_tinh": "Cái", "ton_toi_thieu": 30, "nhom_hang": "Vật tư đóng gói", "ma_kho": "KHO-02"},
    {"ma_sp": "SP006", "ten_sp": "Màng PE quấn pallet", "don_vi_tinh": "Cuộn", "ton_toi_thieu": 8, "nhom_hang": "Vật tư đóng gói", "ma_kho": "KHO-02"},
    {"ma_sp": "SP007", "ten_sp": "Tem mã vạch", "don_vi_tinh": "Cuộn", "ton_toi_thieu": 20, "nhom_hang": "Vật tư kho", "ma_kho": "KHO-03"},
    {"ma_sp": "SP008", "ten_sp": "Pin AA Panasonic", "don_vi_tinh": "Vỉ", "ton_toi_thieu": 15, "nhom_hang": "Thiết bị văn phòng", "ma_kho": "KHO-03"},
]

SAMPLE_TRANSACTIONS = [
    {"ma_sp": "SP001", "loai": "nhap", "so_luong": 120, "ngay_gio": datetime.datetime(2026, 6, 1, 8, 0, 0), "ma_kho": "KHO-01", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP002", "loai": "nhap", "so_luong": 40, "ngay_gio": datetime.datetime(2026, 6, 1, 8, 15, 0), "ma_kho": "KHO-01", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP003", "loai": "nhap", "so_luong": 60, "ngay_gio": datetime.datetime(2026, 6, 1, 8, 30, 0), "ma_kho": "KHO-02", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP004", "loai": "nhap", "so_luong": 45, "ngay_gio": datetime.datetime(2026, 6, 1, 8, 45, 0), "ma_kho": "KHO-01", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP005", "loai": "nhap", "so_luong": 100, "ngay_gio": datetime.datetime(2026, 6, 1, 9, 0, 0), "ma_kho": "KHO-02", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP006", "loai": "nhap", "so_luong": 20, "ngay_gio": datetime.datetime(2026, 6, 1, 9, 15, 0), "ma_kho": "KHO-02", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP007", "loai": "nhap", "so_luong": 60, "ngay_gio": datetime.datetime(2026, 6, 1, 9, 30, 0), "ma_kho": "KHO-03", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP008", "loai": "nhap", "so_luong": 35, "ngay_gio": datetime.datetime(2026, 6, 1, 9, 45, 0), "ma_kho": "KHO-03", "ghi_chu": "Tồn đầu kỳ"},
    {"ma_sp": "SP001", "loai": "xuat", "so_luong": 35, "ngay_gio": datetime.datetime(2026, 6, 3, 10, 0, 0), "ma_kho": "KHO-01", "ghi_chu": "Cấp phát văn phòng"},
    {"ma_sp": "SP002", "loai": "xuat", "so_luong": 31, "ngay_gio": datetime.datetime(2026, 6, 3, 10, 30, 0), "ma_kho": "KHO-01", "ghi_chu": "Cấp phát phòng kế toán"},
    {"ma_sp": "SP003", "loai": "xuat", "so_luong": 30, "ngay_gio": datetime.datetime(2026, 6, 4, 14, 0, 0), "ma_kho": "KHO-02", "ghi_chu": "Đóng gói đơn hàng"},
    {"ma_sp": "SP004", "loai": "xuat", "so_luong": 20, "ngay_gio": datetime.datetime(2026, 6, 4, 14, 30, 0), "ma_kho": "KHO-01", "ghi_chu": "Cấp phát nội bộ"},
    {"ma_sp": "SP005", "loai": "xuat", "so_luong": 75, "ngay_gio": datetime.datetime(2026, 6, 5, 9, 20, 0), "ma_kho": "KHO-02", "ghi_chu": "Đóng gói pallet"},
    {"ma_sp": "SP006", "loai": "xuat", "so_luong": 15, "ngay_gio": datetime.datetime(2026, 6, 5, 9, 45, 0), "ma_kho": "KHO-02", "ghi_chu": "Quấn pallet xuất kho"},
    {"ma_sp": "SP007", "loai": "xuat", "so_luong": 25, "ngay_gio": datetime.datetime(2026, 6, 6, 11, 0, 0), "ma_kho": "KHO-03", "ghi_chu": "Dán nhãn lô hàng"},
    {"ma_sp": "SP008", "loai": "xuat", "so_luong": 22, "ngay_gio": datetime.datetime(2026, 6, 6, 11, 30, 0), "ma_kho": "KHO-03", "ghi_chu": "Cấp phát thiết bị"},
    {"ma_sp": "SP001", "loai": "xuat", "so_luong": 10, "ngay_gio": datetime.datetime(2026, 6, 8, 8, 20, 0), "ma_kho": "KHO-01", "ghi_chu": "Giao dịch hôm nay"},
    {"ma_sp": "SP002", "loai": "xuat", "so_luong": 5, "ngay_gio": datetime.datetime(2026, 6, 8, 9, 10, 0), "ma_kho": "KHO-01", "ghi_chu": "Giao dịch hôm nay"},
    {"ma_sp": "SP004", "loai": "nhap", "so_luong": 10, "ngay_gio": datetime.datetime(2026, 6, 8, 10, 0, 0), "ma_kho": "KHO-01", "ghi_chu": "Bổ sung trong ngày"},
    {"ma_sp": "SP005", "loai": "xuat", "so_luong": 5, "ngay_gio": datetime.datetime(2026, 6, 8, 11, 15, 0), "ma_kho": "KHO-02", "ghi_chu": "Giao dịch hôm nay"},
]


def _connect():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _format_datetime(value):
    if pd.isna(value):
        return datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, datetime.datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return pd.to_datetime(value).to_pydatetime().isoformat(sep=" ", timespec="seconds")


def _table_columns(conn, table_name):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}


def _ensure_column(conn, table_name, column_name, definition):
    if column_name not in _table_columns(conn, table_name):
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def _drop_column_if_exists(conn, table_name, column_name):
    if column_name not in _table_columns(conn, table_name):
        return

    try:
        conn.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
    except sqlite3.OperationalError:
        # Older SQLite versions cannot drop columns. The app still ignores legacy columns.
        pass


def _migrate_legacy_location(conn):
    product_cols = _table_columns(conn, "san_pham")
    if "vi_tri" in product_cols and "ma_kho" in product_cols:
        conn.execute(
            """
            UPDATE san_pham
            SET ma_kho = vi_tri
            WHERE COALESCE(ma_kho, '') = '' AND COALESCE(vi_tri, '') != ''
            """
        )

    transaction_cols = _table_columns(conn, "giao_dich")
    if "vi_tri" in transaction_cols and "ma_kho" in transaction_cols:
        conn.execute(
            """
            UPDATE giao_dich
            SET ma_kho = vi_tri
            WHERE COALESCE(ma_kho, '') = '' AND COALESCE(vi_tri, '') != ''
            """
        )


def init_db():
    """Tự động khởi tạo SQLite database và dữ liệu mẫu nếu chưa có dữ liệu."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS san_pham (
                ma_sp TEXT PRIMARY KEY,
                ten_sp TEXT NOT NULL UNIQUE,
                don_vi_tinh TEXT NOT NULL,
                ton_toi_thieu INTEGER NOT NULL DEFAULT 5,
                nhom_hang TEXT NOT NULL DEFAULT 'Chưa phân loại',
                ma_kho TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS giao_dich (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_sp TEXT NOT NULL,
                loai TEXT NOT NULL CHECK (loai IN ('nhap', 'xuat')),
                so_luong INTEGER NOT NULL CHECK (so_luong > 0),
                ngay_gio TEXT NOT NULL,
                ma_kho TEXT NOT NULL DEFAULT '',
                ghi_chu TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (ma_sp) REFERENCES san_pham(ma_sp) ON DELETE CASCADE
            )
            """
        )
        _ensure_column(conn, "san_pham", "ma_kho", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "giao_dich", "ma_kho", "TEXT NOT NULL DEFAULT ''")
        _migrate_legacy_location(conn)
        _drop_column_if_exists(conn, "san_pham", "vi_tri")
        _drop_column_if_exists(conn, "giao_dich", "vi_tri")

        product_count = conn.execute("SELECT COUNT(*) FROM san_pham").fetchone()[0]
        if product_count == 0:
            _replace_all(conn, pd.DataFrame(SAMPLE_PRODUCTS), pd.DataFrame(SAMPLE_TRANSACTIONS))


def load_data():
    """Đọc dữ liệu từ SQLite và trả về hai DataFrame: sản phẩm, giao dịch."""
    init_db()
    with _connect() as conn:
        df_sp = pd.read_sql_query(
            "SELECT ma_sp, ten_sp, don_vi_tinh, ton_toi_thieu, nhom_hang, ma_kho FROM san_pham ORDER BY ma_sp",
            conn,
        )
        df_gd = pd.read_sql_query(
            "SELECT ma_sp, loai, so_luong, ngay_gio, ma_kho, ghi_chu FROM giao_dich ORDER BY ngay_gio",
            conn,
        )

    return _normalize_products(df_sp), _normalize_transactions(df_gd)


def save_data(df_sp, df_gd):
    """
    Ghi toàn bộ DataFrame vào SQLite.
    Hàm này giữ interface cũ để các lớp nghiệp vụ hiện tại không phải đổi.
    """
    init_db()
    df_sp = _normalize_products(df_sp)
    df_gd = _normalize_transactions(df_gd)

    try:
        with _connect() as conn:
            _replace_all(conn, df_sp, df_gd)
    except sqlite3.Error as e:
        raise Exception(f"Lỗi ghi dữ liệu SQLite: {str(e)}")


def reset_sample_data():
    """Ghi lại toàn bộ dữ liệu mẫu vào SQLite."""
    save_data(pd.DataFrame(SAMPLE_PRODUCTS), pd.DataFrame(SAMPLE_TRANSACTIONS))


def _replace_all(conn, df_sp, df_gd):
    df_sp = _normalize_products(df_sp)
    df_gd = _normalize_transactions(df_gd)

    conn.execute("DELETE FROM giao_dich")
    conn.execute("DELETE FROM san_pham")

    product_rows = [
        (
            row["ma_sp"],
            row["ten_sp"],
            row["don_vi_tinh"],
            int(row["ton_toi_thieu"]),
            row["nhom_hang"],
            row["ma_kho"],
        )
        for _, row in df_sp.iterrows()
    ]
    conn.executemany(
        """
        INSERT INTO san_pham (ma_sp, ten_sp, don_vi_tinh, ton_toi_thieu, nhom_hang, ma_kho)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        product_rows,
    )

    transaction_rows = [
        (
            row["ma_sp"],
            row["loai"],
            int(row["so_luong"]),
            _format_datetime(row["ngay_gio"]),
            row["ma_kho"],
            row["ghi_chu"],
        )
        for _, row in df_gd.iterrows()
    ]
    conn.executemany(
        """
        INSERT INTO giao_dich (ma_sp, loai, so_luong, ngay_gio, ma_kho, ghi_chu)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        transaction_rows,
    )


def _normalize_products(df_sp):
    df_sp = df_sp.copy()
    if "ma_kho" not in df_sp.columns and "vi_tri" in df_sp.columns:
        df_sp["ma_kho"] = df_sp["vi_tri"]

    for col in PRODUCT_COLUMNS:
        if col not in df_sp.columns:
            if col == "ton_toi_thieu":
                df_sp[col] = 5
            elif col == "nhom_hang":
                df_sp[col] = "Chưa phân loại"
            else:
                df_sp[col] = ""

    df_sp = df_sp[PRODUCT_COLUMNS]
    df_sp["ma_sp"] = df_sp["ma_sp"].astype(str).str.strip()
    df_sp["ten_sp"] = df_sp["ten_sp"].astype(str).str.strip()
    df_sp["don_vi_tinh"] = df_sp["don_vi_tinh"].astype(str).str.strip()
    df_sp["ton_toi_thieu"] = pd.to_numeric(df_sp["ton_toi_thieu"], errors="coerce").fillna(5).astype(int)
    df_sp["nhom_hang"] = df_sp["nhom_hang"].fillna("Chưa phân loại").astype(str).str.strip()
    df_sp["ma_kho"] = df_sp["ma_kho"].fillna("").astype(str).str.strip().str.upper()
    return df_sp


def _normalize_transactions(df_gd):
    df_gd = df_gd.copy()
    if "ma_kho" not in df_gd.columns and "vi_tri" in df_gd.columns:
        df_gd["ma_kho"] = df_gd["vi_tri"]

    for col in TRANSACTION_COLUMNS:
        if col not in df_gd.columns:
            if col == "ngay_gio":
                df_gd[col] = datetime.datetime.now()
            elif col == "so_luong":
                df_gd[col] = 0
            else:
                df_gd[col] = ""

    df_gd = df_gd[TRANSACTION_COLUMNS]
    if df_gd.empty:
        df_gd["ngay_gio"] = pd.to_datetime(df_gd["ngay_gio"])
        return df_gd

    df_gd["ma_sp"] = df_gd["ma_sp"].astype(str).str.strip()
    df_gd["loai"] = df_gd["loai"].astype(str).str.strip()
    df_gd["so_luong"] = pd.to_numeric(df_gd["so_luong"], errors="coerce").fillna(0).astype(int)
    df_gd["ngay_gio"] = pd.to_datetime(df_gd["ngay_gio"])
    df_gd["ma_kho"] = df_gd["ma_kho"].fillna("").astype(str).str.strip().str.upper()
    df_gd["ghi_chu"] = df_gd["ghi_chu"].fillna("").astype(str).str.strip()
    return df_gd
