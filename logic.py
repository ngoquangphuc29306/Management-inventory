# -*- coding: utf-8 -*-
"""
Module Nghiệp vụ (Business Logic Layer) cho Hệ thống quản lý tồn kho.
Thực hiện các thao tác xử lý nghiệp vụ sản phẩm, giao dịch và tính toán tồn kho.
"""

import os
import io
import datetime
import unicodedata
import pandas as pd
from fpdf import FPDF
import db


def _normalize_text(value):
    """Chuẩn hóa chuỗi để so khớp tên cột và tên sản phẩm ổn định hơn."""
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("đ", "d")
    return " ".join(text.replace("_", " ").split())


def _generate_next_product_code(existing_codes):
    max_num = 0
    for code in existing_codes:
        code_text = str(code).strip().upper()
        if code_text.startswith("SP") and code_text[2:].isdigit():
            max_num = max(max_num, int(code_text[2:]))

    existing_set = {str(code).strip().upper() for code in existing_codes}
    next_num = max_num + 1
    while True:
        new_code = f"SP{next_num:03d}"
        if new_code not in existing_set:
            return new_code
        next_num += 1


def _standardize_transaction_upload_columns(df_upload):
    column_aliases = {
        'ma_sp': {'ma sp', 'ma san pham', 'sku', 'product code'},
        'so_luong': {'so luong', 'sl', 'quantity'},
        'ma_kho': {'ma kho', 'kho', 'warehouse', 'warehouse code', 'vi tri', 'location', 'bin', 'ke', 'ke hang'},
        'ghi_chu': {'ghi chu', 'note', 'notes'},
        'ngay_gio': {'ngay gio', 'thoi gian', 'ngay', 'datetime', 'date'},
    }

    return _rename_columns_by_alias(df_upload, column_aliases)


def _standardize_product_upload_columns(df_upload):
    column_aliases = {
        'ten_sp': {'ten sp', 'ten san pham', 'san pham', 'ten hang', 'ten mat hang', 'product name'},
        'don_vi_tinh': {'don vi', 'don vi tinh', 'dvt', 'unit'},
        'ton_toi_thieu': {'ton toi thieu', 'muc ton toi thieu', 'minimum stock', 'min stock'},
        'nhom_hang': {'nhom hang', 'loai hang', 'category'},
        'ma_kho': {'ma kho', 'kho', 'warehouse', 'warehouse code', 'vi tri', 'location', 'bin', 'ke', 'ke hang'},
    }

    return _rename_columns_by_alias(df_upload, column_aliases)


def _rename_columns_by_alias(df_upload, column_aliases):
    rename_map = {}
    for col in df_upload.columns:
        normalized_col = _normalize_text(col)
        for standard_col, aliases in column_aliases.items():
            if normalized_col in aliases:
                rename_map[col] = standard_col
                break

    return df_upload.rename(columns=rename_map)

def get_inventory_summary(df_sp, df_gd):
    """
    Tính toán tồn kho hiện tại dựa trên tổng số lượng nhập và xuất của từng sản phẩm.
    Trả về DataFrame tóm tắt gồm: mã, tên, đơn vị tính, tồn tối thiểu, nhóm hàng, tổng nhập, tổng xuất, tồn hiện tại, trạng thái.
    """
    if df_sp.empty:
        return pd.DataFrame(columns=['ma_sp', 'ten_sp', 'don_vi_tinh', 'ton_toi_thieu', 'nhom_hang', 'tong_nhap', 'tong_xuat', 'ton_hien_tai', 'trang_thai'])
    
    # Tính tổng nhập
    df_nhap = df_gd[(df_gd['loai'] == 'nhap') & (df_gd['so_luong'] > 0)]
    sum_nhap = df_nhap.groupby('ma_sp')['so_luong'].sum().reset_index(name='tong_nhap')
    
    # Tính tổng xuất
    df_xuat = df_gd[(df_gd['loai'] == 'xuat') & (df_gd['so_luong'] > 0)]
    sum_xuat = df_xuat.groupby('ma_sp')['so_luong'].sum().reset_index(name='tong_xuat')
    
    # Liên kết dữ liệu sản phẩm với tổng nhập, tổng xuất
    df_summary = df_sp.merge(sum_nhap, on='ma_sp', how='left')
    df_summary = df_summary.merge(sum_xuat, on='ma_sp', how='left')
    
    # Điền giá trị trống bằng 0 và định dạng kiểu số
    df_summary['tong_nhap'] = df_summary['tong_nhap'].fillna(0).astype(int)
    df_summary['tong_xuat'] = df_summary['tong_xuat'].fillna(0).astype(int)
    df_summary['ton_hien_tai'] = df_summary['tong_nhap'] - df_summary['tong_xuat']
    
    # Đánh giá trạng thái tồn kho
    df_summary['trang_thai'] = df_summary.apply(
        lambda r: "Cần nhập hàng" if r['ton_hien_tai'] < r['ton_toi_thieu'] else "Bình thường", 
        axis=1
    )
    
    return df_summary


def add_product(ten_sp, don_vi_tinh, ton_toi_thieu, nhom_hang="Chưa phân loại", ma_kho=""):
    """
    Nghiệp vụ thêm sản phẩm mới.
    Mã sản phẩm được tự sinh theo format SP + số thứ tự tăng dần.
    """
    ten_sp = ten_sp.strip()
    don_vi_tinh = don_vi_tinh.strip()
    nhom_hang = nhom_hang.strip() if nhom_hang else "Chưa phân loại"
    ma_kho = ma_kho.strip().upper() if ma_kho else ""
    
    if not ten_sp or not don_vi_tinh:
        raise ValueError("Vui lòng điền đầy đủ các thông tin bắt buộc (*).")
        
    df_sp, df_gd = db.load_data()

    existing_names = {_normalize_text(name) for name in df_sp['ten_sp'].fillna('').values}
    if _normalize_text(ten_sp) in existing_names:
        raise ValueError(f"Tên sản phẩm '{ten_sp}' đã tồn tại trong danh mục.")

    ma_sp = _generate_next_product_code(df_sp['ma_sp'].values)
        
    new_sp = {
        "ma_sp": ma_sp,
        "ten_sp": ten_sp,
        "don_vi_tinh": don_vi_tinh,
        "ton_toi_thieu": ton_toi_thieu,
        "nhom_hang": nhom_hang
    }

    new_sp["ma_kho"] = ma_kho
    
    df_sp = pd.concat([df_sp, pd.DataFrame([new_sp])], ignore_index=True)
    db.save_data(df_sp, df_gd)
    return ma_sp


def update_product(ma_sp, ten_sp, don_vi_tinh, ton_toi_thieu, nhom_hang="Chưa phân loại", ma_kho=None):
    """
    Cập nhật thông tin sản phẩm (Tên, đơn vị tính, tồn tối thiểu, nhóm hàng).
    Mã sản phẩm (ma_sp) là khóa chính, không thay đổi.
    """
    ma_sp = ma_sp.strip()
    ten_sp = ten_sp.strip()
    don_vi_tinh = don_vi_tinh.strip()
    nhom_hang = nhom_hang.strip() if nhom_hang else "Chưa phân loại"
    ma_kho = ma_kho.strip().upper() if ma_kho is not None else None
    
    if not ten_sp or not don_vi_tinh:
        raise ValueError("Tên sản phẩm và Đơn vị tính không được để trống.")
        
    df_sp, df_gd = db.load_data()
    
    if ma_sp not in df_sp['ma_sp'].values:
        raise ValueError(f"Mã sản phẩm '{ma_sp}' không tồn tại.")

    normalized_new_name = _normalize_text(ten_sp)
    duplicate_name = df_sp[
        (df_sp['ma_sp'] != ma_sp) &
        (df_sp['ten_sp'].fillna('').apply(_normalize_text) == normalized_new_name)
    ]
    if not duplicate_name.empty:
        raise ValueError(f"Tên sản phẩm '{ten_sp}' đã tồn tại trong danh mục.")
        
    idx = df_sp[df_sp['ma_sp'] == ma_sp].index[0]
    df_sp.loc[idx, 'ten_sp'] = ten_sp
    df_sp.loc[idx, 'don_vi_tinh'] = don_vi_tinh
    df_sp.loc[idx, 'ton_toi_thieu'] = ton_toi_thieu
    df_sp.loc[idx, 'nhom_hang'] = nhom_hang
    if ma_kho is not None:
        if 'ma_kho' not in df_sp.columns:
            df_sp['ma_kho'] = ''
        df_sp.loc[idx, 'ma_kho'] = ma_kho
    
    db.save_data(df_sp, df_gd)


def delete_product(ma_sp):
    """
    Xóa sản phẩm khỏi danh mục và xóa tất cả giao dịch liên quan để tránh rác dữ liệu.
    """
    ma_sp = ma_sp.strip()
    df_sp, df_gd = db.load_data()
    
    if ma_sp not in df_sp['ma_sp'].values:
        raise ValueError(f"Mã sản phẩm '{ma_sp}' không tồn tại.")
        
    # Loại bỏ sản phẩm và các dòng giao dịch liên quan
    df_sp = df_sp[df_sp['ma_sp'] != ma_sp]
    df_gd = df_gd[df_gd['ma_sp'] != ma_sp]
    
    db.save_data(df_sp, df_gd)


def record_transaction(ma_sp, loai, so_luong, ghi_chu=""):
    """
    Ghi nhận một giao dịch Nhập hoặc Xuất.
    Kiểm tra tồn kho hiện tại đối với giao dịch Xuất.
    """
    ma_sp = ma_sp.strip()
    if so_luong <= 0:
        raise ValueError("Số lượng giao dịch phải lớn hơn 0.")
        
    if loai not in ['nhap', 'xuat']:
        raise ValueError("Loại giao dịch không hợp lệ.")
        
    df_sp, df_gd = db.load_data()
    
    if ma_sp not in df_sp['ma_sp'].values:
        raise ValueError(f"Sản phẩm mã '{ma_sp}' không tồn tại.")

    product_row = df_sp[df_sp['ma_sp'] == ma_sp].iloc[0]
    ma_kho = '' if pd.isna(product_row.get('ma_kho', '')) else str(product_row.get('ma_kho', '')).strip().upper()
        
    # Kiểm tra tồn kho nếu là giao dịch Xuất
    if loai == 'xuat':
        df_summary = get_inventory_summary(df_sp, df_gd)
        row = df_summary[df_summary['ma_sp'] == ma_sp]
        ton_hien_tai = row['ton_hien_tai'].values[0] if not row.empty else 0
        
        if ton_hien_tai < so_luong:
            raise ValueError(f"Không đủ tồn kho để xuất. Số tồn hiện có: {ton_hien_tai} {row['don_vi_tinh'].values[0] if not row.empty else ''}, yêu cầu xuất: {so_luong}.")
            
    new_gd = {
        "ma_sp": ma_sp,
        "loai": loai,
        "so_luong": so_luong,
        "ngay_gio": datetime.datetime.now(),
        "ma_kho": ma_kho,
        "ghi_chu": ghi_chu.strip() if ghi_chu else ""
    }
    
    df_gd = pd.concat([df_gd, pd.DataFrame([new_gd])], ignore_index=True)
    db.save_data(df_sp, df_gd)


def import_products_from_excel(file_bytes):
    """
    Nhập sản phẩm hàng loạt từ file Excel tải lên.
    Tự sinh mã sản phẩm theo format SP###.
    Trả về: (số lượng sản phẩm thêm mới thành công, danh sách lỗi nếu có)
    """
    try:
        df_upload = pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Không thể đọc file Excel: {str(e)}")

    df_upload = _standardize_product_upload_columns(df_upload)
        
    # Kiểm tra các cột bắt buộc
    required_cols = ['ten_sp', 'don_vi_tinh']
    for col in required_cols:
        if col not in df_upload.columns:
            raise ValueError("File Excel thiếu cột bắt buộc. File mẫu cần có: Tên sản phẩm, Đơn vị tính, Tồn tối thiểu, Nhóm hàng, Mã kho.")
            
    # Chuẩn hóa dữ liệu tải lên
    df_upload['ten_sp'] = df_upload['ten_sp'].astype(str).str.strip()
    df_upload['don_vi_tinh'] = df_upload['don_vi_tinh'].astype(str).str.strip()
    
    if 'ton_toi_thieu' in df_upload.columns:
        df_upload['ton_toi_thieu'] = pd.to_numeric(df_upload['ton_toi_thieu'], errors='coerce').fillna(5).astype(int)
    else:
        df_upload['ton_toi_thieu'] = 5
        
    if 'nhom_hang' in df_upload.columns:
        df_upload['nhom_hang'] = df_upload['nhom_hang'].fillna('Chưa phân loại').astype(str).str.strip()
    else:
        df_upload['nhom_hang'] = 'Chưa phân loại'

    if 'ma_kho' in df_upload.columns:
        df_upload['ma_kho'] = df_upload['ma_kho'].fillna('').astype(str).str.strip().str.upper()
    else:
        df_upload['ma_kho'] = ''
        
    # Loại bỏ dòng trống không có tên sản phẩm
    df_upload = df_upload[df_upload['ten_sp'].notna()]
    df_upload = df_upload[df_upload['ten_sp'] != '']
    
    if df_upload.empty:
        raise ValueError("Không tìm thấy dữ liệu hợp lệ trong file Excel.")
        
    df_sp, df_gd = db.load_data()
    existing_codes = set(df_sp['ma_sp'].astype(str).str.strip().values)
    existing_names = {_normalize_text(name) for name in df_sp['ten_sp'].fillna('').values}
    file_names = set()
    
    added_count = 0
    new_rows = []
    errors = []
    
    for idx, row in df_upload.iterrows():
        row_num = idx + 2
        ten_sp = str(row['ten_sp']).strip()
        don_vi_tinh = str(row['don_vi_tinh']).strip()
        normalized_name = _normalize_text(ten_sp)

        if not ten_sp or ten_sp.lower() == 'nan':
            errors.append(f"Dòng {row_num}: Tên sản phẩm không được để trống.")
            continue

        if not don_vi_tinh or don_vi_tinh.lower() == 'nan':
            errors.append(f"Dòng {row_num}: Đơn vị tính không được để trống.")
            continue

        if normalized_name in existing_names:
            errors.append(f"Dòng {row_num}: Tên sản phẩm '{ten_sp}' đã tồn tại trong danh mục.")
            continue

        if normalized_name in file_names:
            errors.append(f"Dòng {row_num}: Tên sản phẩm '{ten_sp}' bị trùng trong file Excel.")
            continue

        file_names.add(normalized_name)
        ma = _generate_next_product_code(existing_codes)
        existing_codes.add(ma)

        new_row = {
            "ma_sp": ma,
            "ten_sp": ten_sp,
            "don_vi_tinh": don_vi_tinh,
            "ton_toi_thieu": row['ton_toi_thieu'],
            "nhom_hang": row['nhom_hang']
        }

        new_row["ma_kho"] = row['ma_kho']

        new_rows.append(new_row)
        added_count += 1

    if errors:
        return 0, errors
            
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_sp = pd.concat([df_sp, df_new], ignore_index=True)
        db.save_data(df_sp, df_gd)
        
    return added_count, []


def generate_template_excel():
    """Tạo tệp mẫu để tải lên sản phẩm."""
    df_template = pd.DataFrame([
        {"Tên sản phẩm": "Bút chì 2B G-Star", "Đơn vị tính": "Cây", "Tồn tối thiểu": 10, "Nhóm hàng": "Văn phòng phẩm", "Mã kho": "KHO-01"},
        {"Tên sản phẩm": "Bìa lá A4 xanh", "Đơn vị tính": "Xấp", "Tồn tối thiểu": 5, "Nhóm hàng": "Văn phòng phẩm", "Mã kho": "KHO-01"}
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()


def import_transactions_from_excel(file_bytes, default_loai="nhap"):
    """
    Nhập giao dịch hàng loạt từ file Excel tải lên.
    Trả về: (số lượng giao dịch nhập thành công, danh sách lỗi nếu có)
    """
    if default_loai not in ['nhap', 'xuat']:
        raise ValueError("Loại giao dịch mặc định không hợp lệ.")

    try:
        df_upload = pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Không thể đọc file Excel giao dịch: {str(e)}")

    df_upload = _standardize_transaction_upload_columns(df_upload)

    required_cols = ['ma_sp', 'so_luong']
    for col in required_cols:
        if col not in df_upload.columns:
            raise ValueError("File Excel thiếu cột bắt buộc. Cột cần có: Mã sản phẩm, Số lượng. Có thể thêm: Mã kho, Ghi chú, Ngày giờ.")
            
    df_sp, df_gd = db.load_data()
    
    # Chuẩn hóa dữ liệu tải lên
    df_upload['ma_sp'] = df_upload['ma_sp'].astype(str).str.strip()
    if 'ma_kho' in df_upload.columns:
        df_upload['ma_kho'] = df_upload['ma_kho'].fillna('').astype(str).str.strip().str.upper()
    if 'ghi_chu' in df_upload.columns:
        df_upload['ghi_chu'] = df_upload['ghi_chu'].fillna('').astype(str).str.strip()
    
    new_transactions = []
    errors = []
    
    # Sử dụng tồn kho chạy ảo (running stock level) để kiểm tra các giao dịch xuất kho lũy kế
    df_summary = get_inventory_summary(df_sp, df_gd)
    running_stock = {row['ma_sp']: row['ton_hien_tai'] for _, row in df_summary.iterrows()}
    sp_units = {row['ma_sp']: row['don_vi_tinh'] for _, row in df_sp.iterrows()}
    valid_sp_codes = set(df_sp['ma_sp'].astype(str).str.strip().values)
    if 'ma_kho' in df_sp.columns:
        product_warehouses = {
            row['ma_sp']: '' if pd.isna(row.get('ma_kho', '')) else str(row.get('ma_kho', '')).strip().upper()
            for _, row in df_sp.iterrows()
        }
    else:
        product_warehouses = {row['ma_sp']: '' for _, row in df_sp.iterrows()}
    
    for idx, row in df_upload.iterrows():
        row_num = idx + 2  # Bắt đầu từ dòng 2 (bỏ qua header)
        ma = str(row['ma_sp']).strip()
        loai = default_loai
        
        if not ma or ma.lower() == 'nan':
            errors.append(f"Dòng {row_num}: Mã sản phẩm không được để trống.")
            continue

        if ma not in valid_sp_codes:
            errors.append(f"Dòng {row_num}: Mã sản phẩm '{ma}' không tồn tại trong danh mục.")
            continue

        if 'ma_kho' in df_upload.columns:
            tx_warehouse = str(row.get('ma_kho', '')).strip().upper()
            product_warehouse = product_warehouses.get(ma, '')

            if product_warehouse and not tx_warehouse:
                errors.append(f"Dòng {row_num}: Sản phẩm '{ma}' đang thuộc mã kho '{product_warehouse}', file Excel phải điền đúng cột Mã kho.")
                continue

            if tx_warehouse and not product_warehouse:
                errors.append(f"Dòng {row_num}: Sản phẩm '{ma}' chưa khai báo mã kho trong danh mục, không thể đối chiếu mã kho '{tx_warehouse}'.")
                continue

            if tx_warehouse and product_warehouse and _normalize_text(tx_warehouse) != _normalize_text(product_warehouse):
                errors.append(f"Dòng {row_num}: Mã kho '{tx_warehouse}' không khớp với mã kho danh mục của sản phẩm '{ma}' là '{product_warehouse}'.")
                continue
            
        try:
            qty = int(row['so_luong'])
            if qty <= 0:
                errors.append(f"Dòng {row_num}: Số lượng '{row['so_luong']}' phải lớn hơn 0.")
                continue
        except Exception:
            errors.append(f"Dòng {row_num}: Số lượng '{row['so_luong']}' không phải là số nguyên hợp lệ.")
            continue
            
        # Kiểm tra ngày giờ nếu được điền
        if 'ngay_gio' in row and pd.notna(row['ngay_gio']):
            try:
                ngay_gio = pd.to_datetime(row['ngay_gio'])
            except Exception:
                errors.append(f"Dòng {row_num}: Định dạng ngày giờ '{row['ngay_gio']}' không hợp lệ.")
                continue
        else:
            ngay_gio = datetime.datetime.now() + datetime.timedelta(milliseconds=idx)
            
        if loai == 'xuat':
            current_stock = running_stock.get(ma, 0)
            if current_stock < qty:
                errors.append(f"Dòng {row_num}: Không đủ tồn kho để xuất. Tồn hiện tại: {current_stock} {sp_units[ma]}, yêu cầu xuất: {qty}.")
                continue
            running_stock[ma] = current_stock - qty
        else:
            running_stock[ma] = running_stock.get(ma, 0) + qty
            
        new_transaction = {
            "ma_sp": ma,
            "loai": loai,
            "so_luong": qty,
            "ngay_gio": ngay_gio,
            "ma_kho": product_warehouses.get(ma, "")
        }

        if 'ma_kho' in df_upload.columns:
            new_transaction["ma_kho"] = row.get('ma_kho', '')
        if 'ghi_chu' in df_upload.columns:
            new_transaction["ghi_chu"] = row.get('ghi_chu', '')

        new_transactions.append(new_transaction)
        
    if not errors and new_transactions:
        df_new_gd = pd.DataFrame(new_transactions)
        df_gd = pd.concat([df_gd, df_new_gd], ignore_index=True)
        db.save_data(df_sp, df_gd)
        return len(new_transactions), []
    else:
        return 0, errors


def generate_transaction_template_excel():
    """Tạo tệp mẫu Excel để nhập giao dịch hàng loạt."""
    df_template = pd.DataFrame([
        {"Mã sản phẩm": "SP001", "Số lượng": 50, "Mã kho": "KHO-01", "Ghi chú": "Nhập bổ sung"},
        {"Mã sản phẩm": "SP002", "Số lượng": 3, "Mã kho": "KHO-01", "Ghi chú": ""}
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()


class InventoryPDF(FPDF):
    """Lớp sinh tài liệu PDF hỗ trợ tùy biến Header và Footer."""
    def header(self):
        # Banner đầu trang dạng khối màu navy đậm sang trọng
        self.set_fill_color(30, 58, 138)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        
        # Tiêu đề báo cáo
        self.set_y(10)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 8, 'BÁO CÁO TỒN KHO HÀNG HÓA', 0, 1, 'C')
        
        # Thời điểm xuất (Sử dụng font Regular '' thay vì 'I' nghiêng để tránh lỗi bộ gõ)
        self.set_font('Arial', '', 8)
        self.cell(0, 5, f'Thời gian xuất báo cáo: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        
        # Khôi phục màu chữ mặc định và thụt lề
        self.set_text_color(17, 24, 39)
        self.set_y(40)
        
    def footer(self):
        # Trang ở chân trang
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        self.set_text_color(156, 163, 175)
        self.cell(0, 10, f'Trang {self.page_no()}', 0, 0, 'C')


def generate_report_pdf(df_inv):
    """
    Tạo báo cáo tồn kho định dạng PDF, hỗ trợ font unicode tiếng Việt (Arial hệ thống).
    """
    pdf = InventoryPDF()
    
    # Sử dụng font hệ thống Windows hỗ trợ đầy đủ tiếng Việt Unicode
    font_path = r"C:\Windows\Fonts\arial.ttf"
    font_bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    
    if os.path.exists(font_path):
        pdf.add_font("Arial", "", font_path)
    if os.path.exists(font_bold_path):
        pdf.add_font("Arial", "B", font_bold_path)
        
    pdf.add_page()
    pdf.set_font("Arial", "", 10)
    
    # Tiêu đề bảng báo cáo
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "BẢNG CHI TIẾT TỒN KHO VÀ CẢNH BÁO", 0, 1, "L")
    pdf.ln(2)
    
    # Định dạng các cột
    cols = ['Mã SP', 'Tên sản phẩm', 'Đơn vị', 'Tồn hiện tại', 'Tồn tối thiểu', 'Trạng thái']
    col_widths = [20, 55, 20, 25, 25, 45]
    
    # Vẽ Header bảng
    pdf.set_fill_color(243, 244, 246)
    pdf.set_text_color(31, 41, 55)
    pdf.set_font("Arial", "B", 9)
    for col, width in zip(cols, col_widths):
        pdf.cell(width, 10, col, 1, 0, 'C', True)
    pdf.ln()
    
    # Vẽ các hàng dữ liệu
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(55, 65, 81)
    
    for _, row in df_inv.iterrows():
        # Lấy tọa độ Y trước khi vẽ để tránh lỗi tràn trang khi vẽ bảng dài
        if pdf.get_y() > 260:
            pdf.add_page()
            # Vẽ lại Header bảng ở trang mới
            pdf.set_fill_color(243, 244, 246)
            pdf.set_text_color(31, 41, 55)
            pdf.set_font("Arial", "B", 9)
            for col, width in zip(cols, col_widths):
                pdf.cell(width, 10, col, 1, 0, 'C', True)
            pdf.ln()
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(55, 65, 81)
            
        pdf.cell(col_widths[0], 8, str(row['ma_sp']), 1, 0, 'C')
        pdf.cell(col_widths[1], 8, str(row['ten_sp']), 1, 0, 'L')
        pdf.cell(col_widths[2], 8, str(row['don_vi_tinh']), 1, 0, 'C')
        pdf.cell(col_widths[3], 8, str(row['ton_hien_tai']), 1, 0, 'C')
        pdf.cell(col_widths[4], 8, str(row['ton_toi_thieu']), 1, 0, 'C')
        
        # Highlight trạng thái
        trang_thai = str(row['trang_thai'])
        if trang_thai == "Cần nhập hàng":
            pdf.set_text_color(220, 38, 38)
            pdf.set_font("Arial", "B", 9)
        else:
            pdf.set_text_color(16, 185, 129)
            pdf.set_font("Arial", "", 9)
            
        pdf.cell(col_widths[5], 8, trang_thai, 1, 0, 'C')
        pdf.ln()
        
        # Reset màu chữ
        pdf.set_text_color(55, 65, 81)
        pdf.set_font("Arial", "", 9)
        
    return bytes(pdf.output())
