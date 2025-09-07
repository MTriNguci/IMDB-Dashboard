import plotly.express as px
import plotly.graph_objects as go
from .viz1_query_manager import get_viz1_query_manager



def generate_system_information_visualizations(trino_connector=None, start_date='2025-08-08', end_date='2025-09-04', area=None):
    """Generate visualizations for system information dashboard using SQL queries"""
    # Get query manager to use EXACT same queries
    query_manager = get_viz1_query_manager()
    
    # Query 1: Total Events Card - Sử dụng SQL từ Trino
    total_events_data = query_manager.get_total_events_card_data(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    total_events = total_events_data['total_events'].iloc[0] if not total_events_data.empty else 0
    
    # Create total events card visualization
    fig_total_events = go.Figure(go.Indicator(
        mode="number",
        value=total_events,
        title={"text": "Tổng số sự kiện"},
        number={'font': {'size': 50, 'color': '#5959ff'}},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    pie_height = 480
    small_card_height = int(pie_height / 3)
    fig_total_events.update_layout(
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=pie_height,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Query 2: System Events Pie Chart - Sử dụng SQL từ Trino
    system_events_data = query_manager.get_system_events_pie_data(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    
    # Kiểm tra dữ liệu có tồn tại không
    if not system_events_data.empty and system_events_data['total_events'].sum() > 0:
        fig_system_pie = px.pie(
            system_events_data, 
            values='total_events', 
            names='Tổng thông báo hệ thống',
            title='Phân bố thông báo theo hệ thống',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
    else:
        # Tạo biểu đồ trống nếu không có dữ liệu
        fig_system_pie = go.Figure()
        fig_system_pie.add_annotation(
            text="Không có dữ liệu",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='white')
        )
        fig_system_pie.update_layout(
            title='Phân bố thông báo theo hệ thống',
            showlegend=False
        )
    
    fig_system_pie.update_layout(
        template='plotly_dark', 
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=pie_height,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    if not system_events_data.empty and system_events_data['total_events'].sum() > 0:
        fig_system_pie.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Phần trăm: %{percent}<extra></extra>'
        )
    
    # Query 3: AVG Processing Time
    avg_processing_time_data = query_manager.get_avg_processing_time(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    avg_text = None
    if avg_processing_time_data is not None and not avg_processing_time_data.empty:
        # Cột trả về có tên " " theo implement trong query_manager
        first_col = avg_processing_time_data.columns[0]
        avg_text = str(avg_processing_time_data.iloc[0][first_col])
    else:
        avg_text = "Không có dữ liệu"

    # Tạo card hiển thị thời gian xử lý trung bình (bên phải pie chart)
    fig_avg_processing = go.Figure()
    fig_avg_processing.add_annotation(
        text=f"<b>{avg_text}</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=24, color='#59ff59'),
        align="center"
    )
    fig_avg_processing.update_layout(
        title={"text": "Thời gian tiếp nhận xử lý trung bình", "x": 0.5},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=small_card_height,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    # Query 4: AVG Duration Processing Time
    avg_duration_processing_time_data = query_manager.get_avg_processed_duration(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    avg_text = None
    if avg_duration_processing_time_data is not None and not avg_duration_processing_time_data.empty:
        # Cột trả về có tên " " theo implement trong query_manager
        first_col = avg_duration_processing_time_data.columns[0]
        avg_text = str(avg_duration_processing_time_data.iloc[0][first_col])
    else:
        avg_text = "Không có dữ liệu"

    # Tạo card hiển thị thời gian xử lý trung bình (bên phải pie chart)
    fig_avg_handling = go.Figure()
    fig_avg_handling.add_annotation(
        text=f"<b>{avg_text}</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=24, color='#59ff59'),
        align="center"
    )
    fig_avg_handling.update_layout(
        title={"text": "Thời gian khắc phục trung bình", "x": 0.5},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=small_card_height,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    #query 5: AVG Loss Connection
    avg_loss_connection_data = query_manager.get_avg_loss_connection(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    avg_text = None
    if avg_loss_connection_data is not None and not avg_loss_connection_data.empty:
        # Cột trả về có tên " " theo implement trong query_manager
        first_col = avg_loss_connection_data.columns[0]
        avg_text = str(avg_loss_connection_data.iloc[0][first_col])
    else:
        avg_text = "Không có dữ liệu"
    # Tạo card hiển thị thời gian xử lý trung bình (bên phải pie chart)
    fig_avg_loss_connection = go.Figure()
    fig_avg_loss_connection.add_annotation(
        text=f"<b>{avg_text}</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=24, color='#59ff59'),
        align="center"
    )
    fig_avg_loss_connection.update_layout(
        title={"text": "Thời gian mất kết nối trung bình", "x": 0.5},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=small_card_height,
        margin=dict(l=10, r=10, t=50, b=10)
    )
     

    # Query 6: Notification Statistics Table
    notification_data = query_manager.get_notification_statistics(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    
    # # Create notification statistics table
    # fig_notification_table = go.Figure(data=[go.Table(
    #     header=dict(
    #         values=['<b>Hệ thống</b>', '<b>Tên thông báo</b>', '<b>Số lượng</b>'],
    #         fill_color="#050767",
    #         font=dict(color='white', size=14),
    #         align='center',
    #         height=40
    #     ),
    #     cells=dict(
    #         values=[
    #             notification_data['Hệ thống'] if not notification_data.empty else [],
    #             notification_data['Tên thông báo'] if not notification_data.empty else [],
    #             notification_data['Số lượng'] if not notification_data.empty else []
    #         ],
    #         fill_color="#0A0DC0",
    #         font=dict(color='white', size=12),
    #         align='center',
    #         height=35
    #     )
    # )])
    
    # fig_notification_table.update_layout(
    #     title={
    #         'text': '<b>Thống kê thông báo</b>',
    #         'x': 0.5,
    #         'font': {'size': 18, 'color': 'white'}
    #     },
    #     template='plotly_dark',
    #     font=dict(color='white'),
    #     paper_bgcolor='black',
    #     plot_bgcolor='black',
    #     height=400,
    #     margin=dict(l=20, r=20, t=60, b=20)
    # )
    fig_notification_table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Hệ thống</b>', '<b>Tên thông báo</b>', '<b>Số lượng</b>'],
            fill_color="#050767",
            font=dict(color='white', size=14),
            align='center',
            height=40,
            line_color='rgba(0,0,0,0)'   # bỏ border header
        ),
        cells=dict(
            values=[
                notification_data['Hệ thống'] if not notification_data.empty else [],
                notification_data['Tên thông báo'] if not notification_data.empty else [],
                notification_data['Số lượng'] if not notification_data.empty else []
            ],
            # màu xen kẽ giữa các dòng
            fill_color=[["#2527A2", "#2123C6"] * (len(notification_data)//2 + 1)],
            font=dict(color='white', size=12),
            align='center',
            height=35,
            line_color='rgba(0,0,0,0)'   # bỏ border cell
        )
    )])

    fig_notification_table.update_layout(
        title={
            'text': '<b>Thống kê thông báo</b>',
            'x': 0.5,
            'font': {'size': 18, 'color': 'white'}
        },
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Query 7: Average Downtime by Device Type Table
    downtime_data = query_manager.get_avg_downtime_by_device_type(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    
    # Create average downtime table
    fig_downtime_table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Loại thiết bị</b>', '<b>Thời gian ngừng hoạt động trung bình</b>', '<b>Tỷ lệ % thiết bị hoạt động bình thường</b>'],
            fill_color='#050767',
            font=dict(color='white', size=14),
            align='center',
            height=40,
            line_color='rgba(0,0,0,0)'   # bỏ border header

        ),
        cells=dict(
            values=[
                downtime_data['Loại thiết bị'] if not downtime_data.empty else [],
                downtime_data['Thời gian ngừng hoạt động trung bình'] if not downtime_data.empty else [],
                downtime_data['Tỷ lệ % thiết bị hoạt động bình thường'] if not downtime_data.empty else []
            ],
            fill_color=[["#2527A2", "#2123C6"] * (len(notification_data)//2 + 1)],
            font=dict(color='white', size=12),
            align='center',
            height=35,
            line_color='rgba(0,0,0,0)'   # bỏ border cell

        )
    )])
    
    fig_downtime_table.update_layout(
        title={
            'text': '<b>Thời gian ngừng hoạt động trung bình của loại thiết bị</b>',
            'x': 0.5,
            'font': {'size': 18, 'color': 'white'}
        },
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig_total_events, fig_system_pie, fig_avg_processing, fig_avg_handling, fig_avg_loss_connection, fig_notification_table, fig_downtime_table

