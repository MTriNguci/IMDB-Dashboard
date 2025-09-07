"""
Query Manager for IMDB Dashboard
Contains all data queries from dash files to ensure consistency between Plotly and Excel
"""

##################### MÔI TRƯỜNG ##############################
import pandas as pd
from typing import Dict, Tuple, Any

class QueryManager:
    """Manages all data queries to ensure consistency between Plotly and Excel"""
    
    def __init__(self):
        self._cache = {}
         

    def get_sum_tanks (self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """Tổng số lượng bồn"""
        cache_key = 'env_sum_tanks'
        if cache_key not in self._cache:
            if trino_connector:
                query = """
                WITH
                  agg AS (
                    SELECT 
                      CAST(DATE(delta.lakehouse.rpdaily.date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh') AS TIMESTAMP) AS log_date,
                      departmentId,
                      CASE
                        WHEN departmentId = 'BB' THEN 'Bàu Bàng'
                        WHEN departmentId = 'KLH' THEN 'Khu Liên Hợp'
                        WHEN departmentId = 'TH' THEN 'Thới Hòa'
                        WHEN departmentId = 'MP' THEN 'Mỹ Phước 1'
                        ELSE 'Khác'
                      END AS area,
                      COALESCE(SUM(getWaterTurn), 0) AS total_get_water_turn,
                      COALESCE(SUM(km), 0) AS total_km,
                      COALESCE(SUM(fuel), 0) AS total_fuel,
                      COALESCE(SUM(drivingTime) / 60, 0) AS total_driving_time,
                      COALESCE(SUM(irrigationFuel), 0) AS total_watering_fuel
                    FROM delta.lakehouse.rpDaily
                """

                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                              THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                    GROUP BY 
                      CAST(DATE(delta.lakehouse.rpdaily.date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh') AS TIMESTAMP),
                      departmentId
                  )
                  SELECT COALESCE(SUM(total_get_water_turn), 0) as " "
                  FROM agg
                """

                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    self._cache[cache_key] = result if result is not None and not result.empty else pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query sum tanks: {str(e)}")
                    self._cache[cache_key] = pd.DataFrame({' ': [0]})
            else:
                self._cache[cache_key] = pd.DataFrame({' ': [0]})
        return self._cache[cache_key]
    def get_sum_travel_distance (self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """Tổng số km di chuyển"""
        cache_key = 'env_sum_travel_km'
        if cache_key not in self._cache:
            if trino_connector:
                query = """
                WITH agg AS (
                  SELECT 
                    CAST(DATE(delta.lakehouse.rpdaily.date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh') AS TIMESTAMP) AS log_date,
                    departmentId,
                    CASE
                      WHEN departmentId = 'BB' THEN 'Bàu Bàng'
                      WHEN departmentId = 'KLH' THEN 'Khu Liên Hợp'
                      WHEN departmentId = 'TH' THEN 'Thới Hòa'
                      WHEN departmentId = 'MP' THEN 'Mỹ Phước 1'
                      ELSE 'Khác'
                    END AS area,
                    COALESCE(SUM(getWaterTurn), 0) AS total_get_water_turn,
                    COALESCE(SUM(km), 0) AS total_km,
                    COALESCE(SUM(fuel), 0) AS total_fuel,
                    COALESCE(SUM(drivingTime) / 60, 0) AS total_driving_time,
                    COALESCE(SUM(irrigationFuel), 0) AS total_watering_fuel
                  FROM delta.lakehouse.rpDaily
                """

                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                              THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                  GROUP BY 
                    CAST(DATE(delta.lakehouse.rpDaily.date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh') AS TIMESTAMP),
                    departmentId
                )
                SELECT COALESCE(SUM(total_km), 0) as " "
                FROM agg
                """

                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    self._cache[cache_key] = result if result is not None and not result.empty else pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query travel distance: {str(e)}")
                    self._cache[cache_key] = pd.DataFrame({' ': [0]})
            else:
                self._cache[cache_key] = pd.DataFrame({' ': [0]})
        return self._cache[cache_key]
    def get_sum_operation_time (self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """Tổng số giờ hoạt động"""
        cache_key = 'env_sum_operating_hours'
        if cache_key not in self._cache:
            if trino_connector:
                query = """
                WITH agg AS (
                  SELECT
                    CAST(at_timezone("date", 'Asia/Ho_Chi_Minh') AS DATE) AS log_date,
                    departmentId,
                    CASE
                      WHEN departmentId = 'BB'  THEN 'Bàu Bàng'
                      WHEN departmentId = 'KLH' THEN 'Khu Liên Hợp'
                      WHEN departmentId = 'TH'  THEN 'Thới Hòa'
                      WHEN departmentId = 'MP'  THEN 'Mỹ Phước 1'
                      ELSE 'Khác'
                    END AS area,
                    COALESCE(SUM(getWaterTurn), 0)                     AS total_get_water_turn,
                    COALESCE(SUM(km), 0)                               AS total_km,
                    COALESCE(SUM(fuel), 0)                             AS total_fuel,
                    COALESCE(SUM(CAST(drivingTime AS DOUBLE))/60.0, 0) AS total_driving_time,
                    COALESCE(SUM(irrigationFuel), 0)                   AS total_watering_fuel
                  FROM delta.lakehouse.rpDaily
                """

                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                              THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                  GROUP BY 1, departmentId
                )
                SELECT COALESCE(SUM(total_driving_time), 0) AS " "
                FROM agg
                """

                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    self._cache[cache_key] = result if result is not None and not result.empty else pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query operation time: {str(e)}")
                    self._cache[cache_key] = pd.DataFrame({' ': [0]})
            else:
                self._cache[cache_key] = pd.DataFrame({' ': [0]})
        return self._cache[cache_key]
    def get_sum_FuelConsumption_Transportation (self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """Tổng nhiên liệu tiêu hao vận chuyển (lít)"""
        cache_key = 'env_fuel_transport'
        if cache_key not in self._cache:
            if trino_connector:
                query = """
                WITH agg AS (
                  SELECT
                    CAST(("date" AT TIME ZONE 'Asia/Ho_Chi_Minh') AS TIMESTAMP) AS log_date,
                    departmentId,
                    CASE
                      WHEN departmentId = 'BB'  THEN 'Bàu Bàng'
                      WHEN departmentId = 'KLH' THEN 'Khu Liên Hợp'
                      WHEN departmentId = 'TH'  THEN 'Thới Hòa'
                      WHEN departmentId = 'MP'  THEN 'Mỹ Phước 1'
                      ELSE 'Khác'
                    END AS area,
                    COALESCE(SUM(getWaterTurn),        0) AS total_get_water_turn,
                    COALESCE(SUM(km),                  0) AS total_km,
                    COALESCE(SUM(fuel),                0) AS total_fuel,
                    COALESCE(SUM(drivingTime) / 60,    0) AS total_driving_time,
                    COALESCE(SUM(irrigationFuel),      0) AS total_watering_fuel
                  FROM delta.lakehouse.rpDaily
                """

                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                              THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                  GROUP BY CAST(("date" AT TIME ZONE 'Asia/Ho_Chi_Minh') AS TIMESTAMP), departmentId
                )
                SELECT COALESCE(SUM(total_fuel), 0) as " "
                FROM agg
                """

                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    self._cache[cache_key] = result if result is not None and not result.empty else pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query fuel transport: {str(e)}")
                    self._cache[cache_key] = pd.DataFrame({' ': [0]})
            else:
                self._cache[cache_key] = pd.DataFrame({' ': [0]})
        return self._cache[cache_key]
    def get_sum_FuelConsumption_Watering (self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """Tổng nhiên liệu tiêu hao tưới nước"""
        cache_key = 'env_fuel_watering'
        if cache_key not in self._cache:
            if trino_connector:
                query = """
                WITH agg AS (
                  SELECT 
                    CAST(DATE(delta.lakehouse.rpdaily.date) AS TIMESTAMP) AS log_date,  
                    departmentId,
                    CASE
                      WHEN departmentId = 'BB' THEN 'Bàu Bàng'
                      WHEN departmentId = 'KLH' THEN 'Khu Liên Hợp'
                      WHEN departmentId = 'TH' THEN 'Thới Hòa'
                      WHEN departmentId = 'MP' THEN 'Mỹ Phước 1'
                      ELSE 'Khác'
                    END AS area,
                    COALESCE(SUM(getWaterTurn), 0) AS total_get_water_turn,
                    COALESCE(SUM(km), 0) AS total_km,
                    COALESCE(SUM(fuel), 0) AS total_fuel,
                    COALESCE(SUM(drivingTime) / 60, 0) AS total_driving_time,
                    COALESCE(SUM(irrigationFuel), 0) AS total_watering_fuel
                  FROM delta.lakehouse.rpDaily
                """

                if start_date and end_date:
                    query += f"""
                      WHERE (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.rpDaily."Date" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                              THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                  GROUP BY CAST(DATE(delta.lakehouse.rpdaily.date) AS TIMESTAMP), departmentId
                )
                SELECT COALESCE(SUM(total_watering_fuel), 0) AS " "
                FROM agg
                """

                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    self._cache[cache_key] = result if result is not None and not result.empty else pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query fuel watering: {str(e)}")
                    self._cache[cache_key] = pd.DataFrame({' ': [0]})
            else:
                self._cache[cache_key] = pd.DataFrame({' ': [0]})
        return self._cache[cache_key]
    def get_num_times_leaves (self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """Số lần xe ra khỏi khu vực"""
        cache_key = 'env_num_times_leaves'
        if cache_key not in self._cache:
            if trino_connector:
                query = """
                WITH agg AS (
                  SELECT 
                    delta.lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS log_date,  
                    delta.lakehouse.vehicles.DepartmentId,
                    CASE
                      WHEN delta.lakehouse.vehicles.DepartmentId = 'BB' THEN 'Bàu Bàng'
                      WHEN delta.lakehouse.vehicles.DepartmentId = 'KLH' THEN 'Khu Liên Hợp'
                      WHEN delta.lakehouse.vehicles.DepartmentId = 'TH' THEN 'Thới Hòa'
                      WHEN delta.lakehouse.vehicles.DepartmentId = 'MP' THEN 'Mỹ Phước'
                      ELSE 'Khác'
                    END AS area,
                    COUNT(delta.lakehouse.event.OriginalID) AS total_disconnect_gps_events
                  FROM delta.lakehouse.event
                  JOIN delta.lakehouse.vehicles 
                    ON delta.lakehouse.event.AssetID = delta.lakehouse.vehicles.Plate
                  WHERE delta.lakehouse.event.EventType = 'carLeaveArea'
                """

                if start_date and end_date:
                    query += f"""
                      AND (
                        delta.lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        delta.lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) < (
                        (
                          CASE
                            WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                             AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                              THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                            ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                          END
                        ) AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      )
                    """

                query += """
                  GROUP BY 
                    delta.lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh',
                    delta.lakehouse.vehicles.DepartmentId
                )
                SELECT COALESCE(SUM(total_disconnect_gps_events), 0) AS " "
                FROM agg
                """

                if area:
                    query += f" WHERE area = '{area}'"

                try:
                    result = trino_connector.execute_query(query)
                    self._cache[cache_key] = result if result is not None and not result.empty else pd.DataFrame({' ': [0]})
                except Exception as e:
                    print(f"Lỗi khi thực thi query num times leaves: {str(e)}")
                    self._cache[cache_key] = pd.DataFrame({' ': [0]})
            else:
                self._cache[cache_key] = pd.DataFrame({' ': [0]})
        return self._cache[cache_key]

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

def get_viz3_query_manager() -> QueryManager:
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
