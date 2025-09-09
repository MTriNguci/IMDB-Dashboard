import pandas as pd
import os
from typing import Dict, Any



def get_trino_config() -> Dict[str, Any]:
    """
    Lấy cấu hình kết nối Trino từ environment variables hoặc giá trị mặc định
    
    Returns:
        Dict[str, Any]: Dictionary chứa cấu hình kết nối Trino
    """
    return {
        'host': os.getenv('TRINO_HOST', '192.168.255.217'),
        'port': int(os.getenv('TRINO_PORT', '8889')),
        'user': os.getenv('TRINO_USER', 'trino'),
        'catalog': os.getenv('TRINO_CATALOG', 'delta'),
        'schema': os.getenv('TRINO_SCHEMA', 'lakehouse'),
        'password': os.getenv('TRINO_PASSWORD', None),
        'http_scheme': os.getenv('TRINO_HTTP_SCHEME', 'http'),
        'verify': os.getenv('TRINO_VERIFY', 'true').lower() == 'true',
        'request_timeout': int(os.getenv('TRINO_REQUEST_TIMEOUT', '30')),
        'session_properties': {
            'query_max_run_time': os.getenv('TRINO_QUERY_MAX_RUN_TIME', '1h'),
            'query_max_execution_time': os.getenv('TRINO_QUERY_MAX_EXECUTION_TIME', '1h'),
            'query_max_planning_time': os.getenv('TRINO_QUERY_MAX_PLANNING_TIME', '10m')
        }
    }

def get_trino_connection_string() -> str:
    """
    Tạo connection string cho Trino
    
    Returns:
        str: Connection string
    """
    config = get_trino_config()
    return f"{config['http_scheme']}://{config['user']}@{config['host']}:{config['port']}/{config['catalog']}/{config['schema']}"