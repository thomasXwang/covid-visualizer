import streamlit as st

import datetime
# from datetime import date

import os 
from PIL import Image

import pandas as pd
import numpy as np

import plotly.graph_objects as go


DATA_SOURCE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"



@st.cache
def load_data(data_url):
    df = pd.read_csv(data_url)
    return df


@st.cache
def get_countries(df):
    return sorted(df["Country/Region"].unique().tolist())


def show_sidebar(countries):
    selected_country = st.sidebar.selectbox("Select a country", countries)

    return selected_country


def main():

    st.header("Covid-19 visualizations")


    st.subheader("Input Dataframe")
    df_original = load_data(DATA_SOURCE)
    st.write("DF Original")
    st.write(df_original.shape)
    st.write(df_original)

    st.write(df_original.describe())
    # st.write(df_original.dtypes)

    st.info("Data Loaded")

    df =  df_original.copy(deep=True)

    countries = get_countries(df_original)
    st.write(countries)

    selected_country = show_sidebar(countries)

    df_country = df[df["Country/Region"] == selected_country]
    st.write(df_country)

    dfs_plot = {}

    df_plot = df_country.copy(deep=True)
    df_plot = df_plot.drop(columns=["Province/State", "Country/Region", "Lat", "Long"])
    df_plot = df_plot.sum(axis=0)
    df_plot = pd.DataFrame(df_plot)
    st.write(df_plot.columns.tolist())
    df_plot.columns = ["Cases"]
    
    dfs_plot[selected_country] = df_plot
    
    st.write(df_plot)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dfs_plot[selected_country].index, 
        y=dfs_plot[selected_country]["Cases"], 
        name="Cases", 
        # line_color="red"
    ))

    fig.update_layout(title_text='Time Series with Rangeslider',
                  xaxis_rangeslider_visible=True)
    # fig.update_layout(xaxis_range=['2020-01-01','2020-03-20'],
    #               title_text="Manually Set Date Range")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Infected count",
        title_text=f"Number of cases in {selected_country}",
        
        width=1000,
        height=800  )

    st.write(fig)

    # st.write("DF")
    # df =  df_original.copy(deep=True)

    # st.write(df.shape)
    # st.write(df)

  


main()