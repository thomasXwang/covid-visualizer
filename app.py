import streamlit as st

import datetime

import os 
from PIL import Image

import pandas as pd
import numpy as np
import math

import plotly.express as px
import plotly.graph_objects as go

DATA_SOURCE_URL = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series"

CONFIRMED_SOURCE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
DEATHS_SOURCE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

COUNTRY_COL = "Country/Region"
PROVINCE_COL = "Province/State"

# Max scale factor for bubble size
MAX_SCALE = 10000


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
def get_fig(dfs_plot, log_scale_choice):
    fig = go.Figure()

    for country, df in dfs_plot.items():
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df["Cases"], 
            name=f"{country}", 
            # Unsuccessful attempt to add non-hovering text
            # https://plotly.com/python/text-and-annotations/#adding-text-to-data-in-line-and-scatter-plots
            # text=f"{country}",
            # textposition="top center",
            # mode= "lines+text",
            # line_color="red"
        ))

    # fig.update_layout(xaxis_range=['2020-01-01','2020-03-20'],
    #               title_text="Manually Set Date Range")
    fig.update_layout(
        xaxis_title="To Date",
        yaxis_title="Total number of cases",
        title_text="Total number of cases of Covid-19",

        xaxis_rangeslider_visible=True,
        
        width=1000,
        height=800)

    if log_scale_choice == "Logarithmic":
        fig.update_yaxes(type="log")

    return fig


@st.cache
def get_map_plot(df2, scale=50):
    # https://plotly.com/python/scatter-plots-on-maps/
    # https://plotly.com/python/bubble-maps/
    df = df2.copy(deep=True)

    # df["Description"] = df[COUNTRY_COL].str.cat(df[df.columns.tolist()[-1]].astype(str), sep="_")
    # fig = px.scatter_geo(df, locations="iso_alpha", color="continent",
    #                  hover_name=COUNTRY_COL, size=df.columns.tolist()[-1],
    #                  projection="natural earth")

    # st.write(df)
    # scale = 50

    df["text"] = (
        df[COUNTRY_COL] 
        + "<br> " 
        + df[PROVINCE_COL].replace(np.nan, '', regex=True) 
        + "<br>"
        + df[df.columns.tolist()[-1]].apply(str)
    ).str.replace("<br> <br>", "<br>")
    # df["text"] = df.agg(lambda x: f"{x[COUNTRY_COL]} - {x[PROVINCE_COL]} :  {str(x[df.columns.tolist()[-1]])}", axis=1)
    # st.write(df["text"])
    # st.write(df[COUNTRY_COL])

    fig = go.Figure(data=go.Scattergeo(
        lon = df['Long'],
        lat = df['Lat'],
        hoverinfo="text",
        # text = df[COUNTRY_COL],
        text = df["text"],
        mode = 'markers',
        marker = dict(
            # Changed it to np.max to avoid errors when JHU gives a negative number
            size = np.maximum(df2[df2.columns.tolist()[-1]]/scale, 0),
            color = "red",
            line_width = 1,
            sizemode="area"
        )
    ))

    fig.update_layout(
        title="Number of cases of Covid-19",
        
        width=1000,
        height=500)

    return fig


@st.cache
def get_df_mortality_rate(df_confirmed, df_deaths):

    df_countries = df_confirmed.copy(deep=True).iloc[:, :4]

    df_confirmed_copy = df_confirmed.copy(deep=True)
    df_deaths_copy = df_deaths.copy(deep=True)
    df_confirmed_reduced = df_confirmed_copy.iloc[:, 4:].sum(axis=1).replace(0, 1)
    df_deaths_reduced = df_deaths_copy.iloc[:, 4:].sum(axis=1)

    df_mortality_rates = df_deaths_reduced / df_confirmed_reduced

    return pd.concat([df_countries, df_mortality_rates], axis=1)


@st.cache
def get_fig_country(country, df_confirmed, df_deaths):
    fig = go.Figure()

    df_confirmed_country = get_df_plot(df_confirmed, country)
    df_deaths_country = get_df_plot(df_deaths, country)

    # df_confirmed_country = get_df_plot(df_confirmed, country).cumsum(axis=0)
    # df_deaths_country = get_df_plot(df_deaths, country).cumsum(axis=0)

    # st.write(df_confirmed_country)
    # st.write(df_deaths_country)

    mortality_rate = df_deaths_country.iloc[-1,0] / df_confirmed_country.iloc[-1,0]

    fig.add_trace(go.Scatter(
        x=df_confirmed_country.index, 
        y=df_confirmed_country["Cases"], 
        name=f"Confirmed cases",
        yaxis="y1" 
    ))
    fig.add_trace(go.Scatter(
        x=df_deaths_country.index, 
        y=df_deaths_country["Cases"], 
        name=f"Deaths",
        yaxis="y2", 
    ))

    fig.update_layout(
        xaxis_title="To Date",
        yaxis=dict(
            title="Number of Confirmed cases",
            titlefont=dict(color="#1f77b4"),
            tickfont=dict(color="#1f77b4"),
        ),
        yaxis2=dict(
            title="Number of Deaths",
            titlefont=dict(color="#ff7f0e"),
            tickfont=dict(color="#ff7f0e"),
            anchor="x",
            overlaying="y",
            side="right",
        ),
        title_text=f"Total number of cases of Covid-19 in {country}",

        xaxis_rangeslider_visible=True,
        
        width=1000,
        height=800)

    return (mortality_rate, fig)


def main():

    st.header("Covid-19 visualizer")

    st.subheader("Input Data")

    st.sidebar.header("⚙️ Parameters")

    viz_choice = st.sidebar.selectbox(
        "Visualization",
        ["World view", "Country view"],
        index=0
    )

    

    df_confirmed = load_data(CONFIRMED_SOURCE)
    df_deaths = load_data(DEATHS_SOURCE)

    st.info("Data Loaded")
    df_original = df_confirmed
    st.write(f"[Data]({DATA_SOURCE_URL}) last updated on: {df_original.columns.tolist()[-1]}")

    # st.write("Data is updated daily")
    # st.write("It is provided by John Hopkins University: https://github.com/CSSEGISandData/COVID-19")
    
    if viz_choice == "World view":

        data_choice = st.sidebar.radio(
        "Visualize numbers of ",
        ["Infections", "Deaths", "Mortality Rate"],
        index=0
        )
        log_scale_choice = st.sidebar.radio(
            "Plot Y-axis Scale",
            ["Standard", "Logarithmic"]
        )
    
        df_original = df_confirmed
        if data_choice == "Deaths":
            df_original = df_deaths
        if data_choice == "Mortality Rate":
            df_original = get_df_mortality_rate(df_confirmed, df_deaths)
        # st.write("DF Original")
        
        # st.write(f"[Data]({DATA_SOURCE_URL}) last updated on: {df_original.columns.tolist()[-1]}")
        show_data = st.checkbox("Show Data")
        if show_data:
            st.write(df_original.shape)
            st.write(df_original)

        # st.write(df_original.describe())
        # st.write(df_original.dtypes)

        

        df =  df_original.copy(deep=True)

        countries = get_countries(df_original)
        # st.write(countries)


        st.subheader("Evolution of the total number of cases")

        
        top_n = st.slider(
            "Select number of most-infected countries to view",
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

            fig = get_fig(dfs_plot, log_scale_choice)

            st.write(fig)




        st.subheader("Map of infections")


        log_max_scale = math.log(MAX_SCALE)
        log_scale = st.slider(
            "Bubble size",
            min_value=1,
            max_value=int(log_max_scale),
            value=5
        )
        scale = math.exp(log_scale)
        st.write(scale)
        st.write(int(log_max_scale))

        fig = get_map_plot(df, scale)

        st.write(fig)

    # st.write("DF")
    # df =  df_original.copy(deep=True)

    # st.write(df.shape)
    # st.write(df)

    if viz_choice == "Country view":
        country_choice = st.selectbox(
            "Country",
            get_top_countries(df_original, n=len(get_countries(df_original)))
        )
    
        mortality_rate, fig = get_fig_country(country_choice, df_confirmed, df_deaths)

        st.write(f"Mortality rate in {country_choice}: {100*mortality_rate:.2f} %")

        st.write(fig)



    st.info("""\
        Source code: [GitHub](https://github.com/Thomas2512/covid-visualizer) | [Thomas Wang](https://github.com/Thomas2512/)
    """)
    st.info("""\
        Data Source: [John Hopkins University](https://github.com/CSSEGISandData/COVID-19)
    """)
  
main()