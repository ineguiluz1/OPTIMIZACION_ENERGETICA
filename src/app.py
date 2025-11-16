import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Inversor Dashboard", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_data(path: str = "../data/inversor_data_with_heating.csv"):
    df = pd.read_csv(path)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df

data = load_data()

st.title("Dashboard Energético — Sistema de Inversor")


# ============================================================================
# Función para crear diagrama Sankey
# ============================================================================
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


# ============================================================================
# Función para crear stack area chart 
# ============================================================================
def create_stacked_area_chart(df):
    """Crea un gráfico de área apilada para consumo energético a lo largo del tiempo"""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')
    
    x = df['Datetime']
    y1 = df['DirectConsumption(W)'] / 1000  # Convertir a kW
    y2 = df['BatteryDischarging(W)'] / 1000
    y3 = df['ExternalEnergySupply(W)'] / 1000
    
    ax.stackplot(x, y1, y2, y3, 
        labels=['Direct Consumption (PV)', 'Battery Discharging', 'External Energy Supply'],
        colors=['#FFD700', '#1E90FF', '#FF4500'],
        alpha=0.7
    )
    
    ax.set_title('Energy Sources Over Time (Stacked Area Chart)', fontsize=14, fontweight='bold', color='black', pad=15)
    ax.set_xlabel('Time', fontsize=11, color='black')
    ax.set_ylabel('Power (kW)', fontsize=11, color='black')
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.tick_params(colors='black', labelsize=9)
    
    # Rotary labels para mejor legibilidad
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    fig.tight_layout()
    
    return fig





# ============================================================================
# Mostrar Sankey Diagram
# ============================================================================
st.subheader("Energy Sources Flow")
sankey_fig = create_sankey_diagram(data)
st.plotly_chart(sankey_fig, use_container_width=True)


# ============================================================================
# Mostrar Stack Area Chart
# ============================================================================
st.subheader("Energy Consumption Over Time")
stacked_area_fig = create_stacked_area_chart(data)
st.pyplot(stacked_area_fig, use_container_width=False)