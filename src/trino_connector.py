import trino
import pandas as pd
from typing import Optional, Dict, Any, List
import logging
import os
# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrinoConnector:
    """
    Class để kết nối và thao tác với Trino database
    """
    
    def __init__(self, host: str, port: int = 8889, user: str = "trino", 
                 catalog: str = "delta", schema: str = "lakehouse", 
                 password: Optional[str] = None, **kwargs):
        """
        Khởi tạo kết nối Trino
        
        Args:
            host: Địa chỉ host của Trino server
            port: Port của Trino server (mặc định 8080)
            user: Tên người dùng
            catalog: Catalog name
            schema: Schema name
            password: Mật khẩu (nếu cần)
            **kwargs: Các tham số bổ sung cho kết nối
        """
        self.host = host
        self.port = port
        self.user = user
        self.catalog = catalog
        self.schema = schema
        self.password = password
        self.connection_params = kwargs
        self.conn = None
        
    def connect(self) -> bool:
        """
        Thiết lập kết nối tới Trino
        
        Returns:
            bool: True nếu kết nối thành công, False nếu thất bại
        """
        try:
            # Tạo connection parameters
            conn_params = {
                'host': self.host,
                'port': self.port,
                'user': self.user,
                'catalog': self.catalog,
                'schema': self.schema,
                **self.connection_params
            }
            
            # Thêm password nếu có
            if self.password:
                conn_params['password'] = self.password
                
            # Tạo kết nối
            self.conn = trino.dbapi.connect(**conn_params)
            logger.info(f"✅✅✅Kết nối thành công tới Trino tại {self.host}:{self.port}")
            
                # In danh sách catalog
            # catalogs = self.get_catalogs()
            # logger.info(f"🔎 Catalogs có sẵn: {catalogs}")

            # In danh sách schema trong catalog hiện tại
            # schemas = self.get_schemas()
            # logger.info(f"🔎 Schemas trong catalog '{self.catalog}': {schemas}")

            # In danh sách bảng trong schema hiện tại
            tables = self.get_tables()
            logger.info(f"🔎 Tables trong {self.catalog}.{self.schema}: {tables}")
            # for tb in tables:
            #     self.preview_table(tb, limit=3)
            
            return True
            
        except Exception as e:
            logger.error(f"Lỗi kết nối tới Trino: {str(e)}")
            return False
    
    def disconnect(self):
        """
        Đóng kết nối Trino
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("Đã đóng kết nối Trino")
            except Exception as e:
                logger.error(f"Lỗi khi đóng kết nối: {str(e)}")
            finally:
                self.conn = None
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Thực thi câu truy vấn SQL và trả về DataFrame
        
        Args:
            query: Câu truy vấn SQL
            
        Returns:
            pd.DataFrame hoặc None nếu có lỗi
        """
        if not self.conn:
            logger.error("Chưa kết nối tới Trino. Vui lòng gọi connect() trước.")
            return None
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            # Lấy tên cột
            columns = [desc[0] for desc in cursor.description]
            
            # Lấy dữ liệu
            rows = cursor.fetchall()
            
            # Tạo DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            cursor.close()
            logger.info(f"Thực thi query thành công. Trả về {len(df)} dòng dữ liệu.")
            return df
            
        except Exception as e:
            logger.error(f"Lỗi khi thực thi query: {str(e)}")
            return None
    
    def get_tables(self) -> List[str]:
        """
        Lấy danh sách các bảng trong schema hiện tại
        
        Returns:
            List[str]: Danh sách tên bảng
        """
        query = f"SHOW TABLES FROM {self.catalog}.{self.schema}"
        df = self.execute_query(query)
        
        if df is not None and not df.empty:
            return df['Table'].tolist()
        return []
    
    def get_schemas(self) -> List[str]:
        """
        Lấy danh sách các schema trong catalog hiện tại
        
        Returns:
            List[str]: Danh sách tên schema
        """
        query = f"SHOW SCHEMAS FROM {self.catalog}"
        df = self.execute_query(query)
        
        if df is not None and not df.empty:
            return df['Schema'].tolist()
        return []
    
    def get_catalogs(self) -> List[str]:
        """
        Lấy danh sách các catalog
        
        Returns:
            List[str]: Danh sách tên catalog
        """
        query = "SHOW CATALOGS"
        df = self.execute_query(query)
        
        if df is not None and not df.empty:
            return df['Catalog'].tolist()
        return []
    
    def describe_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        Mô tả cấu trúc của bảng
        
        Args:
            table_name: Tên bảng
            
        Returns:
            pd.DataFrame chứa thông tin cột hoặc None nếu có lỗi
        """
        query = f"DESCRIBE {self.catalog}.{self.schema}.{table_name}"
        return self.execute_query(query)
    
    def test_connection(self) -> bool:
        """
        Kiểm tra kết nối bằng cách thực thi một query đơn giản
        
        Returns:
            bool: True nếu kết nối hoạt động, False nếu không
        """
        try:
            result = self.execute_query("SELECT 1 as test")
            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"Test connection thất bại: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def preview_table(self, table_name: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """
        Xem trước dữ liệu trong bảng
        
        Args:
            table_name (str): tên bảng
            limit (int): số dòng cần lấy
        
        Returns:
            pd.DataFrame hoặc None
        """
        full_table = f"{self.catalog}.{self.schema}.{table_name}"
        query = f"SELECT * FROM {full_table} LIMIT {limit}"
        df = self.execute_query(query)
        if df is not None and not df.empty:
            logger.info(f"📊 Preview {limit} dòng từ bảng {full_table}:")
            logger.info(f"\n{df}")

                    # Tạo thư mục nếu chưa có
            # save_dir = "./"
            # os.makedirs(save_dir, exist_ok=True)

            # # Lưu CSV (tên file = table_name.csv)
            # file_path = os.path.join(save_dir, f"{table_name}.csv")
            # df.to_csv(file_path, index=False, encoding="utf-8-sig")
            return df
        else:
            logger.warning(f"⚠️ Không lấy được dữ liệu từ {full_table}")
            return None
        


def create_trino_connection(host: str, port: int = 8080, user: str = "admin",
                          catalog: str = "hive", schema: str = "default",
                          password: Optional[str] = None, **kwargs) -> TrinoConnector:
    """
    Factory function để tạo TrinoConnector
    
    Args:
        host: Địa chỉ host của Trino server
        port: Port của Trino server
        user: Tên người dùng
        catalog: Catalog name
        schema: Schema name
        password: Mật khẩu
        **kwargs: Các tham số bổ sung
        
    Returns:
        TrinoConnector: Instance của TrinoConnector
    """
    return TrinoConnector(host, port, user, catalog, schema, password, **kwargs)










