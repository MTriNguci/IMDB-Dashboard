import plotly.express as px
from .query_manager import get_query_manager

def generate_visualizations(series, splits):
    # Get query manager to use EXACT same queries
    query_manager = get_query_manager()
    
    # Use EXACT same data from QueryManager
    top_five_genres = query_manager.get_creators_pie_data()
    fig_donut1 = px.pie(top_five_genres, 
                             names='creators',  
                             values='count', 
                             title='Top creators',
                             
                             hole=0.5)
    fig_donut1.update_layout(template='plotly_dark', font=dict(color='yellow'))

    # Use EXACT same data from QueryManager
    top_values_country = query_manager.get_production_company_bar_data()
    fig_bar_country = px.bar(top_values_country, x='count', y="production_company", orientation='h',
                             color='count', text='percentage',
                             title='Top Productions Company',
                             labels={'count': 'Count', 'index': 'Production Company', 'percentage': 'Percentage'})
    fig_bar_country.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_bar_country.update_layout(yaxis_title='Production Company')
    fig_bar_country.update_layout(yaxis=dict(categoryorder='total ascending'))
    fig_bar_country.update_layout(template='plotly_dark', font=dict(color='yellow'))

    # Use EXACT same data from QueryManager
    top_values_language = query_manager.get_stars_bar_data()
    fig_bar_language = px.bar(top_values_language, y='count', x="stars", orientation='v',
                              color='count', text='percentage',
                              title='Top stars',
                              labels={'count': 'Count', 'index': 'stars', 'percentage': 'Percentage'})
    fig_bar_language.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_bar_language.update_layout(yaxis=dict(categoryorder='total ascending'))
    fig_bar_language.update_layout(template='plotly_dark', font=dict(color='yellow'))

    # Use EXACT same data from QueryManager
    top_values = query_manager.get_language_bar_data()
    fig_bar_language2 = px.bar(top_values, y='count', x="language", orientation='v',
                               color='count', text='percentage',
                               title='Top Languages',
                               labels={'count': 'Count', 'index': 'Language', 'percentage': 'Percentage'})

    fig_bar_language2.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_bar_language2.update_layout(yaxis=dict(categoryorder='total ascending'))
    fig_bar_language2.update_layout(template='plotly_dark', font=dict(color='yellow'))

    return fig_donut1, fig_bar_country, fig_bar_language, fig_bar_language2