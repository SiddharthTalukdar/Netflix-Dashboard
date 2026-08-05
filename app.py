import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration setup
st.set_page_config(page_title="Netflix Analytics Dashboard", page_icon="🎬", layout="wide")

# Load the raw dataset
my_netflix_dataframe = pd.read_csv("netflix_titles.csv")

# Fill missing text values so app does not crash
my_netflix_dataframe['director'] = my_netflix_dataframe['director'].fillna("Unknown Director")
my_netflix_dataframe['country'] = my_netflix_dataframe['country'].fillna("Unknown Country")
my_netflix_dataframe['rating'] = my_netflix_dataframe['rating'].fillna("Not Rated")
my_netflix_dataframe['cast'] = my_netflix_dataframe['cast'].fillna("Unknown Cast")

# Parse date added string into a clear year column
my_netflix_dataframe['date_added_clean'] = my_netflix_dataframe['date_added'].str.strip()
my_netflix_dataframe['date_added_parsed'] = pd.to_datetime(my_netflix_dataframe['date_added_clean'], format='mixed', errors='coerce')
my_netflix_dataframe['year_added'] = my_netflix_dataframe['date_added_parsed'].dt.year

# Extract numeric values for duration
my_netflix_dataframe['duration_num'] = my_netflix_dataframe['duration'].str.extract(r'(\d+)').astype(float)

# Dashboard title and introduction
st.title("🎬 Netflix Content Analysis Dashboard")
st.write("An exploratory data analysis dashboard analyzing global Netflix movies, TV shows, genres, and production trends.")

# Sidebar filter for content type
st.sidebar.header("Filter Options")
selected_content_type_choice = st.sidebar.selectbox("Select Content Type:", ["All", "Movie", "TV Show"])

# Filter dataframe based on user choice
if selected_content_type_choice == "All":
    my_filtered_netflix_dataframe = my_netflix_dataframe.copy()
else:
    my_filtered_netflix_dataframe = my_netflix_dataframe[my_netflix_dataframe['type'] == selected_content_type_choice]

st.divider()

# Section 1: Calculate total summary metrics
st.header("Overall Key Metrics")

total_number_of_titles_count = len(my_filtered_netflix_dataframe)
total_number_of_movies_count = len(my_filtered_netflix_dataframe[my_filtered_netflix_dataframe['type'] == 'Movie'])
total_number_of_tv_shows_count = len(my_filtered_netflix_dataframe[my_filtered_netflix_dataframe['type'] == 'TV Show'])

first_metric_column, second_metric_column, third_metric_column = st.columns(3)
first_metric_column.metric("Total Selected Titles", total_number_of_titles_count)
second_metric_column.metric("Total Movies", total_number_of_movies_count)
third_metric_column.metric("Total TV Shows", total_number_of_tv_shows_count)

st.divider()

# Section 2: Movie vs TV Show ratio visual split
st.header("Movie vs TV Show Ratio")

content_type_counts_dataframe = my_filtered_netflix_dataframe['type'].value_counts().reset_index()
content_type_counts_dataframe.columns = ['Type', 'Total Count']

first_ratio_column, second_ratio_column = st.columns(2)

with first_ratio_column:
    # Pie chart representation
    content_type_pie_chart_figure = px.pie(
        content_type_counts_dataframe, 
        names='Type', 
        values='Total Count', 
        title="Content Type Split (Pie Chart)",
        color='Type',
        color_discrete_map={'Movie': '#E50914', 'TV Show': '#003366'}
    )
    st.plotly_chart(content_type_pie_chart_figure, use_container_width=True)

with second_ratio_column:
    # Bar chart representation
    content_type_bar_chart_figure = px.bar(
        content_type_counts_dataframe, 
        x='Type', 
        y='Total Count', 
        color='Type', 
        title="Content Type Comparison (Bar Chart)",
        color_discrete_map={'Movie': '#E50914', 'TV Show': '#003366'}
    )
    st.plotly_chart(content_type_bar_chart_figure, use_container_width=True)

st.divider()

# Section 3: Time series charts for addition year and release year
st.header("Content Added Over Time")
yearly_added_content_dataframe = my_filtered_netflix_dataframe.groupby(['year_added', 'type']).size().reset_index(name='Count').dropna()

titles_added_line_chart_figure = px.line(
    yearly_added_content_dataframe, 
    x='year_added', 
    y='Count', 
    color='type', 
    markers=True,
    title="Titles Added to Netflix Per Year"
)
st.plotly_chart(titles_added_line_chart_figure, use_container_width=True)

st.header("Release Year Trends")
release_year_counts_dataframe = my_filtered_netflix_dataframe['release_year'].value_counts().reset_index()
release_year_counts_dataframe.columns = ['Release Year', 'Count']
release_year_counts_dataframe = release_year_counts_dataframe.sort_values('Release Year')

release_year_bar_chart_figure = px.bar(
    release_year_counts_dataframe, 
    x='Release Year', 
    y='Count', 
    title="Content Distribution by Original Release Year"
)
st.plotly_chart(release_year_bar_chart_figure, use_container_width=True)

st.divider()

# Section 4: Top 10 Countries and Directors (filters out ANY Unknown entries)
first_top_ten_column, second_top_ten_column = st.columns(2)

with first_top_ten_column:
    st.header("Top 10 Content Producing Countries")
    # Strictly remove any country containing the word Unknown
    countries_cleaned_dataframe = my_filtered_netflix_dataframe[~my_filtered_netflix_dataframe['country'].str.contains("Unknown", case=False, na=False)]
    top_ten_countries_counts_dataframe = countries_cleaned_dataframe['country'].str.split(', ').explode().value_counts()
    top_ten_countries_counts_dataframe = top_ten_countries_counts_dataframe[~top_ten_countries_counts_dataframe.index.str.contains("Unknown", case=False)].head(10).reset_index()
    top_ten_countries_counts_dataframe.columns = ['Country', 'Count']

    top_countries_bar_chart_figure = px.bar(top_ten_countries_counts_dataframe, x='Count', y='Country', orientation='h', title="Top 10 Countries")
    top_countries_bar_chart_figure.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(top_countries_bar_chart_figure, use_container_width=True)

with second_top_ten_column:
    st.header("Top 10 Directors")
    # Strictly remove any director containing the word Unknown
    directors_cleaned_dataframe = my_filtered_netflix_dataframe[~my_filtered_netflix_dataframe['director'].str.contains("Unknown", case=False, na=False)]
    top_ten_directors_counts_dataframe = directors_cleaned_dataframe['director'].str.split(', ').explode().value_counts()
    top_ten_directors_counts_dataframe = top_ten_directors_counts_dataframe[~top_ten_directors_counts_dataframe.index.str.contains("Unknown", case=False)].head(10).reset_index()
    top_ten_directors_counts_dataframe.columns = ['Director', 'Count']

    top_directors_bar_chart_figure = px.bar(top_ten_directors_counts_dataframe, x='Count', y='Director', orientation='h', title="Top 10 Directors")
    top_directors_bar_chart_figure.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(top_directors_bar_chart_figure, use_container_width=True)

st.divider()

# Section 5: Top 10 Genres and Top Actors (filters out ANY Unknown entries)
first_genre_actor_column, second_genre_actor_column = st.columns(2)

with first_genre_actor_column:
    st.header("Top 10 Genres")
    top_ten_genres_counts_dataframe = my_filtered_netflix_dataframe['listed_in'].str.split(', ').explode().value_counts().head(10).reset_index()
    top_ten_genres_counts_dataframe.columns = ['Genre', 'Count']

    top_genres_bar_chart_figure = px.bar(top_ten_genres_counts_dataframe, x='Count', y='Genre', orientation='h', title="Most Popular Genres")
    top_genres_bar_chart_figure.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(top_genres_bar_chart_figure, use_container_width=True)

with second_genre_actor_column:
    st.header("Top Featured Actors")
    # Strictly remove any cast member containing the word Unknown
    actors_cleaned_dataframe = my_filtered_netflix_dataframe[~my_filtered_netflix_dataframe['cast'].str.contains("Unknown", case=False, na=False)]
    top_ten_actors_counts_dataframe = actors_cleaned_dataframe['cast'].str.split(', ').explode().value_counts()
    top_ten_actors_counts_dataframe = top_ten_actors_counts_dataframe[~top_ten_actors_counts_dataframe.index.str.contains("Unknown", case=False)].head(10).reset_index()
    top_ten_actors_counts_dataframe.columns = ['Actor', 'Count']

    top_actors_bar_chart_figure = px.bar(top_ten_actors_counts_dataframe, x='Count', y='Actor', orientation='h', title="Most Featured Actors")
    top_actors_bar_chart_figure.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(top_actors_bar_chart_figure, use_container_width=True)

st.divider()

# Section 6: Audience Rating Distribution and Duration Analysis
st.header("Rating Distribution")
audience_rating_counts_dataframe = my_filtered_netflix_dataframe['rating'].value_counts().head(10).reset_index()
audience_rating_counts_dataframe.columns = ['Rating', 'Count']

audience_ratings_bar_chart_figure = px.bar(audience_rating_counts_dataframe, x='Rating', y='Count', title="Most Common Audience Ratings")
st.plotly_chart(audience_ratings_bar_chart_figure, use_container_width=True)

first_duration_column, second_duration_column = st.columns(2)

with first_duration_column:
    st.header("Movie Duration Breakdown")
    movies_duration_dataframe = my_filtered_netflix_dataframe[my_filtered_netflix_dataframe['type'] == 'Movie'].dropna(subset=['duration_num'])
    movie_duration_histogram_figure = px.histogram(movies_duration_dataframe, x='duration_num', nbins=30, title="Movie Runtime (Minutes)")
    movie_duration_histogram_figure.update_layout(xaxis_title="Duration (Minutes)", yaxis_title="Number of Movies")
    st.plotly_chart(movie_duration_histogram_figure, use_container_width=True)

with second_duration_column:
    st.header("TV Show Season Count")
    tv_shows_duration_dataframe = my_filtered_netflix_dataframe[my_filtered_netflix_dataframe['type'] == 'TV Show'].dropna(subset=['duration_num'])
    tv_show_seasons_counts_dataframe = tv_shows_duration_dataframe['duration_num'].value_counts().reset_index()
    tv_show_seasons_counts_dataframe.columns = ['Seasons', 'Count']
    tv_show_seasons_counts_dataframe = tv_show_seasons_counts_dataframe.sort_values('Seasons')

    tv_show_seasons_bar_chart_figure = px.bar(tv_show_seasons_counts_dataframe, x='Seasons', y='Count', title="TV Show Seasons Distribution")
    tv_show_seasons_bar_chart_figure.update_layout(xaxis_title="Number of Seasons", yaxis_title="Number of Shows")
    st.plotly_chart(tv_show_seasons_bar_chart_figure, use_container_width=True)

st.divider()

# Section 7: Earliest vs Most Recent Movie/Show releases
st.header("Oldest vs Newest Titles")

minimum_release_year_value = int(my_filtered_netflix_dataframe['release_year'].min())
maximum_release_year_value = int(my_filtered_netflix_dataframe['release_year'].max())

first_age_metric_column, second_age_metric_column = st.columns(2)
first_age_metric_column.metric("Earliest Release Year", minimum_release_year_value)
second_age_metric_column.metric("Latest Release Year", maximum_release_year_value)

oldest_titles_dataframe = my_filtered_netflix_dataframe[my_filtered_netflix_dataframe['release_year'] == minimum_release_year_value][['title', 'type', 'release_year', 'director', 'country']]
newest_titles_dataframe = my_filtered_netflix_dataframe[my_filtered_netflix_dataframe['release_year'] == maximum_release_year_value][['title', 'type', 'release_year', 'director', 'country']].head(5)

first_tab_option, second_tab_option = st.tabs(["📜 Earliest Releases", "🆕 Recent Releases"])
with first_tab_option:
    st.dataframe(oldest_titles_dataframe, use_container_width=True)
with second_tab_option:
    st.dataframe(newest_titles_dataframe, use_container_width=True)

st.divider()

# Section 8: Interactive search bar functionality
st.header("Advanced Search Bar")

user_search_input_query = st.text_input("Search by Movie Title, Director, or Actor Name:", "")

if user_search_input_query.strip():
    search_term_lowercase = user_search_input_query.lower()
    matching_search_results_dataframe = my_filtered_netflix_dataframe[
        my_filtered_netflix_dataframe['title'].str.lower().str.contains(search_term_lowercase, na=False) |
        my_filtered_netflix_dataframe['director'].str.lower().str.contains(search_term_lowercase, na=False) |
        my_filtered_netflix_dataframe['cast'].str.lower().str.contains(search_term_lowercase, na=False)
    ]
    st.write(f"Found **{len(matching_search_results_dataframe)}** result(s) for **'{user_search_input_query}'**:")
    st.dataframe(matching_search_results_dataframe[['title', 'type', 'director', 'cast', 'country', 'release_year', 'rating', 'duration']], use_container_width=True)
else:
    st.info("Enter a keyword above to search through titles, directors, or actors.")