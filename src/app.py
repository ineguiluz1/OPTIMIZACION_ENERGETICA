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
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
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
    
    /* Botones mejorados */
    .stButton>button {
        font-size: 18px;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: white;
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        border: none;
        border-radius: 12px;
        padding: 16px 32px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
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
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    div[data-baseweb="radio"] label {
        color: #000000 !important;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        color: #000000;
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
    st.title("⚡ Dashboard Energético — Sistema de Inversor")
    st.write("")

    st.session_state.setdefault("page", "Weather")

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
    col_filter1, col_filter2 = st.columns([1, 2])
    
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

    st.divider()

    st.subheader("📈 Evolución del Consumo (2024 - 2025)")
    st.write("")

    # Preparar datos para gráficos de consumo
    data_hist = data.copy()
    data_hist['YearWeek'] = data_hist['Datetime'].dt.to_period('W').apply(lambda r: r.start_time)

    # Calcular medias semanales
    weekly_consumption = data_hist.groupby('YearWeek')[['TotalConsumption(W)', 'HeatingSystem(W)']].mean().reset_index()
    weekly_consumption.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']

    cols = st.columns(2, gap='large')

    with cols[0]:
        chart_total = alt.Chart(weekly_consumption).mark_area(
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
            x=alt.X('Fecha:T', title='Fecha', axis=alt.Axis(format='%b %Y', labelColor='#2d3748', titleColor='#2d3748')),
            y=alt.Y('Consumo Total (W):Q', title='Consumo Total (W)', axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana', format='%d %b %Y'),
                alt.Tooltip('Consumo Total (W):Q', format='.2f', title='Consumo (W)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text='🏠 Consumo Total', fontSize=18, color='#2d3748', anchor='start')
        ).configure_view(
            strokeWidth=0
        ).interactive()
    
        st.altair_chart(chart_total, use_container_width=True)

    with cols[1]:
        chart_heating = alt.Chart(weekly_consumption).mark_area(
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
            x=alt.X('Fecha:T', title='Fecha', axis=alt.Axis(format='%b %Y', labelColor='#2d3748', titleColor='#2d3748')),
            y=alt.Y('Calefacción (W):Q', title='Consumo Calefacción (W)', axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana', format='%d %b %Y'),
                alt.Tooltip('Calefacción (W):Q', format='.2f', title='Calefacción (W)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text='🔥 Sistema de Calefacción', fontSize=18, color='#2d3748', anchor='start')
        ).configure_view(
            strokeWidth=0
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
    st.markdown("### 📈 Temperatura y Precipitación Media Semanal (2024 - 2025)")
    st.write("")
    
    # Calcular datos semanales
    weekly_temp = data_copy.groupby('YearWeek')['temperature'].mean().reset_index()
    weekly_temp.columns = ['Fecha', 'Temperatura Media (°C)']
    
    weekly_prec = data_copy.groupby('YearWeek')['precipitation'].mean().reset_index()
    weekly_prec.columns = ['Fecha', 'Precipitación Media (mm/h)']
    
    cols = st.columns([1, 1], gap='large')

    with cols[0]:
        chart = alt.Chart(weekly_temp).mark_area(
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
            x=alt.X('Fecha:T', title='Fecha', axis=alt.Axis(format='%b %Y', labelColor='#2d3748', titleColor='#2d3748')),
            y=alt.Y('Temperatura Media (°C):Q', title='Temperatura Media (°C)', axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana', format='%d %b %Y'),
                alt.Tooltip('Temperatura Media (°C):Q', format='.2f', title='Temperatura (°C)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text='🌡️ Temperatura', fontSize=18, color='#2d3748', anchor='start')
        ).configure_view(
            strokeWidth=0
        ).interactive()
    
        st.altair_chart(chart, use_container_width=True)

    with cols[1]:
        chart_prec = alt.Chart(weekly_prec).mark_area(
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
            x=alt.X('Fecha:T', title='Fecha', axis=alt.Axis(format='%b %Y', labelColor='#2d3748', titleColor='#2d3748')),
            y=alt.Y('Precipitación Media (mm/h):Q', title='Precipitación Media (mm/h)', axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana', format='%d %b %Y'),
                alt.Tooltip('Precipitación Media (mm/h):Q', format='.2f', title='Precipitación (mm/h)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text='💧 Precipitación', fontSize=18, color='#2d3748', anchor='start')
        ).configure_view(
            strokeWidth=0
        ).interactive()
        
        st.altair_chart(chart_prec, use_container_width=True)

    st.divider()

    # Gráfico de Radiación
    st.markdown("### ☀️ Radiación Media Semanal (2024 - 2025)")
    st.write("")
    
    weekly_rad = data_copy.groupby('YearWeek')['radiation'].mean().reset_index()
    weekly_rad.columns = ['Fecha', 'Radiación Media (W/m²)']
    
    chart_rad = alt.Chart(weekly_rad).mark_area(
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
        x=alt.X('Fecha:T', title='Fecha', axis=alt.Axis(format='%b %Y', labelColor='#2d3748', titleColor='#2d3748')),
        y=alt.Y('Radiación Media (W/m²):Q', title='Radiación Media (W/m²)', axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
        tooltip=[
            alt.Tooltip('Fecha:T', title='Semana', format='%d %b %Y'),
            alt.Tooltip('Radiación Media (W/m²):Q', format='.2f', title='Radiación (W/m²)')
        ]
    ).properties(
        height=400,
        title=alt.TitleParams(text='☀️ Radiación Solar', fontSize=18, color='#2d3748', anchor='start')
    ).configure_view(
        strokeWidth=0
    ).interactive()
    
    st.altair_chart(chart_rad, use_container_width=True)
