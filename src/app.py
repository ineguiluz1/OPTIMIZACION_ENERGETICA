import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
import altair as alt

@st.cache_data
def load_data(path: str = "../data/inversor_data_with_heating.csv"):
    df = pd.read_csv(path)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df

def create_sankey_diagram(df):
    """Crea un diagrama Sankey mostrando las fuentes de consumo total"""
    
    # Calcular totales
    total_direct = df['DirectConsumption(W)'].sum() / 1000  # Convertir a kWh (usando suma de W como aproximación)
    total_battery = df['BatteryDischarging(W)'].sum() / 1000
    total_external = df['ExternalEnergySupply(W)'].sum() / 1000
    
    # Crear Sankey correctamente (3 nodos fuente + 1 consumo total)
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=[
                "Direct Consumption\n(PV)",
                "Battery Discharging",
                "External Energy\nSupply",
                "Total Consumption"
            ],
            color=["gold", "steelblue", "orangered", "purple"],
            x=[0.1, 0.1, 0.1, 0.9],
            y=[0.1, 0.5, 0.9, 0.5]
        ),
        link=dict(
            source=[0, 1, 2],
            target=[3, 3, 3],
            value=[total_direct, total_battery, total_external],
        )
    )])
    
    fig.update_layout(
        title={
            'text': "Energy Sources Flow to Total Consumption",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'black'}
        },
        font=dict(size=11, family="Arial"),
        height=500,
        paper_bgcolor='rgba(240, 240, 240, 1)',
        plot_bgcolor='rgba(240, 240, 240, 1)'
    )
    fig.update_traces(
        textfont=dict(
            color='black',
            size=20,
            family='Trebuchet MS'
        )
    )
    
    return fig

page = st.session_state.setdefault("page", "Inicio")

data = load_data()
data['Datetime'] = pd.to_datetime(data['Datetime'])

temp_min = data['temperature'].min()
temp_max = data['temperature'].max()

prec_min = data['precipitation'].loc[data['precipitation'] != 0].min()
prec_max = data['precipitation'].max()

wind_min = data['WindSpeed'].loc[data['WindSpeed'] != 0].min()
wind_max = data['WindSpeed'].max()

YEARS = data['Datetime'].dt.year.unique()


st.markdown("""
    <style>
    .stButton>button {
        font-size: 26px;             
        font-family: 'Poppins Semibold';  
        color: #00000;
        padding: 10px 24px;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# Datos históricos y en tiempo real
# ============================================================================
if page == "Inicio":
    st.title("Dashboard Energético — Sistema de Inversor")
    st.write("")

    st.session_state.setdefault("page", "Weather")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("METEOROLOGÍA"):
            st.session_state["page"] = "Weather"

    with col2:
        if st.button("DATOS HISTÓRICOS"):
            st.session_state["page"] = "Histórico"

    with col3:
        if st.button("EN TIEMPO REAL"):
            st.session_state["page"] = "En tiempo real"


if page == "Histórico":
    st.subheader("Energy Sources Flow")
    sankey_fig = create_sankey_diagram(data)
    st.plotly_chart(sankey_fig, use_container_width=True)

if page == "Weather":
    with st.container():
        cols = st.columns(2, gap='medium')

        with cols[0]:
            st.metric("Temperatura máxima:", f"{temp_max:.2f} °C")
        
        with cols[1]:
            st.metric("Temperatura mínima:", f"{temp_min:.2f} °C")

        cols = st.columns(2, gap='medium')

        with cols[0]:
            st.metric("Precipitación máxima:", f"{prec_max:.2f} mm/h")
        
        with cols[1]:
            st.metric("Precipitación mínima:", f"{prec_min:.2f} mm/h")

        cols = st.columns(2, gap='medium')

        with cols[0]:
            st.metric("Velocidad del viento máxima:", f"{wind_max:.2f} km/h")

        with cols[1]:
            st.metric("Velocidad del viento mínima:", f"{wind_min:.2f} km/h")

        selected_years = st.multiselect(
            "Selecciona los años para filtrar los datos:",
            options=YEARS
        )

        if not selected_years:
            st.warning("You must select at least 1 year.", icon="⚠️")
        
        data_year = data[data['Datetime'].dt.year.isin(selected_years)]

        cols = st.columns([3, 1])

        with cols[0].container(border=True, height=200):
            st.altair_chart(
                alt.Chart(data_year)
                .mark_bar(width=1)
                .encode(
                    alt.X("Datetime", timeUnit="monthdate").title("date"),
                    alt.Y("temperature").title("temperature range (C)"),
                    alt.Y2("temperature"),
                    alt.Color("Datetime:N", timeUnit="year").title("year"),
                    alt.XOffset("Datetime:N", timeUnit="year"),
                )
                .configure_legend(orient="bottom")
            )


