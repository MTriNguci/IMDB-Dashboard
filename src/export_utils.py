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
from .viz1_query_manager import get_viz1_query_manager









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
