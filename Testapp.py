"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LOADING DATA
DATE_TIME = "date/time"
DATA_URL = (
    "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data

data = load_data(100000)

# CREATING FUNCTION FOR MAPS

def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2,3))

with row1_1:
    st.title("Merged Data")
    hour_selected = st.slider("Select hours", 0, 23)

with row1_2:
    st.write(
    """
    ##
    Examining how traffic varies over time in New York City.
    By sliding the slider on the left you can view different slices of time and explore different transportation trends.
    """)

# FILTERING DATA BY HOUR SELECTED
data = data[data[DATE_TIME].dt.hour == hour_selected]

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.columns((2,1,1,1))

# SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
Location_1= [40.7900, -73.8700]
Location_2= [40.6650, -73.7821]
Location_3= [40.7090, -74.1805]
zoom_level = 12
midpoint = (np.average(data["lat"]), np.average(data["lon"]))

with row2_1:
    st.write("**All New York City from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))
    map(data, midpoint[0], midpoint[1], 11)

with row2_2:
    st.write("**Location_1**")
    map(data,Location_1[0],Location_1[1], zoom_level)

with row2_3:
    st.write("**Location_2**")
    map(data, Location_2[0],Location_2[1], zoom_level)

with row2_4:
    st.write("**Location_3**")
    map(data, Location_3[0],Location_3[1], zoom_level)

# FILTERING DATA FOR THE HISTOGRAM
filtered = data[
    (data[DATE_TIME].dt.hour >= hour_selected) & (data[DATE_TIME].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Vehicles    per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ).configure_mark(
        opacity=0.2,
        color='red'
    ), use_container_width=True)
