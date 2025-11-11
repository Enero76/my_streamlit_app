from matplotlib import markers
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df


st.write("Hello world!")

mpg_df_raw = load_data(path = "data/mpg.csv")

mpg_df = deepcopy(mpg_df_raw)

st.title("My Web Page!")
st.header("This is the header!")

#st.table(data=mpg_df)

value = st.checkbox("my checkbox")

if value == True:
    st.subheader("This is true")
    st.dataframe(data=mpg_df)

left_col, middle_col, right_col = st.columns([3,1,1])

#left_col.checkbox("This is the left column")

#with right_col:
#    st.checkbox("This is the right column")

years = ["All"] + sorted(pd.unique(mpg_df["year"]))
year = left_col.selectbox("Choose a Year",years)

show_means = middle_col.radio("Show Class Means", ["Yes","No"])

plot_types = ["Matplotlib", "Plotly"]

plot_type = right_col.radio("Show Class Means", plot_types)

if year == "All":
    reduced_df = mpg_df
else:
    reduced_df = mpg_df[mpg_df["year"] == year]

st.dataframe(reduced_df)

means = reduced_df.groupby("class").mean(numeric_only=True)



m_fig, ax = plt.subplots(figsize = (10,8))
ax.scatter(reduced_df["displ"],reduced_df["hwy"], alpha = 0.7)





#st.pyplot(m_fig)

p_fig = px.scatter(reduced_df, x = "displ", y="hwy",
                   opacity=0.5, range_x=[1,8], range_y=[1,20],
                   width=750,height=600,
                   labels={"displ" :  "Displacement (liters)",
                           "hwy" : "MPG"},
                    title = "Engine Size vs Highway")
p_fig.update_layout(title_font_size = 22)

#if show_means == True:
#    p_fig.add_trace(go.scatter(x=means["displ"],y=means["hwy"],marker = dict({})))
#    p_fig.update_layout()

st.plotly_chart(p_fig)

if plot_type == "Matplotlib":
    st.pyplot(m_fig)
else:
    st.plotly_chart(p_fig)

url = "https://www.jaimedata.org"
st.write("Source of data: ", url)

st.subheader("Streamlit Map")
ds_geo = px.data.carshare()

ds_geo["lat"] = ds_geo["centroid_lat"]
ds_geo["lon"] = ds_geo["centroid_lon"]

st.map(ds_geo)
st.dataframe(ds_geo.head())