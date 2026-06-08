# Warehouse Management System

Ứng dụng quản lý tồn kho chạy trên Streamlit, dùng SQLite làm cơ sở dữ liệu nội bộ. Project hỗ trợ quản lý danh mục sản phẩm, ghi nhận nhập/xuất kho, import Excel hàng loạt, tra cứu tồn kho, cảnh báo dưới mức tồn tối thiểu và xuất báo cáo Excel/PDF.

## Tính Năng Chính

- Dashboard tổng quan tồn kho theo thời gian thực.
- Quản lý danh mục sản phẩm với mã sản phẩm tự sinh theo format `SP###`.
- Ghi nhận giao dịch nhập kho và xuất kho thủ công.
- Import hàng loạt giao dịch nhập/xuất kho từ file Excel.
- Import hàng loạt sản phẩm mới từ file Excel, tự sinh mã sản phẩm.
- Đối chiếu `Mã kho` khi import giao dịch để tránh nhập/xuất nhầm kho.
- Tra cứu tồn kho, lọc sản phẩm và xem trạng thái cảnh báo.
- Nhật ký giao dịch có lọc theo sản phẩm, thời gian và loại giao dịch.
- Xuất báo cáo tồn kho ra `.xlsx` và `.pdf`.
- Dữ liệu lưu trong SQLite, không cần server database riêng.

## Công Nghệ Sử Dụng

- Python 3.10+
- Streamlit
- SQLite3
- Pandas
- Plotly
- OpenPyXL
- fpdf2
- Ionicons SVG cho hệ icon giao diện

## Cấu Trúc Project

```text
.
├── app.py                         # Giao diện Streamlit
├── db.py                          # Lớp truy cập SQLite và dữ liệu mẫu
├── logic.py                       # Nghiệp vụ tồn kho, import/export, báo cáo
├── inventory.db                   # SQLite database local
├── requirements.txt               # Danh sách thư viện Python cần cài
├── .streamlit/
│   └── config.toml                # Theme Streamlit
├── scripts/
│   └── reset_inventory_data.py    # Reset dữ liệu mẫu vào SQLite
└── ionicons.designerpack/         # Bộ icon SVG dùng trong giao diện
```

## Yêu Cầu Môi Trường

- Python 3.10 trở lên.
- `pip` đi kèm Python.
- Trình duyệt web hiện đại.

Kiểm tra Python:

```powershell
python --version
```

## Cài Đặt

Clone project về máy:

```powershell
git clone <repository-url>
cd <ten-thu-muc-project>
```

Tạo virtual environment:

```powershell
python -m venv .venv
```

Kích hoạt virtual environment trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Nếu dùng Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Nếu dùng macOS/Linux:

```bash
source .venv/bin/activate
```

Cài dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Chạy Ứng Dụng

Chạy Streamlit:

```powershell
streamlit run app.py
```

Sau khi chạy, mở trình duyệt tại:

```text
http://localhost:8501
```

Nếu port `8501` đang được dùng, chạy bằng port khác:

```powershell
streamlit run app.py --server.port 8502
```

## Dữ Liệu Và SQLite

Ứng dụng dùng file `inventory.db` làm database local. Nếu file này chưa tồn tại hoặc chưa có dữ liệu, app sẽ tự khởi tạo bảng và nạp dữ liệu mẫu.

Các bảng chính:

- `san_pham`: danh mục sản phẩm.
- `giao_dich`: nhật ký nhập/xuất kho.

Cột `Mã kho` được lưu nội bộ bằng tên `ma_kho`. Đây là mã kho thực tế như `KHO-01`, `KHO-02`, `KHO-03`, không phải vị trí kệ.

## Reset Dữ Liệu Mẫu

Khi muốn đưa database về dữ liệu mẫu ban đầu:

```powershell
python scripts\reset_inventory_data.py
```

Lệnh này sẽ ghi lại dữ liệu mẫu vào SQLite.

## Quy Tắc Nghiệp Vụ

### Thêm Sản Phẩm

Thêm sản phẩm dùng để khai báo một mặt hàng mới vào danh mục. Hệ thống tự sinh mã sản phẩm theo format:

```text
SP001, SP002, SP003, ...
```

Tên sản phẩm không được trùng với sản phẩm đã có trong danh mục.

### Nhập Kho Và Xuất Kho

Nhập kho/xuất kho là giao dịch làm thay đổi số lượng tồn của sản phẩm đã có trong danh mục.

- Nhập kho: tăng số lượng tồn.
- Xuất kho: giảm số lượng tồn.
- Không cho xuất nếu số lượng tồn không đủ.
- Giao dịch thủ công tự lấy `Mã kho` từ sản phẩm trong danh mục.
- Import Excel có thể kèm `Mã kho`; nếu điền thì phải khớp với mã kho trong danh mục.

## Định Dạng File Excel

### File Import Sản Phẩm

File sản phẩm không cần cột mã sản phẩm vì hệ thống tự sinh mã.

Cột bắt buộc:

| Cột | Ghi chú |
| --- | --- |
| Tên sản phẩm | Không được trống, không được trùng |
| Đơn vị tính | Ví dụ: Cái, Ram, Cuộn |

Cột tùy chọn:

| Cột | Ghi chú |
| --- | --- |
| Tồn tối thiểu | Nếu trống, mặc định là `5` |
| Nhóm hàng | Nếu trống, mặc định là `Chưa phân loại` |
| Mã kho | Ví dụ: `KHO-01` |

Ví dụ:

| Tên sản phẩm | Đơn vị tính | Tồn tối thiểu | Nhóm hàng | Mã kho |
| --- | --- | ---: | --- | --- |
| Bút chì 2B G-Star | Cây | 10 | Văn phòng phẩm | KHO-01 |
| Bìa lá A4 xanh | Xấp | 5 | Văn phòng phẩm | KHO-01 |

### File Import Giao Dịch

Cột bắt buộc:

| Cột | Ghi chú |
| --- | --- |
| Mã sản phẩm | Phải tồn tại trong danh mục |
| Số lượng | Số nguyên dương |

Cột tùy chọn:

| Cột | Ghi chú |
| --- | --- |
| Mã kho | Nếu điền thì phải khớp với danh mục |
| Ghi chú | Nội dung ghi chú giao dịch |
| Ngày giờ | Nếu trống, hệ thống dùng thời điểm import |

Ví dụ:

| Mã sản phẩm | Số lượng | Mã kho | Ghi chú |
| --- | ---: | --- | --- |
| SP001 | 50 | KHO-01 | Nhập bổ sung |
| SP002 | 3 | KHO-01 |  |

Lưu ý: tránh nhập dữ liệu rác ngoài vùng bảng trong Excel. Nếu có ký tự thừa ở các ô xa bảng, Excel có thể hiểu các dòng trống là một phần dữ liệu.

## Xuất Báo Cáo

Trang `Xuất Bản Báo cáo` hỗ trợ:

- Tải file Excel báo cáo tồn kho.
- Tạo file PDF báo cáo tồn kho.

PDF được tạo theo yêu cầu: bấm `Tạo file PDF Báo cáo (.pdf)` trước, sau đó bấm nút tải PDF hiện ra. Cách này giúp trang báo cáo mở nhanh hơn vì app không tạo PDF ngay khi vào tab.

## Lỗi Thường Gặp

### Không chạy được `streamlit`

Kiểm tra virtual environment đã được kích hoạt và dependencies đã cài:

```powershell
pip install -r requirements.txt
```

### Port 8501 đang được sử dụng

Chạy bằng port khác:

```powershell
streamlit run app.py --server.port 8502
```

### Import Excel báo lỗi dòng trống

Nguyên nhân thường gặp là trong file Excel có ô rác nằm ngoài bảng, ví dụ một ký tự ở cột xa hoặc dòng xa. Xóa các dòng/cột thừa rồi lưu lại file.

### PDF lỗi font tiếng Việt

Trên Windows, app dùng font Arial hệ thống tại:

```text
C:\Windows\Fonts\arial.ttf
C:\Windows\Fonts\arialbd.ttf
```

Nếu chạy trên Linux/macOS và PDF bị lỗi tiếng Việt, cần cài font Unicode phù hợp hoặc điều chỉnh đường dẫn font trong `logic.py`.

## Ghi Chú Khi Deploy

Project này phù hợp để chạy local hoặc deploy dạng Streamlit app đơn giản. Nếu deploy cho nhiều người dùng đồng thời, cần lưu ý:

- SQLite phù hợp cho app nhỏ/local; với nhiều user ghi dữ liệu cùng lúc nên cân nhắc PostgreSQL/MySQL.
- Không commit dữ liệu thật hoặc thông tin nhạy cảm vào repository.
- Nên backup `inventory.db` định kỳ nếu dùng trong vận hành thật.

## Lệnh Nhanh

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

Chưa khai báo license. Nếu phát hành công khai, nên bổ sung file `LICENSE` phù hợp với mục đích sử dụng.
