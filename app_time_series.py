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


def main():

    st.header("Covid-19 visualizations")

    dates = get_dates()
    # st.write(dates)

    st.subheader("Input Dataframe")
    df_original = load_data(DATA_SOURCE)
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

  


main()