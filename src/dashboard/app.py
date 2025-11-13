import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Inversor Dashboard", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_data(path: str = "../data/inversor_data.csv"):
    df = pd.read_csv(path)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df

data = load_data()

st.title("Dashboard Energético — Sistema de Inversor")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Consumo Promedio (W)", f"{data['TotalConsumption(W)'].mean():.0f}")
col2.metric("PV Máximo (W)", f"{data['PV_PowerGeneration(W)'].max():.0f}")
col3.metric("Batería Descargada (Wh)", f"{(data['BatteryDischarging(W)'].sum() / 4):.0f}")
col4.metric("Energía Red (kWh)", f"{(data['ExternalEnergySupply(W)'].sum() / 4000):.2f}")

tab1, tab2, tab3, tab4 = st.tabs(["Series Temporales", "Análisis Diario", "Correlaciones", "Detalles"])

with tab1:
    st.subheader("Consumo Total vs Generación PV")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Datetime'], y=data['TotalConsumption(W)'], mode='lines', name='Consumo Total', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=data['Datetime'], y=data['PV_PowerGeneration(W)'], mode='lines', name='Generación PV', line=dict(color='orange', width=2)))
    fig.update_layout(height=400, hovermode='x unified', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Suministro Externo")
        fig = go.Figure(data=[go.Scatter(x=data['Datetime'], y=data['ExternalEnergySupply(W)'], fill='tozeroy', name='Red', line=dict(color='blue'))])
        fig.update_layout(height=350, template='plotly_dark', hovermode='x')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Carga y Descarga de Batería")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Datetime'], y=data['BatteryCharging(W)'], fill='tozeroy', name='Cargando', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=data['Datetime'], y=-data['BatteryDischarging(W)'], fill='tozeroy', name='Descargando', line=dict(color='purple')))
        fig.update_layout(height=350, template='plotly_dark', hovermode='x')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Análisis por Día")
    data['Date'] = data['Datetime'].dt.date
    daily = data.groupby('Date').agg({
        'TotalConsumption(W)': 'mean',
        'PV_PowerGeneration(W)': 'sum',
        'ExternalEnergySupply(W)': 'sum'
    }).reset_index()
    
    fig = px.bar(daily, x='Date', y=['PV_PowerGeneration(W)', 'ExternalEnergySupply(W)'], 
                 barmode='group', template='plotly_dark', height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Consumo Promedio Horario")
    data['Hour'] = data['Datetime'].dt.hour
    hourly = data.groupby('Hour')['TotalConsumption(W)'].mean()
    fig = go.Figure(data=[go.Bar(x=hourly.index, y=hourly.values, marker_color='indianred')])
    fig.update_layout(height=350, template='plotly_dark', xaxis_title='Hora', yaxis_title='Consumo (W)')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Matriz de Correlación")
    cols = ['TotalConsumption(W)', 'PV_PowerGeneration(W)', 'ExternalEnergySupply(W)', 'BatteryCharging(W)', 'BatteryDischarging(W)', 'temperature', 'radiation']
    corr = data[cols].corr()
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', template='plotly_dark', height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Consumo Directo vs Otros")
    fig = go.Figure(data=[
        go.Scatter(x=data['Datetime'], y=data['DirectConsumption(W)'], name='Consumo Directo', mode='lines'),
        go.Scatter(x=data['Datetime'], y=data['GridFeedIn(W)'], name='Inyección Red', mode='lines')
    ])
    fig.update_layout(height=400, template='plotly_dark', hovermode='x')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Datos en Tiempo Real")
    st.dataframe(data.tail(20).iloc[::-1], use_container_width=True)