import pandas as pd
import os
from typing import Dict, Any

def get_constants(movies, series, movies_splits, series_splits):

    num_of_works=movies.shape[0]+series.shape[0]

    countries_movies=movies_splits["country"]["country"].groupby(movies_splits["country"]["country"]).count().sort_values(ascending=False).index 
    countries_series=series_splits["country"]["country"].groupby(movies_splits["country"]["country"]).count().sort_values(ascending=False).index 
    num_of_countries=len(countries_movies.append(countries_series).unique())

    languages_movies=movies_splits["language"]["language"].groupby(movies_splits["language"]["language"]).count().sort_values(ascending=False).index
    language_series=series_splits["language"]["language"].groupby(movies_splits["language"]["language"]).count().sort_values(ascending=False).index
    num_of_lang=len(languages_movies.append(language_series).unique())
    avg_votes=int((movies["votes"].mean()+series["votes"].mean())/2)

    return num_of_works,num_of_countries,num_of_lang,avg_votes

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