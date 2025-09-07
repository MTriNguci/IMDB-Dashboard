from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from src.const import get_constants, get_trino_config
from src.trino_connector import TrinoConnector, create_trino_connection
import base64
from datetime import datetime

from src.viz1_System_Information import generate_system_information_visualizations
from src.viz2_Energy import generate_energy_visualizations
from src.viz3_Environment import generate_environment_visualizations
from src.export_utils import create_excel_data
from src.viz1_query_manager import get_viz1_query_manager

# Load data từ delta.lakehouse thay vì đọc CSV
print("🔄 Đang kết nối và load dữ liệu từ delta.lakehouse...")

# Khởi tạo kết nối Trino
trino_config = get_trino_config()
trino_connector = create_trino_connection(**trino_config)
trino_connector.connect()





# Tính toán constants từ dữ liệu delta.lakehouse
# Khởi tạo các biến cần thiết cho QueryManager
movies = pd.DataFrame()  # Placeholder
series = pd.DataFrame()  # Placeholder
movies_splits = {}       # Placeholder
series_splits = {}       # Placeholder

# Tính toán số liệu thống kê cơ bản
# Initialize QueryManager to ensure consistency between Plotly and Excel
query_manager = get_viz1_query_manager()


# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR], title='Khu Công Nghiệp & Đô Thị Thông Minh BECAMEX')
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

MAX_OPTIONS_DISPLAY = 100

# Generate options for the dropdown từ delta.lakehouse data
# Tạo dropdown với tên các bảng có sẵn
available_tables = [
    'areaunit', 'asset', 'company', 'dim_area', 'dim_date', 'dim_device', 'dim_vehicle',
    'event', 'eventinfor', 'eventtype', 'fact_lpd', 'factory', 'handytalkiegps',
    'history', 'intersection', 'lpr_table', 'monitoringhistory', 'rpdaily',
    'silver_lpr', 'stg_lpr_table', 'test_asset', 'test_info', 'vehicles'
]

dropdown_options_movie = [{'label': table, 'value': table} for table in available_tables[:MAX_OPTIONS_DISPLAY]]
dropdown_options_series = dropdown_options_movie  # Sử dụng cùng options


offcanvas = html.Div(
    [
        dbc.Button("Data Explorer", id="open-data-offcanvas", n_clicks=0, style={'backgroundColor':'#5959ff','color':'white','fontWeight': 'bold','border':'none'}),
        dbc.Offcanvas(html.Div([
            dcc.Dropdown(
            id='data-dropdown',
            options=dropdown_options_movie,
            placeholder='Select a data table...',
            searchable=True,
            style={'color':'black'}
            ),
            dcc.Loading(html.Div(id='data-explorer-content'),type='circle',color='#5959ff',style={'marginTop': '60px'})]),
            id="data-explorer-offcanvas",
            title="Data Explorer",
            is_open=False,
            style={'backgroundColor':"black",'color':'#5959ff'}
        ),
        dbc.Button("Export Data", id="export-data-btn", n_clicks=0, style={'backgroundColor':'#5959ff','color':'white','fontWeight': 'bold','border':'none'}),
        dbc.Button("CREATE PDF", id="run", n_clicks=0, style={'backgroundColor':'#ff5959','color':'white','fontWeight': 'bold','border':'none'}),
        dcc.Download(id="download-excel")
    ],
    style={'display': 'flex', 'justifyContent': 'space-between','marginTop': '20px'}
)


# Define the layout of the app
app.layout = html.Div([
    # Add JavaScript libraries for PDF generation
    html.Script(src="/assets/js/html2canvas.js"),
    html.Script(src="/assets/js/jspdf.js"),
    html.Script(src="/assets/js/print_pdf.js"),
    
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Delta Lakehouse Analytics", style={'color': '#5959ff', 'fontWeight': 'bold'}), width=2),
            dbc.Col(
                dcc.Tabs(id='graph-tabs', value='overview', children=[
                    # dcc.Tab(label='Overview', value='overview',style=tab_style['idle'],selected_style=tab_style['active']),
                    # dcc.Tab(label='Assets', value='assets',style=tab_style['idle'],selected_style=tab_style['active']),
                    # dcc.Tab(label='Events', value='events',style=tab_style['idle'],selected_style=tab_style['active']),
                    # dcc.Tab(label='Analytics', value='analytics',style=tab_style['idle'],selected_style=tab_style['active'])
                ], style={'marginTop': '15px', 'width':'600px','height':'50px'})
            ,width=6),
            dbc.Col(offcanvas, width=4)
        ]),
        # dbc.Row([
            # dbc.Col(generate_stats_card("Total Records",num_of_works,"./assets/movie-icon.png"), width=3),
            # dbc.Col(generate_stats_card("Tables", num_of_lang,"./assets/language-icon.svg"), width=3),
            # dbc.Col(generate_stats_card("Categories",num_of_countries,"./assets/country-icon.png"), width=3),
            # dbc.Col(generate_stats_card("Data Points",avg_votes,"./assets/vote-icon.png"), width=3),
        # ],style={'marginBlock': '10px'}),
        dbc.Row([
            dcc.Tabs(id='tabs', value='vehicles', children=[
                # dcc.Tab(label='Vehicles', value='vehicles',style={'border':'1px line white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold'},selected_style={'border':'1px solid white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold','textDecoration': 'underline'}),
                # dcc.Tab(label='Assets', value='assets',style={'border':'1px solid white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold'},selected_style={'border':'1px solid white','backgroundColor':'black','color': '#5959ff','fontWeight': 'bold','textDecoration': 'underline'}),
            ], style={'padding': '0px'})
        ]),
        dbc.Row([
            dcc.Loading([
                html.Div(id='tabs-content')
            ],type='default',color='#5959ff')
        ])
    ], style={'padding': '0px'}, id='mainContainer')
],style={'backgroundColor': 'black', 'minHeight': '100vh'})

@app.callback(
    Output("data-explorer-offcanvas", "is_open"),
    Input("open-data-offcanvas", "n_clicks"),
    [State("data-explorer-offcanvas", "is_open")],
)
def toggle_offcanvas_data(n1, is_open):
    if n1:
        return not is_open
    return is_open






# Callback to update data explorer based on dropdown selection
@app.callback(
    Output('data-explorer-content', 'children'),
    [Input('data-dropdown', 'value')]
)
def update_data_explorer(selected_data):
    if not selected_data or movies.empty:
        return html.Div("Không có dữ liệu từ delta.lakehouse", style={'color': '#5959ff'})
    
    # Hiển thị thông tin cơ bản về bảng được chọn
    return html.Div([
        html.H6(f"Bảng: {selected_data}", style={'color': '#5959ff'}),
        html.P(f"Số dòng: {len(movies)}", style={'color': '#5959ff'}),
        html.P(f"Số cột: {len(movies.columns)}", style={'color': '#5959ff'}),
        html.P("Các cột:", style={'color': '#5959ff'}),
        html.Ul([html.Li(col, style={'color': '#5959ff'}) for col in movies.columns[:10]])
    ], style={'marginTop': '10px', 'textAlign': 'center'})

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




@app.callback(
    Output('tabs-content', 'children'),
    [Input('graph-tabs', 'value'),Input('tabs', 'value')]
)
def update_tab(tab, tab2):
    # Tạo visualizations cho system information
    if tab == 'overview':
        return create_system_information_dashboard()
    # elif tab == 'assets':
    #     return create_delta_visualizations(event_df, {}, "Assets Analysis")
    # elif tab == 'events':
    #     return create_delta_visualizations(event_df, {}, "Events Analysis")
    # elif tab == 'analytics':
    #     return create_delta_visualizations(event_df, {}, "Advanced Analytics")
    else:
        return create_system_information_dashboard()

def create_system_information_dashboard():
    """Tạo dashboard cho system information với SQL queries từ Trino"""
    try:
        # Tạo visualizations sử dụng SQL queries từ Trino
        fig_total_events, fig_system_pie, fig_avg_processing, fig_avg_handling, fig_avg_loss_connection, fig_notification_table, fig_downtime_table = generate_system_information_visualizations(
            trino_connector=trino_connector,
            start_date='2025-08-08',  # Có thể thay đổi thành dynamic
            end_date='2025-09-04',    # Có thể thay đổi thành dynamic
            area=None                 # Có thể thay đổi thành dynamic
        )
        
        # Tạo energy visualizations
        fig_consumed_electricity, fig_energy_cost, fig_green_energy, fig_co2_emission = generate_energy_visualizations(
            trino_connector=trino_connector,
            start_date='2025-08-08',
            end_date='2025-09-04',
            area=None
        )
        
        # Tạo environment visualizations (6 cards)
        (
            fig_env_tanks,
            fig_env_km,
            fig_env_hours,
            fig_env_fuel_transport,
            fig_env_fuel_watering,
            fig_env_leaves,
        ) = generate_environment_visualizations(
            trino_connector=trino_connector,
            start_date='2025-08-08',
            end_date='2025-09-04',
            area=None
        )
        
        return html.Div([
            html.H3("Tình trang Thông báo và Hoạt động Hệ thống", 
                    style={'color': '#00d4ff', 'textAlign': 'center', 'marginBottom': '20px', 'marginTop': '40px'}),

            
            # Row 1: Left (3 stacked small cards), Middle (Pie), Right (Total events)
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_total_events)
                    ], style={'backgroundColor': "#05089a", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=4, style={'display': 'flex', 'flexDirection': 'column'}),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_system_pie)
                    ], style={'backgroundColor': "#05089a", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=4, style={'display': 'flex', 'flexDirection': 'column'}),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_avg_processing)
                    ], style={'backgroundColor': "#05089a", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px', 'height': 'calc(33.33% - 7px)'}),
                    html.Div([
                        dcc.Graph(figure=fig_avg_handling)
                    ], style={'backgroundColor': "#05089a", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px', 'height': 'calc(33.33% - 7px)'}),
                    html.Div([
                        dcc.Graph(figure=fig_avg_loss_connection)
                    ], style={'backgroundColor': "#05089a", 'padding': '10px', 'borderRadius': '10px', 'height': 'calc(33.33% - 6px)'})
                ], width=4, style={'display': 'flex', 'flexDirection': 'column', 'height': '100%'}),

            ], style={'marginBottom': '20px', 'alignItems': 'stretch'}),
            
            # Row 2: Hai bảng mới
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_notification_table)
                    ], style={'backgroundColor': "#05089a", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_downtime_table)
                    ], style={'backgroundColor': "#05089a", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6)
            ], style={'marginBottom': '20px', 'alignItems': 'stretch'}),
            
            # Row 3: Energy Dashboard
            html.H3("Năng lượng", 
                   style={'color': '#00d4ff', 'textAlign': 'center', 'marginBottom': '20px', 'marginTop': '40px'}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_consumed_electricity)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_energy_cost)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6)
            ], style={'marginBottom': '20px', 'alignItems': 'stretch'}),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_green_energy)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_co2_emission)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6)
            ], style={'marginBottom': '20px', 'alignItems': 'stretch'}),
            
            # Row 4: Environment Dashboard
            html.H3("Môi trường", 
                   style={'color': '#00d4ff', 'textAlign': 'center', 'marginBottom': '20px', 'marginTop': '10px'}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_env_tanks)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px'}),
                    html.Div([
                        dcc.Graph(figure=fig_env_km)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px'}),
                    html.Div([
                        dcc.Graph(figure=fig_env_hours)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px'})
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_env_fuel_transport)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px'}),
                    html.Div([
                        dcc.Graph(figure=fig_env_fuel_watering)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px'}),
                    html.Div([
                        dcc.Graph(figure=fig_env_leaves)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px'})
                ], width=6)
            ], style={'marginBottom': '20px', 'alignItems': 'stretch'})
        ])
        
    except Exception as e:
        return html.Div([
            html.H3("Thông tin Hệ thống - Delta Lakehouse", 
                   style={'color': '#5959ff', 'textAlign': 'center', 'marginBottom': '20px'}),
            html.Div([
                html.H5("Lỗi khi tải dữ liệu", style={'color': '#ff5959'}),
                html.P(f"Chi tiết lỗi: {str(e)}", style={'color': 'white'}),
                html.P("Vui lòng kiểm tra kết nối Trino và cấu hình", style={'color': '#ff5959'})
            ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center'})
        ])




if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', port=8050)
    finally:
        # Đóng kết nối Trino khi ứng dụng kết thúc
        if 'trino_connector' in locals() and trino_connector:
            trino_connector.disconnect()