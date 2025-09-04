import plotly.express as px
from .query_manager import get_query_manager

def generate_visualizations(series, splits):
    # Get query manager to use EXACT same queries
    query_manager = get_query_manager()
    
    # Use EXACT same data from QueryManager
    top_five_genres = query_manager.get_parental_guide_treemap_data()
    fig_treemap = px.treemap(top_five_genres, 
                             path=['parentalguide'],  
                             values='count', 
                             title='Top Parental Guides',
                             color='count',color_continuous_scale='viridis')
    fig_treemap.update_layout(template='plotly_dark', font=dict(color='yellow'))

    # Use EXACT same data from QueryManager
    top_values_language = query_manager.get_genre_bar_data()
    fig_bar_language = px.bar(top_values_language, x='count', y="genre", orientation='h',
                              color='count', text='percentage',
                              title='Top genres',
                              labels={'count': 'Count', 'index': 'genre', 'percentage': 'Percentage'},
                              color_continuous_scale='Viridis')
    fig_bar_language.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_bar_language.update_layout(yaxis=dict(categoryorder='total ascending'))
    fig_bar_language.update_layout(template='plotly_dark', font=dict(color='yellow'))

    # Use EXACT same data from QueryManager
    top_countries = query_manager.get_country_choropleth_data()
    fig_choropleth = px.choropleth(top_countries, 
                                    locations="country",
                                    color="count",
                                    hover_name="country",
                                    title="Top Countries producing",
                                    projection="natural earth",
                                    color_continuous_scale='Viridis')
    fig_choropleth.update_layout(template='plotly_dark', font=dict(color='yellow'))
    
    # Use EXACT same data from QueryManager
    ratings_data = query_manager.get_ratings_box_data()
    fig_boxplot = px.box(ratings_data, x="rating", title='Ratings Distribution')
    fig_boxplot.update_traces(marker=dict(color='yellow'))
    fig_boxplot.update_layout(template='plotly_dark', font=dict(color='yellow'))

    return fig_treemap, fig_bar_language, fig_choropleth, fig_boxplot