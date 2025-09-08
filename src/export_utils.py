import io
import pandas as pd
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .viz1_query_manager import get_viz1_query_manager
from openpyxl import load_workbook
from openpyxl.chart import PieChart, Reference
from openpyxl.drawing.image import Image
from io import BytesIO




###################### SHEET BÁO CÁO TỔNG QUAN ##############################
def fill_overview_report_sheet(ws, wb, trino_connector=None, start_date='2025-08-08', end_date='2025-09-04', area=None):
    """Fill the 'Báo cáo tổng quan' sheet with dashboard data.
    
    Args:
        ws: Worksheet object for the overview report sheet
        wb: Workbook object
        trino_connector: Database connector
        start_date: Start date for data query
        end_date: End date for data query
        area: Area filter for data query
    """
    
    img = Image("./assets/becamex.png")
    img.width = 200
    img.height = 50
    ws.add_image(img, 'A2')
    # From here on, do best-effort filling; never fail the whole export
    qm = get_viz1_query_manager()

    try:
        print("fill_overview_report_sheet: Getting total events data...")
        total_events_df = qm.get_total_events_card_data(
            trino_connector=trino_connector,
            start_date=start_date,
            end_date=end_date,
            area=area
        )
        total_events_value = 0
        if total_events_df is not None and not total_events_df.empty and 'total_events' in total_events_df.columns:
            total_events_value = total_events_df['total_events'].iloc[0]
        ws['D10'] = total_events_value
        print(f"fill_overview_report_sheet: Set total_events_value = {total_events_value} at D10")
    except Exception as e:
        print(f"fill_overview_report_sheet total_events error: {e}")
        ws['D10'] = 0

    try:
        print("fill_overview_report_sheet: Getting system pie data...")
        system_pie_df = qm.get_system_events_pie_data(
            trino_connector=trino_connector,
            start_date=start_date,
            end_date=end_date,
            area=area
        )
        sys_info_scalar = 0
        if system_pie_df is not None and not system_pie_df.empty and 'total_events' in system_pie_df.columns:
            sys_info_scalar = int(system_pie_df['total_events'].sum())
        ws['D11'] = sys_info_scalar
        print(f"fill_overview_report_sheet: Set sys_info_scalar = {sys_info_scalar} at D11")
    except Exception as e:
        print(f"fill_overview_report_sheet system_pie error: {e}")
        ws['D11'] = 0

    try:
        print("fill_overview_report_sheet: Getting avg processed duration data...")
        avg_processed_df = qm.get_avg_processed_duration(
            trino_connector=trino_connector,
            start_date=start_date,
            end_date=end_date,
            area=area
        )
        avg_processed_value = ''
        if avg_processed_df is not None and not avg_processed_df.empty:
            avg_processed_value = str(avg_processed_df.iloc[0][avg_processed_df.columns[0]])
        ws['D12'] = avg_processed_value
        print(f"fill_overview_report_sheet: Set avg_processed_duration = '{avg_processed_value}' at D12")
    except Exception as e:
        print(f"fill_overview_report_sheet avg_processed_duration error: {e}")
        ws['D12'] = ''

    try:
        print("fill_overview_report_sheet: Getting avg loss connection data...")
        avg_loss_df = qm.get_avg_loss_connection(
            trino_connector=trino_connector,
            start_date=start_date,
            end_date=end_date,
            area=area
        )
        avg_loss_value = ''
        if avg_loss_df is not None and not avg_loss_df.empty:
            avg_loss_value = str(avg_loss_df.iloc[0][avg_loss_df.columns[0]])
        ws['D13'] = avg_loss_value
        print(f"fill_overview_report_sheet: Set avg_loss_connection = '{avg_loss_value}' at D13")
    except Exception as e:
        print(f"fill_overview_report_sheet avg_loss_connection error: {e}")
        ws['D13'] = ''

    # Insert Pie chart from hidden data sheet (best-effort)
    try:
        print(f"fill_overview_report_sheet: Checking system_pie_df...")
        if 'system_pie_df' in locals() and system_pie_df is not None and not system_pie_df.empty:
            print(f"fill_overview_report_sheet: system_pie_df found with {len(system_pie_df)} rows")
            print(f"fill_overview_report_sheet: system_pie_df columns: {list(system_pie_df.columns)}")
            
            # Create or get hidden data sheet (always create new to avoid merged cell issues)
            # if 'Data' in wb.sheetnames:
            #     # Remove existing Data sheet to avoid merged cell conflicts
            #     wb.remove(wb['Data'])
            #     print("fill_overview_report_sheet: Removed existing 'Data' sheet")
            
            ws_data = wb.create_sheet(title='Data_temp')
            print("fill_overview_report_sheet: Created new 'Data' sheet")

            # Write headers
            ws_data['A1'] = 'Hệ thống'
            ws_data['B1'] = 'Số lượng'
            r = 2
            for _, row in system_pie_df.iterrows():
                system_name = str(row.get('Tổng thông báo hệ thống', ''))
                event_count = int(row.get('total_events', 0)) if pd.notna(row.get('total_events', 0)) else 0
                ws_data[f'A{r}'] = system_name
                ws_data[f'B{r}'] = event_count
                print(f"fill_overview_report_sheet: Writing data - {system_name}: {event_count}")
                r += 1

            # Build pie from Data sheet
            if r > 2:
                print(f"fill_overview_report_sheet: Creating pie chart with {r-2} entries")
                pie = PieChart()
                labels = Reference(ws_data, min_col=1, min_row=2, max_row=r-1)
                data = Reference(ws_data, min_col=2, min_row=1, max_row=r-1)  # include header for title
                pie.add_data(data, titles_from_data=True)
                pie.set_categories(labels)


                # Anchor at H10 and size to span roughly H–L
                print("fill_overview_report_sheet: Adding pie chart to worksheet at H10")
                ws.add_chart(pie, 'H12')
                try:
                    pie.width = 17  # approx width to span H–L
                    pie.height = 6.5
                    print("fill_overview_report_sheet: Set pie chart dimensions")
                except Exception as e:
                    print(f"fill_overview_report_sheet: Error setting pie chart dimensions: {e}")

            # Hide data sheet
            try:
                ws_data.sheet_state = 'hidden'
                print("fill_overview_report_sheet: Hidden 'Data' sheet")
            except Exception as e:
                print(f"fill_overview_report_sheet: Error hiding 'Data' sheet: {e}")
        else:
            print("fill_overview_report_sheet: system_pie_df not available or empty")
    except Exception as e:
        print(f"fill_overview_report_sheet pie chart error: {e}")
        import traceback
        traceback.print_exc()

    # Energy numbers
    try:
        print("fill_overview_report_sheet: Getting energy data...")
        from .viz2_query_manager import get_viz2_query_manager
        q2 = get_viz2_query_manager()
        df_cons = q2.get_consumed_electricity(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
        consumed_value = float(df_cons.iloc[0, 0]) if df_cons is not None and not df_cons.empty else 0
        ws['D27'] = consumed_value
        print(f"fill_overview_report_sheet: Set consumed_electricity = {consumed_value} at D27")
    except Exception as e:
        print(f"fill_overview_report_sheet consumed_electricity error: {e}")
        ws['D27'] = 0

    try:
        df_cost = q2.get_energy_cost(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
        cost_value = float(df_cost.iloc[0, 0]) if df_cost is not None and not df_cost.empty else 0
        ws['J27'] = cost_value
        print(f"fill_overview_report_sheet: Set energy_cost = {cost_value} at J27")
    except Exception as e:
        print(f"fill_overview_report_sheet energy_cost error: {e}")
        ws['J27'] = 0

    try:
        df_green = q2.get_green_energy_percentage(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
        green_value = float(df_green.iloc[0, 0]) if df_green is not None and not df_green.empty else 0
        ws['D28'] = green_value
        print(f"fill_overview_report_sheet: Set green_energy_percentage = {green_value} at D28")
    except Exception as e:
        print(f"fill_overview_report_sheet green_energy_percentage error: {e}")
        ws['D28'] = 0

    try:
        df_co2 = q2.get_CO2_emission(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
        co2_value = float(df_co2.iloc[0, 0]) if df_co2 is not None and not df_co2.empty else 0
        ws['J28'] = co2_value
        print(f"fill_overview_report_sheet: Set co2_emission = {co2_value} at J28")
    except Exception as e:
        print(f"fill_overview_report_sheet co2_emission error: {e}")
        ws['J28'] = 0


def export_excel_data(trino_connector=None, start_date='2025-08-08', end_date='2025-09-04', area=None):
    """Create a copy from template.xlsx and fill cells with current dashboard values.

    Returns bytes of the resulting workbook for download.
    """
    try:
        # Locate template (resolve robustly regardless of CWD)
        base_dir = os.path.abspath(os.path.dirname(__file__))
        print(f"export_excel_data base_dir: {base_dir}")

        possible_paths = [
        os.path.join(base_dir, 'assets', 'template.xlsx'),  
        os.path.join(base_dir, 'template.xlsx'),            
        'assets/template.xlsx',                             
        'template.xlsx'  ]
        
        template_path = None
        for p in possible_paths:
            if os.path.exists(p):
                template_path = p
                break
        if template_path is None:
            raise FileNotFoundError("template.xlsx not found in expected paths.")

        # Load workbook and select the 'Báo cáo tổng quan' sheet
        wb = load_workbook(template_path)
        if 'Báo cáo tổng quan' in wb.sheetnames:
            ws = wb['Báo cáo tổng quan']
        else:
            print("Warning: 'Báo cáo tổng quan' sheet not found, using active sheet")
            ws = wb.active
    except Exception as e:
        print(f"export_excel_data error loading template: {e}")
        # Fallback: minimal workbook with error details
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Export"
            ws['A1'] = "Export failed while loading template"
            ws['A2'] = str(e)
            ws['A4'] = "Ensure template.xlsx exists and is readable."
            fallback = BytesIO()
            wb.save(fallback)
            fallback.seek(0)
            return fallback.getvalue()
        except Exception as inner:
            print(f"export_excel_data fallback error: {inner}")
            return None

    # Fill the overview report sheet with data
    print(f"export_excel_data: Starting to fill overview report sheet...")
    print(f"export_excel_data: Using worksheet '{ws.title}'")
    fill_overview_report_sheet(ws, wb, trino_connector, start_date, end_date, area)
    print(f"export_excel_data: Finished filling overview report sheet")

    # Save to bytes (always)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()



def create_dashboard_pdf():
    """Create PDF of the dashboard using JavaScript html2canvas and jsPDF - Optimized version"""
    try:
        print("Starting optimized PDF creation...")
        
        # Optimized Chrome options for faster performance
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Skip loading images for faster rendering
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to the dashboard
            dashboard_url = "http://127.0.0.1:8050"
            print(f"Navigating to: {dashboard_url}")
            driver.get(dashboard_url)
            
            # Reduced wait time for page load
            wait = WebDriverWait(driver, 15)  # Reduced from 30 to 15
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
            
            # Reduced wait for charts to load
            print("Waiting for charts to load...")
            time.sleep(1)  # Reduced from 3 to 1 second
            
            # Use local libraries instead of CDN for faster loading
            print("Loading local JavaScript libraries...")
            
            # Load html2canvas from local assets
            html2canvas_script = """
            var script = document.createElement('script');
            script.src = '/assets/js/html2canvas.min.js';
            document.head.appendChild(script);
            """
            driver.execute_script(html2canvas_script)
            time.sleep(0.5)  # Reduced wait time
            
            # Load jsPDF from local assets
            jspdf_script = """
            var script = document.createElement('script');
            script.src = '/assets/js/jspdf.js';
            document.head.appendChild(script);
            """
            driver.execute_script(jspdf_script)
            time.sleep(0.5)  # Reduced wait time
            
            # Optimized PDF creation script
            print("Creating PDF with optimized settings...")
            
            pdf_creation_script = """
            return new Promise((resolve, reject) => {
                // Reduced wait time for libraries
                setTimeout(() => {
                    try {
                        const printArea = document.getElementById("mainContainer") || document.body;
                        
                        // Reduced scale from 3 to 1.5 for faster rendering
                        html2canvas(printArea, {
                            scale: 1.5,
                            useCORS: true,
                            allowTaint: true,
                            backgroundColor: '#000000',
                            logging: false,
                            width: printArea.scrollWidth,
                            height: printArea.scrollHeight
                        }).then(function(canvas) {
                            var imgData = canvas.toDataURL('image/jpeg', 0.8); // Use JPEG with compression
                            var doc = new jsPDF('p', 'mm', "a4");
                            
                            const pageHeight = doc.internal.pageSize.getHeight();
                            const imgWidth = doc.internal.pageSize.getWidth();
                            var imgHeight = canvas.height * imgWidth / canvas.width;
                            var heightLeft = imgHeight;
                            
                            var position = 5; // Reduced padding

                            doc.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
                            heightLeft -= pageHeight;

                            while (heightLeft >= 0) {
                                position += heightLeft - imgHeight;
                                doc.addPage();
                                doc.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
                                heightLeft -= pageHeight;
                            }
                            
                            // Get PDF as base64 string
                            var pdfOutput = doc.output('datauristring');
                            resolve(pdfOutput);
                        }).catch(function(error) {
                            reject(error);
                        });
                    } catch (error) {
                        reject(error);
                    }
                }, 1000); // Reduced from 2000 to 1000ms
            });
            """
            
            # Execute the PDF creation script
            pdf_data_url = driver.execute_async_script(pdf_creation_script)
            
            if pdf_data_url:
                # Extract base64 data from data URL
                pdf_base64 = pdf_data_url.split(',')[1]
                pdf_content = bytes(pdf_base64, 'utf-8')
                
                # Decode base64 to get actual PDF bytes
                import base64
                pdf_bytes = base64.b64decode(pdf_content)
                
                print(f"PDF created successfully, size: {len(pdf_bytes)} bytes")
                return pdf_bytes
            else:
                print("Failed to create PDF")
                return None
                
        finally:
            driver.quit()
            print("Chrome driver closed")
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None
