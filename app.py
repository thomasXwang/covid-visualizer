import streamlit as st

from datetime import date, datetime

import os 
from PIL import Image

import pandas as pd
import numpy as np

image_file = "Champs fleurs printemps.jpg"
audio_file = "Crimson Fly.mp3" 

image = Image.open(image_file)
st.image(image, caption='I love flowers!!', use_column_width=True)

st.header("Wandi's Website")

name = st.text_input("Enter your name")

st.write(f"Hello {name}, and welcome to my humble website!")


number = st.number_input("Enter a number to get its square:")

st.write(f"Number² is equal to : {number*number}")

@st.cache
def load_music(file):
    audio_file = open(file, 'rb')
    audio_bytes = audio_file.read()
    return audio_bytes

audio_bytes = load_music(audio_file)

st.audio(audio_bytes, format="audio/mp3")


# Let's print out a great interactive graph !
st.subheader("Random graph")

n_graphs = st.slider("Number of graphs",
          min_value=1,
          max_value=10,
          format="%i"
)

n_max = st.slider("Max number",
          min_value=1,
          max_value=1000,
          format="%i"
)

chart_data = pd.DataFrame(
    np.random.randn(n_max, n_graphs),
    # columns=[f"x{i}" for i in range(n_max)]
)

st.area_chart(chart_data)