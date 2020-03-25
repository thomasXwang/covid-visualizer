import streamlit as st

import datetime
# from datetime import date

import os 
from PIL import Image

import pandas as pd
import numpy as np

import plotly.graph_objects as go


DATA_SOURCE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

COUNTRY_COL = "Country/Region"
PROVINCE_COL = "Province/State"


@st.cache
def load_data(data_url):
    df = pd.read_csv(data_url)
    return df


@st.cache
def get_countries(df):
    return sorted(df[COUNTRY_COL].unique().tolist())


@st.cache
def get_top_countries(df2, n=6):

    df = df2.copy(deep=True)
    df = df.drop(columns=[PROVINCE_COL, "Lat", "Long"])
    # st.write(df.groupby(COUNTRY_COL).agg("sum"))
    top = df.groupby(COUNTRY_COL).agg("sum").sort_values(by=df.columns.tolist()[-1], ascending=False)
    # st.write(top)
    top_countries = top.head(n).index.tolist()
    # st.write(top_countries)

    return top_countries


@st.cache
def get_df_plot(df, country):
    df_country = df[df[COUNTRY_COL] == country]
    # st.write(df_country)

    df_plot = df_country.copy(deep=True)
    df_plot = df_plot.drop(columns=[PROVINCE_COL, COUNTRY_COL, "Lat", "Long"])
    df_plot = df_plot.sum(axis=0)
    df_plot = pd.DataFrame(df_plot)
    # st.write(df_plot.columns.tolist())
    df_plot.columns = ["Cases"]

    return df_plot


@st.cache
def get_fig(dfs_plot):
    fig = go.Figure()

    for country, df in dfs_plot.items():
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df["Cases"], 
            name=f"{country}", 
            # line_color="red"
        ))

    fig.update_layout(title_text='Time Series with Rangeslider',
                xaxis_rangeslider_visible=True)
    # fig.update_layout(xaxis_range=['2020-01-01','2020-03-20'],
    #               title_text="Manually Set Date Range")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of cases",
        title_text=f"Number of cases of Covid-19",
        
        width=1000,
        height=800)

    return fig



def main():

    st.header("Covid-19 visualizations")

    st.subheader("Input Dataframe")
    
    df_original = load_data(DATA_SOURCE)
    st.write("DF Original")
    st.write(df_original.shape)
    st.write(df_original)

    # st.write(df_original.describe())
    # st.write(df_original.dtypes)

    st.info("Data Loaded")

    df =  df_original.copy(deep=True)

    countries = get_countries(df_original)
    # st.write(countries)


    st.subheader("Evolution of number of cases")

    
    top_n = st.slider(
        "Select number of most-infected countries",
        min_value=5,
        max_value=20,
        value=7
    )

    top_countries = get_top_countries(df, n=top_n)
    # st.write(top_countries)


    selected_countries = st.multiselect(
        "Select the countries you want to visualize",
        countries,
        default=top_countries
    )

    if selected_countries != []:

        dfs_plot = {}

        for country in selected_countries:
            
            df_plot = get_df_plot(df, country)
            dfs_plot[country] = df_plot

            # st.write(f"{country}")
            # st.write(df_plot)
            # st.write(dfs_plot.keys())


        # st.write(dfs_plot.keys())

        fig = get_fig(dfs_plot)

        st.write(fig)

    # st.write("DF")
    # df =  df_original.copy(deep=True)

    # st.write(df.shape)
    # st.write(df)

  
main()