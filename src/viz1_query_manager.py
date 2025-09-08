"""
Query Manager for IMDB Dashboard
Contains all data queries from dash files to ensure consistency between Plotly and Excel
"""
###################### TÌNH TRẠNG THÔNG BÁO VÀ HOẠT ĐỘNG HỆ THỐNG ##############################
import pandas as pd
from typing import Dict, Tuple, Any

class viz1_QueryManager:
    """Manages all data queries to ensure consistency between Plotly and Excel"""
    
    def __init__(self):
        self._cache = {}
        

    
    # ==================== SYSTEM INFORMATION QUERIES ====================
    
    def get_total_events_card_data(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
      """Get total events count for card display using full Trino SQL query"""
      if 'total_events_card' not in self._cache:
          if trino_connector:
              # Query gốc Trino với đầy đủ mapping
              query = """
              SELECT
                system_name AS "Tổng thông báo hệ thống",
                SUM(cnt) AS total_events
              FROM
                (
                  SELECT
                    lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS log_date,
                    lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS CreateDate_local,
                    lakehouse.event."ResolvedDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS ResolvedDate_local,
                    -- Mapping các trường
                    CASE lakehouse.event."SourceSystem"
                      WHEN 'EMS' THEN 'Năng lượng'
                      WHEN 'Security' THEN 'An ninh'
                      WHEN 'Environment' THEN 'Môi trường'
                      WHEN 'CyberSecurity' THEN 'An ninh mạng'
                      ELSE 'Không xác định'
                    END AS system_name,
                    CASE lakehouse.event."Level"
                      WHEN 0 THEN 'Nhắc nhở'
                      WHEN 1 THEN 'Thông báo'
                      WHEN 2 THEN 'Khẩn cấp'
                      ELSE 'Không xác định'
                    END AS level_name,
                    CASE lakehouse.event."Status"
                      WHEN 0 THEN 'Chưa xác minh'
                      WHEN 1 THEN 'Đang xử lý'
                      WHEN 2 THEN 'Đã xử lý'
                      ELSE 'Không xác định'
                    END AS status_name,
                    CASE lakehouse.event."Layers"."Area"
                      WHEN 'khu_lien_hop' THEN 'Khu Liên Hợp'
                      WHEN 'bau_bang' THEN 'Bàu Bàng'
                      WHEN 'thoi_hoa' THEN 'Thới Hòa'
                      WHEN 'my_phuoc_1' THEN 'Mỹ Phước 1'
                      WHEN 'my_phuoc_2' THEN 'Mỹ Phước 2'
                      WHEN 'my_phuoc_3' THEN 'Mỹ Phước 3'
                      ELSE 'Không xác định'
                    END AS area,
                    CONCAT (
                      CASE lakehouse.asset."Type"
                        WHEN 'lighting_cabinet' THEN 'Tủ chiếu sáng: '
                        WHEN 'traffic_cabinet' THEN 'Tủ giao thông: '
                        WHEN 'distribution_cabinet' THEN 'Tủ phân phối: '
                        WHEN 'handy_talkie' THEN 'Bộ đàm: '
                        WHEN 'camera_bullet' THEN 'Camera bullet: '
                        WHEN 'camera_ptz' THEN 'Camera PTZ: '
                        WHEN 'backhoe' THEN 'Xe xúc đào: '
                        WHEN 'cranes' THEN 'Cần cẩu: '
                        WHEN 'dump truck' THEN 'Xe ben: '
                        WHEN 'excavator' THEN 'Máy xúc: '
                        WHEN 'firetruck' THEN 'Xe cứu hỏa: '
                        WHEN 'garbage' THEN 'Xe rác: '
                        WHEN 'loader' THEN 'Xe xúc: '
                        WHEN 'manlift' THEN 'Xe nâng người: '
                        WHEN 'sweeper' THEN 'Xe quét đường: '
                        WHEN 'tractor' THEN 'Máy kéo: '
                        WHEN 'truck' THEN 'Xe tải: '
                        WHEN 'watering' THEN 'Xe tưới nước: '
                        ELSE 'Tài sản: '
                      END,
                      COALESCE(lakehouse.event."AssetID", ''),
                      CASE
                        WHEN lakehouse.event."SourceSystem" = 'EMS'
                        AND (
                          lakehouse.event."Detail"."Parameter" IS NOT NULL
                          OR lakehouse.event."Detail"."Value" IS NOT NULL
                          OR lakehouse.event."Detail"."Threshold" IS NOT NULL
                        ) THEN ' | ' || CONCAT_WS (
                          ' | ',
                          IF (
                            lakehouse.event."Detail"."Parameter" IS NOT NULL,
                            'Thông số: ' || lakehouse.event."Detail"."Parameter",
                            NULL
                          ),
                          IF (
                            lakehouse.event."Detail"."Value" IS NOT NULL,
                            'Giá trị: ' || lakehouse.event."Detail"."Value",
                            NULL
                          ),
                          IF (
                            lakehouse.event."Detail"."Threshold" IS NOT NULL,
                            'Ngưỡng: ' || lakehouse.event."Detail"."Threshold",
                            NULL
                          )
                        )
                        WHEN lakehouse.event."SourceSystem" = 'Security'
                        AND lakehouse.event."Detail"."license_number" IS NOT NULL THEN ' | Biển số xe: ' || lakehouse.event."Detail"."license_number"
                        WHEN lakehouse.event."SourceSystem" = 'Environment'
                        AND lakehouse.event."Detail"."pumpStation" IS NOT NULL THEN ' | Trạm bơm: ' || lakehouse.event."Detail"."pumpStation"
                        ELSE ''
                      END
                    ) AS content,
                    -- Cờ active/số lượng
                    CASE
                      WHEN lakehouse.event."IsActive" IS NOT NULL THEN 1
                      ELSE 0
                    END AS cnt
                  FROM
                    lakehouse.event
                    LEFT JOIN lakehouse.asset ON lakehouse.event."AssetID" = lakehouse.asset."AssetID"
                  WHERE
                    NOT (
                      lakehouse.event."SourceSystem" = 'Environment'
                      AND lakehouse.event."Layers"."Area" IN ('my_phuoc_2', 'my_phuoc_3', 'van_don', 'kcn_vd', 'ha_long')
                    )
              """

              # Thêm điều kiện thời gian nếu có
              if start_date and end_date:
                  query += f"""
                    AND (
                      lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                    ) >= TIMESTAMP '{start_date}'
                    AND (
                      lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                    ) < TIMESTAMP '{end_date}'
                  """

              query += ") AS virtual_table"

              # Thêm điều kiện area nếu có
              if area:
                  query += f" WHERE area = '{area}'"

              query += """
              GROUP BY 1
              ORDER BY total_events DESC
              LIMIT 100
              """

              try:
                  result = trino_connector.execute_query(query)
                  if result is not None and not result.empty:
                      self._cache['total_events_card'] = result
                  else:
                      print("Không có dữ liệu trả về từ query total events.")
                      self._cache['total_events_card'] = pd.DataFrame({'Tổng thông báo hệ thống': [], 'total_events': []})
              except Exception as e:
                  print(f"Lỗi khi thực thi query total events: {str(e)}")
                  self._cache['total_events_card'] = pd.DataFrame({'Tổng thông báo hệ thống': [], 'total_events': []})
          else:
              # fallback nếu không có trino_connector
              self._cache['total_events_card'] = pd.DataFrame({'Tổng thông báo hệ thống': ['N/A'], 'total_events': [0]})
      return self._cache['total_events_card']

    
    def get_system_events_pie_data(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """Get system events data for pie chart using SQL query"""
        if 'system_events_pie' not in self._cache:
            if trino_connector:
                # Query 2: System Events Pie Chart - SQL từ Trino
                query = """
                SELECT
                  system_name AS "Tổng thông báo hệ thống",
                  SUM(cnt) AS total_events
                FROM
                  (
                    SELECT
                      lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS log_date,
                      CASE lakehouse.event."SourceSystem"
                        WHEN 'EMS' THEN 'Năng lượng'
                        WHEN 'Security' THEN 'An ninh'
                        WHEN 'Environment' THEN 'Môi trường'
                        WHEN 'CyberSecurity' THEN 'An ninh mạng'
                        ELSE 'Không xác định'
                      END AS system_name,
                      CASE lakehouse.event."Layers"."Area"
                        WHEN 'khu_lien_hop' THEN 'Khu Liên Hợp'
                        WHEN 'bau_bang' THEN 'Bàu Bàng'
                        WHEN 'thoi_hoa' THEN 'Thới Hòa'
                        WHEN 'my_phuoc_1' THEN 'Mỹ Phước 1'
                        WHEN 'my_phuoc_2' THEN 'Mỹ Phước 2'
                        WHEN 'my_phuoc_3' THEN 'Mỹ Phước 3'
                        ELSE 'Không xác định'
                      END AS area,
                      CASE
                        WHEN lakehouse.event."IsActive" IS NOT NULL THEN 1
                        ELSE 0
                      END AS cnt
                    FROM
                      lakehouse.event
                      LEFT JOIN lakehouse.asset ON lakehouse.event."AssetID" = lakehouse.asset."AssetID"
                    WHERE
                      NOT (
                        lakehouse.event."SourceSystem" = 'Environment'
                        AND lakehouse.event."Layers"."Area" IN ('my_phuoc_2', 'my_phuoc_3', 'van_don', 'kcn_vd', 'ha_long')
                      )
                """
                
                # Thêm điều kiện thời gian nếu có
                if start_date and end_date:
                    query += f"""
                      AND (
                        lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) <= TIMESTAMP '{end_date}'
                    """
                
                query += ") AS virtual_table"
                
                # Thêm điều kiện area nếu có
                if area:
                    query += f" WHERE area = '{area}'"
                
                query += """
                GROUP BY
                  1
                ORDER BY
                  total_events DESC
                LIMIT
                  100
                """
                
                try:
                    result = trino_connector.execute_query(query)
                    if result is not None and not result.empty:
                        self._cache['system_events_pie'] = result
                    else:
                        # Fallback data
                        print("Không có dữ liệu trả về từ query system events.")
                        self._cache['system_events_pie'] = pd.DataFrame({
                            'Tổng thông báo hệ thống': ['Năng lượng', 'An ninh', 'Môi trường', 'An ninh mạng'],
                            'total_events': [0, 0, 0, 0]
                        })
                except Exception as e:
                    print(f"Lỗi khi thực thi query system events: {str(e)}")
                    # Fallback data
                    self._cache['system_events_pie'] = pd.DataFrame({
                        'Tổng thông báo hệ thống': ['Năng lượng', 'An ninh', 'Môi trường', 'An ninh mạng'],
                        'total_events': [0, 0, 0, 0]
                    })
            else:
                # Fallback data nếu không có trino_connector
                self._cache['system_events_pie'] = pd.DataFrame({
                    'Tổng thông báo hệ thống': ['Năng lượng', 'An ninh', 'Môi trường', 'An ninh mạng'],
                    'total_events': [0, 0, 0, 0]
                })
        return self._cache['system_events_pie']
    
 
    
    def get_system_information_data(self) -> Dict[str, pd.DataFrame]:
        """Get all System Information data"""
        return {
            'total_events_card': self.get_total_events_card_data(),
            'system_events_pie': self.get_system_events_pie_data()
        }
    
    def get_avg_processing_time(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
      """
      Tính thời gian trung bình xử lý sự kiện từ CreateDate đến ProcessingAt
      có filter theo start_date, end_date, area (nếu truyền).

      Args:
          trino_connector: TrinoConnector instance
          start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
          end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
          area (str): tên khu vực ('Khu Liên Hợp', 'Bàu Bàng', ...)

      Returns:
          pd.DataFrame: 1 dòng với cột " " (chuỗi thời gian) hoặc "Không có dữ liệu"
      """
      if 'avg_processing_time' not in self._cache:
          if trino_connector:
              query = """
              WITH w AS (
                SELECT * FROM (
                  VALUES (
                    CAST(NULL AS timestamp with time zone),
                    CAST(NULL AS timestamp with time zone)
                  )
                ) AS v(start_local, end_local)
              """

              # Nếu có start/end date thì thêm UNION ALL
              if start_date and end_date:
                  query += f"""
                    UNION ALL
                    SELECT
                      with_timezone(CAST(TIMESTAMP '{start_date}' AS timestamp), 'Asia/Ho_Chi_Minh'),
                      with_timezone(
                        CASE
                          WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                          ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                        END,
                        'Asia/Ho_Chi_Minh'
                      )
                  """

              query += """
              ),
              src AS (
                SELECT
                  at_timezone(e."ProcessingAt", 'Asia/Ho_Chi_Minh') AS "ProcessingAt_local",
                  at_timezone(e."CreateDate",   'Asia/Ho_Chi_Minh') AS "CreateDate_local",
                  CASE e."Layers"."Area"
                    WHEN 'khu_lien_hop' THEN 'Khu Liên Hợp'
                    WHEN 'bau_bang'     THEN 'Bàu Bàng'
                    WHEN 'thoi_hoa'     THEN 'Thới Hòa'
                    WHEN 'my_phuoc_1'   THEN 'Mỹ Phước 1'
                    WHEN 'my_phuoc_2'   THEN 'Mỹ Phước 2'
                    WHEN 'my_phuoc_3'   THEN 'Mỹ Phước 3'
                    ELSE 'Không xác định'
                  END AS area
                FROM lakehouse.event e
                WHERE e."ProcessingAt" IS NOT NULL
                AND NOT (
                  e."SourceSystem" = 'Environment'
                  AND e."Layers"."Area" IN ('my_phuoc_2','my_phuoc_3','van_don','kcn_vd','ha_long')
                )
              ),
              calc AS (
                SELECT
                  CASE
                    WHEN w.start_local IS NOT NULL
                    AND w.end_local   IS NOT NULL
                    AND LEAST(s."ProcessingAt_local", w.end_local) > GREATEST(s."CreateDate_local", w.start_local)
                    THEN
                      to_unixtime(LEAST(s."ProcessingAt_local", w.end_local))
                      - to_unixtime(GREATEST(s."CreateDate_local", w.start_local))
                    ELSE NULL
                  END AS diff_seconds,
                  w.start_local,
                  w.end_local,
                  s.area
                FROM src s
                CROSS JOIN w
              """

              if area:
                  query += f" WHERE s.area = '{area}'"

              query += """
              )
              SELECT
                CASE
                  WHEN MAX(start_local) IS NULL OR MAX(end_local) IS NULL OR AVG(diff_seconds) IS NULL
                    THEN 'Không có dữ liệu'
                  ELSE
                    CONCAT(
                      LPAD(CAST(CAST(FLOOR(AVG(diff_seconds) / 3600) AS INTEGER) AS VARCHAR), 2, '0'), ' giờ ',
                      LPAD(CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 3600) / 60) AS INTEGER) AS VARCHAR), 2, '0'), ' phút ',
                      LPAD(CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 60)) AS INTEGER) AS VARCHAR), 2, '0'), ' giây'
                    )
                END AS " "
              FROM calc
              LIMIT 1
              """

              try:
                  result = trino_connector.execute_query(query)
                  if result is not None and not result.empty:
                      self._cache['avg_processing_time'] = result
                  else:
                      self._cache['avg_processing_time'] = pd.DataFrame({' ': ['Không có dữ liệu']})
              except Exception as e:
                  print(f"Lỗi khi thực thi query avg processing time: {str(e)}")
                  self._cache['avg_processing_time'] = pd.DataFrame({' ': ['Không có dữ liệu']})
          else:
              self._cache['avg_processing_time'] = pd.DataFrame({' ': ['Không có dữ liệu']})

      return self._cache['avg_processing_time']

    def get_avg_processed_duration(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
      """
      Tính thời gian trung bình xử lý sự kiện từ ProcessingAt đến ProcessedAt
      có filter theo start_date, end_date, area (nếu truyền).

      Args:
          trino_connector: TrinoConnector instance
          start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
          end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
          area (str): tên khu vực ('Khu Liên Hợp', 'Bàu Bàng', ...)

      Returns:
          pd.DataFrame: 1 dòng với cột " " (chuỗi thời gian) hoặc "Không có dữ liệu"
      """
      if 'avg_processed_duration' not in self._cache:
          if trino_connector:
              query = """
              WITH w AS (
                SELECT * FROM (
                  VALUES (
                    CAST(NULL AS timestamp with time zone),
                    CAST(NULL AS timestamp with time zone)
                  )
                ) AS v(start_local, end_local)
              """

              # Nếu có start/end date thì thêm UNION ALL
              if start_date and end_date:
                  query += f"""
                    UNION ALL
                    SELECT
                      with_timezone(CAST(TIMESTAMP '{start_date}' AS timestamp), 'Asia/Ho_Chi_Minh'),
                      with_timezone(
                        CASE
                          WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                          ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                        END,
                        'Asia/Ho_Chi_Minh'
                      )
                  """

              query += """
              ),
              src AS (
                SELECT
                  at_timezone(e."ProcessingAt", 'Asia/Ho_Chi_Minh') AS "ProcessingAt_local",
                  at_timezone(e."ProcessedAt",  'Asia/Ho_Chi_Minh') AS "ProcessedAt_local",
                  CASE e."Layers"."Area"
                    WHEN 'khu_lien_hop' THEN 'Khu Liên Hợp'
                    WHEN 'bau_bang'     THEN 'Bàu Bàng'
                    WHEN 'thoi_hoa'     THEN 'Thới Hòa'
                    WHEN 'my_phuoc_1'   THEN 'Mỹ Phước 1'
                    WHEN 'my_phuoc_2'   THEN 'Mỹ Phước 2'
                    WHEN 'my_phuoc_3'   THEN 'Mỹ Phước 3'
                    ELSE 'Không xác định'
                  END AS area
                FROM lakehouse.event e
                WHERE e."ProcessingAt" IS NOT NULL
                AND e."ProcessedAt"  IS NOT NULL
                AND NOT (
                  e."SourceSystem" = 'Environment'
                  AND e."Layers"."Area" IN ('my_phuoc_2','my_phuoc_3','van_don','kcn_vd','ha_long')
                )
              ),
              calc AS (
                SELECT
                  CASE
                    WHEN w.start_local IS NOT NULL
                    AND w.end_local   IS NOT NULL
                    AND LEAST(s."ProcessedAt_local", w.end_local) > GREATEST(s."ProcessingAt_local", w.start_local)
                    THEN
                      to_unixtime(LEAST(s."ProcessedAt_local", w.end_local))
                      - to_unixtime(GREATEST(s."ProcessingAt_local", w.start_local))
                    ELSE NULL
                  END AS diff_seconds,
                  w.start_local,
                  w.end_local,
                  s.area
                FROM src s
                CROSS JOIN w
              """

              if area:
                  query += f" WHERE s.area = '{area}'"

              query += """
              )
              SELECT
                CASE
                  WHEN MAX(start_local) IS NULL OR MAX(end_local) IS NULL OR AVG(diff_seconds) IS NULL
                    THEN 'Không có dữ liệu'
                  ELSE
                    CONCAT(
                      LPAD(CAST(CAST(FLOOR(AVG(diff_seconds) / 3600) AS INTEGER) AS VARCHAR), 2, '0'), ' giờ ',
                      LPAD(CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 3600) / 60) AS INTEGER) AS VARCHAR), 2, '0'), ' phút ',
                      LPAD(CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 60)) AS INTEGER) AS VARCHAR), 2, '0'), ' giây'
                    )
                END AS " "
              FROM calc
              LIMIT 1
              """

              try:
                  result = trino_connector.execute_query(query)
                  if result is not None and not result.empty:
                      self._cache['avg_processed_duration'] = result
                  else:
                      self._cache['avg_processed_duration'] = pd.DataFrame({' ': ['Không có dữ liệu']})
              except Exception as e:
                  print(f"Lỗi khi thực thi query avg processed duration: {str(e)}")
                  self._cache['avg_processed_duration'] = pd.DataFrame({' ': ['Không có dữ liệu']})
          else:
              self._cache['avg_processed_duration'] = pd.DataFrame({' ': ['Không có dữ liệu']})

      return self._cache['avg_processed_duration']
    def get_avg_loss_connection(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
      """
      Tính thời gian trung bình từ CreateDate đến AutoCheckAt
      có filter theo start_date, end_date, area (nếu truyền).

      Args:
          trino_connector: TrinoConnector instance
          start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
          end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
          area (str): tên khu vực ('Khu Liên Hợp', 'Bàu Bàng', ...)

      Returns:
          pd.DataFrame: 1 dòng với cột " " (chuỗi thời gian) hoặc "Không có dữ liệu"
      """
      if 'avg_created_to_autocheck_duration' not in self._cache:
          if trino_connector:
              query = """
              WITH w AS (
                SELECT * FROM (
                  VALUES (
                    CAST(NULL AS timestamp with time zone),
                    CAST(NULL AS timestamp with time zone)
                  )
                ) AS v(start_local, end_local)
              """

              # Nếu có start/end date thì thêm UNION ALL
              if start_date and end_date:
                  query += f"""
                    UNION ALL
                    SELECT
                      with_timezone(CAST(TIMESTAMP '{start_date}' AS timestamp), 'Asia/Ho_Chi_Minh'),
                      with_timezone(
                        CASE
                          WHEN extract(hour   FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          AND extract(minute FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          AND extract(second FROM CAST(TIMESTAMP '{end_date}' AS timestamp)) = 0
                          THEN date_add('day', 1, CAST(TIMESTAMP '{end_date}' AS timestamp))
                          ELSE CAST(TIMESTAMP '{end_date}' AS timestamp)
                        END,
                        'Asia/Ho_Chi_Minh'
                      )
                  """

              query += """
              ),
              src AS (
                SELECT
                  at_timezone(e."AutoCheckAt", 'Asia/Ho_Chi_Minh') AS "AutoCheckAt_local",
                  at_timezone(e."CreateDate",  'Asia/Ho_Chi_Minh') AS "CreateDate_local",
                  CASE e."Layers"."Area"
                    WHEN 'khu_lien_hop' THEN 'Khu Liên Hợp'
                    WHEN 'bau_bang'     THEN 'Bàu Bàng'
                    WHEN 'thoi_hoa'     THEN 'Thới Hòa'
                    WHEN 'my_phuoc_1'   THEN 'Mỹ Phước 1'
                    WHEN 'my_phuoc_2'   THEN 'Mỹ Phước 2'
                    WHEN 'my_phuoc_3'   THEN 'Mỹ Phước 3'
                    ELSE 'Không xác định'
                  END AS area
                FROM lakehouse.event e
                WHERE e."AutoCheckAt" IS NOT NULL
                AND NOT (
                  e."SourceSystem" = 'Environment'
                  AND e."Layers"."Area" IN ('my_phuoc_2','my_phuoc_3','van_don','kcn_vd','ha_long')
                )
              ),
              calc AS (
                SELECT
                  CASE
                    WHEN w.start_local IS NOT NULL
                    AND w.end_local   IS NOT NULL
                    AND LEAST(s."AutoCheckAt_local", w.end_local) > GREATEST(s."CreateDate_local", w.start_local)
                    THEN
                      to_unixtime(LEAST(s."AutoCheckAt_local", w.end_local))
                      - to_unixtime(GREATEST(s."CreateDate_local", w.start_local))
                    ELSE NULL
                  END AS diff_seconds,
                  w.start_local,
                  w.end_local,
                  s.area
                FROM src s
                CROSS JOIN w
              """

              if area:
                  query += f" WHERE s.area = '{area}'"

              query += """
              )
              SELECT
                CASE
                  WHEN MAX(start_local) IS NULL OR MAX(end_local) IS NULL OR AVG(diff_seconds) IS NULL
                    THEN 'Không có dữ liệu'
                  ELSE
                    CONCAT(
                      LPAD(CAST(CAST(FLOOR(AVG(diff_seconds) / 3600) AS INTEGER) AS VARCHAR), 2, '0'), ' giờ ',
                      LPAD(CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 3600) / 60) AS INTEGER) AS VARCHAR), 2, '0'), ' phút ',
                      LPAD(CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 60)) AS INTEGER) AS VARCHAR), 2, '0'), ' giây'
                    )
                END AS " "
              FROM calc
              LIMIT 1
              """

              try:
                  result = trino_connector.execute_query(query)
                  if result is not None and not result.empty:
                      self._cache['avg_created_to_autocheck_duration'] = result
                  else:
                      self._cache['avg_created_to_autocheck_duration'] = pd.DataFrame({' ': ['Không có dữ liệu']})
              except Exception as e:
                  print(f"Lỗi khi thực thi query avg created→autocheck duration: {str(e)}")
                  self._cache['avg_created_to_autocheck_duration'] = pd.DataFrame({' ': ['Không có dữ liệu']})
          else:
              self._cache['avg_created_to_autocheck_duration'] = pd.DataFrame({' ': ['Không có dữ liệu']})

      return self._cache['avg_created_to_autocheck_duration']
    def get_notification_statistics(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """
        Get notification statistics data grouped by system and event name
        
        Args:
            trino_connector: TrinoConnector instance
            start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            area (str): tên khu vực ('Khu Liên Hợp', 'Bàu Bàng', ...)
            
        Returns:
            pd.DataFrame: DataFrame with columns "Hệ thống", "Tên thông báo", "Số lượng"
        """
        if 'notification_statistics' not in self._cache:
            if trino_connector:
                query = """
                SELECT
                  system_name AS "Hệ thống",
                  EventName AS "Tên thông báo",
                  SUM(cnt) AS "Số lượng"
                FROM (
                    SELECT
                      lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS CreateDate_local,
                      lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS log_date,
                      lakehouse.event."ResolvedDate" AT TIME ZONE 'Asia/Ho_Chi_Minh' AS ResolvedDate_local,
                      lakehouse.event."EventName",

                      CASE lakehouse.event."SourceSystem"
                        WHEN 'EMS' THEN 'Năng lượng'
                        WHEN 'Security' THEN 'An ninh'
                        WHEN 'Environment' THEN 'Môi trường'
                        WHEN 'CyberSecurity' THEN 'An ninh mạng'
                        ELSE 'Không xác định'
                      END AS system_name,

                      CASE lakehouse.event."Level"
                        WHEN 0 THEN 'Nhắc nhở'
                        WHEN 1 THEN 'Thông báo'
                        WHEN 2 THEN 'Khẩn cấp'
                        ELSE 'Không xác định'
                      END AS level_name,

                      CASE lakehouse.event."Status"
                        WHEN 0 THEN 'Chưa xác minh'
                        WHEN 1 THEN 'Đang xử lý'
                        WHEN 2 THEN 'Đã xử lý'
                        ELSE 'Không xác định'
                      END AS status_name,

                      CASE lakehouse.event."Layers"."Area"
                        WHEN 'khu_lien_hop' THEN 'Khu Liên Hợp'
                        WHEN 'bau_bang' THEN 'Bàu Bàng'
                        WHEN 'thoi_hoa' THEN 'Thới Hòa'
                        WHEN 'my_phuoc_1' THEN 'Mỹ Phước 1'
                        WHEN 'my_phuoc_2' THEN 'Mỹ Phước 2'
                        WHEN 'my_phuoc_3' THEN 'Mỹ Phước 3'
                        ELSE 'Không xác định'
                      END AS area,

                      CONCAT (
                        CASE lakehouse.asset."Type"
                          WHEN 'lighting_cabinet' THEN 'Tủ chiếu sáng: '
                          WHEN 'traffic_cabinet' THEN 'Tủ giao thông: '
                          WHEN 'distribution_cabinet' THEN 'Tủ phân phối: '
                          WHEN 'handy_talkie' THEN 'Bộ đàm: '
                          WHEN 'camera_bullet' THEN 'Camera bullet: '
                          WHEN 'camera_ptz' THEN 'Camera PTZ: '
                          WHEN 'backhoe' THEN 'Xe xúc đào: '
                          WHEN 'cranes' THEN 'Cần cẩu: '
                          WHEN 'dump truck' THEN 'Xe ben: '
                          WHEN 'excavator' THEN 'Máy xúc: '
                          WHEN 'firetruck' THEN 'Xe cứu hỏa: '
                          WHEN 'garbage' THEN 'Xe rác: '
                          WHEN 'loader' THEN 'Xe xúc: '
                          WHEN 'manlift' THEN 'Xe nâng người: '
                          WHEN 'sweeper' THEN 'Xe quét đường: '
                          WHEN 'tractor' THEN 'Máy kéo: '
                          WHEN 'truck' THEN 'Xe tải: '
                          WHEN 'watering' THEN 'Xe tưới nước: '
                          ELSE 'Tài sản: '
                        END,
                        COALESCE(lakehouse.event."AssetID", ''),
                        CASE
                          WHEN lakehouse.event."SourceSystem" = 'EMS'
                            AND (
                              lakehouse.event."Detail"."Parameter" IS NOT NULL
                              OR lakehouse.event."Detail"."Value" IS NOT NULL
                              OR lakehouse.event."Detail"."Threshold" IS NOT NULL
                            ) THEN ' | ' || CONCAT_WS (
                              ' | ',
                              IF (lakehouse.event."Detail"."Parameter" IS NOT NULL, 'Thông số: ' || lakehouse.event."Detail"."Parameter", NULL),
                              IF (lakehouse.event."Detail"."Value" IS NOT NULL, 'Giá trị: ' || lakehouse.event."Detail"."Value", NULL),
                              IF (lakehouse.event."Detail"."Threshold" IS NOT NULL, 'Giá trị ngưỡng: ' || lakehouse.event."Detail"."Threshold", NULL)
                            )
                          WHEN lakehouse.event."SourceSystem" = 'Security'
                            AND lakehouse.event."Detail"."license_number" IS NOT NULL THEN ' | Biển số xe: ' || lakehouse.event."Detail"."license_number"
                          WHEN lakehouse.event."SourceSystem" = 'Environment'
                            AND lakehouse.event."Detail"."pumpStation" IS NOT NULL THEN ' | Trạm bơm: ' || lakehouse.event."Detail"."pumpStation"
                          ELSE ''
                        END
                      ) AS Content,

                      CASE
                        WHEN lakehouse.event."IsActive" IS NOT NULL THEN 1
                        ELSE 0
                      END AS cnt

                    FROM
                      lakehouse.event
                      LEFT JOIN lakehouse.asset ON lakehouse.event."AssetID" = lakehouse.asset."AssetID"
                     WHERE NOT (
                      lakehouse.event."SourceSystem" = 'Environment'
                      AND lakehouse.event."Layers"."Area" IN ('my_phuoc_2', 'my_phuoc_3', 'van_don', 'kcn_vd', 'ha_long')
                  )
                """

                # Thêm điều kiện thời gian nếu có
                if start_date and end_date:
                    query += f"""
                      AND (
                        lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
                      ) >= TIMESTAMP '{start_date}'
                      AND (
                        lakehouse.event."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh'
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

                query += ") AS virtual_table"

                # Thêm điều kiện area nếu có
                if area:
                    query += f" WHERE area = '{area}'"

                query += """
                GROUP BY
                  system_name,
                  EventName
                ORDER BY "Số lượng" DESC
                LIMIT 1000
                """

                try:
                    result = trino_connector.execute_query(query)
                    if result is not None and not result.empty:
                        self._cache['notification_statistics'] = result
                    else:
                        print("Không có dữ liệu trả về từ query notification statistics.")
                        self._cache['notification_statistics'] = pd.DataFrame({
                            'Hệ thống': [], 
                            'Tên thông báo': [], 
                            'Số lượng': []
                        })
                except Exception as e:
                    print(f"Lỗi khi thực thi query notification statistics: {str(e)}")
                    self._cache['notification_statistics'] = pd.DataFrame({
                        'Hệ thống': [], 
                        'Tên thông báo': [], 
                        'Số lượng': []
                    })
            else:
                # Fallback data nếu không có trino_connector
                self._cache['notification_statistics'] = pd.DataFrame({
                    'Hệ thống': [], 
                    'Tên thông báo': [], 
                    'Số lượng': []
                })
        return self._cache['notification_statistics']

    def get_avg_downtime_by_device_type(self, trino_connector=None, start_date=None, end_date=None, area=None) -> pd.DataFrame:
        """
        Get average downtime by device type
        
        Args:
            trino_connector: TrinoConnector instance
            start_date (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            end_date   (str): yyyy-MM-dd HH:mm:ss (timezone Asia/Ho_Chi_Minh)
            area (str): tên khu vực ('Khu Liên Hợp', 'Bàu Bàng', ...)
            
        Returns:
            pd.DataFrame: DataFrame with columns "Loại thiết bị", "Thời gian ngừng hoạt động trung bình", "Tỷ lệ % thiết bị hoạt động bình thường"
        """
        if 'avg_downtime_by_device_type' not in self._cache:
            if trino_connector:
                query = """
                WITH
                w AS (
                  -- Hàng NULL-NULL để không tham chiếu biến khi không có filter
                  SELECT * FROM (
                    VALUES (
                      CAST(NULL AS timestamp with time zone),
                      CAST(NULL AS timestamp with time zone)
                    )
                  ) AS v(start_local, end_local)
                """

                # Nếu có start/end date thì thêm UNION ALL
                if start_date and end_date:
                    query += f"""
                      UNION ALL
                      SELECT
                        -- Tham số ngày của Metabase là timestamp (không tz) → gắn 'Asia/Ho_Chi_Minh' thành ts with tz
                        with_timezone(CAST(TIMESTAMP '{start_date}' AS timestamp), 'Asia/Ho_Chi_Minh') AS start_local,
                        with_timezone(CAST(TIMESTAMP '{end_date}' AS timestamp), 'Asia/Ho_Chi_Minh') AS end_local
                    """

                query += """
                ),

                typed AS (
                  SELECT
                    CASE
                      WHEN e."AssetType" IN ('camera_bullet','camera_ptz') THEN 'Camera'
                      WHEN e."AssetType" IN ('traffic_cabinet','distribution_cabinet','lighting_cabinet') THEN 'Tủ điện'
                      WHEN e."AssetType" = 'handy_talkie' THEN 'Bộ đàm'
                      WHEN e."AssetType" = 'sweeper' OR e."AssetType" IS NULL THEN 'Xe'
                      ELSE e."AssetType"
                    END AS device_type,
                    (e."AutoCheckAt" AT TIME ZONE 'Asia/Ho_Chi_Minh') AS auto_local,
                    (e."CreateDate"  AT TIME ZONE 'Asia/Ho_Chi_Minh') AS create_local
                  FROM lakehouse.event e
                  WHERE e."AutoCheckAt" IS NOT NULL
                  	AND NOT (
                        e."SourceSystem" = 'Environment' 
                        AND e."Layers"."Area" IN ('my_phuoc_2', 'my_phuoc_3', 'van_don', 'kcn_vd', 'ha_long')
                      )
                """

                # Thêm điều kiện thời gian nếu có
                if start_date and end_date:
                    query += f"""
                      AND (e."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh') >= TIMESTAMP '{start_date}'
                      AND (e."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh') < (
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
                else:
                    # Default: [today-7d, today)
                    query += """
                      AND (e."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh') >= (CURRENT_DATE - INTERVAL '7' DAY)
                      AND (e."CreateDate" AT TIME ZONE 'Asia/Ho_Chi_Minh') < CURRENT_DATE
                    """

                # Thêm điều kiện area nếu có
                if area:
                    query += f"""
                      AND
                        CASE e."Layers"."Area"
                          WHEN 'khu_lien_hop' THEN 'Khu Liên Hợp'
                          WHEN 'bau_bang'     THEN 'Bàu Bàng'
                          WHEN 'thoi_hoa'     THEN 'Thới Hòa'
                          WHEN 'my_phuoc_1'   THEN 'Mỹ Phước 1'
                          WHEN 'my_phuoc_2'   THEN 'Mỹ Phước 2'
                          WHEN 'my_phuoc_3'   THEN 'Mỹ Phước 3'
                          ELSE 'Không xác định'
                        END = '{area}'
                    """

                query += """
                ),

                diffs AS (
                  SELECT
                    t.device_type,
                    t.auto_local,
                    t.create_local,
                    w.start_local,
                    w.end_local,
                    -- Chỉ tính khi có overlap trong cửa sổ
                    CASE
                      WHEN LEAST(t.auto_local, w.end_local) > GREATEST(t.create_local, w.start_local)
                        THEN to_unixtime(LEAST(t.auto_local, w.end_local))
                           - to_unixtime(GREATEST(t.create_local, w.start_local))
                      ELSE NULL
                    END AS diff_seconds,
                    -- Mẫu số khi có cửa sổ; nếu cần fallback sẽ xử lý ở dưới
                    to_unixtime(w.end_local) - to_unixtime(w.start_local) AS window_seconds_override
                  FROM typed t
                  CROSS JOIN w
                )

                SELECT
                  device_type AS "Loại thiết bị",

                  CASE
                    WHEN AVG(diff_seconds) IS NULL THEN 'Không có dữ liệu'
                    ELSE
                      CAST(CAST(FLOOR(AVG(diff_seconds) / 3600) AS BIGINT) AS VARCHAR) || ' giờ ' ||
                      CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 3600) / 60) AS BIGINT) AS VARCHAR) || ' phút ' ||
                      CAST(CAST(FLOOR(MOD(AVG(diff_seconds), 60)) AS BIGINT) AS VARCHAR) || ' giây'
                  END AS "Thời gian ngừng hoạt động trung bình",

                  CAST(
                    ROUND(
                      100 - (
                        COALESCE(AVG(diff_seconds), 0) * 100.0
                      ) / NULLIF(
                            COALESCE(
                              MAX(window_seconds_override),
                              to_unixtime(MAX(auto_local)) - to_unixtime(MIN(create_local))
                            ),
                            0
                          ),
                      2
                    ) AS DECIMAL(5,2)
                  ) AS "Tỷ lệ % thiết bị hoạt động bình thường",

                  CAST(
                    ROUND(
                      100 - (
                        COALESCE(AVG(diff_seconds), 0) * 100.0
                      ) / NULLIF(
                            COALESCE(
                              MAX(window_seconds_override),
                              to_unixtime(MAX(auto_local)) - to_unixtime(MIN(create_local))
                            ),
                            0
                          ),
                      2
                    ) AS DECIMAL(5,2)
                  ) AS sort
                FROM diffs
                GROUP BY device_type
                ORDER BY sort DESC NULLS LAST
                LIMIT 1000
                """

                try:
                    result = trino_connector.execute_query(query)
                    if result is not None and not result.empty:
                        self._cache['avg_downtime_by_device_type'] = result
                    else:
                        print("Không có dữ liệu trả về từ query avg downtime by device type.")
                        self._cache['avg_downtime_by_device_type'] = pd.DataFrame({
                            'Loại thiết bị': [], 
                            'Thời gian ngừng hoạt động trung bình': [], 
                            'Tỷ lệ % thiết bị hoạt động bình thường': []
                        })
                except Exception as e:
                    print(f"Lỗi khi thực thi query avg downtime by device type: {str(e)}")
                    self._cache['avg_downtime_by_device_type'] = pd.DataFrame({
                        'Loại thiết bị': [], 
                        'Thời gian ngừng hoạt động trung bình': [], 
                        'Tỷ lệ % thiết bị hoạt động bình thường': []
                    })
            else:
                # Fallback data nếu không có trino_connector
                self._cache['avg_downtime_by_device_type'] = pd.DataFrame({
                    'Loại thiết bị': [], 
                    'Thời gian ngừng hoạt động trung bình': [], 
                    'Tỷ lệ % thiết bị hoạt động bình thường': []
                })
        return self._cache['avg_downtime_by_device_type']
    


    
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

def get_viz1_query_manager() -> viz1_QueryManager:
    """Get or create global query manager instance"""
    global _query_manager
    
    if _query_manager is None:
        # Tạo QueryManager với dữ liệu placeholder vì chúng ta sử dụng SQL queries trực tiếp
        _query_manager = viz1_QueryManager()
    
    return _query_manager

def clear_global_query_manager():
    """Clear global query manager instance"""
    global _query_manager
    if _query_manager:
        _query_manager.clear_cache()
        _query_manager = None
