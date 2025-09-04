"""
Demo file để minh họa cách QueryManager hoạt động
Chạy file này để xem cách QueryManager đảm bảo tính nhất quán giữa Plotly và Excel
"""

import pandas as pd
import time
from src.query_manager import get_query_manager, clear_global_query_manager

def demo_query_manager():
    """Demo cách QueryManager hoạt động"""
    
    print("=== DEMO QUERY MANAGER ===\n")
    
    # Giả lập dữ liệu (thay thế bằng dữ liệu thực tế)
    print("1. Tạo dữ liệu mẫu...")
    movies = pd.DataFrame({
        'title': ['Movie1', 'Movie2', 'Movie3'],
        'genre': ['Action', 'Drama', 'Comedy'],
        'rating': [8.5, 7.8, 6.9]
    })
    
    series = pd.DataFrame({
        'title': ['Series1', 'Series2'],
        'parentalguide': ['PG-13', 'R'],
        'rating': [9.1, 8.7],
        'votes': [1000, 800],
        'year': [2020, 2021]
    })
    
    movies_splits = {
        'genre': pd.DataFrame({'genre': ['Action', 'Drama', 'Comedy', 'Action']}),
        'country': pd.DataFrame({'country': ['USA', 'UK', 'France', 'USA']})
    }
    
    series_splits = {
        'creators': pd.DataFrame({'creators': ['Creator1', 'Creator2', 'Creator1']}),
        'production_company': pd.DataFrame({'production_company': ['Company1', 'Company2']}),
        'stars': pd.DataFrame({'stars': ['Star1', 'Star2', 'Star1']}),
        'language': pd.DataFrame({'language': ['English', 'Spanish', 'English']})
    }
    
    print("2. Khởi tạo QueryManager...")
    query_manager = get_query_manager(movies, series, movies_splits, series_splits)
    
    print("3. Lần đầu tiên - QueryManager sẽ query và cache dữ liệu...")
    start_time = time.time()
    
    # Lần đầu tiên - sẽ query dữ liệu
    overview_data = query_manager.get_overview_data()
    creators_data = query_manager.get_content_creators_data()
    
    first_query_time = time.time() - start_time
    print(f"   Thời gian query lần đầu: {first_query_time:.4f} giây")
    
    print("4. Lần thứ hai - QueryManager sử dụng cached data...")
    start_time = time.time()
    
    # Lần thứ hai - sử dụng cached data
    overview_data_cached = query_manager.get_overview_data()
    creators_data_cached = query_manager.get_content_creators_data()
    
    cached_query_time = time.time() - start_time
    print(f"   Thời gian sử dụng cache: {cached_query_time:.4f} giây")
    
    print(f"   Tốc độ cải thiện: {first_query_time/cached_query_time:.1f}x nhanh hơn!")
    
    print("\n5. Thông tin về cache:")
    cache_info = query_manager.get_cache_info()
    for tab, data_dict in cache_info.items():
        print(f"   {tab}: {data_dict}")
    
    print("\n6. So sánh dữ liệu (đảm bảo tính nhất quán):")
    print(f"   Overview data giống nhau: {overview_data is overview_data_cached}")
    print(f"   Creators data giống nhau: {creators_data is creators_data_cached}")
    
    print("\n7. Xem dữ liệu đã cache:")
    print("   Overview - Parental Guide:")
    print(overview_data['parental_guide'].head())
    
    print("\n   Content Creators - Top Creators:")
    print(creators_data['creators'].head())
    
    print("\n8. Xóa cache...")
    query_manager.clear_cache()
    print("   Cache đã được xóa!")
    
    print("\n9. Kiểm tra cache sau khi xóa:")
    cache_info_after = query_manager.get_cache_info()
    print(f"   Cache info: {cache_info_after}")
    
    print("\n=== KẾT LUẬN ===")
    print("✅ QueryManager giúp:")
    print("   - Single source of truth: Chỉ cần chỉnh sửa query ở một nơi")
    print("   - Perfect consistency: Dữ liệu Excel giống 100% với Plotly")
    print("   - Tránh query lại dữ liệu")
    print("   - Cải thiện hiệu suất đáng kể")
    print("   - Dễ dàng quản lý và debug")

if __name__ == "__main__":
    try:
        demo_query_manager()
    except Exception as e:
        print(f"Lỗi khi chạy demo: {e}")
        print("Hãy đảm bảo đã cài đặt đầy đủ dependencies và cấu trúc thư mục đúng")
