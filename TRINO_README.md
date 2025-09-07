# Hướng dẫn sử dụng Trino trong IMDB Dashboard

## Tổng quan

Dashboard IMDB đã được tích hợp với Trino để sử dụng delta.lakehouse làm nguồn dữ liệu chính thay vì đọc từ file CSV. Tính năng này cho phép:

- Tự động kết nối tới Trino server khi khởi động
- Load tất cả dữ liệu từ delta.lakehouse (23 bảng có sẵn)
- Tạo visualizations động dựa trên cấu trúc dữ liệu thực tế
- Fallback tự động về CSV nếu không kết nối được Trino
- Quản lý kết nối tự động trong background

## Cài đặt

### 1. Cài đặt thư viện

Thư viện `trino` đã được thêm vào `requirements.txt`. Chạy lệnh sau để cài đặt:

```bash
pip install -r requirements.txt
```

### 2. Cấu hình kết nối

Tạo file `.env` từ file mẫu `trino_config_example.env`:

```bash
cp trino_config_example.env .env
```

Chỉnh sửa file `.env` với thông tin kết nối Trino của bạn:

```env
TRINO_HOST=your-trino-host
TRINO_PORT=8080
TRINO_USER=your-username
TRINO_CATALOG=hive
TRINO_SCHEMA=default
TRINO_PASSWORD=your-password
```

## Sử dụng

### 1. Dữ liệu trong delta.lakehouse

Dashboard sẽ tự động load tất cả 23 bảng có sẵn trong delta.lakehouse:

**Bảng chính được sử dụng:**
- `vehicles` - Được sử dụng làm movies data
- `asset` - Được sử dụng làm series data

**Các bảng khác:**
- `areaunit`, `company`, `dim_area`, `dim_date`, `dim_device`, `dim_vehicle`
- `event`, `eventinfor`, `eventtype`, `fact_lpd`, `factory`, `handytalkiegps`
- `history`, `intersection`, `lpr_table`, `monitoringhistory`, `rpdaily`
- `silver_lpr`, `stg_lpr_table`, `test_asset`, `test_info`

Dashboard sẽ tự động phân tích cấu trúc dữ liệu và tạo visualizations phù hợp.

### 2. Khởi động ứng dụng

```bash
python app.py
```

Dashboard sẽ tự động:
1. Kết nối tới Trino server (delta.lakehouse)
2. Load tất cả 23 bảng từ delta.lakehouse
3. Tạo visualizations động dựa trên cấu trúc dữ liệu thực tế
4. Nếu không kết nối được, sẽ fallback về CSV files
5. Hiển thị thông báo trạng thái kết nối trong console

## Cấu trúc dữ liệu

### Bảng vehicles (Movies data)
Được sử dụng làm dữ liệu movies, chứa thông tin về các phương tiện

### Bảng asset (Series data)  
Được sử dụng làm dữ liệu series, chứa thông tin về các tài sản

### Các bảng khác
Dashboard sẽ tự động phân tích cấu trúc của tất cả 23 bảng và tạo visualizations phù hợp:
- Biểu đồ số lượng dữ liệu theo cột
- Thống kê số liệu (heatmap)
- Phân bố dữ liệu text
- Thông tin tổng quan (gauge chart)

## Test kết nối

Sử dụng script test để kiểm tra kết nối:

```bash
python test_trino.py
```

Script này sẽ:
1. Test kết nối tới Trino
2. Kiểm tra các bảng cần thiết
3. Hiển thị thông tin về dữ liệu có sẵn

## Cấu trúc code

### Files chính

- `src/trino_connector.py`: Class chính để kết nối và thao tác với Trino
- `src/const.py`: Chứa hàm cấu hình kết nối Trino
- `app.py`: Tích hợp giao diện Trino vào dashboard

### Class TrinoConnector

Class này cung cấp các phương thức:

- `connect()`: Thiết lập kết nối
- `disconnect()`: Đóng kết nối
- `execute_query(query)`: Thực thi câu truy vấn
- `test_connection()`: Kiểm tra kết nối
- `get_tables()`: Lấy danh sách bảng
- `get_schemas()`: Lấy danh sách schema
- `get_catalogs()`: Lấy danh sách catalog
- `describe_table(table_name)`: Mô tả cấu trúc bảng

## Xử lý lỗi

### Lỗi kết nối
- Kiểm tra Trino server có đang chạy không
- Kiểm tra thông tin host, port, user trong file `.env`
- Kiểm tra firewall và network connectivity

### Lỗi query
- Kiểm tra syntax SQL
- Kiểm tra quyền truy cập của user
- Kiểm tra tên bảng, schema, catalog có đúng không

## Bảo mật

- Không commit file `.env` vào git
- Sử dụng HTTPS khi có thể
- Cấu hình authentication phù hợp
- Giới hạn quyền truy cập của user

## Troubleshooting

### Lỗi "ModuleNotFoundError: No module named 'trino'"
```bash
pip install trino
```

### Lỗi kết nối timeout
- Tăng `TRINO_REQUEST_TIMEOUT` trong file `.env`
- Kiểm tra network connectivity

### Lỗi authentication
- Kiểm tra username/password
- Kiểm tra authentication method của Trino server

## Liên hệ

Nếu gặp vấn đề, vui lòng kiểm tra logs trong console hoặc tạo issue trên repository.
