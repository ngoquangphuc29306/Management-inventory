# Warehouse Management System

Ứng dụng quản lý tồn kho xây dựng bằng Streamlit và SQLite. Project phục vụ các nghiệp vụ cơ bản của kho: quản lý danh mục sản phẩm, nhập kho, xuất kho, import Excel, tra cứu tồn kho, cảnh báo tồn tối thiểu và xuất báo cáo Excel/PDF.

## Tính năng

- Dashboard tổng quan tồn kho.
- Quản lý danh mục sản phẩm.
- Tự sinh mã sản phẩm theo format `SP001`, `SP002`, `SP003`, ...
- Ghi nhận nhập kho và xuất kho thủ công.
- Import sản phẩm hàng loạt từ Excel.
- Import giao dịch nhập/xuất kho hàng loạt từ Excel.
- Kiểm tra tồn kho trước khi xuất.
- Đối chiếu `Mã kho` khi import giao dịch.
- Tra cứu tồn kho theo sản phẩm, nhóm hàng và trạng thái.
- Nhật ký giao dịch có bộ lọc và phân trang.
- Xuất báo cáo tồn kho ra Excel và PDF.
- Lưu dữ liệu bằng SQLite, không cần cài database server riêng.

## Công nghệ sử dụng

- Python 3.10+
- Streamlit
- SQLite3
- Pandas
- Plotly
- OpenPyXL
- fpdf2
- Ionicons SVG

## Cấu trúc thư mục

```text
app.py
db.py
logic.py
requirements.txt
README.md
.streamlit/config.toml
scripts/reset_inventory_data.py
ionicons.designerpack/
feather/
```

Trong đó:

- `app.py`: giao diện Streamlit.
- `db.py`: kết nối SQLite, schema và dữ liệu mẫu.
- `logic.py`: nghiệp vụ tồn kho, import/export Excel, xuất PDF.
- `requirements.txt`: danh sách thư viện cần cài.
- `scripts/reset_inventory_data.py`: reset database về dữ liệu mẫu.
- `ionicons.designerpack/`: bộ icon đang dùng trong giao diện.

## Yêu cầu môi trường

- Python 3.10 trở lên.
- pip.
- Trình duyệt web hiện đại.

Kiểm tra phiên bản Python:

```powershell
python --version
```

## Cài đặt

Clone repository:

```powershell
git clone https://github.com/ngoquangphuc29306/Management-inventory.git
cd Management-inventory
```

Tạo môi trường ảo:

```powershell
python -m venv .venv
```

Kích hoạt môi trường ảo trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Nếu dùng Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Nếu dùng macOS hoặc Linux:

```bash
source .venv/bin/activate
```

Cài thư viện:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Chạy ứng dụng

Chạy app:

```powershell
streamlit run app.py
```

Mở trình duyệt tại:

```text
http://localhost:8501
```

Nếu port `8501` đã được dùng, chạy bằng port khác:

```powershell
streamlit run app.py --server.port 8502
```

## Dữ liệu SQLite

Ứng dụng dùng file `inventory.db` để lưu dữ liệu local. File này được ignore khỏi Git để tránh đẩy dữ liệu vận hành lên repository.

Khi chạy app lần đầu, nếu chưa có dữ liệu, hệ thống sẽ tự tạo database và nạp dữ liệu mẫu.

Các bảng chính:

- `san_pham`: danh mục sản phẩm.
- `giao_dich`: nhật ký nhập/xuất kho.

Một số cột quan trọng:

- `ma_sp`: mã sản phẩm.
- `ten_sp`: tên sản phẩm.
- `don_vi_tinh`: đơn vị tính.
- `ton_toi_thieu`: mức tồn tối thiểu.
- `nhom_hang`: nhóm hàng.
- `ma_kho`: mã kho thực tế, ví dụ `KHO-01`, `KHO-02`.

## Reset dữ liệu mẫu

Chạy lệnh sau để reset database về dữ liệu mẫu:

```powershell
python scripts\reset_inventory_data.py
```

## Quy tắc nghiệp vụ

### Thêm sản phẩm

Thêm sản phẩm nghĩa là khai báo một mặt hàng mới vào danh mục. Hệ thống tự sinh mã sản phẩm theo format `SP###`.

Ví dụ:

- `SP001`
- `SP002`
- `SP003`

Tên sản phẩm không được trùng với sản phẩm đã có.

### Nhập kho

Nhập kho làm tăng số lượng tồn của một sản phẩm đã có trong danh mục.

### Xuất kho

Xuất kho làm giảm số lượng tồn của một sản phẩm đã có trong danh mục.

Hệ thống không cho xuất nếu số lượng tồn hiện tại không đủ.

### Mã kho

`Mã kho` là mã kho thực tế của sản phẩm, không phải vị trí kệ. Khi import giao dịch Excel, nếu file có cột `Mã kho`, giá trị này phải khớp với mã kho trong danh mục sản phẩm.

## File Excel import sản phẩm

File sản phẩm không cần cột mã sản phẩm vì hệ thống tự sinh mã.

Cột bắt buộc:

| Cột | Ghi chú |
| --- | --- |
| Tên sản phẩm | Không được trống, không được trùng |
| Đơn vị tính | Ví dụ: Cái, Ram, Cuộn |

Cột tùy chọn:

| Cột | Ghi chú |
| --- | --- |
| Tồn tối thiểu | Nếu trống, mặc định là 5 |
| Nhóm hàng | Nếu trống, mặc định là Chưa phân loại |
| Mã kho | Ví dụ: KHO-01 |

Ví dụ:

| Tên sản phẩm | Đơn vị tính | Tồn tối thiểu | Nhóm hàng | Mã kho |
| --- | --- | ---: | --- | --- |
| Bút chì 2B G-Star | Cây | 10 | Văn phòng phẩm | KHO-01 |
| Bìa lá A4 xanh | Xấp | 5 | Văn phòng phẩm | KHO-01 |

## File Excel import giao dịch

Cột bắt buộc:

| Cột | Ghi chú |
| --- | --- |
| Mã sản phẩm | Phải tồn tại trong danh mục |
| Số lượng | Số nguyên dương |

Cột tùy chọn:

| Cột | Ghi chú |
| --- | --- |
| Mã kho | Nếu điền thì phải khớp với danh mục |
| Ghi chú | Ghi chú giao dịch |
| Ngày giờ | Nếu trống, hệ thống dùng thời điểm import |

Ví dụ:

| Mã sản phẩm | Số lượng | Mã kho | Ghi chú |
| --- | ---: | --- | --- |
| SP001 | 50 | KHO-01 | Nhập bổ sung |
| SP002 | 3 | KHO-01 |  |

Lưu ý: không để dữ liệu rác ngoài vùng bảng trong Excel. Nếu có ký tự thừa ở các ô xa bảng, Excel có thể khiến hệ thống đọc thêm các dòng trống.

## Xuất báo cáo

Trang `Xuất Bản Báo cáo` hỗ trợ:

- Tải báo cáo tồn kho dạng Excel.
- Tạo và tải báo cáo tồn kho dạng PDF.

PDF được tạo theo yêu cầu. Bấm `Tạo file PDF Báo cáo (.pdf)` trước, sau đó nút tải PDF sẽ xuất hiện.

## Lỗi thường gặp

### Không chạy được streamlit

Kiểm tra đã kích hoạt môi trường ảo và cài dependencies:

```powershell
pip install -r requirements.txt
```

### Port 8501 đang được sử dụng

Chạy bằng port khác:

```powershell
streamlit run app.py --server.port 8502
```

### Import Excel báo lỗi dòng trống

Nguyên nhân thường gặp là file Excel có ô rác ngoài vùng bảng. Hãy xóa các dòng/cột thừa rồi lưu lại file.

### PDF lỗi font tiếng Việt

Trên Windows, app dùng font Arial hệ thống. Nếu chạy trên Linux hoặc macOS và PDF bị lỗi tiếng Việt, cần cài font Unicode phù hợp hoặc chỉnh đường dẫn font trong `logic.py`.

## Ghi chú deploy

SQLite phù hợp cho app nhỏ hoặc chạy local. Nếu triển khai cho nhiều người dùng ghi dữ liệu cùng lúc, nên cân nhắc chuyển sang PostgreSQL hoặc MySQL.

Không nên commit dữ liệu thật lên repository. File `inventory.db` đã được đưa vào `.gitignore`.

## Lệnh nhanh

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Reset dữ liệu mẫu:

```powershell
python scripts\reset_inventory_data.py
```

## License

Project hiện chưa khai báo license. Nếu phát hành công khai, nên bổ sung file `LICENSE`.
