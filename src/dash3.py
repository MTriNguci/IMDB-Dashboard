import plotly.express as px
from .query_manager import get_query_manager

def generate_visualizations(series, splits):
    # Get query manager to use EXACT same queries
    query_manager = get_query_manager()
    
    # Use EXACT same data from QueryManager
    df1 = query_manager.get_parental_guide_mean_votes_data()
    fig_bar_mean_votes = px.bar(df1, x="Parental Guide", y="Mean Votes", title='Parental Guide by Mean Votes', color="Mean Votes")
    fig_bar_mean_votes.update_layout(template='plotly_dark', font=dict(color='yellow'))

    # Use EXACT same data from QueryManager
    df2 = query_manager.get_parental_guide_count_data()
    fig_bar_count = px.bar(df2, x="Parental Guide", y="Count", title='Parental Guide by Count', color="Count")
    fig_bar_count.update_layout(template='plotly_dark', font=dict(color='yellow'))

    return fig_bar_mean_votes, fig_bar_count