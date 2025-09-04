"""
Query Manager for IMDB Dashboard
Contains all data queries from dash files to ensure consistency between Plotly and Excel
"""

import pandas as pd
from typing import Dict, Tuple, Any

class QueryManager:
    """Manages all data queries to ensure consistency between Plotly and Excel"""
    
    def __init__(self, movies: pd.DataFrame, series: pd.DataFrame, 
                 movies_splits: Dict[str, pd.DataFrame], series_splits: Dict[str, pd.DataFrame]):
        self.movies = movies
        self.series = series
        self.movies_splits = movies_splits
        self.series_splits = series_splits
        self._cache = {}
        
    # ==================== OVERVIEW TAB QUERIES (from dash1.py) ====================
    
    def get_parental_guide_treemap_data(self) -> pd.DataFrame:
        """Get data for Parental Guide Treemap - EXACTLY from dash1.py"""
        if 'parental_guide_treemap' not in self._cache:
            # EXACTLY the same query as in dash1.py
            top_five_genres = self.series["parentalguide"].value_counts().head(10).reset_index(name='count')
            self._cache['parental_guide_treemap'] = top_five_genres
        return self._cache['parental_guide_treemap']
    
    def get_genre_bar_data(self) -> pd.DataFrame:
        """Get data for Genre Bar Chart - EXACTLY from dash1.py"""
        if 'genre_bar' not in self._cache:
            # EXACTLY the same query as in dash1.py
            top_values_language = self.movies_splits["genre"]["genre"].value_counts().head(15).reset_index(name='count')
            total_count_language = top_values_language['count'].sum()
            top_values_language['percentage'] = (top_values_language['count'] / total_count_language) * 100
            self._cache['genre_bar'] = top_values_language
        return self._cache['genre_bar']
    
    def get_country_choropleth_data(self) -> pd.DataFrame:
        """Get data for Country Choropleth - EXACTLY from dash1.py"""
        if 'country_choropleth' not in self._cache:
            # EXACTLY the same query as in dash1.py
            top_countries = self.movies_splits["country"]["country"].value_counts().head(30).reset_index(name='count')
            
            # EXACTLY the same country mapping as in dash1.py
            country_mapping = {
                'United States': 'USA',
                'United Kingdom': 'GBR',
                'France': 'FRA',
                'Canada': 'CAN',
                'Germany': 'DEU',
                'Japan': 'JPN',
                'India': 'IND',
                'Australia': 'AUS',
                'China': 'CHN',
                'Italy': 'ITA',
                'Spain': 'ESP',
                'Mexico': 'MEX',
                'Hong Kong': 'HKG',
                'Sweden': 'SWE',
                'Denmark': 'DNK',
                'New Zealand': 'NZL',
                'Belgium': 'BEL',
                'South Korea': 'KOR',
                'Ireland': 'IRL',
                'Czech Republic': 'CZE',
                'Switzerland': 'CHE',
                'Hungary': 'HUN',
                'Norway': 'NOR',
                'United Arab Emirates': 'ARE',
                'Netherlands': 'NLD',
                'South Africa': 'ZAF',
                'Poland': 'POL',
                'West Germany': 'DEU',
                'Austria': 'AUT',
                'Turkey': 'TUR'
            }
            top_countries['country'] = top_countries['country'].map(country_mapping)
            self._cache['country_choropleth'] = top_countries
        return self._cache['country_choropleth']
    
    def get_ratings_box_data(self) -> pd.DataFrame:
        """Get data for Ratings Box Plot - EXACTLY from dash1.py"""
        if 'ratings_box' not in self._cache:
            # EXACTLY the same query as in dash1.py
            ratings_data = self.series[["rating", "votes"]].copy()
            self._cache['ratings_box'] = ratings_data
        return self._cache['ratings_box']
    
    # ==================== CONTENT CREATORS TAB QUERIES (from dash2.py) ====================
    
    def get_creators_pie_data(self) -> pd.DataFrame:
        """Get data for Creators Pie Chart - EXACTLY from dash2.py"""
        if 'creators_pie' not in self._cache:
            # EXACTLY the same query as in dash2.py
            top_five_genres = self.series_splits["creators"]["creators"].value_counts().head(3).reset_index(name='count')
            self._cache['creators_pie'] = top_five_genres
        return self._cache['creators_pie']
    
    def get_production_company_bar_data(self) -> pd.DataFrame:
        """Get data for Production Company Bar Chart - EXACTLY from dash2.py"""
        if 'production_company_bar' not in self._cache:
            # EXACTLY the same query as in dash2.py
            top_values_country = self.series_splits["production_company"]["production_company"].value_counts().head(10).reset_index(name='count')
            total_count_country = top_values_country['count'].sum()
            top_values_country['percentage'] = (top_values_country['count'] / total_count_country) * 100
            self._cache['production_company_bar'] = top_values_country
        return self._cache['production_company_bar']
    
    def get_stars_bar_data(self) -> pd.DataFrame:
        """Get data for Stars Bar Chart - EXACTLY from dash2.py"""
        if 'stars_bar' not in self._cache:
            # EXACTLY the same query as in dash2.py
            top_values_language = self.series_splits["stars"]["stars"].value_counts().head(10).reset_index(name='count')
            total_count_language = top_values_language['count'].sum()
            top_values_language['percentage'] = (top_values_language['count'] / total_count_language) * 100
            self._cache['stars_bar'] = top_values_language
        return self._cache['stars_bar']
    
    def get_language_bar_data(self) -> pd.DataFrame:
        """Get data for Language Bar Chart - EXACTLY from dash2.py"""
        if 'language_bar' not in self._cache:
            # EXACTLY the same query as in dash2.py
            top_values = self.series_splits["language"]["language"].value_counts().head(10).reset_index(name='count')
            total_count = top_values['count'].sum()
            top_values['percentage'] = (top_values['count'] / total_count) * 100
            self._cache['language_bar'] = top_values
        return self._cache['language_bar']
    
    # ==================== PARENTAL GUIDE TAB QUERIES (from dash3.py) ====================
    
    def get_parental_guide_mean_votes_data(self) -> pd.DataFrame:
        """Get data for Parental Guide Mean Votes - EXACTLY from dash3.py"""
        if 'parental_guide_mean_votes' not in self._cache:
            # EXACTLY the same query as in dash3.py
            parental_votes_data = self.series.groupby("parentalguide")["votes"].mean().reset_index()
            parental_votes_data.columns = ['Parental Guide', 'Mean Votes']
            parental_votes_data = parental_votes_data.sort_values(by=["Mean Votes"], ascending=False)
            self._cache['parental_guide_mean_votes'] = parental_votes_data
        return self._cache['parental_guide_mean_votes']
    
    def get_parental_guide_count_data(self) -> pd.DataFrame:
        """Get data for Parental Guide Count - EXACTLY from dash3.py"""
        if 'parental_guide_count' not in self._cache:
            # EXACTLY the same query as in dash3.py
            parental_count_data = self.series.groupby("parentalguide").size().reset_index(name='count')
            parental_count_data.columns = ['Parental Guide', 'Count']
            parental_count_data = parental_count_data.sort_values(by=["Count"], ascending=False)
            self._cache['parental_guide_count'] = parental_count_data
        return self._cache['parental_guide_count']
    
    # ==================== YEAR TAB QUERIES (from dash4.py) ====================
    
    def get_year_work_count_data(self) -> pd.DataFrame:
        """Get data for Year Work Count - EXACTLY from dash4.py"""
        if 'year_work_count' not in self._cache:
            # EXACTLY the same query as in dash4.py
            year_count_data = self.series.groupby("year").size().reset_index(name='count')
            year_count_data.columns = ['Year', 'Count']
            self._cache['year_work_count'] = year_count_data
        return self._cache['year_work_count']
    
    def get_year_mean_votes_data(self) -> pd.DataFrame:
        """Get data for Year Mean Votes - EXACTLY from dash4.py"""
        if 'year_mean_votes' not in self._cache:
            # EXACTLY the same query as in dash4.py
            year_votes_data = self.series.groupby("year")["votes"].mean().reset_index()
            year_votes_data.columns = ['Year', 'Mean Votes']
            self._cache['year_mean_votes'] = year_votes_data
        return self._cache['year_mean_votes']
    
    # ==================== CONVENIENCE METHODS ====================
    
    def get_overview_data(self) -> Dict[str, pd.DataFrame]:
        """Get all Overview tab data using EXACT queries from dash1.py"""
        return {
            'parental_guide': self.get_parental_guide_treemap_data(),
            'genre': self.get_genre_bar_data(),
            'country': self.get_country_choropleth_data(),
            'ratings': self.get_ratings_box_data()
        }
    
    def get_content_creators_data(self) -> Dict[str, pd.DataFrame]:
        """Get all Content Creators tab data using EXACT queries from dash2.py"""
        return {
            'creators': self.get_creators_pie_data(),
            'production_company': self.get_production_company_bar_data(),
            'stars': self.get_stars_bar_data(),
            'language': self.get_language_bar_data()
        }
    
    def get_parental_guide_data(self) -> Dict[str, pd.DataFrame]:
        """Get all Parental Guide tab data using EXACT queries from dash3.py"""
        return {
            'mean_votes': self.get_parental_guide_mean_votes_data(),
            'count': self.get_parental_guide_count_data()
        }
    
    def get_year_data(self) -> Dict[str, pd.DataFrame]:
        """Get all Year tab data using EXACT queries from dash4.py"""
        return {
            'work_count': self.get_year_work_count_data(),
            'mean_votes': self.get_year_mean_votes_data()
        }
    
    def get_all_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Get all data using EXACT queries from all dash files"""
        return {
            'overview': self.get_overview_data(),
            'content_creators': self.get_content_creators_data(),
            'parental_guide': self.get_parental_guide_data(),
            'year': self.get_year_data()
        }
    
    def get_raw_data(self) -> Dict[str, pd.DataFrame]:
        """Get raw data for export"""
        return {
            'movies': self.movies,
            'series': self.series
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data"""
        cache_info = {}
        for key, value in self._cache.items():
            if isinstance(value, pd.DataFrame):
                cache_info[key] = f"DataFrame({value.shape[0]} rows, {value.shape[1]} cols)"
            else:
                cache_info[key] = type(value).__name__
        return cache_info

# Global instance
_query_manager = None

def get_query_manager(movies: pd.DataFrame = None, series: pd.DataFrame = None, 
                     movies_splits: Dict[str, pd.DataFrame] = None, 
                     series_splits: Dict[str, pd.DataFrame] = None) -> QueryManager:
    """Get or create global query manager instance"""
    global _query_manager
    
    if _query_manager is None and all([movies is not None, series is not None, 
                                      movies_splits is not None, series_splits is not None]):
        _query_manager = QueryManager(movies, series, movies_splits, series_splits)
    
    return _query_manager

def clear_global_query_manager():
    """Clear global query manager instance"""
    global _query_manager
    if _query_manager:
        _query_manager.clear_cache()
        _query_manager = None
