from matplotlib import markers
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
import os

geojson_path = 'data/georef-switzerland-kanton.geojson'

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_geojson(path):
    with open(path, 'r') as file:
        json_file = json.load(file)
    return json_file

# Ruta base = carpeta donde está este archivo .py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Read the csv file
csv_path = os.path.join(BASE_DIR, "data", "renewable_power_plants_CH.csv")
df_plants_raw = load_data(csv_path)
df_plants = deepcopy(df_plants_raw)

# Create the page title
left_col, middle_col, right_col = st.columns([1,10,1])
with middle_col:
    st.set_page_config(layout="wide")
    st.title("Renewable Energy in Switzerland")


###############################
# Energy Production per Canton
###############################
swiss_areas = load_geojson(geojson_path)

df_plants.loc[df_plants['energy_source_level_3'].isnull(),'energy_source_level_3'] = str("Unknown")
# Create a dictionary to map canton names in the dataset and the geojson:
cantons_dict ={
    "GE" : "Genève",
    "SH" : "Schaffhausen",
    "UR" : "Uri",
    "BE" : "Bern",
    "FR" : "Fribourg",
    "AR" : "Aargau",
    "GR" : "Graubünden",
    "LU" : "Luzern",
    "BS" : "Basel-Stadt",
    "TI" : "Ticino",
    "OB" : "Obwalden",
    "AR" : "Appenzell Ausserrhoden",
    "SO" : "Solothurn",
    "SZ" : "Schwyz",
    "JU" : "Jura",
    "SG" : "St. Gallen",
    "VS" : "Valais",
    "TG" : "Thurgau",
    "VA" : "Vaud",
    "BL" : "Basel-Landschaft",
    "ZH" : "Zürich",
    "NI" : "Nidwalden",
    "GL" : "Glarus",
    "NE" : "Neuchâtel",
    "ZG" : "Zug",
    "AI" : "Appenzell Innerrhoden"    
}
df_plants['canton_str'] = df_plants['canton'].map(cantons_dict)

df_sum = df_plants.groupby("canton_str", as_index=False)["production"].sum()

with middle_col:
    st.header("Energy Production per Canton")

    fig = go.Figure(go.Choroplethmap(geojson=swiss_areas, locations=df_sum.canton_str,
                                    featureidkey='properties.kan_name',
                                    z=df_sum["production"],
                                    colorscale="Viridis",
                                    zmin=0,
                                    zmax=df_sum["production"].max(),
                                    marker_opacity=0.5, marker_line_width=0,
                                    hovertext=df_sum.apply(
                                        lambda row: f"{row['canton_str']}<br>{row['production']:,.0f} MWh",
                                        axis=1),
                                    hoverinfo="text"
                                    ))

    fig.update_layout(map_style="carto-positron",
                    map_zoom=7, map_center = {"lat": 46.79911910358427, "lon": 8.116236707428286},
                    margin={"r":0,"t":40,"l":0,"b":0}, title={
                            'text': "Renewable Energy Production in Switzerland",
                            'x': 0.5,
                            'xanchor': 'center'
                                }
                    ,height=700
                    ,width=1200
                    )

    st.plotly_chart(fig, use_container_width=False)

##################################
# Renewable Plants in Switzerland
##################################

with middle_col:
    st.write("\n\n")
    st.write("\n\n")
    st.write("\n\n")
    st.header("Renewable Plants in Switzerland")

    fig = px.scatter_map(
        df_plants,
        lat="lat",
        lon="lon",
        size="electrical_capacity",                 # Tamaño del círculo
        color="energy_source_level_2",              # for the classification
        labels={
                "energy_source_level_2": "Energy Source",
                "electrical_capacity" : "Installed Capacity (MW)",
                "energy_source_level_3" : "Plant Type",
                "production" : "Production (MWh)",
                },
        hover_data = {
                        "energy_source_level_2" : True,
                        "electrical_capacity" : True,
                        "energy_source_level_3" : True,
                        "production" : True,
                        "lat" : False,
                        "lon" : False,
                    },
        hover_name="municipality",      # Texto al pasar el ratón
        size_max=30,                  # Tamaño máximo de los círculos
        zoom=7,
        map_style="carto-positron",
        center={"lat": 46.8, "lon": 8.2},
        title="Renewable Power plants in Switzerland",
        height=700,
        width=1200
    )

    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, title={
            'text': "Renewable Power Plants in Switzerland",
            'x': 0.5,
            'xanchor': 'center'
        })

    st.plotly_chart(fig, use_container_width=False)


#####################
# Both Maps Together
#####################
with middle_col:
    st.write("\n\n")
    st.write("\n\n")
    st.write("\n\n")
    st.header("Renewable Plants and Cantons Production")
    df_sum = df_plants.groupby("canton_str", as_index=False)["production"].sum()

    fig = go.Figure(go.Choroplethmap(
        geojson=swiss_areas,
        locations=df_sum.canton_str,
        featureidkey='properties.kan_name',
        z=df_sum["production"],
        colorscale="Viridis",
        zmin=0,
        zmax=df_sum["production"].max(),
        marker_opacity=0.5,
        marker_line_width=0,
        hovertext=df_sum.apply(
            lambda row: f"{row['canton_str']}<br>{row['production']:,.0f} MWh",
            axis=1),
        hoverinfo="text"
    ))

    fig.update_layout(
        map_style="carto-positron",
        map_zoom=7,
        map_center={"lat": 46.79911910358427, "lon": 8.116236707428286},
        margin={"r":0,"t":40,"l":0,"b":0},
        title={
            'text': "Renewable Energy Production in Switzerland",
            'x': 0.5,
            'xanchor': 'center'
        },
        height=700
    )

    # We add the scatter plot:
    scatter = px.scatter_map(
        df_plants,
        lat="lat",
        lon="lon",
        size="electrical_capacity",
        color="energy_source_level_2",
        labels={
            "energy_source_level_2": "Energy Source",
            "electrical_capacity": "Installed Capacity (MW)",
            "energy_source_level_3": "Plant Type",
            "production": "Production (MWh)",
        },
        hover_data={
            "energy_source_level_2": True,
            "electrical_capacity": True,
            "energy_source_level_3": True,
            "production": True,
            "lat": False,
            "lon": False,
        },
        hover_name="municipality",
        size_max=30,
        zoom=7,
        map_style="carto-positron",
        center={"lat": 46.8, "lon": 8.2},
        height=700,
        width=1200
    )

    # Añadimos las trazas de scatter al fig principal
    for trace in scatter.data:
        fig.add_trace(trace)

    fig.update_layout(
        legend=dict(
            title="Energy Source",   # título de la leyenda
            x=0.02,                  # posición horizontal (0 = izquierda, 1 = derecha)
            y=0.98,                  # posición vertical (0 = abajo, 1 = arriba)
            bgcolor="rgba(255,255,255,0.7)",  # fondo semitransparente para que no tape el mapa
            bordercolor="gray",
            borderwidth=1,
        ),
        coloraxis_colorbar=dict(
            title="Production (MWh)",
            x=1.02                    # mueve la barra de colores un poco a la derecha
        ),
        height=700,
        width=1200
    )

    st.plotly_chart(fig, use_container_width=False)