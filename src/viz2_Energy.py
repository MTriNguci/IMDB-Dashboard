import plotly.express as px
import plotly.graph_objects as go
from .viz2_query_manager import get_viz2_query_manager


def generate_energy_visualizations(trino_connector=None, start_date='2025-08-08', end_date='2025-09-04', area=None):
    """Generate visualizations for energy dashboard using SQL queries"""
    # Get query manager to use EXACT same queries
    query_manager = get_viz2_query_manager()
    
    # Query 1: Consumed Electricity Card
    consumed_electricity_data = query_manager.get_consumed_electricity(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    
    # Format consumed electricity value
    consumed_value = 0
    if consumed_electricity_data is not None and not consumed_electricity_data.empty:
        first_col = consumed_electricity_data.columns[0]
        consumed_value = float(consumed_electricity_data.iloc[0][first_col])
    
    # Create consumed electricity card
    fig_consumed_electricity = go.Figure()
    fig_consumed_electricity.add_annotation(
        text=f"<b>{consumed_value:,.0f} kWh</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=32, color='white'),
        align="center"
    )
    fig_consumed_electricity.update_layout(
        title={"text": "Điện năng tiêu thụ", "x": 0.5, "font": {"size": 16, "color": "white"}},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Query 2: Energy Cost Card
    energy_cost_data = query_manager.get_energy_cost(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    
    # Format energy cost value
    cost_value = 0
    if energy_cost_data is not None and not energy_cost_data.empty:
        first_col = energy_cost_data.columns[0]
        cost_value = float(energy_cost_data.iloc[0][first_col])
    
    # Create energy cost card
    fig_energy_cost = go.Figure()
    fig_energy_cost.add_annotation(
        text=f"<b>{cost_value:,.0f} VND</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=32, color='white'),
        align="center"
    )
    fig_energy_cost.update_layout(
        title={"text": "Chi phí năng lượng", "x": 0.5, "font": {"size": 16, "color": "white"}},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Query 3: Green Energy Percentage Card
    green_energy_data = query_manager.get_green_energy_percentage(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    
    # Format green energy percentage value
    green_percentage = 0
    if green_energy_data is not None and not green_energy_data.empty:
        first_col = green_energy_data.columns[0]
        green_percentage = float(green_energy_data.iloc[0][first_col])
    
    # Create green energy percentage card
    fig_green_energy = go.Figure()
    fig_green_energy.add_annotation(
        text=f"<b>{green_percentage:.1f}%</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=32, color='white'),
        align="center"
    )
    fig_green_energy.update_layout(
        title={"text": "Tỷ lệ năng lượng xanh", "x": 0.5, "font": {"size": 16, "color": "white"}},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Query 4: CO2 Emission Card
    co2_emission_data = query_manager.get_CO2_emission(
        trino_connector=trino_connector,
        start_date=start_date,
        end_date=end_date,
        area=area
    )
    
    # Format CO2 emission value
    co2_value = 0
    if co2_emission_data is not None and not co2_emission_data.empty:
        first_col = co2_emission_data.columns[0]
        co2_value = float(co2_emission_data.iloc[0][first_col])
    
    # Create CO2 emission card
    fig_co2_emission = go.Figure()
    fig_co2_emission.add_annotation(
        text=f"<b>{co2_value:,.0f} t-CO2</b>",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=32, color='white'),
        align="center"
    )
    fig_co2_emission.update_layout(
        title={"text": "Phát thải carbon", "x": 0.5, "font": {"size": 16, "color": "white"}},
        template='plotly_dark',
        font=dict(color='white'),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig_consumed_electricity, fig_energy_cost, fig_green_energy, fig_co2_emission
