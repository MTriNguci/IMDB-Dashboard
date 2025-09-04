import io
import pandas as pd
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
from .query_manager import get_query_manager

def create_excel_data(movies, series, movies_splits, series_splits):
    """Create Excel data for all chart visualizations using EXACT same queries from dash files"""
    
    # Get query manager to use EXACT same queries as dash files
    query_manager = get_query_manager(movies, series, movies_splits, series_splits)
    
    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Get all data using EXACT same queries as dash files
        all_data = query_manager.get_all_data()
        raw_data = query_manager.get_raw_data()
        
        # Overview Tab Data (from dash1) - using EXACT same queries
        overview_data = all_data['overview']
        overview_data['parental_guide'].to_excel(writer, sheet_name='Overview_Parental_Guide', index=False)
        overview_data['genre'].to_excel(writer, sheet_name='Overview_Genres', index=False)
        overview_data['country'].to_excel(writer, sheet_name='Overview_Countries', index=False)
        overview_data['ratings'].to_excel(writer, sheet_name='Overview_Ratings', index=False)
        
        # Content Creators Tab Data (from dash2) - using EXACT same queries
        creators_data = all_data['content_creators']
        creators_data['creators'].to_excel(writer, sheet_name='Creators_Top_Creators', index=False)
        creators_data['production_company'].to_excel(writer, sheet_name='Creators_Production_Companies', index=False)
        creators_data['stars'].to_excel(writer, sheet_name='Creators_Top_Stars', index=False)
        creators_data['language'].to_excel(writer, sheet_name='Creators_Languages', index=False)
        
        # Parental Guide Tab Data (from dash3) - using EXACT same queries
        parental_data = all_data['parental_guide']
        parental_data['mean_votes'].to_excel(writer, sheet_name='Parental_Guide_Mean_Votes', index=False)
        parental_data['count'].to_excel(writer, sheet_name='Parental_Guide_Count', index=False)
        
        # Year Tab Data (from dash4) - using EXACT same queries
        year_data = all_data['year']
        year_data['work_count'].to_excel(writer, sheet_name='Year_Work_Count', index=False)
        year_data['mean_votes'].to_excel(writer, sheet_name='Year_Mean_Votes', index=False)
        
        # Raw Data
        raw_data['movies'].to_excel(writer, sheet_name='Raw_Movies_Data', index=False)
        raw_data['series'].to_excel(writer, sheet_name='Raw_Series_Data', index=False)

        workbook = writer.book
        add_charts_to_excel(workbook, movies, series, movies_splits, series_splits)
        writer.book.save(output)
    
    output.seek(0)
    return output

def add_charts_to_excel(workbook, movies, series, movies_splits, series_splits):
    """Add charts to Excel sheets - Matching Plotly chart types as closely as possible"""
    from openpyxl.chart import BarChart, PieChart, LineChart, Reference, ScatterChart
    from openpyxl.chart.label import DataLabelList
    from openpyxl.chart.axis import DateAxis
    
    try:
        # Add note about chart type limitations
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            sheet.cell(row=1, column=6, value="Note: Excel charts may differ from Plotly due to Excel limitations")
            sheet.cell(row=1, column=6).font = sheet.cell(row=1, column=6).font.copy(bold=True, color="FF0000")
        
        # 1. Overview_Parental_Guide - Pie Chart (matches Plotly pie chart)
        sheet = workbook['Overview_Parental_Guide']
        chart = PieChart()
        chart.title = "Top Parental Guides (Pie Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showPercent = True
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Pie Chart to {sheet.title} (matches Plotly pie chart)")
        
        # 2. Overview_Genres - Horizontal Bar Chart (closest to Plotly treemap)
        sheet = workbook['Overview_Genres']
        chart = BarChart()
        chart.title = "Top Genres (Horizontal Bar - closest to Plotly Treemap)"
        chart.height = 15
        chart.width = 20
        chart.type = "bar"  # Horizontal bar chart
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=max(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=max(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Horizontal Bar Chart to {sheet.title} (closest to Plotly treemap)")
        
        # 3. Overview_Countries - Bar Chart (closest to Plotly choropleth)
        sheet = workbook['Overview_Countries']
        chart = BarChart()
        chart.title = "Top Countries (Bar Chart - closest to Plotly Choropleth)"
        chart.height = 15
        chart.width = 20
        chart.type = "col"  # Vertical bar chart
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(31, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(31, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Bar Chart to {sheet.title} (closest to Plotly choropleth)")
        
        # 4. Overview_Ratings - Bar Chart (closest to Plotly box plot)
        sheet = workbook['Overview_Ratings']
        chart = BarChart()
        chart.title = "Ratings Distribution (Bar Chart - closest to Plotly Box Plot)"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        # Create rating bins for visualization (histogram-like)
        rating_bins = pd.cut(series['rating'], bins=10)
        rating_dist = rating_bins.value_counts().sort_index()
        
        # Add rating distribution to sheet
        for i, (bin_name, count) in enumerate(rating_dist.items(), start=2):
            sheet.cell(row=i, column=3, value=str(bin_name))
            sheet.cell(row=i, column=4, value=count)
        
        sheet.cell(row=1, column=3, value="Rating Range")
        sheet.cell(row=1, column=4, value="Count")
        
        data = Reference(sheet, min_col=4, min_row=1, max_row=min(12, sheet.max_row))
        cats = Reference(sheet, min_col=3, min_row=2, max_row=min(12, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Bar Chart to {sheet.title} (closest to Plotly box plot)")
        
        # 5. Creators_Top_Creators - Pie Chart (matches Plotly pie chart)
        sheet = workbook['Creators_Top_Creators']
        chart = PieChart()
        chart.title = "Top Creators (Pie Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showPercent = True
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Pie Chart to {sheet.title} (matches Plotly pie chart)")
        
        # 6. Creators_Production_Companies - Bar Chart (matches Plotly bar chart)
        sheet = workbook['Creators_Production_Companies']
        chart = BarChart()
        chart.title = "Top Production Companies (Bar Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Bar Chart to {sheet.title} (matches Plotly bar chart)")
        
        # 7. Creators_Top_Stars - Bar Chart (matches Plotly bar chart)
        sheet = workbook['Creators_Top_Stars']
        chart = BarChart()
        chart.title = "Top Stars (Bar Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Bar Chart to {sheet.title} (matches Plotly bar chart)")
        
        # 8. Creators_Languages - Bar Chart (matches Plotly bar chart)
        sheet = workbook['Creators_Languages']
        chart = BarChart()
        chart.title = "Top Languages (Bar Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Bar Chart to {sheet.title} (matches Plotly bar chart)")
        
        # 9. Parental_Guide_Mean_Votes - Bar Chart (matches Plotly bar chart)
        sheet = workbook['Parental_Guide_Mean_Votes']
        chart = BarChart()
        chart.title = "Parental Guide by Mean Votes (Bar Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Bar Chart to {sheet.title} (matches Plotly bar chart)")
        
        # 10. Parental_Guide_Count - Bar Chart (matches Plotly bar chart)
        sheet = workbook['Parental_Guide_Count']
        chart = BarChart()
        chart.title = "Parental Guide by Count (Bar Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Bar Chart to {sheet.title} (matches Plotly bar chart)")
        
        # 11. Year_Work_Count - Line Chart (matches Plotly line chart)
        sheet = workbook['Year_Work_Count']
        chart = LineChart()
        chart.title = "Work Count Over Time (Line Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Line Chart to {sheet.title} (matches Plotly line chart)")
        
        # 12. Year_Mean_Votes - Line Chart (matches Plotly line chart)
        sheet = workbook['Year_Mean_Votes']
        chart = LineChart()
        chart.title = "Work Votes Over Time (Line Chart - matches Plotly)"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showVal = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added Line Chart to {sheet.title} (matches Plotly line chart)")
        
        print("All charts added successfully with Plotly-matching types!")
        
    except Exception as e:
        print(f"Error adding charts: {e}")

def create_dashboard_pdf():
    """Create PDF of the dashboard using JavaScript html2canvas and jsPDF"""
    try:
        print("Starting JavaScript-based PDF creation...")
        
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to the dashboard
            dashboard_url = "http://127.0.0.1:8050"
            print(f"Navigating to: {dashboard_url}")
            driver.get(dashboard_url)
            
            # Wait for the page to load completely
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
            
            # Additional wait for charts to load
            print("Waiting for charts to load...")
            time.sleep(10)
            
            # Inject the JavaScript libraries and PDF creation script
            print("Injecting JavaScript libraries...")
            
            # Load html2canvas library
            html2canvas_script = """
            var script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.4.1/html2canvas.min.js';
            document.head.appendChild(script);
            """
            driver.execute_script(html2canvas_script)
            time.sleep(3)  # Wait for library to load
            
            # Load jsPDF library
            jspdf_script = """
            var script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.1/jspdf.debug.js';
            document.head.appendChild(script);
            """
            driver.execute_script(jspdf_script)
            time.sleep(3)  # Wait for library to load
            
            # Create PDF using the JavaScript approach
            print("Creating PDF using html2canvas and jsPDF...")
            
            pdf_creation_script = """
            return new Promise((resolve, reject) => {
                // Wait a bit more for libraries to be fully loaded
                setTimeout(() => {
                    try {
                        const printArea = document.getElementById("mainContainer") || document.body;
                        
                        html2canvas(printArea, {scale: 3}).then(function(canvas) {
                            var imgData = canvas.toDataURL('image/png');
                            var doc = new jsPDF('p', 'mm', "a4");
                            
                            const pageHeight = doc.internal.pageSize.getHeight();
                            const imgWidth = doc.internal.pageSize.getWidth();
                            var imgHeight = canvas.height * imgWidth / canvas.width;
                            var heightLeft = imgHeight;
                            
                            var position = 10; // give some top padding to first page

                            doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                            heightLeft -= pageHeight;

                            while (heightLeft >= 0) {
                                position += heightLeft - imgHeight; // top padding for other pages
                                doc.addPage();
                                doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
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
                }, 2000);
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
                
                print(f"PDF created successfully using JavaScript, size: {len(pdf_bytes)} bytes")
                return pdf_bytes
            else:
                print("Failed to create PDF using JavaScript")
                return None
                
        finally:
            driver.quit()
            print("Chrome driver closed")
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None
