import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
import altair as alt

# Configuración de página
st.set_page_config(
    page_title="Dashboard Energético",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_data(path: str = "../data/inversor_data_with_heating.csv"):
    df = pd.read_csv(path)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df

def create_sankey_diagram(df):
    """Crea un diagrama Sankey mostrando las fuentes de consumo total"""
    
    # Calcular totales
    total_direct = df['DirectConsumption(W)'].sum() / 1000
    total_battery = df['BatteryDischarging(W)'].sum() / 1000
    total_external = df['ExternalEnergySupply(W)'].sum() / 1000
    
    # Crear Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='#cbd5e0', width=2),
            label=[
                "Direct Consumption\n(PV)",
                "Battery Discharging",
                "External Energy\nSupply",
                "Total Consumption"
            ],
            color=["#A0AEC0", "#718096", "#4A5568", "#2D3748"],
            x=[0.1, 0.1, 0.1, 0.9],
            y=[0.1, 0.5, 0.9, 0.5]
        ),
        link=dict(
            source=[0, 1, 2],
            target=[3, 3, 3],
            value=[total_direct, total_battery, total_external],
            color=[
                "rgba(255,99,71,0.4)",    # rojo intenso (tomato)
                "rgba(30,144,255,0.4)",   # azul vivo (dodgerblue)
                "rgba(60,179,113,0.4)"    # verde visible (mediumseagreen)
            ]
        )
    )])
    
    fig.update_layout(
        title={
            'text': "Energy Sources Flow to Total Consumption",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#000000', 'family': 'Poppins'}
        },
        font=dict(size=14, family="Inter", color='#000000'),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    fig.update_traces(textfont=dict(color='black', size=14, family='Inter'))
    
    return fig

def create_sankey_diagram_heating_system(df):
    """Crea un diagrama Sankey mostrando las fuentes del sistema de calefacción"""
    
    # Calcular el consumo total de calefacción
    total_heating = df['HeatingSystem(W)'].sum() / 1000
    
    # Calcular totales de cada fuente
    total_direct = df['DirectConsumption(W)'].sum() / 1000
    total_battery = df['BatteryDischarging(W)'].sum() / 1000
    total_external = df['ExternalEnergySupply(W)'].sum() / 1000
    total_consumption = df['TotalConsumption(W)'].sum() / 1000
    
    # Calcular proporción de cada fuente destinada a calefacción
    heating_ratio = total_heating / total_consumption if total_consumption > 0 else 0
    
    heating_direct = total_direct * heating_ratio
    heating_battery = total_battery * heating_ratio
    heating_external = total_external * heating_ratio
    
    # Crear Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='#cbd5e0', width=2),
            label=[
                "Direct Consumption\n(PV)",
                "Battery Discharging",
                "External Energy\nSupply",
                "Heating System\nTotal"
            ],
            color=["#FFA07A", "#87CEEB", "#98FB98", "#FF6347"],
            x=[0.1, 0.1, 0.1, 0.9],
            y=[0.1, 0.5, 0.9, 0.5]
        ),
        link=dict(
            source=[0, 1, 2],
            target=[3, 3, 3],
            value=[heating_direct, heating_battery, heating_external],
            color=[
                "rgba(255,140,0,0.4)",    # naranja oscuro
                "rgba(70,130,180,0.4)",   # azul acero
                "rgba(34,139,34,0.4)"     # verde bosque
            ]
        )
    )])
    
    fig.update_layout(
        title={
            'text': "Heating System Energy Sources Flow",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#000000', 'family': 'Poppins'}
        },
        font=dict(size=14, family="Inter", color='#000000'),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    fig.update_traces(textfont=dict(color='black', size=14, family='Inter'))
    
    return fig

def show_navigation_menu():
    """Muestra el menú de navegación entre páginas"""
    st.markdown("---")
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        if st.button("🌤️ METEOROLOGÍA", key="nav_weather", use_container_width=True):
            st.session_state["page"] = "Weather"
            st.rerun()
    
    with col2:
        if st.button("📊 DATOS HISTÓRICOS", key="nav_historico", use_container_width=True):
            st.session_state["page"] = "Histórico"
            st.rerun()
    
    with col3:
        if st.button("⚡ EN TIEMPO REAL", key="nav_realtime", use_container_width=True):
            st.session_state["page"] = "En tiempo real"
            st.rerun()
    
    st.markdown("---")

page = st.session_state.setdefault("page", "Inicio")

data = load_data()
data['Datetime'] = pd.to_datetime(data['Datetime'])

temp_min = data['temperature'].min()
temp_max = data['temperature'].max()

prec_min = data['precipitation'].loc[data['precipitation'] != 0].min()
prec_max = data['precipitation'].max()

wind_min = data['WindSpeed'].loc[data['WindSpeed'] != 0].min()
wind_max = data['WindSpeed'].max()

radiation_min = data['radiation'].loc[data['radiation'] != 0].min()
radiation_max = data['radiation'].max()

YEARS = data['Datetime'].dt.year.unique()


# CSS personalizado minimalista
st.markdown("""
    <style>
    /* Importar fuentes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@400;600;700&display=swap');
    
    /* Fondo general minimalista */
    .stApp {
        background: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Contenedor principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Títulos */
    h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: #2d3748;
        text-align: center;
        font-size: 3rem !important;
        margin-bottom: 2rem;
    }
    
    h2, h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: #2d3748;
    }
    
    /* Botones de navegación minimalistas */
    .stButton>button {
        font-size: 15px;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: #2d3748;
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.25s ease;
        width: 100%;
        position: relative;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #cbd5e0;
        background: #f7fafc;
        color: #1a202c;
    }
    
    .stButton>button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    
    /* Métricas mejoradas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #718096;
    }
    
    div[data-testid="metric-container"] {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        border-color: #cbd5e0;
    }
    
    /* Contenedores con borde */
    [data-testid="stVerticalBlock"] > div:has(> div.element-container) {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #cbd5e0, transparent);
    }
    
    /* Checkbox */
    .stCheckbox {
        color: #2d3748;
        font-weight: 500;
    }

    /* Estilos para widgets (Radio, DateInput) */
    .stRadio > label, .stDateInput > label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 0.3rem !important;
    }
    
    div[data-baseweb="radio"] label {
        color: #000000 !important;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        color: #000000;
    }
    
    /* Selector de fecha más compacto y estético */
    div[data-baseweb="input"] {
        border-radius: 8px !important;
        border: 1.5px solid #cbd5e0 !important;
        transition: all 0.2s ease !important;
        font-size: 14px !important;
        padding: 2px 8px !important;
    }
    
    div[data-baseweb="input"]:hover {
        border-color: #805AD5 !important;
        box-shadow: 0 2px 8px rgba(128, 90, 213, 0.15) !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #805AD5 !important;
        box-shadow: 0 0 0 3px rgba(128, 90, 213, 0.1) !important;
    }
    
    input[type="date"], input[type="text"] {
        font-size: 14px !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Contenedores de gráficos con fondo blanco */
    div[data-testid="stPlotlyChart"] {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }
    
    div.stAltairChart {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        overflow: hidden;
    }
    
    /* Asegurar bordes redondeados en los canvas de Altair */
    div.stAltairChart > div {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* DataFrames */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# Página de Inicio
# ============================================================================
if page == "Inicio":

    
    st.write("")
    st.title("⚡ Dashboard Energético — Sistema de Inversor")
    st.write("")

    # Logo centrado
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        st.image("../media/dashboard_logo.png")

    st.session_state.setdefault("page", "Weather")

    st.divider()

    col1, col2, col3 = st.columns(3, gap="large")


    with col1:
        if st.button("🌤️ METEOROLOGÍA"):
            st.session_state["page"] = "Weather"
            st.rerun()

    with col2:
        if st.button("📊 DATOS HISTÓRICOS"):
            st.session_state["page"] = "Histórico"
            st.rerun()

    with col3:
        if st.button("⚡ EN TIEMPO REAL"):
            st.session_state["page"] = "En tiempo real"
            st.rerun()


# ============================================================================
# Página de Datos Históricos
# ============================================================================
if page == "Histórico":
    st.title("📊 Datos Históricos")
    
    # Menú de navegación
    show_navigation_menu()
    
    # Controles de filtrado
    col_filter1, col_filter2 = st.columns([1, 1])
    
    with col_filter1:
        view_mode = st.radio(
            "Modo de visualización:",
            ["Total Histórico", "Por Día"],
            horizontal=True
        )
    
    filtered_data = data.copy()
    chart_title = "Flujo de Energía - Total Histórico"
    
    if view_mode == "Por Día":
        with col_filter2:
            # Obtener límites de fechas
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )
            
            # Filtrar datos
            filtered_data = data[data['Datetime'].dt.date == selected_date]
            chart_title = f"Flujo de Energía - {selected_date.strftime('%d/%m/%Y')}"
    
    if filtered_data.empty:
        st.warning(f"No hay datos disponibles para la fecha seleccionada.")
    else:
        sankey_fig = create_sankey_diagram(filtered_data)
        # Actualizar título del gráfico
        sankey_fig.update_layout(title_text=chart_title)
        st.plotly_chart(sankey_fig, use_container_width=True)

    sankey_fig = create_sankey_diagram_heating_system(filtered_data)
    # Actualizar título del gráfico
    sankey_fig.update_layout(title_text="Flujo de Energía - Sistema de Calefacción")
    st.plotly_chart(sankey_fig, use_container_width=True)

    st.divider()

    # Nueva sección: Stacked Area Chart de Fuentes de Energía
    st.subheader("📊 Desglose de Fuentes de Energía")
    st.write("")

    # Controles de visualización para stacked area chart
    col_stack1, col_stack2 = st.columns([1, 1])
    
    with col_stack1:
        stack_view_mode = st.radio(
            "Modo de visualización de fuentes:",
            ["Semanal", "Diario", "Periodo Específico"],
            horizontal=True,
            key="stack_view_mode"
        )
    
    # Preparar datos para stacked area chart
    data_stack = data.copy()
    
    if stack_view_mode == "Semanal":
        # Vista semanal - medias
        data_stack['YearWeek'] = data_stack['Datetime'].dt.to_period('W').apply(lambda r: r.start_time)
        weekly_sources = data_stack.groupby('YearWeek')[['DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].mean().reset_index()
        weekly_sources.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
        
        # Transformar a formato largo para stacked area
        stack_data = pd.melt(
            weekly_sources,
            id_vars=['Fecha'],
            value_vars=['Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)'],
            var_name='Fuente',
            value_name='Potencia (W)'
        )
        date_format_stack = '%b %Y'
        tooltip_date_format_stack = '%d %b %Y'
        stack_title_suffix = " - Media Semanal"
    elif stack_view_mode == "Diario":
        # Vista diaria con granularidad de 15 minutos
        with col_stack2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_stack_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="stack_date_selector"
            )
        
        # Filtrar datos para el día seleccionado
        daily_stack_data = data_stack[data_stack['Datetime'].dt.date == selected_stack_date].copy()
        daily_stack_data = daily_stack_data[['Datetime', 'DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].copy()
        daily_stack_data.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
        
        # Transformar a formato largo para stacked area
        stack_data = pd.melt(
            daily_stack_data,
            id_vars=['Fecha'],
            value_vars=['Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)'],
            var_name='Fuente',
            value_name='Potencia (W)'
        )
        date_format_stack = '%H:%M'
        tooltip_date_format_stack = '%H:%M'
        stack_title_suffix = f" - {selected_stack_date.strftime('%d/%m/%Y')}"
    else:  # Periodo Específico
        with col_stack2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            date_range_stack = st.date_input(
                "Seleccionar rango de fechas:",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="stack_range_selector"
            )
        
        # Manejar selección de rango
        if isinstance(date_range_stack, tuple) and len(date_range_stack) == 2:
            start_date, end_date = date_range_stack
            period_stack_data = data_stack[(data_stack['Datetime'].dt.date >= start_date) & 
                                          (data_stack['Datetime'].dt.date <= end_date)].copy()
            
            # Usar datos con granularidad de 15 minutos
            period_stack_data = period_stack_data[['Datetime', 'DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].copy()
            period_stack_data.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
            
            stack_data = pd.melt(
                period_stack_data,
                id_vars=['Fecha'],
                value_vars=['Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)'],
                var_name='Fuente',
                value_name='Potencia (W)'
            )
            date_format_stack = '%d %b %H:%M'
            tooltip_date_format_stack = '%d %b %Y %H:%M'
            stack_title_suffix = f" - {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
        else:
            selected_date = date_range_stack if not isinstance(date_range_stack, tuple) else date_range_stack[0]
            daily_stack_data = data_stack[data_stack['Datetime'].dt.date == selected_date].copy()
            daily_stack_data = daily_stack_data[['Datetime', 'DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].copy()
            daily_stack_data.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
            
            stack_data = pd.melt(
                daily_stack_data,
                id_vars=['Fecha'],
                value_vars=['Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)'],
                var_name='Fuente',
                value_name='Potencia (W)'
            )
            date_format_stack = '%H:%M'
            tooltip_date_format_stack = '%H:%M'
            stack_title_suffix = f" - {selected_date.strftime('%d/%m/%Y')}"
    
    # Crear stacked area chart
    stacked_chart = alt.Chart(stack_data).mark_area(
        opacity=0.8
    ).encode(
        x=alt.X('Fecha:T', 
                title='Fecha' if stack_view_mode == 'Semanal' else 'Hora',
                axis=alt.Axis(format=date_format_stack, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
        y=alt.Y('Potencia (W):Q', 
                title='Potencia (W)',
                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
        color=alt.Color('Fuente:N',
                       scale=alt.Scale(
                           domain=['Consumo Directo (W)', 'Descarga Batería (W)', 'Suministro Externo (W)'],
                           range=['#FF6347', '#1E90FF', '#3CB371']  # Tomato, DodgerBlue, MediumSeaGreen
                       ),
                       legend=alt.Legend(title='Fuente de Energía', orient='top')),
        tooltip=[
            alt.Tooltip('Fecha:T', 
                       title='Semana' if stack_view_mode == 'Semanal' else 'Hora',
                       format=tooltip_date_format_stack),
            alt.Tooltip('Fuente:N', title='Fuente'),
            alt.Tooltip('Potencia (W):Q', format='.2f', title='Potencia (W)')
        ]
    ).properties(
        height=400,
        title=alt.TitleParams(text=f'Fuentes de Energía{stack_title_suffix}', fontSize=18, color='#2d3748', anchor='middle')
    ).configure(
        background='white'
    ).configure_view(
        strokeWidth=0,
        fill='white'
    ).configure_axis(
        gridColor='#f7fafc',
        domainColor='#e2e8f0'
    ).configure_legend(
        labelColor='#2d3748',
        titleColor='#2d3748'
    ).interactive()
    
    st.altair_chart(stacked_chart, use_container_width=True)

    st.divider()

    st.subheader("📈 Evolución del Consumo (2024 - 2025)")
    st.write("")

    # Controles de visualización para gráficos de consumo
    col_view1, col_view2 = st.columns([1, 1])
    
    with col_view1:
        consumption_view_mode = st.radio(
            "Modo de visualización de consumo:",
            ["Semanal", "Diario", "Periodo Específico"],
            horizontal=True,
            key="consumption_view_mode"
        )
    
    # Preparar datos para gráficos de consumo
    data_hist = data.copy()
    
    if consumption_view_mode == "Semanal":
        # Vista semanal (comportamiento actual)
        data_hist['YearWeek'] = data_hist['Datetime'].dt.to_period('W').apply(lambda r: r.start_time)
        weekly_consumption = data_hist.groupby('YearWeek')[['TotalConsumption(W)', 'HeatingSystem(W)']].mean().reset_index()
        weekly_consumption.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
        consumption_data = weekly_consumption
        date_format = '%b %Y'
        tooltip_date_format = '%d %b %Y'
        chart_title_suffix = " - Media Semanal"
    elif consumption_view_mode == "Diario":
        # Vista diaria con granularidad de 15 minutos
        with col_view2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_consumption_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="consumption_date_selector"
            )
        
        # Filtrar datos para el día seleccionado
        daily_data = data_hist[data_hist['Datetime'].dt.date == selected_consumption_date].copy()
        daily_data = daily_data[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
        daily_data.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
        consumption_data = daily_data
        date_format = '%H:%M'
        tooltip_date_format = '%H:%M'
        chart_title_suffix = f" - {selected_consumption_date.strftime('%d/%m/%Y')}"
    else:  # Periodo Específico
        with col_view2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            date_range = st.date_input(
                "Seleccionar rango de fechas:",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="consumption_range_selector"
            )
        
        # Manejar selección de rango
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            # Filtrar datos para el rango seleccionado
            period_data = data_hist[(data_hist['Datetime'].dt.date >= start_date) & 
                                   (data_hist['Datetime'].dt.date <= end_date)].copy()
            
            # Usar datos con granularidad de 15 minutos
            period_data = period_data[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
            period_data.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
            consumption_data = period_data
            date_format = '%d %b %H:%M'
            tooltip_date_format = '%d %b %Y %H:%M'
            chart_title_suffix = f" - {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
        else:
            # Si solo se seleccionó una fecha, usar vista diaria
            selected_date = date_range if not isinstance(date_range, tuple) else date_range[0]
            daily_data = data_hist[data_hist['Datetime'].dt.date == selected_date].copy()
            daily_data = daily_data[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
            daily_data.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
            consumption_data = daily_data
            date_format = '%H:%M'
            tooltip_date_format = '%H:%M'
            chart_title_suffix = f" - {selected_date.strftime('%d/%m/%Y')}"

    cols = st.columns(2, gap='large')

    with cols[0]:
        chart_total = alt.Chart(consumption_data).mark_area(
            line={'color': '#805AD5'},  # Púrpura
            color=alt.Gradient(
                gradient='linear',
                stops=[
                    alt.GradientStop(color='#805AD5', offset=0),
                    alt.GradientStop(color='rgba(128,90,213,0.1)', offset=1)
                ],
                x1=0, x2=0, y1=0, y2=1
            )
        ).encode(
            x=alt.X('Fecha:T', title='Fecha' if consumption_view_mode == 'Semanal' else 'Hora', 
                    axis=alt.Axis(format=date_format, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Consumo Total (W):Q', title='Consumo Total (W)', 
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana' if consumption_view_mode == 'Semanal' else 'Hora', 
                           format=tooltip_date_format),
                alt.Tooltip('Consumo Total (W):Q', format='.2f', title='Consumo (W)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text=f'Consumo Total{chart_title_suffix}', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).interactive()
    
        st.altair_chart(chart_total, use_container_width=True)

    with cols[1]:
        chart_heating = alt.Chart(consumption_data).mark_area(
            line={'color': '#E53E3E'},  # Rojo para calefacción
            color=alt.Gradient(
                gradient='linear',
                stops=[
                    alt.GradientStop(color='#E53E3E', offset=0),
                    alt.GradientStop(color='rgba(229,62,62,0.1)', offset=1)
                ],
                x1=0, x2=0, y1=0, y2=1
            )
        ).encode(
            x=alt.X('Fecha:T', title='Fecha' if consumption_view_mode == 'Semanal' else 'Hora', 
                    axis=alt.Axis(format=date_format, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Calefacción (W):Q', title='Consumo Calefacción (W)', 
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana' if consumption_view_mode == 'Semanal' else 'Hora', 
                           format=tooltip_date_format),
                alt.Tooltip('Calefacción (W):Q', format='.2f', title='Calefacción (W)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text=f'Sistema de Calefacción{chart_title_suffix}', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).interactive()
    
        st.altair_chart(chart_heating, use_container_width=True)


# ============================================================================
# Página de En Tiempo Real
# ============================================================================
if page == "En tiempo real":
    st.title("⚡ En Tiempo Real")
    
    # Menú de navegación
    show_navigation_menu()
    
    st.info("Esta sección está en desarrollo...")


# ============================================================================
# Página de Meteorología
# ============================================================================
if page == "Weather":
    st.title("🌤️ Datos Meteorológicos")
    
    # Menú de navegación
    show_navigation_menu()
    
    # Sección de métricas
    st.markdown("### 📊 Resumen de Datos")
    
    # Temperatura
    with st.container():
        cols = st.columns(4, gap='medium')
        
        with cols[0]:
            st.metric("🌡️ Temp. Máxima", f"{temp_max:.2f} °C")
        
        with cols[1]:
            st.metric("❄️ Temp. Mínima", f"{temp_min:.2f} °C")
        
        with cols[2]:
            st.metric("💧 Precip. Máxima", f"{prec_max:.2f} mm/h")
        
        with cols[3]:
            st.metric("💧 Precip. Mínima", f"{prec_min:.2f} mm/h")

    # Viento y Radiación
    with st.container():
        cols = st.columns(4, gap='medium')
        
        with cols[0]:
            st.metric("💨 Viento Máx.", f"{wind_max:.2f} km/h")
        
        with cols[1]:
            st.metric("🍃 Viento Mín.", f"{wind_min:.2f} km/h")
        
        with cols[2]:
            st.metric("☀️ Radiación Máx.", f"{radiation_max:.2f} W/m²")
        
        with cols[3]:
            st.metric("🌤️ Radiación Mín.", f"{radiation_min:.2f} W/m²")

    st.divider()

    # Checkbox para datos raw
    raw_data = st.checkbox("📋 Mostrar Datos Crudos")

    if raw_data:
        st.dataframe(
            data[['Datetime', 'temperature', 'precipitation', 'WindSpeed', 'radiation']],
            use_container_width=True
        )

    st.divider()

    # Preparar datos para gráficos
    data_copy = data.copy()
    data_copy['Year'] = data_copy['Datetime'].dt.year
    data_copy['Week'] = data_copy['Datetime'].dt.isocalendar().week
    data_copy['YearWeek'] = data_copy['Datetime'].dt.to_period('W').apply(lambda r: r.start_time)

    # Gráficos de Temperatura y Precipitación
    st.markdown("### 📈 Temperatura y Precipitación (2024 - 2025)")
    st.write("")
    
    # Controles de visualización para gráficos de meteorología
    col_weather1, col_weather2 = st.columns([1, 1])
    
    with col_weather1:
        weather_view_mode = st.radio(
            "Modo de visualización de meteorología:",
            ["Semanal", "Diario", "Periodo Específico"],
            horizontal=True,
            key="weather_view_mode"
        )
    
    if weather_view_mode == "Semanal":
        # Calcular datos semanales
        weekly_temp = data_copy.groupby('YearWeek')['temperature'].mean().reset_index()
        weekly_temp.columns = ['Fecha', 'Temperatura Media (°C)']
        
        weekly_prec = data_copy.groupby('YearWeek')['precipitation'].mean().reset_index()
        weekly_prec.columns = ['Fecha', 'Precipitación Media (mm/h)']
        
        temp_data = weekly_temp
        prec_data = weekly_prec
        date_format_weather = '%b %Y'
        tooltip_date_format_weather = '%d %b %Y'
    elif weather_view_mode == "Diario":
        with col_weather2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_weather_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="weather_date_selector"
            )
            
        daily_weather = data_copy[data_copy['Datetime'].dt.date == selected_weather_date].copy()
        
        temp_data = daily_weather[['Datetime', 'temperature']].copy()
        temp_data.columns = ['Fecha', 'Temperatura Media (°C)']
        
        prec_data = daily_weather[['Datetime', 'precipitation']].copy()
        prec_data.columns = ['Fecha', 'Precipitación Media (mm/h)']
        
        date_format_weather = '%H:%M'
        tooltip_date_format_weather = '%H:%M'
    else:  # Periodo Específico
        with col_weather2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            date_range_weather = st.date_input(
                "Seleccionar rango de fechas:",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="weather_range_selector"
            )
            
        if isinstance(date_range_weather, tuple) and len(date_range_weather) == 2:
            start_date, end_date = date_range_weather
            period_weather = data_copy[(data_copy['Datetime'].dt.date >= start_date) & 
                                      (data_copy['Datetime'].dt.date <= end_date)].copy()
            
            temp_data = period_weather[['Datetime', 'temperature']].copy()
            temp_data.columns = ['Fecha', 'Temperatura Media (°C)']
            
            prec_data = period_weather[['Datetime', 'precipitation']].copy()
            prec_data.columns = ['Fecha', 'Precipitación Media (mm/h)']
            
            date_format_weather = '%d %b %H:%M'
            tooltip_date_format_weather = '%d %b %Y %H:%M'
        else:
            selected_date = date_range_weather if not isinstance(date_range_weather, tuple) else date_range_weather[0]
            daily_weather = data_copy[data_copy['Datetime'].dt.date == selected_date].copy()
            
            temp_data = daily_weather[['Datetime', 'temperature']].copy()
            temp_data.columns = ['Fecha', 'Temperatura Media (°C)']
            
            prec_data = daily_weather[['Datetime', 'precipitation']].copy()
            prec_data.columns = ['Fecha', 'Precipitación Media (mm/h)']
            
            date_format_weather = '%H:%M'
            tooltip_date_format_weather = '%H:%M'
    
    cols = st.columns([1, 1], gap='large')

    with cols[0]:
        chart = alt.Chart(temp_data).mark_area(
            line={'color': '#EF4444'},
            color=alt.Gradient(
                gradient='linear',
                stops=[
                    alt.GradientStop(color='#EF4444', offset=0),
                    alt.GradientStop(color='rgba(239,68,68,0.1)', offset=1)
                ],
                x1=0, x2=0, y1=0, y2=1
            )
        ).encode(
            x=alt.X('Fecha:T', title='Fecha' if weather_view_mode == 'Semanal' else 'Hora', 
                    axis=alt.Axis(format=date_format_weather, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Temperatura Media (°C):Q', title='Temperatura Media (°C)', 
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana' if weather_view_mode == 'Semanal' else 'Hora', 
                           format=tooltip_date_format_weather),
                alt.Tooltip('Temperatura Media (°C):Q', format='.2f', title='Temperatura (°C)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text='🌡️ Temperatura', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).interactive()
    
        st.altair_chart(chart, use_container_width=True)

    with cols[1]:
        chart_prec = alt.Chart(prec_data).mark_area(
            line={'color': '#3B82F6'},
            color=alt.Gradient(
                gradient='linear',
                stops=[
                    alt.GradientStop(color='#3B82F6', offset=0),
                    alt.GradientStop(color='rgba(59,130,246,0.1)', offset=1)
                ],
                x1=0, x2=0, y1=0, y2=1
            )
        ).encode(
            x=alt.X('Fecha:T', title='Fecha' if weather_view_mode == 'Semanal' else 'Hora', 
                    axis=alt.Axis(format=date_format_weather, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Precipitación Media (mm/h):Q', title='Precipitación Media (mm/h)', 
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana' if weather_view_mode == 'Semanal' else 'Hora', 
                           format=tooltip_date_format_weather),
                alt.Tooltip('Precipitación Media (mm/h):Q', format='.2f', title='Precipitación (mm/h)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text='💧 Precipitación', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).interactive()
        
        st.altair_chart(chart_prec, use_container_width=True)

    st.divider()

    # Gráfico de Radiación
    st.markdown("### ☀️ Radiación (2024 - 2025)")
    st.write("")
    
    if weather_view_mode == "Semanal":
        weekly_rad = data_copy.groupby('YearWeek')['radiation'].mean().reset_index()
        weekly_rad.columns = ['Fecha', 'Radiación Media (W/m²)']
        rad_data = weekly_rad
    elif weather_view_mode == "Diario":
        daily_rad = data_copy[data_copy['Datetime'].dt.date == selected_weather_date].copy()
        rad_data = daily_rad[['Datetime', 'radiation']].copy()
        rad_data.columns = ['Fecha', 'Radiación Media (W/m²)']
    else:  # Periodo Específico
        if isinstance(date_range_weather, tuple) and len(date_range_weather) == 2:
            start_date, end_date = date_range_weather
            period_rad = data_copy[(data_copy['Datetime'].dt.date >= start_date) & 
                                  (data_copy['Datetime'].dt.date <= end_date)].copy()
            rad_data = period_rad[['Datetime', 'radiation']].copy()
            rad_data.columns = ['Fecha', 'Radiación Media (W/m²)']
        else:
            selected_date = date_range_weather if not isinstance(date_range_weather, tuple) else date_range_weather[0]
            daily_rad = data_copy[data_copy['Datetime'].dt.date == selected_date].copy()
            rad_data = daily_rad[['Datetime', 'radiation']].copy()
            rad_data.columns = ['Fecha', 'Radiación Media (W/m²)']
    
    chart_rad = alt.Chart(rad_data).mark_area(
        line={'color': '#F97316'},
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color='#F97316', offset=0),
                alt.GradientStop(color='rgba(249,115,22,0.1)', offset=1)
            ],
            x1=0, x2=0, y1=0, y2=1
        )
    ).encode(
        x=alt.X('Fecha:T', title='Fecha' if weather_view_mode == 'Semanal' else 'Hora', 
                axis=alt.Axis(format=date_format_weather, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
        y=alt.Y('Radiación Media (W/m²):Q', title='Radiación Media (W/m²)', 
                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
        tooltip=[
            alt.Tooltip('Fecha:T', title='Semana' if weather_view_mode == 'Semanal' else 'Hora', 
                       format=tooltip_date_format_weather),
            alt.Tooltip('Radiación Media (W/m²):Q', format='.2f', title='Radiación (W/m²)')
        ]
    ).properties(
        height=400,
        title=alt.TitleParams(text='☀️ Radiación Solar', fontSize=18, color='#2d3748', anchor='middle')
    ).configure(
        background='white'
    ).configure_view(
        strokeWidth=0,
        fill='white'
    ).configure_axis(
        gridColor='#f7fafc',
        domainColor='#e2e8f0'
    ).interactive()
    
    st.altair_chart(chart_rad, use_container_width=True)
