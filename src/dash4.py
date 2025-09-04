import plotly.express as px
from .query_manager import get_query_manager

# Define visualizations
def generate_visualizations(series, splits):
    # Get query manager to use EXACT same queries
    query_manager = get_query_manager()
    
    # Use EXACT same data from QueryManager
    df1 = query_manager.get_year_work_count_data()
    fig_line_count = px.line(df1, x='Year', y='Count', title='Work Count Over Time')

    # Update line color to yellow
    fig_line_count.update_traces(line=dict(color='yellow'))

    # Update layout with dark template and yellow font color
    fig_line_count.update_layout(template='plotly_dark', font=dict(color='yellow'))

    # Use EXACT same data from QueryManager
    df2 = query_manager.get_year_mean_votes_data()
    fig_line_votes = px.line(df2, x='Year', y='Mean Votes', title='Work Votes Over Time')

    # Update line color to yellow
    fig_line_votes.update_traces(line=dict(color='yellow'))

    # Update layout with dark template and yellow font color
    fig_line_votes.update_layout(template='plotly_dark', font=dict(color='yellow'))

    return fig_line_count, fig_line_votes