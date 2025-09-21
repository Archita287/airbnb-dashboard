# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 23:20:00 2025

@author: Archita
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Global Variables and Page Configuration ---
# Define numeric columns in the global scope
numeric_cols = ['price', 'service_fee', 'minimum_nights', 'number_of_reviews', 'reviews_per_month', 'availability_365']

st.set_page_config(
    page_title="Airbnb Listings Dashboard",
    layout="wide",
)

# --- Data Loading and Cleaning ---
@st.cache_data
def load_data(file_path):
    """
    Loads data and performs initial cleaning.
    """
    df = pd.read_csv(file_path)

    # Clean up column names and whitespace
    df.columns = df.columns.str.strip().str.replace(' ', '_')

    # Convert columns to numeric, handling missing values and commas
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('$', '').str.replace(',', '').astype(float)
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Convert 'last_review' to datetime
    df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')
    
    return df

try:
    data = load_data('airbnb_project_cleaned.csv')
    st.success("Data loaded successfully!")
except FileNotFoundError:
    st.error("Error: The file `airbnb_project_cleaned.csv` was not found. Please make sure it's in the same directory.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# Neighborhood group selection
unique_neighbourhood_groups = data['neighbourhood_group'].unique()
selected_groups = st.sidebar.multiselect(
    "Select Neighbourhood Group(s)",
    options=unique_neighbourhood_groups,
    default=unique_neighbourhood_groups
)
filtered_data = data[data['neighbourhood_group'].isin(selected_groups)]

# Room type selection
unique_room_types = filtered_data['room_type'].unique()
selected_room_types = st.sidebar.multiselect(
    "Select Room Type(s)",
    options=unique_room_types,
    default=unique_room_types
)
filtered_data = filtered_data[filtered_data['room_type'].isin(selected_room_types)]

# --- Main Dashboard Layout ---
st.title("Airbnb Listings Dashboard")
st.markdown("Explore key metrics and distributions of Airbnb listings using this interactive dashboard.")

if filtered_data.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()

# --- Section 1: Distribution Plots ---
st.header("1. Listing Distributions")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Room Type Distribution by Neighbourhood Group")
    fig_bar = px.bar(
        filtered_data.groupby(['neighbourhood_group', 'room_type']).size().reset_index(name='count'),
        x='neighbourhood_group',
        y='count',
        color='room_type',
        title='Count of Room Types by Neighbourhood Group',
        labels={'count': 'Number of Listings', 'neighbourhood_group': 'Neighbourhood Group', 'room_type': 'Room Type'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
with col2:
    st.subheader("Percentage Distribution of Room Types")
    room_type_counts = filtered_data['room_type'].value_counts().reset_index()
    room_type_counts.columns = ['room_type', 'count']
    fig_pie_room_type = px.pie(
        room_type_counts,
        values='count',
        names='room_type',
        title='Distribution of Room Types',
        hole=0.4 # Donut chart for better aesthetics
    )
    st.plotly_chart(fig_pie_room_type, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Distribution of Neighbourhood Groups (Exploding Pie)")
    neighbourhood_counts = filtered_data['neighbourhood_group'].value_counts().reset_index()
    neighbourhood_counts.columns = ['neighbourhood_group', 'count']
    
    # Use plotly.graph_objects to create the exploding pie chart
    fig_pie_group = go.Figure(data=[go.Pie(
        labels=neighbourhood_counts['neighbourhood_group'],
        values=neighbourhood_counts['count'],
        pull=[0.1] * len(neighbourhood_counts), # Exploding effect
        hole=0.3 # Optional: makes it a donut chart
    )])
    
    fig_pie_group.update_traces(marker=dict(line=dict(color='#000000', width=1)))
    fig_pie_group.update_layout(title_text='Distribution of Neighbourhood Groups')
    
    st.plotly_chart(fig_pie_group, use_container_width=True)

with col4:
    st.subheader("Instant Bookable Listings")
    instant_bookable_counts = filtered_data['instant_bookable'].value_counts().reset_index()
    instant_bookable_counts.columns = ['instant_bookable', 'count']
    fig_pie_instant = px.pie(
        instant_bookable_counts,
        values='count',
        names='instant_bookable',
        title='Listings by Instant Bookability',
        labels={'instant_bookable': 'Instant Bookable'}
    )
    st.plotly_chart(fig_pie_instant, use_container_width=True)

st.markdown("---")

# --- Section 2: Price and Review Analysis ---
st.header("2. Price and Review Analysis")
col5, col6 = st.columns(2)

with col5:
    st.subheader("Average Reviews per Month")
    avg_reviews_by_group = filtered_data.groupby('neighbourhood_group')['reviews_per_month'].mean().reset_index()
    fig_avg_reviews = px.bar(
        avg_reviews_by_group,
        x='neighbourhood_group',
        y='reviews_per_month',
        color='reviews_per_month',
        title='Average Reviews Per Month by Neighbourhood Group',
        labels={'reviews_per_month': 'Average Reviews per Month'}
    )
    st.plotly_chart(fig_avg_reviews, use_container_width=True)

with col6:
    st.subheader("Price vs. Minimum Nights (Bubble Plot)")
    fig_bubble = px.scatter(
        filtered_data.dropna(subset=['reviews_per_month']),
        x='minimum_nights',
        y='price',
        size='reviews_per_month',
        color='room_type',
        hover_name='NAME',
        title='Price vs. Minimum Nights (Bubble Size by Reviews/Month)',
        labels={'minimum_nights': 'Minimum Nights', 'price': 'Price ($)', 'reviews_per_month': 'Reviews per Month'}
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

st.subheader("Price vs. Availability (Color by Room Type)")
fig_scatter = px.scatter(
    filtered_data,
    x='availability_365',
    y='price',
    color='room_type',
    hover_name='NAME',
    title='Price vs. Availability 365 (Color by Room Type)',
    labels={'availability_365': 'Availability (Days)', 'price': 'Price ($)'}
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- Section 3: Detailed Plots ---
st.header("3. Advanced Visualizations")
col7, col8 = st.columns(2)

with col7:
    st.subheader("Minimum Nights per Neighbourhood Group")
    fig_box = px.box(
        filtered_data,
        x='neighbourhood_group',
        y='minimum_nights',
        color='neighbourhood_group',
        title='Minimum Nights per Neighbourhood Group',
        labels={'minimum_nights': 'Minimum Nights', 'neighbourhood_group': 'Neighbourhood Group'}
    )
    st.plotly_chart(fig_box, use_container_width=True)

with col8:
    st.subheader("Correlation Heatmap")
    numeric_df = filtered_data[numeric_cols].corr()
    fig_heatmap = px.imshow(
        numeric_df,
        text_auto=".2f",
        title='Correlation Heatmap of Numeric Features',
        color_continuous_scale=px.colors.diverging.RdBu_r,
        aspect="auto"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)