"""
Query Manager for IMDB Dashboard
Contains all data queries from dash files to ensure consistency between Plotly and Excel
"""

##################### NĂNG LƯỢNG ##############################
import pandas as pd
from typing import Dict, Tuple, Any

class QueryManager:
    """Manages all data queries to ensure consistency between Plotly and Excel"""
    
    def __init__(self):
        self._cache = {}
        

    def get_consumed_electricity(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """
        Get consumed electricity data
        
        Args:
            trino_connector: TrinoConnector instance
            start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            area (str): tên khu vực
            
        Returns:
            pd.DataFrame: DataFrame with consumed electricity data
        """
        if 'consumed_electricity' not in self._cache:
            if trino_connector:
                query = """
                WITH AreaUnitGroupMapping AS (
                  SELECT
                    _id AS AreaUnitId,
                    CASE
                      WHEN _id IN (
                        '675856de410581bb3ca38f8c','675856de410581bb3ca38f8e',
                        '675856de410581bb3ca38f9b','675856de410581bb3ca38f9c',
                        '675967b416e8b725f1bdaf46','675967ca16e8b725f1bdaf47'
                      ) THEN '675856de410581bb3ca38f8c'
                      WHEN _id IN (
                        '675856de410581bb3ca38f97','675856de410581bb3ca38fa1',
                        '675856de410581bb3ca38fa2'
                      ) THEN '675856de410581bb3ca38f97'
                      WHEN _id IN (
                        '675856de410581bb3ca38f95','675856de410581bb3ca38f9d',
                        '675856de410581bb3ca38f9e'
                      ) THEN '675856de410581bb3ca38f95'
                      WHEN _id = '675856de410581bb3ca38f96' THEN '675856de410581bb3ca38f96'
                      WHEN _id = '675856de410581bb3ca38fa3' THEN '675856de410581bb3ca38fa3'
                      WHEN _id IN (
                        '675856de410581bb3ca38fa4','675856de410581bb3ca38f9f',
                        '675856de410581bb3ca38fa0'
                      ) THEN '675856de410581bb3ca38fa4'
                    END AS ParentAreaUnitId
                  FROM delta.lakehouse.areaunit
                  WHERE _id IN (
                    '675856de410581bb3ca38f8c','675856de410581bb3ca38f8e',
                    '675856de410581bb3ca38f9b','675856de410581bb3ca38f9c',
                    '675967b416e8b725f1bdaf46','675967ca16e8b725f1bdaf47',
                    '675856de410581bb3ca38f97','675856de410581bb3ca38fa1',
                    '675856de410581bb3ca38fa2','675856de410581bb3ca38f95',
                    '675856de410581bb3ca38f9d','675856de410581bb3ca38f9e',
                    '675856de410581bb3ca38f96','675856de410581bb3ca38fa3',
                    '675856de410581bb3ca38fa4','675856de410581bb3ca38f9f',
                    '675856de410581bb3ca38fa0'
                  )
                ),
                history_with_group AS (
                  SELECT
                    delta.lakehouse.history.*,
                    date_add('hour', 7, delta.lakehouse.history.date) AS LocalDateTime,
                    ParentAreaUnitId
                  FROM delta.lakehouse.history 
                  JOIN AreaUnitGroupMapping
                    ON delta.lakehouse.history.AreaUnitId = AreaUnitGroupMapping.AreaUnitId
                """

                # Thêm điều kiện thời gian nếu có
                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN
                              extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                            THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                ),
                agg AS (
                  SELECT
                    CAST(DATE(LocalDateTime) AS TIMESTAMP) AS ReportDate,
                    ParentAreaUnitId,
                    SUM(Usage.Total)    AS TotalUsage,
                    SUM(Cost.Total)     AS TotalCost,
                    SUM(CarbonEmission) AS TotalCarbonEmission,
                    SUM(
                      CASE WHEN EnergySource = 'solar'
                          THEN Usage.Total
                          ELSE 0
                      END
                    ) AS SolarUsage
                  FROM history_with_group
                  GROUP BY
                    CAST(DATE(LocalDateTime) AS TIMESTAMP),
                    ParentAreaUnitId
                )
                SELECT
                  COALESCE(SUM(TotalUsage), 0) as " "
                FROM agg
                LEFT JOIN delta.lakehouse.areaunit
                  ON ParentAreaUnitId = delta.lakehouse.areaunit._id
                """

                # Thêm điều kiện area nếu có
                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    if result is not None and not result.empty:
                        self._cache['consumed_electricity'] = result
                    else:
                        print("Không có dữ liệu trả về từ query consumed electricity.")
                        self._cache['consumed_electricity'] = pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query consumed electricity: {str(e)}")
                    self._cache['consumed_electricity'] = pd.DataFrame({' ': [0]})
            else:
                # Fallback data nếu không có trino_connector
                self._cache['consumed_electricity'] = pd.DataFrame({' ': [0]})
        return self._cache['consumed_electricity']
    def get_energy_cost(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """
        Get energy cost data
        
        Args:
            trino_connector: TrinoConnector instance
            start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            area (str): tên khu vực
            
        Returns:
            pd.DataFrame: DataFrame with energy cost data
        """
        if 'energy_cost' not in self._cache:
            if trino_connector:
                query = """
                WITH AreaUnitGroupMapping AS (
                  SELECT
                    _id AS AreaUnitId,
                    CASE
                      WHEN _id IN (
                        '675856de410581bb3ca38f8c','675856de410581bb3ca38f8e',
                        '675856de410581bb3ca38f9b','675856de410581bb3ca38f9c',
                        '675967b416e8b725f1bdaf46','675967ca16e8b725f1bdaf47'
                      ) THEN '675856de410581bb3ca38f8c'
                      WHEN _id IN (
                        '675856de410581bb3ca38f97','675856de410581bb3ca38fa1',
                        '675856de410581bb3ca38fa2'
                      ) THEN '675856de410581bb3ca38f97'
                      WHEN _id IN (
                        '675856de410581bb3ca38f95','675856de410581bb3ca38f9d',
                        '675856de410581bb3ca38f9e'
                      ) THEN '675856de410581bb3ca38f95'
                      WHEN _id = '675856de410581bb3ca38f96' THEN '675856de410581bb3ca38f96'
                      WHEN _id = '675856de410581bb3ca38fa3' THEN '675856de410581bb3ca38fa3'
                      WHEN _id IN (
                        '675856de410581bb3ca38fa4','675856de410581bb3ca38f9f',
                        '675856de410581bb3ca38fa0'
                      ) THEN '675856de410581bb3ca38fa4'
                    END AS ParentAreaUnitId
                  FROM delta.lakehouse.areaunit
                  WHERE _id IN (
                    '675856de410581bb3ca38f8c','675856de410581bb3ca38f8e',
                    '675856de410581bb3ca38f9b','675856de410581bb3ca38f9c',
                    '675967b416e8b725f1bdaf46','675967ca16e8b725f1bdaf47',
                    '675856de410581bb3ca38f97','675856de410581bb3ca38fa1',
                    '675856de410581bb3ca38fa2','675856de410581bb3ca38f95',
                    '675856de410581bb3ca38f9d','675856de410581bb3ca38f9e',
                    '675856de410581bb3ca38f96','675856de410581bb3ca38fa3',
                    '675856de410581bb3ca38fa4','675856de410581bb3ca38f9f',
                    '675856de410581bb3ca38fa0'
                  )
                ),
                history_with_group AS (
                  SELECT
                    delta.lakehouse.history.*,
                    date_add('hour', 7, delta.lakehouse.history.date) AS LocalDateTime,
                    ParentAreaUnitId
                  FROM delta.lakehouse.history 
                  JOIN AreaUnitGroupMapping
                    ON delta.lakehouse.history.AreaUnitId = AreaUnitGroupMapping.AreaUnitId
                """

                # Thêm điều kiện thời gian nếu có
                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN
                              extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                            THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                ),
                agg AS (
                  SELECT
                    CAST(DATE(LocalDateTime) AS TIMESTAMP) AS ReportDate,
                    ParentAreaUnitId,
                    SUM(Usage.Total)    AS TotalUsage,
                    SUM(Cost.Total)     AS TotalCost,
                    SUM(CarbonEmission) AS TotalCarbonEmission,
                    SUM(
                      CASE WHEN EnergySource = 'solar'
                           THEN Usage.Total
                           ELSE 0
                      END
                    ) AS SolarUsage
                  FROM history_with_group
                  GROUP BY
                    CAST(DATE(LocalDateTime) AS TIMESTAMP),
                    ParentAreaUnitId
                )
                SELECT
                  COALESCE(SUM(TotalCost), 0) as " "
                FROM agg
                LEFT JOIN delta.lakehouse.areaunit
                  ON ParentAreaUnitId = delta.lakehouse.areaunit._id
                """

                # Thêm điều kiện area nếu có
                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    if result is not None and not result.empty:
                        self._cache['energy_cost'] = result
                    else:
                        print("Không có dữ liệu trả về từ query energy cost.")
                        self._cache['energy_cost'] = pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query energy cost: {str(e)}")
                    self._cache['energy_cost'] = pd.DataFrame({' ': [0]})
            else:
                # Fallback data nếu không có trino_connector
                self._cache['energy_cost'] = pd.DataFrame({' ': [0]})
        return self._cache['energy_cost']
    def get_green_energy_percentage(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """
        Get green energy percentage data
        
        Args:
            trino_connector: TrinoConnector instance
            start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            area (str): tên khu vực
            
        Returns:
            pd.DataFrame: DataFrame with green energy percentage data
        """
        if 'green_energy_percentage' not in self._cache:
            if trino_connector:
                query = """
                WITH AreaUnitGroupMapping AS (
                  SELECT
                    _id AS AreaUnitId,
                    CASE
                      WHEN _id IN (
                        '675856de410581bb3ca38f8c','675856de410581bb3ca38f8e',
                        '675856de410581bb3ca38f9b','675856de410581bb3ca38f9c',
                        '675967b416e8b725f1bdaf46','675967ca16e8b725f1bdaf47'
                      ) THEN '675856de410581bb3ca38f8c'
                      WHEN _id IN (
                        '675856de410581bb3ca38f97','675856de410581bb3ca38fa1',
                        '675856de410581bb3ca38fa2'
                      ) THEN '675856de410581bb3ca38f97'
                      WHEN _id IN (
                        '675856de410581bb3ca38f95','675856de410581bb3ca38f9d',
                        '675856de410581bb3ca38f9e'
                      ) THEN '675856de410581bb3ca38f95'
                      WHEN _id = '675856de410581bb3ca38f96' THEN '675856de410581bb3ca38f96'
                      WHEN _id = '675856de410581bb3ca38fa3' THEN '675856de410581bb3ca38fa3'
                      WHEN _id IN (
                        '675856de410581bb3ca38fa4','675856de410581bb3ca38f9f',
                        '675856de410581bb3ca38fa0'
                      ) THEN '675856de410581bb3ca38fa4'
                    END AS ParentAreaUnitId
                  FROM delta.lakehouse.areaunit
                  WHERE _id IN (
                    '675856de410581bb3ca38f8c','675856de410581bb3ca38f8e',
                    '675856de410581bb3ca38f9b','675856de410581bb3ca38f9c',
                    '675967b416e8b725f1bdaf46','675967ca16e8b725f1bdaf47',
                    '675856de410581bb3ca38f97','675856de410581bb3ca38fa1',
                    '675856de410581bb3ca38fa2','675856de410581bb3ca38f95',
                    '675856de410581bb3ca38f9d','675856de410581bb3ca38f9e',
                    '675856de410581bb3ca38f96','675856de410581bb3ca38fa3',
                    '675856de410581bb3ca38fa4','675856de410581bb3ca38f9f',
                    '675856de410581bb3ca38fa0'
                  )
                ),
                history_with_group AS (
                  SELECT
                    delta.lakehouse.history.*,
                    date_add('hour', 7, delta.lakehouse.history.date) AS LocalDateTime,
                    ParentAreaUnitId
                  FROM delta.lakehouse.history 
                  JOIN AreaUnitGroupMapping
                    ON delta.lakehouse.history.AreaUnitId = AreaUnitGroupMapping.AreaUnitId
                """

                # Thêm điều kiện thời gian nếu có
                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN
                              extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                            THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                ),
                agg AS (
                  SELECT
                    CAST(DATE(LocalDateTime) AS TIMESTAMP) AS ReportDate,
                    ParentAreaUnitId,
                    SUM(Usage.Total)    AS TotalUsage,
                    SUM(Cost.Total)     AS TotalCost,
                    SUM(CarbonEmission) AS TotalCarbonEmission,
                    SUM(
                      CASE WHEN EnergySource = 'solar'
                           THEN Usage.Total
                           ELSE 0
                      END
                    ) AS SolarUsage
                  FROM history_with_group
                  GROUP BY
                    CAST(DATE(LocalDateTime) AS TIMESTAMP),
                    ParentAreaUnitId
                )
                SELECT
                  COALESCE(
                    ROUND(SUM(SolarUsage) / SUM(TotalUsage) * 100, 2),
                    0
                  ) as " "
                FROM agg
                LEFT JOIN delta.lakehouse.areaunit 
                  ON ParentAreaUnitId = delta.lakehouse.areaunit._id
                """

                # Thêm điều kiện area nếu có
                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    if result is not None and not result.empty:
                        self._cache['green_energy_percentage'] = result
                    else:
                        print("Không có dữ liệu trả về từ query green energy percentage.")
                        self._cache['green_energy_percentage'] = pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query green energy percentage: {str(e)}")
                    self._cache['green_energy_percentage'] = pd.DataFrame({' ': [0]})
            else:
                # Fallback data nếu không có trino_connector
                self._cache['green_energy_percentage'] = pd.DataFrame({' ': [0]})
        return self._cache['green_energy_percentage']
    def get_CO2_emission(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """
        Get CO2 emission data
        
        Args:
            trino_connector: TrinoConnector instance
            start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            area (str): tên khu vực
            
        Returns:
            pd.DataFrame: DataFrame with CO2 emission data
        """
        if 'co2_emission' not in self._cache:
            if trino_connector:
                query = """
                WITH AreaUnitGroupMapping AS (
                  SELECT
                    _id AS AreaUnitId,
                    CASE
                      WHEN _id IN (
                        '675856de410581bb3ca38f8c',
                        '675856de410581bb3ca38f8e',
                        '675856de410581bb3ca38f9b',
                        '675856de410581bb3ca38f9c',
                        '675967b416e8b725f1bdaf46',
                        '675967ca16e8b725f1bdaf47'
                      ) THEN '675856de410581bb3ca38f8c'
                      WHEN _id IN (
                        '675856de410581bb3ca38f97',
                        '675856de410581bb3ca38fa1',
                        '675856de410581bb3ca38fa2'
                      ) THEN '675856de410581bb3ca38f97'
                      WHEN _id IN (
                        '675856de410581bb3ca38f95',
                        '675856de410581bb3ca38f9d',
                        '675856de410581bb3ca38f9e'
                      ) THEN '675856de410581bb3ca38f95'
                      WHEN _id = '675856de410581bb3ca38f96' THEN '675856de410581bb3ca38f96'
                      WHEN _id = '675856de410581bb3ca38fa3' THEN '675856de410581bb3ca38fa3'
                      WHEN _id IN (
                        '675856de410581bb3ca38fa4',
                        '675856de410581bb3ca38f9f',
                        '675856de410581bb3ca38fa0'
                      ) THEN '675856de410581bb3ca38fa4'
                    END AS ParentAreaUnitId
                  FROM delta.lakehouse.areaunit
                  WHERE _id IN (
                    '675856de410581bb3ca38f8c',
                    '675856de410581bb3ca38f8e',
                    '675856de410581bb3ca38f9b',
                    '675856de410581bb3ca38f9c',
                    '675967b416e8b725f1bdaf46',
                    '675967ca16e8b725f1bdaf47',
                    '675856de410581bb3ca38f97',
                    '675856de410581bb3ca38fa1',
                    '675856de410581bb3ca38fa2',
                    '675856de410581bb3ca38f95',
                    '675856de410581bb3ca38f9d',
                    '675856de410581bb3ca38f9e',
                    '675856de410581bb3ca38f96',
                    '675856de410581bb3ca38fa3',
                    '675856de410581bb3ca38fa4',
                    '675856de410581bb3ca38f9f',
                    '675856de410581bb3ca38fa0'
                  )
                ),
                history_with_group AS (
                  SELECT
                    delta.lakehouse.history.*,
                    date_add('hour', 7, delta.lakehouse.history.date) AS LocalDateTime,
                    ParentAreaUnitId
                  FROM delta.lakehouse.history
                  JOIN AreaUnitGroupMapping ON delta.lakehouse.history.AreaUnitId = AreaUnitGroupMapping.AreaUnitId
                """

                # Thêm điều kiện thời gian nếu có
                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.history."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN
                              extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0 AND
                              extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                            THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                ),
                agg AS (
                  SELECT
                    CAST(DATE(LocalDateTime) AS TIMESTAMP) AS ReportDate,
                    history_with_group.ParentAreaUnitId,
                    SUM(history_with_group.Usage.Total) AS TotalUsage,
                    SUM(history_with_group.Cost.Total) AS TotalCost,
                    SUM(history_with_group.CarbonEmission) AS TotalCarbonEmission,
                    SUM(
                      CASE
                        WHEN history_with_group.EnergySource = 'solar' THEN history_with_group.Usage.Total
                        ELSE 0
                      END
                    ) AS SolarUsage
                  FROM history_with_group 
                  GROUP BY
                    CAST(DATE(LocalDateTime) AS TIMESTAMP),
                    history_with_group.ParentAreaUnitId
                )
                SELECT 
                  COALESCE(SUM(TotalCarbonEmission), 0) as " "
                FROM agg
                LEFT JOIN delta.lakehouse.areaunit ON ParentAreaUnitId = delta.lakehouse.areaunit._id
                """

                # Thêm điều kiện area nếu có
                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    if result is not None and not result.empty:
                        self._cache['co2_emission'] = result
                    else:
                        print("Không có dữ liệu trả về từ query CO2 emission.")
                        self._cache['co2_emission'] = pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query CO2 emission: {str(e)}")
                    self._cache['co2_emission'] = pd.DataFrame({' ': [0]})
            else:
                # Fallback data nếu không có trino_connector
                self._cache['co2_emission'] = pd.DataFrame({' ': [0]})
        return self._cache['co2_emission']





    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data"""
        cache_info = {}
        for key, value in self._cache.items():
            if isinstance(value, pd.DataFrame):
                cache_info[key] = f"DataFrame({value.shape[0]} rows, {value.shape[1]} cols)"
            else:
                cache_info[key] = type(value).__name__
        return cache_info

# Global instance
_query_manager = None

def get_viz2_query_manager() -> QueryManager:
    """Get or create global query manager instance"""
    global _query_manager
    
    if _query_manager is None:
        # Tạo QueryManager với dữ liệu placeholder vì chúng ta sử dụng SQL queries trực tiếp

        _query_manager = QueryManager()
    
    return _query_manager

def clear_global_query_manager():
    """Clear global query manager instance"""
    global _query_manager
    if _query_manager:
        _query_manager.clear_cache()
        _query_manager = None
