import streamlit as st

import datetime
# from datetime import date

import os 
from PIL import Image

import pandas as pd
import numpy as np

import plotly.graph_objects as go


DATA_SOURCE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
# date = "01-22-2020"
# data_url = DATA_SOURCE + date + ".csv"
# # st.write(data_url)
# test_df = pd.read_csv(data_url)

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)


@st.cache
def get_dates():

    START_DATE = datetime.date(2020, 1, 22)
    END_DATE = datetime.date(2020, 3, 22)
    # END_DATE = datetime.date.today() + datetime.timedelta(-1)

    # st.write(END_DATE)
    # st.write(START_DATE)

    dates = [dt.strftime("%m-%d-%Y") for dt in daterange(START_DATE, END_DATE)]
    # st.write(dates)

    return dates


@st.cache
def get_data(folder_url, dates):
    dfs = []
    columns = []
    for date in dates:
        # st.write(date)
        data_url = folder_url + date + ".csv"
        # st.write(data_url)
        df = pd.read_csv(data_url)
        # st.write(df)
        # st.write(len(df.columns.tolist()))
        dfs.append(df)
        for col in df.columns.tolist():
            if col not in columns:
                columns.append(col)

    # st.write(columns)


    concat_df = pd.concat(dfs)
    # st.write(concat_df.shape)

    # st.write(concat_df)

    concat_df = concat_df.drop_duplicates()

    return concat_df


def preprocess_countries(df2):
    df = df2.copy(deep=True)
    df = df.replace("Mainland China", "China")
    return df


@st.cache
def fill_nan_lat_long(df2):
    df = df2.copy(deep=True)
    df['Latitude'] = df.groupby(["Province/State", "Country/Region"])["Latitude"].bfill()
    df['Longitude'] = df.groupby(["Province/State", "Country/Region"])["Longitude"].bfill()
    return df


# To complete after features have been developed
def merge_new_format(df2):

    df = df2.copy(deep=True)
    old_columns = [
        "Province/State",
        "Country/Region",
        "Last Update",
        "Confirmed",
        "Deaths",
        "Recovered",
        "Latitude",
        "Longitude"
    ]
    new_columns = [
        "Province_State",
        "Country_Region",
        "Last_Update",
        "Confirmed",
        "Deaths",
        "Recovered",
        "Lat",
        "Long_"
    ]

    # st.write("rows with nan")
    # st.write(df.loc[df[old_columns[i]].isnull(), :].shape)
    # st.write(df.loc[df[old_columns[i]].isnull(), :])


    for i in range(len(old_columns)):
        st.write(f"rows with nan for {old_columns[i]}")
        st.write(df.loc[df[old_columns[i]].isnull(), :].shape)
        st.write(df.loc[df[old_columns[i]].isnull(), :])

        df.loc[df[old_columns[i]].isnull(), old_columns[i]] = df.loc[df[old_columns[i]].isnull(), new_columns[i]]

        st.write("After")
        st.write(df.loc[df[old_columns[i]].isnull(), :].shape)
    
    return df


def main():

    st.header("Covid-19 visualizations")

    dates = get_dates()
    # st.write(dates)

    st.subheader("Input Dataframe")
    df_original = get_data(DATA_SOURCE, dates)
    st.write("DF Original")
    st.write(df_original.shape)
    st.write(df_original)

    df_original.describe()
    st.write(df_original.dtypes)

    st.info("Data Loaded")

    st.write("DF")
    df =  df_original.copy(deep=True)

    st.write(df.shape)
    st.write(df)

    # df2 = merge_new_format(df)

    # st.write("after modif")
    # st.write(df2)

    df2 = preprocess_countries(df)

    df2 = fill_nan_lat_long(df2)
    st.write(df2.shape)
    st.write(df2)

    countries = sorted(df2["Country/Region"].unique().tolist())
    st.write(countries)
    

    selected_country = st.selectbox(
        "Select the countries you want to visualize",
        countries,
        index=4
    )

    # selected_countries = st.multiselect(
    #     "Select the countries you want to visualize",
    #     countries,
    #     default=["France", "China"]
    # )

    df_restricted = df2[df2["Country/Region"] == selected_country]

    # df_restricted = df2[df2["Country/Region"].isin(selected_countries)]
    st.write(df_restricted)

    df_plot = df_restricted.groupby(["Country/Region", "Last Update"])[["Confirmed", "Deaths", "Recovered"]].agg("sum")
    df_plot = df_plot.unstack(level=0)
    st.write("df_plot")
    st.write(df_plot.index)
    st.write(df_plot["Confirmed"])

    # https://plotly.com/python/time-series/#time-series-plot-with-custom-date-range
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["Confirmed"][selected_country], name="Confirmed", line_color="red"))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["Deaths"][selected_country], name="Deaths", line_color="black"))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["Recovered"][selected_country], name="Recovered", line_color="green"))

    fig.update_layout(title_text='Time Series with Rangeslider',
                  xaxis_rangeslider_visible=True)
    # fig.update_layout(xaxis_range=['2020-01-01','2020-03-20'],
    #               title_text="Manually Set Date Range")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Infected count",
        title_text=f"Covid infected count in {selected_country}",
        
        width=1000,
        height=800  )

    st.write(fig)
main()