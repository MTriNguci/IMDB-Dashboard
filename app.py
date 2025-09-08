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
from src.export_utils import export_excel_data, create_dashboard_pdf
from src.viz1_query_manager import get_viz1_query_manager
from src.viz2_query_manager import get_viz2_query_manager
from src.viz3_query_manager import get_viz3_query_manager
# Load data từ delta.lakehouse thay vì đọc CSV
print("🔄 Đang kết nối và load dữ liệu từ delta.lakehouse...")

# Khởi tạo kết nối Trino
trino_config = get_trino_config()
trino_connector = create_trino_connection(**trino_config)
trino_connector.connect()







# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR], title='Khu Công Nghiệp & Đô Thị Thông Minh BECAMEX',suppress_callback_exceptions=True)
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
# available_tables = [
#     'areaunit', 'asset', 'company', 'dim_area', 'dim_date', 'dim_device', 'dim_vehicle',
#     'event', 'eventinfor', 'eventtype', 'fact_lpd', 'factory', 'handytalkiegps',
#     'history', 'intersection', 'lpr_table', 'monitoringhistory', 'rpdaily',
#     'silver_lpr', 'stg_lpr_table', 'test_asset', 'test_info', 'vehicles'
# ]

# dropdown_options_movie = [{'label': table, 'value': table} for table in available_tables[:MAX_OPTIONS_DISPLAY]]
# dropdown_options_series = dropdown_options_movie  # Sử dụng cùng options


# Filter components
filter_section = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label("Từ ngày:", style={'color': '#00d4ff', 'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.DatePickerSingle(
                id='start-date-picker',
                date='2025-08-08',
                display_format='DD/MM/YYYY',
                style={'backgroundColor': '#1a1a2e', 'color': '#00d4ff'}
            )
        ], width=3),
        dbc.Col([
            html.Label("Đến ngày:", style={'color': '#00d4ff', 'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.DatePickerSingle(
                id='end-date-picker',
                date='2025-09-04',
                display_format='DD/MM/YYYY',
                style={'backgroundColor': '#1a1a2e', 'color': '#00d4ff'}
            )
        ], width=3),
        dbc.Col([
            html.Label("Khu vực:", style={'color': '#00d4ff', 'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='area-filter',
                options=[
                    {'label': 'Tất cả khu vực', 'value': None},
                    {'label': 'Khu Liên Hợp', 'value': 'Khu Liên Hợp'},
                    {'label': 'Bàu Bàng', 'value': 'Bàu Bàng'},
                    {'label': 'Thới Hòa', 'value': 'Thới Hòa'},
                    {'label': 'Mỹ Phước 1', 'value': 'Mỹ Phước 1'},
                    {'label': 'Mỹ Phước 2', 'value': 'Mỹ Phước 2'},
                    {'label': 'Mỹ Phước 3', 'value': 'Mỹ Phước 3'},
                ],
                value=None,
                placeholder="Chọn khu vực...",
                style={'color': 'black'}
            )
        ], width=3),
        # dbc.Col([
        #     html.Label("Tự động cập nhật:", style={'color': '#00d4ff', 'fontWeight': 'bold', 'marginBottom': '5px'}),
        #     html.Div("✓ Dashboard tự động cập nhật khi thay đổi bộ lọc", 
        #             style={'color': '#28a745', 'fontSize': '12px', 'fontWeight': 'bold'})
        # ], width=3)
    ], style={'marginBottom': '20px', 'alignItems': 'end'})
], style={'backgroundColor': '#1a1a2e', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '20px'})

offcanvas = html.Div(
    [
        dbc.Button("Export Excel", id="export-data-btn", n_clicks=0, style={'backgroundColor':'#5959ff','color':'white','fontWeight': 'bold','border':'none'}),
        dbc.Button("Export PDF", id="run", n_clicks=0, style={'backgroundColor':'#ff5959','color':'white','fontWeight': 'bold','border':'none'}),
        dcc.Download(id="download-excel"),
        dcc.Download(id="download-pdf"),
        html.Div(id='export-debug', style={'color':'#5959ff','fontSize':'12px'}),
        html.Div(id='pdf-export-debug', style={'color':'#ff5959','fontSize':'12px'}),
        dcc.Store(id='filter-store', data={'start_date': '2025-08-08', 'end_date': '2025-09-04', 'area': None})
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
                ], style={'marginTop': '15px', 'width':'600px','height':'50px'})
            ,width=6),
            dbc.Col(offcanvas, width=4)
        ]),

        dbc.Row([
            dcc.Tabs(id='tabs', value='vehicles', children=[  
            ], style={'padding': '0px'})
        ]),
        dbc.Row([
            filter_section
        ]),
        dbc.Row([
            dcc.Loading([
                html.Div(id='tabs-content')
            ],type='default',color='#5959ff')
        ])
    ], style={'padding': '0px'}, id='mainContainer')
],style={'backgroundColor': "#033264", 'minHeight': '100vh'})

@app.callback(
    Output("data-explorer-offcanvas", "is_open"),
    Input("open-data-offcanvas", "n_clicks"),
    [State("data-explorer-offcanvas", "is_open")],
)
def toggle_offcanvas_data(n1, is_open):
    if n1:
        return not is_open
    return is_open

# Callback to update filter store when any filter changes
@app.callback(
    Output('filter-store', 'data'),
    [Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date'),
     Input('area-filter', 'value')],
    prevent_initial_call=False
)
def update_filter_store(start_date, end_date, area):
    filter_data = {
        'start_date': start_date or '2025-08-08',
        'end_date': end_date or '2025-09-04',
        'area': area
    }
    print(f"Filter updated: {filter_data}")
    return filter_data








# Callback for Excel download
@app.callback(
    [Output("download-excel", "data"), Output('export-debug', 'children')],
    [Input("export-data-btn", "n_clicks")],
    [State('filter-store', 'data')],
    prevent_initial_call=True
)
def download_excel(n_clicks, filter_data):
    print(f"download_excel triggered with n_clicks={n_clicks}")
    if n_clicks is None:
        return None, ""
    
    # Get filter values
    start_date = filter_data.get('start_date', '2025-08-08')
    end_date = filter_data.get('end_date', '2025-09-04')
    area = filter_data.get('area', None)
    
    print(f"Using filters - Start: {start_date}, End: {end_date}, Area: {area}")
    
    # Clear cache before export to ensure fresh data

    
    qm1 = get_viz1_query_manager()
    qm2 = get_viz2_query_manager()
    qm3 = get_viz3_query_manager()
    
    qm1._cache.clear()
    qm2._cache.clear()
    qm3._cache.clear()
    
    print("Cache cleared for Excel export...")
    
    # Create Excel data
    excel_bytes = export_excel_data(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    print("Excel data prepared for download.")
    if excel_bytes is None:
        return None, ""
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Dashboard_Data_{timestamp}.xlsx"
    
    return dcc.send_bytes(lambda b: b.write(excel_bytes), filename=filename), ""

# Callback for PDF download
@app.callback(
    [Output("download-pdf", "data"), Output('pdf-export-debug', 'children')],
    [Input("run", "n_clicks")],
    prevent_initial_call=True
)
def download_pdf(n_clicks):
    print(f"download_pdf triggered with n_clicks={n_clicks}")
    if n_clicks is None:
        return None, ""
    
    # Create PDF data
    pdf_bytes = create_dashboard_pdf()
    print("PDF data prepared for download.")
    if pdf_bytes is None:
        return None, ""
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Dashboard_Report_{timestamp}.pdf"
    
    return dcc.send_bytes(lambda b: b.write(pdf_bytes), filename=filename), ""

@app.callback(
    Output('tabs-content', 'children'),
    [Input('graph-tabs', 'value'), Input('tabs', 'value'), Input('filter-store', 'data')]
)
def update_tab(tab, tab2, filter_data):
    # Get filter values
    start_date = filter_data.get('start_date', '2025-08-08')
    end_date = filter_data.get('end_date', '2025-09-04')
    area = filter_data.get('area', None)
    
    # Tạo visualizations cho system information
    if tab == 'overview':
        return create_system_information_dashboard(start_date, end_date, area)
    # elif tab == 'assets':
    #     return create_delta_visualizations(event_df, {}, "Assets Analysis")
    # elif tab == 'events':
    #     return create_delta_visualizations(event_df, {}, "Events Analysis")
    # elif tab == 'analytics':
    #     return create_delta_visualizations(event_df, {}, "Advanced Analytics")
    else:
        return create_system_information_dashboard(start_date, end_date, area)

def create_system_information_dashboard(start_date='2025-08-08', end_date='2025-09-04', area=None):
    """Tạo dashboard cho system information với SQL queries từ Trino"""
    try:
        print(f"Creating dashboard with filters - Start: {start_date}, End: {end_date}, Area: {area}")
        
        # Clear cache để đảm bảo dữ liệu mới được load

        
        qm1 = get_viz1_query_manager()
        qm2 = get_viz2_query_manager()
        qm3 = get_viz3_query_manager()
        
        # Clear all caches
        qm1._cache.clear()
        qm2._cache.clear()
        qm3._cache.clear()
        
        print("Cache cleared, loading fresh data...")
        
        # Tạo visualizations sử dụng SQL queries từ Trino
        fig_total_events, fig_system_pie, fig_avg_processing, fig_avg_handling, fig_avg_loss_connection, fig_notification_table, fig_downtime_table = generate_system_information_visualizations(
            trino_connector=trino_connector,
            start_date=start_date,
            end_date=end_date,
            area=area
        )
        
        # Tạo energy visualizations
        fig_consumed_electricity, fig_energy_cost, fig_green_energy, fig_co2_emission = generate_energy_visualizations(
            trino_connector=trino_connector,
            start_date=start_date,
            end_date=end_date,
            area=area
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
            start_date=start_date,
            end_date=end_date,
            area=area
        )
        
        return html.Div([
            html.H3("Tình trang Thông báo và Hoạt động Hệ thống", 
                    style={'color': '#00d4ff', 'textAlign': 'left', 'marginBottom': '20px', 'marginTop': '40px','fontWeight': 'bold'   }),

            
            # Row 1: Left (3 stacked small cards), Middle (Pie), Right (Total events)
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_total_events)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=4, style={'display': 'flex', 'flexDirection': 'column'}),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_system_pie)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=4, style={'display': 'flex', 'flexDirection': 'column'}),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_avg_processing)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px', 'height': 'calc(33.33% - 7px)'}),
                    html.Div([
                        dcc.Graph(figure=fig_avg_handling)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px', 'height': 'calc(33.33% - 7px)'}),
                    html.Div([
                        dcc.Graph(figure=fig_avg_loss_connection)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': 'calc(33.33% - 6px)'})
                ], width=4, style={'display': 'flex', 'flexDirection': 'column', 'height': '100%'}),

            ], style={'marginBottom': '20px', 'alignItems': 'stretch'}),
            
            # Row 2: Hai bảng mới
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_notification_table)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6),
                dbc.Col([
                    html.Div([
                        dcc.Graph(figure=fig_downtime_table)
                    ], style={'backgroundColor': "#1a1a2e", 'padding': '10px', 'borderRadius': '10px', 'height': '100%'})
                ], width=6)
            ], style={'marginBottom': '20px', 'alignItems': 'stretch'}),
            
            # Row 3: Energy Dashboard
            html.H3("Năng lượng", 
                   style={'color': '#00d4ff', 'textAlign': 'left', 'marginBottom': '20px', 'marginTop': '40px','fontWeight': 'bold'   }),
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
                   style={'color': '#00d4ff', 'textAlign': 'left', 'marginBottom': '20px', 'marginTop': '10px','fontWeight': 'bold'}),
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