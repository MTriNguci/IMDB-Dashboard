import plotly.graph_objects as go
from .viz3_query_manager import get_viz3_query_manager


def _make_card(title: str, value_text: str):
    fig = go.Figure()
    fig.add_annotation(
        text=f"<b>{value_text}</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=32, color='white'),
        align="center"
    )
    fig.update_layout(
        title={"text": title, "x": 0.5, "font": {"size": 16, "color": "white"}},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def generate_environment_visualizations(trino_connector=None, start_date='2025-08-08', end_date='2025-09-04', area=None):
    """Generate 6 environment cards following the same theme as Energy cards."""
    qm = get_viz3_query_manager()

    # 1) Tổng số lượng bồn
    df_tanks = qm.get_sum_tanks(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
    val_tanks = 0
    if df_tanks is not None and not df_tanks.empty:
        val_tanks = float(df_tanks.iloc[0][df_tanks.columns[0]])
    fig_tanks = _make_card("Tổng số lượng bồn", f"{val_tanks:,.0f}")

    # 2) Tổng số km di chuyển
    df_km = qm.get_sum_travel_distance(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
    val_km = 0
    if df_km is not None and not df_km.empty:
        val_km = float(df_km.iloc[0][df_km.columns[0]])
    fig_km = _make_card("Tổng số km", f"{val_km:,.0f} km")

    # 3) Tổng số giờ hoạt động
    df_hours = qm.get_sum_operation_time(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
    val_hours = 0
    if df_hours is not None and not df_hours.empty:
        val_hours = float(df_hours.iloc[0][df_hours.columns[0]])
    fig_hours = _make_card("Tổng số giờ hoạt động", f"{val_hours:,.0f} giờ")

    # 4) Nhiên liệu tiêu hao vận chuyển
    df_fuel_transport = qm.get_sum_FuelConsumption_Transportation(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
    val_fuel_transport = 0
    if df_fuel_transport is not None and not df_fuel_transport.empty:
        val_fuel_transport = float(df_fuel_transport.iloc[0][df_fuel_transport.columns[0]])
    fig_fuel_transport = _make_card("Nhiên liệu tiêu hao vận chuyển", f"{val_fuel_transport:,.0f} lít")

    # 5) Nhiên liệu tiêu hao tưới nước
    df_fuel_watering = qm.get_sum_FuelConsumption_Watering(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
    val_fuel_watering = 0
    if df_fuel_watering is not None and not df_fuel_watering.empty:
        val_fuel_watering = float(df_fuel_watering.iloc[0][df_fuel_watering.columns[0]])
    fig_fuel_watering = _make_card("Nhiên liệu tiêu hao tưới nước", f"{val_fuel_watering:,.0f} lít")

    # 6) Số lần xe ra khỏi khu vực
    df_leaves = qm.get_num_times_leaves(trino_connector=trino_connector, start_date=start_date, end_date=end_date, area=area)
    val_leaves = 0
    if df_leaves is not None and not df_leaves.empty:
        val_leaves = float(df_leaves.iloc[0][df_leaves.columns[0]])
    fig_leaves = _make_card("Số lần xe ra khỏi khu vực", f"{val_leaves:,.0f}")

    return fig_tanks, fig_km, fig_hours, fig_fuel_transport, fig_fuel_watering, fig_leaves


