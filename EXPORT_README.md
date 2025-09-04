# Export Utilities - IMDB Dashboard

## Tổng quan

Các hàm liên quan đến việc xuất Excel và PDF đã được tách thành file riêng biệt `src/export_utils.py` để dễ quản lý và bảo trì.

## Cấu trúc file

### `src/query_manager.py`
Quản lý tất cả các câu query để đảm bảo tính nhất quán:

1. **`QueryManager` class**: Chứa tất cả các câu query từ các file dash
2. **Single source of truth**: Chỉ cần chỉnh sửa query ở một nơi
3. **Perfect consistency**: Dữ liệu Excel giống 100% với Plotly
4. **Cache system**: Lưu trữ dữ liệu đã query để tái sử dụng

### `src/export_utils.py`
Chứa các hàm chính để xuất dữ liệu:

1. **`create_excel_data(movies, series, movies_splits, series_splits)`**
   - Tạo file Excel với nhiều sheet chứa dữ liệu từ các biểu đồ
   - **Sử dụng EXACT same queries từ QueryManager** - giống 100% với Plotly
   - Bao gồm dữ liệu từ tất cả các tab: Overview, Content Creators, Parental Guide, Year
   - Tự động thêm biểu đồ vào mỗi sheet

2. **`add_charts_to_excel(workbook, movies, series, movies_splits, series_splits)`**
   - Hàm hỗ trợ để thêm biểu đồ vào các sheet Excel
   - Tạo các loại biểu đồ khác nhau: Pie Chart, Bar Chart, Line Chart

3. **`create_dashboard_pdf()`**
   - Tạo PDF từ screenshot của dashboard
   - Sử dụng Selenium để chụp ảnh các tab khác nhau
   - Kết hợp các screenshot thành một file PDF

### `app.py`
File chính của dashboard, import và sử dụng các hàm từ `export_utils.py`:

```python
from src.export_utils import create_excel_data, create_dashboard_pdf
```

## Cách sử dụng

### Khởi tạo QueryManager
```python
# Trong app.py, sau khi load dữ liệu
from src.query_manager import get_query_manager

query_manager = get_query_manager(movies, series, movies_splits, series_splits)
```

### Xuất Excel (với EXACT same queries)
```python
# Trong callback Excel download
# QueryManager sẽ sử dụng EXACT same queries như Plotly
output = create_excel_data(movies, series, movies_splits, series_splits)
```

### Xuất PDF
```python
# Trong callback PDF download
pdf_content = create_dashboard_pdf()
```

### Kiểm tra cache
```python
# Xem thông tin về dữ liệu đã cache
cache_info = query_manager.get_cache_info()
print(cache_info)

# Xóa cache nếu cần
query_manager.clear_cache()
```

## Lợi ích của việc tách file

1. **Dễ bảo trì**: Các hàm xuất dữ liệu được tập trung vào một nơi
2. **Tái sử dụng**: Có thể dễ dàng import và sử dụng ở các file khác
3. **Code sạch hơn**: File `app.py` ngắn gọn và tập trung vào logic chính
4. **Dễ test**: Có thể test riêng các hàm xuất dữ liệu
5. **Dễ mở rộng**: Thêm các định dạng xuất mới (CSV, JSON, etc.)

## Lợi ích của QueryManager

1. **Single source of truth**: Chỉ cần chỉnh sửa query ở một nơi
2. **Perfect consistency**: Dữ liệu Excel giống 100% với Plotly
3. **Tránh query lại**: Dữ liệu được cache và tái sử dụng
4. **Hiệu suất cao**: Không cần xử lý dữ liệu lại khi export
5. **Dễ debug**: Có thể kiểm tra dữ liệu đã cache
6. **Quản lý bộ nhớ**: Tự động quản lý cache và giải phóng khi cần

## Dependencies

File `export_utils.py` cần các thư viện sau:
- `pandas`: Xử lý dữ liệu
- `openpyxl`: Tạo file Excel
- `selenium`: Chụp screenshot cho PDF
- `PIL`: Xử lý hình ảnh
- `os`, `time`: Hỗ trợ hệ thống

## Tương thích giữa Excel và Plotly

### Giới hạn của Excel
Excel không hỗ trợ tất cả các loại biểu đồ của Plotly. Các biểu đồ được chuyển đổi như sau:

| Plotly Chart Type | Excel Chart Type | Ghi chú |
|-------------------|------------------|---------|
| **Treemap** | Horizontal Bar Chart | Sử dụng horizontal bar để mô phỏng cấu trúc phân cấp |
| **Choropleth** | Vertical Bar Chart | Sử dụng vertical bar để hiển thị dữ liệu theo quốc gia |
| **Box Plot** | Bar Chart (Histogram) | Sử dụng bar chart với bins để mô phỏng phân phối |
| **Pie Chart** | Pie Chart | **Hoàn toàn tương thích** |
| **Bar Chart** | Bar Chart | **Hoàn toàn tương thích** |
| **Line Chart** | Line Chart | **Hoàn toàn tương thích** |

### Cải tiến trong Excel
- **Data Labels**: Hiển thị cả giá trị và phần trăm
- **Chart Titles**: Ghi rõ loại biểu đồ và sự tương thích với Plotly
- **Ghi chú**: Thông báo về sự khác biệt do giới hạn của Excel

## Lưu ý

- Đảm bảo Chrome driver được cài đặt để tạo PDF
- Các đường dẫn file tạm (`/tmp/`) có thể cần điều chỉnh trên Windows
- Cần cài đặt đầy đủ các dependencies trong `requirements.txt`
- **Excel charts sẽ khác với Plotly** do giới hạn kỹ thuật của Excel
