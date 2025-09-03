from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from src.const import get_constants
import io
import base64
from datetime import datetime
import pdfkit
import tempfile
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time

from src.dash1 import generate_visualizations as generate_visualizations1
from src.dash2 import generate_visualizations as generate_visualizations2
from src.dash3 import generate_visualizations as generate_visualizations3
from src.dash4 import generate_visualizations as generate_visualizations4

movies = pd.read_csv('./movie_after_cleaning.csv')
movies_splits = pd.read_excel("./splits_movie.xlsx", sheet_name=None)
series = pd.read_csv('./series_after_cleaning.csv')
series_splits = pd.read_excel("./splits_series.xlsx", sheet_name=None)

# Define function to load data based on tab selection
def load_data(tab):
    if tab == 'movie':
        return movies, movies_splits
    elif tab == 'series':
        return series, series_splits

num_of_works,num_of_countries,num_of_lang,avg_votes = get_constants(movies, series, movies_splits, series_splits)


# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='IMDB Data Analysis Dashboard')
server = app.server

def generate_stats_card (title, value, image_path):
    return html.Div(
        dbc.Card([
            dbc.CardImg(src=image_path, top=True, style={'width': '50px','alignSelf': 'center'}),
            dbc.CardBody([
                html.P(value, className="card-value", style={'margin': '0px','fontSize': '22px','fontWeight': 'bold'}),
                html.H4(title, className="card-title", style={'margin': '0px','fontSize': '18px','fontWeight': 'bold'})
            ], style={'textAlign': 'center'}),
        ], style={'paddingBlock':'10px',"backgroundColor":'#5959ff','border':'none','borderRadius':'10px'})
    )


tab_style = {
    'idle':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'backgroundColor': '#5959ff',
        'border':'none'
    },
    'active':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'border':'none',
        'textDecoration': 'underline',
        'backgroundColor': '#5959ff'
    }
}

MAX_OPTIONS_DISPLAY = 3300

# Generate options for the dropdown
dropdown_options_movie = [{'label': title, 'value': title} for title in movies['title'][:MAX_OPTIONS_DISPLAY]]
dropdown_options_series = [{'label': title, 'value': title} for title in series['title'][:MAX_OPTIONS_DISPLAY]]


offcanvas = html.Div(
    [
        dbc.Button("Movie Recommendation", id="open-movie-offcanvas", n_clicks=0, style={'backgroundColor':'#5959ff','color':'white','fontWeight': 'bold','border':'none'}),
        dbc.Offcanvas(html.Div([
            dcc.Dropdown(
            id='movie-dropdown',
            options=dropdown_options_movie,
            placeholder='Select a movie...',
            searchable=True,
            style={'color':'black'}
            ),
            dcc.Loading(html.Div(id='movie-recommendation-content'),type='circle',color='#5959ff',style={'marginTop': '60px'})]),
            id="movie-recommendation-offcanvas",
            title="Movie Recommendations",
            is_open=False,
            style={'backgroundColor':"black",'color':'#5959ff'}
        ),
        dbc.Button("Series Recommendation", id="open-series-offcanvas", n_clicks=0, style={'backgroundColor':'#5959ff','color':'white','fontWeight': 'bold','border':'none'}),
        dbc.Offcanvas(html.Div([
            dcc.Dropdown(
            id='series-dropdown',
            options=dropdown_options_series,
            placeholder='Select a series...',
            searchable=True,
            style={'color':'black'}
            ),
            dcc.Loading(html.Div(id='series-recommendation-content'),type='circle',color='#5959ff',style={'marginTop': '60px'})]),
            id="series-recommendation-offcanvas",
            title="Series Recommendations",
            is_open=False,
            style={'backgroundColor':"black",'color':'#5959ff'}
        ),
        dbc.Button("Export Data", id="export-data-btn", n_clicks=0, style={'backgroundColor':'#5959ff','color':'white','fontWeight': 'bold','border':'none'}),
        dbc.Button("Export PDF", id="export-pdf-btn", n_clicks=0, style={'backgroundColor':'#ff5959','color':'white','fontWeight': 'bold','border':'none'}),
        dcc.Download(id="download-excel"),
        dcc.Download(id="download-pdf")
    ],
    style={'display': 'flex', 'justifyContent': 'space-between','marginTop': '20px'}
)

# Define the layout of the app
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Img(src="./assets/imdb.png",width=150), width=2),
            dbc.Col(
                dcc.Tabs(id='graph-tabs', value='overview', children=[
                    dcc.Tab(label='Overview', value='overview',style=tab_style['idle'],selected_style=tab_style['active']),
                    dcc.Tab(label='Content creators', value='content_creators',style=tab_style['idle'],selected_style=tab_style['active']),
                    dcc.Tab(label='Parental Guide', value='parental',style=tab_style['idle'],selected_style=tab_style['active']),
                    dcc.Tab(label='Year', value='year',style=tab_style['idle'],selected_style=tab_style['active'])
                ], style={'marginTop': '15px', 'width':'600px','height':'50px'})
            ,width=6),
            dbc.Col(offcanvas, width=4)
        ]),
        dbc.Row([
            
            dbc.Col(generate_stats_card("Work",num_of_works,"./assets/movie-icon.png"), width=3),
            dbc.Col(generate_stats_card("Language", num_of_lang,"./assets/language-icon.svg"), width=3),
            dbc.Col(generate_stats_card("Country",num_of_countries,"./assets/country-icon.png"), width=3),
            dbc.Col(generate_stats_card("Average Votes",avg_votes,"./assets/vote-icon.png"), width=3),
        ],style={'marginBlock': '10px'}),
        dbc.Row([
            dcc.Tabs(id='tabs', value='movie', children=[
                dcc.Tab(label='Movie', value='movie',style={'border':'1px line white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold'},selected_style={'border':'1px solid white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold','textDecoration': 'underline'}),
                dcc.Tab(label='Series', value='series',style={'border':'1px solid white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold'},selected_style={'border':'1px solid white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold','textDecoration': 'underline'}),
            ], style={'padding': '0px'})
        ]),
        dbc.Row([
            dcc.Loading([
                html.Div(id='tabs-content')
            ],type='default',color='#5959ff')
        ])
    ], style={'padding': '0px'})
],style={'backgroundColor': 'black', 'minHeight': '100vh'})

@app.callback(
    Output("movie-recommendation-offcanvas", "is_open"),
    Input("open-movie-offcanvas", "n_clicks"),
    [State("movie-recommendation-offcanvas", "is_open")],
)
def toggle_offcanvas_movie(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("series-recommendation-offcanvas", "is_open"),
    Input("open-series-offcanvas", "n_clicks"),
    [State("series-recommendation-offcanvas", "is_open")],
)
def toggle_offcanvas_series(n1, is_open):
    if n1:
        return not is_open
    return is_open


# Function to get recommendations
def get_recommendations(df, indices, title, cosine_sim):
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:6]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return df['title'].iloc[movie_indices]

# Function to create Excel data for all charts
def create_excel_data(movies, series, movies_splits, series_splits):
    """Create Excel data for all chart visualizations"""
    
    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Overview Tab Data (from dash1)
        # 1. Parental Guide Treemap data
        parental_guide_data = series["parentalguide"].value_counts().head(10).reset_index()
        parental_guide_data.columns = ['Parental Guide', 'Count']
        parental_guide_data.to_excel(writer, sheet_name='Overview_Parental_Guide', index=False)
        
        # 2. Genre Bar Chart data
        genre_data = movies_splits["genre"]["genre"].value_counts().head(10).reset_index()
        genre_data.columns = ['Genre', 'Count']
        genre_data['Percentage'] = (genre_data['Count'] / genre_data['Count'].sum()) * 100
        genre_data.to_excel(writer, sheet_name='Overview_Genres', index=False)
        
        # 3. Country Choropleth data
        country_data = movies_splits["country"]["country"].value_counts().head(30).reset_index()
        country_data.columns = ['Country', 'Count']
        country_data.to_excel(writer, sheet_name='Overview_Countries', index=False)
        
        # 4. Ratings Box Plot data
        ratings_data = series[["rating", "votes"]].copy()
        ratings_data.to_excel(writer, sheet_name='Overview_Ratings', index=False)
        
        # Content Creators Tab Data (from dash2)
        # 1. Top Creators Pie Chart data
        creators_data = series_splits["creators"]["creators"].value_counts().head(10).reset_index()
        creators_data.columns = ['Creator', 'Count']
        creators_data.to_excel(writer, sheet_name='Creators_Top_Creators', index=False)
        
        # 2. Production Company Bar Chart data
        prod_company_data = series_splits["production_company"]["production_company"].value_counts().head(10).reset_index()
        prod_company_data.columns = ['Production Company', 'Count']
        prod_company_data['Percentage'] = (prod_company_data['Count'] / prod_company_data['Count'].sum()) * 100
        prod_company_data.to_excel(writer, sheet_name='Creators_Production_Companies', index=False)
        
        # 3. Top Stars Bar Chart data
        stars_data = series_splits["stars"]["stars"].value_counts().head(10).reset_index()
        stars_data.columns = ['Star', 'Count']
        stars_data['Percentage'] = (stars_data['Count'] / stars_data['Count'].sum()) * 100
        stars_data.to_excel(writer, sheet_name='Creators_Top_Stars', index=False)
        
        # 4. Languages Bar Chart data
        language_data = series_splits["language"]["language"].value_counts().head(10).reset_index()
        language_data.columns = ['Language', 'Count']
        language_data['Percentage'] = (language_data['Count'] / language_data['Count'].sum()) * 100
        language_data.to_excel(writer, sheet_name='Creators_Languages', index=False)
        
        # Parental Guide Tab Data (from dash3)
        # 1. Parental Guide by Mean Votes
        parental_votes_data = series.groupby("parentalguide")["votes"].mean().reset_index()
        parental_votes_data.columns = ['Parental Guide', 'Mean Votes']
        parental_votes_data = parental_votes_data.sort_values(by=["Mean Votes"], ascending=False)
        parental_votes_data.to_excel(writer, sheet_name='Parental_Guide_Mean_Votes', index=False)
        
        # 2. Parental Guide by Count
        parental_count_data = series.groupby("parentalguide").size().reset_index(name='count')
        parental_count_data.columns = ['Parental Guide', 'Count']
        parental_count_data = parental_count_data.sort_values(by=["Count"], ascending=False)
        parental_count_data.to_excel(writer, sheet_name='Parental_Guide_Count', index=False)
        
        # Year Tab Data (from dash4)
        # 1. Work Count Over Time
        year_count_data = series.groupby("year").size().reset_index(name='count')
        year_count_data.columns = ['Year', 'Count']
        year_count_data.to_excel(writer, sheet_name='Year_Work_Count', index=False)
        
        # 2. Work Votes Over Time
        year_votes_data = series.groupby("year")["votes"].mean().reset_index()
        year_votes_data.columns = ['Year', 'Mean Votes']
        year_votes_data.to_excel(writer, sheet_name='Year_Mean_Votes', index=False)
        
        # Raw Data
        movies.to_excel(writer, sheet_name='Raw_Movies_Data', index=False)
        series.to_excel(writer, sheet_name='Raw_Series_Data', index=False)


        workbook = writer.book
        add_charts_to_excel(workbook, movies, series, movies_splits, series_splits)
        writer.book.save(output)
    # Get the workbook to add charts
    
    # Add charts to each sheet
    
    output.seek(0)
    return output

def add_charts_to_excel(workbook, movies, series, movies_splits, series_splits):
    """Add charts to Excel sheets"""
    from openpyxl.chart import BarChart, PieChart, LineChart, Reference
    from openpyxl.chart.label import DataLabelList
    
    try:
        # 1. Overview_Parental_Guide - Pie Chart
        sheet = workbook['Overview_Parental_Guide']
        chart = PieChart()
        chart.title = "Top Parental Guides"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add data labels
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showPercent = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 2. Overview_Genres - Bar Chart
        sheet = workbook['Overview_Genres']
        chart = BarChart()
        chart.title = "Top Genres"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 3. Overview_Countries - Bar Chart
        sheet = workbook['Overview_Countries']
        chart = BarChart()
        chart.title = "Top Countries"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(31, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(31, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 4. Overview_Ratings - Bar Chart (simulating box plot)
        sheet = workbook['Overview_Ratings']
        chart = BarChart()
        chart.title = "Ratings Distribution"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        # Create rating bins for visualization
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
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 5. Creators_Top_Creators - Pie Chart
        sheet = workbook['Creators_Top_Creators']
        chart = PieChart()
        chart.title = "Top Creators"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showPercent = True
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 6. Creators_Production_Companies - Bar Chart
        sheet = workbook['Creators_Production_Companies']
        chart = BarChart()
        chart.title = "Top Production Companies"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 7. Creators_Top_Stars - Bar Chart
        sheet = workbook['Creators_Top_Stars']
        chart = BarChart()
        chart.title = "Top Stars"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 8. Creators_Languages - Bar Chart
        sheet = workbook['Creators_Languages']
        chart = BarChart()
        chart.title = "Top Languages"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=min(11, sheet.max_row))
        cats = Reference(sheet, min_col=1, min_row=2, max_row=min(11, sheet.max_row))
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 9. Parental_Guide_Mean_Votes - Bar Chart
        sheet = workbook['Parental_Guide_Mean_Votes']
        chart = BarChart()
        chart.title = "Parental Guide by Mean Votes"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 10. Parental_Guide_Count - Bar Chart
        sheet = workbook['Parental_Guide_Count']
        chart = BarChart()
        chart.title = "Parental Guide by Count"
        chart.height = 15
        chart.width = 20
        chart.type = "col"
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 11. Year_Work_Count - Line Chart
        sheet = workbook['Year_Work_Count']
        chart = LineChart()
        chart.title = "Work Count Over Time"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        # 12. Year_Mean_Votes - Line Chart
        sheet = workbook['Year_Mean_Votes']
        chart = LineChart()
        chart.title = "Work Votes Over Time"
        chart.height = 15
        chart.width = 20
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "G2")
        print(f"Added chart to {sheet.title}")
        
        print("All charts added successfully!")
        
    except Exception as e:
        print(f"Error adding charts: {e}")

# Function to create PDF of the dashboard using screenshots
def create_dashboard_pdf():
    """Create PDF of the dashboard using screenshots"""
    try:
        print("Starting screenshot-based PDF creation...")
        
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
        
        # Set display for Xvfb
        os.environ['DISPLAY'] = ':99'
        
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
            
            # Get page dimensions
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            print(f"Page dimensions: {viewport_width}x{total_height}")
            
            # Create a list to store screenshots
            screenshots = []
            
            # Take screenshots of different sections
            sections = [
                ("Overview", "overview"),
                ("Content Creators", "content_creators"), 
                ("Parental Guide", "parental"),
                ("Year Analysis", "year")
            ]
            
            for section_name, section_id in sections:
                try:
                    print(f"Taking screenshot of {section_name} section...")
                    
                    # Click on the section tab
                    tab_selector = f'[value="{section_id}"]'
                    tab_element = driver.find_element(By.CSS_SELECTOR, tab_selector)
                    driver.execute_script("arguments[0].click();", tab_element)
                    
                    # Wait for content to load
                    time.sleep(3)
                    
                    # Take screenshot
                    screenshot_path = f"/tmp/{section_id}_screenshot.png"
                    driver.save_screenshot(screenshot_path)
                    
                    # Open and process the screenshot
                    with Image.open(screenshot_path) as img:
                        # Crop to remove browser UI elements (adjust as needed)
                        # Remove top 100px (browser UI) and bottom 50px
                        cropped_img = img.crop((0, 100, img.width, img.height - 50))
                        screenshots.append((section_name, cropped_img))
                    
                    print(f"Screenshot saved for {section_name}")
                    
                except Exception as e:
                    print(f"Error taking screenshot for {section_name}: {e}")
                    continue
            
            # Create PDF from screenshots
            if screenshots:
                print("Creating PDF from screenshots...")
                pdf_path = "/tmp/dashboard_screenshots.pdf"
                
                # Convert first image to RGB if needed
                first_img = screenshots[0][1]
                if first_img.mode != 'RGB':
                    first_img = first_img.convert('RGB')
                
                # Prepare other images
                other_images = []
                for section_name, img in screenshots[1:]:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    other_images.append(img)
                
                # Save as PDF
                first_img.save(pdf_path, "PDF", save_all=True, append_images=other_images)
                
                # Read the PDF file
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
                
                print(f"PDF created successfully, size: {len(pdf_content)} bytes")
                return pdf_content
            else:
                print("No screenshots were taken successfully")
                return None
                
        finally:
            driver.quit()
            print("Chrome driver closed")
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None

# Callback to update image container based on dropdown selection
@app.callback(
    Output('movie-recommendation-content', 'children'),
    [Input('movie-dropdown', 'value')]
)
def update_recommendation_movie(selected_movie):
    df = movies.copy()
    df["word_cloud"]=movies["description"]+" "+movies["genre"]+" "+movies["director"]+" "+movies["writer"]+" "+movies["country"]
    tfidf = TfidfVectorizer(stop_words='english')
    df["word_cloud"] = df["word_cloud"].fillna('')  
    tfidf_matrix = tfidf.fit_transform(df['word_cloud'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()

    if selected_movie:
        x = []
        for i in range(0, 5):
            x.append(movies[movies["title"] == get_recommendations(movies,indices,selected_movie,cosine_sim).iloc[i]][["link","title"]])
    else:
        return []
    
    return html.Div(children=[
            dcc.Link(f"{i+1} - {data['title'].values[0]}", href=data['link'].values[0], style={'display':'block','color':'#5959ff','marginBlock':'10px'}
                    ,target='_blank') for i, data in enumerate(x)
    ],style={'marginTop': '10px','textAlign': 'center','color': '#5959ff'})

# Callback for Excel download
@app.callback(
    Output("download-excel", "data"),
    Input("export-data-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_excel(n_clicks):
    if n_clicks is None:
        return None
    
    # Create Excel data
    output = create_excel_data(movies, series, movies_splits, series_splits)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"IMDB_Dashboard_Data_{timestamp}.xlsx"
    
    return dcc.send_bytes(
        output.getvalue(),
        filename=filename,
        type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Callback for PDF download
@app.callback(
    Output("download-pdf", "data"),
    Input("export-pdf-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_pdf(n_clicks):
    if n_clicks is None:
        return None
    
    try:
        # Create PDF
        pdf_content = create_dashboard_pdf()
        
        if pdf_content is None:
            return None
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"IMDB_Dashboard_{timestamp}.pdf"
        
        return dcc.send_bytes(
            pdf_content,
            filename=filename,
            type='application/pdf'
        )
        
    except Exception as e:
        print(f"Error in PDF download callback: {e}")
        return None

@app.callback(
    Output('series-recommendation-content', 'children'),
    [Input('series-dropdown', 'value')]
)
def update_recommendation_series(selected_series):
    df = series.copy()
    df["word_cloud"]=series["description"]+" "+series["genre"]+" "+series["creators"]+" "+series["stars"]+" "+series["country"] +" "+ series['production_company'] +" "+ series['parentalguide']
    tfidf = TfidfVectorizer(stop_words='english')
    df["word_cloud"] = df["word_cloud"].fillna('')  
    tfidf_matrix = tfidf.fit_transform(df['word_cloud'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    
    if selected_series:
        x = []
        for i in range(0, 5):
            x.append(series[series["title"] == get_recommendations(series,indices,selected_series,cosine_sim).iloc[i]][["link", "title"]])
    else:
        return []
    return html.Div(children=[
            dcc.Link(f"{i+1} - {data['title'].values[0]}", href=data['link'].values[0], style={'display':'block','color':'#5959ff','marginBlock':'10px'}
                    ,target='_blank') for i, data in enumerate(x)
    ],style={'marginTop': '10px','textAlign': 'center','color': '#5959ff'})


@app.callback(
    Output('tabs-content', 'children'),
    [Input('graph-tabs', 'value'),Input('tabs', 'value')]
)
def update_tab(tab,tab2):
    data, splits = load_data(tab2)

    if tab == 'overview':
        fig1, fig2, fig3, fig4 = generate_visualizations1(data, splits)
        return html.Div([
        html.Div([
            dcc.Graph(id='graph1', figure=fig1),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph2', figure=fig2),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph3', figure=fig3),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph4', figure=fig4),
        ], style={'width': '50%', 'display': 'inline-block'})
    ])
    elif tab == 'content_creators':
        fig1, fig2, fig3, fig4 = generate_visualizations2(data, splits)
        return html.Div([
        html.Div([
            dcc.Graph(id='graph1', figure=fig1),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph2', figure=fig2),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph3', figure=fig3),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph4', figure=fig4),
        ], style={'width': '50%', 'display': 'inline-block'})
    ])
    elif tab == 'parental':
        fig1, fig2 = generate_visualizations3(data, splits)
        return html.Div([
        html.Div([
            dcc.Graph(id='graph1', figure=fig1),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph2', figure=fig2),
        ], style={'width': '50%', 'display': 'inline-block'}),
        ])
    elif tab == 'year':
        fig1, fig2 = generate_visualizations4(data, splits)
        return html.Div([
        html.Div([
            dcc.Graph(id='graph1', figure=fig1),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph2', figure=fig2),
        ], style={'width': '50%', 'display': 'inline-block'}),
        ])


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)