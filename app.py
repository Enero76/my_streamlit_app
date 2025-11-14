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
csv_filename = "renewable_power_plants_CH.csv"

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

# Read the csv and geojson files
csv_path = os.path.join(BASE_DIR, "data", csv_filename)
df_plants_raw = load_data(csv_path)
df_plants = deepcopy(df_plants_raw)

swiss_areas = load_geojson(geojson_path)

df_plants.loc[df_plants['energy_source_level_3'].isnull(),'energy_source_level_3'] = str("Unknown")

total_prod_GW = df_plants['production'].sum()/1000
df_plants_prov = df_plants.copy()
df_plants_prov = df_plants_prov.rename(columns={"energy_source_level_2": "Source"})
df_plants_types = df_plants_prov.groupby('Source').sum()
df_plants_types = df_plants_types[["electrical_capacity","production"]]
#df_plants_types = df_plants_types.rename(columns={
#    "energy_source_level_2": "Energy Source",
#    "electrical_capacity": "Capacity (MW)",
#    "production": "Production (MWh)"})

df_plants_types.columns = ["Capacity (MW)","Production (MWh)"]



# Create the page title

st.set_page_config(layout="wide",page_icon="renewable-icon.png")
st.title("Renewable Energy in Switzerland")




###############################
# Energy Production per Canton
###############################

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

st.header("Renewable Energy Production and Cantons")
st.write(f"Total production in Switzerland is {round(total_prod_GW,3)} GWh")

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
                        'text': "Renewable Energy Production (MWh)",
                        'x': 0.5,
                        'xanchor': 'center'
                            }
                ,height=700
                ,width=1200
                )

st.plotly_chart(fig, width='content')

    #

##################################
# Renewable Plants in Switzerland
##################################

st.write("\n\n")
st.write("\n\n")
st.write("\n\n")
st.header("Renewable Power Plants in Switzerland")




mini_left, mini_middle, mini_right = st.columns([1,1,1])
mini_middle.dataframe(df_plants_types.style.format({"Production (MWh)": "{:,.0f}", "Capacity (MWh)": "{:,.f}"}))



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
    height=700,
    width=1200
)

fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, title={
        'text': "Renewable Power Plants Capacity (MW)",
        'x': 0.5,
        'xanchor': 'center'
    })

st.plotly_chart(fig, width='content')


#####################
# Both Maps Together
#####################

st.write("\n\n")
st.write("\n\n")
st.write("\n\n")
st.header("Renewable Power Plants and Cantons Production")
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
        'text': "Renewable Power Plants and Cantons",
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

st.plotly_chart(fig, width='content')