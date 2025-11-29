import streamlit as st
import pandas as pd
import numpy as np
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
        if st.button("🔮 PREDICCIONES", key="nav_realtime", use_container_width=True):
            st.session_state["page"] = "Predicciones"
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
    
    /* Fondo general minimalista - Forzar tema claro */
    .stApp {
        background: #ffffff !important;
        font-family: 'Inter', sans-serif;
        color-scheme: light !important;
    }
    
    /* Prevenir tema oscuro del sistema */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: #ffffff !important;
            color-scheme: light !important;
        }
    }
    
    /* Contenedor principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Títulos - Estilos específicos para Streamlit */
    h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: #2d3748 !important;
        text-align: center;
        font-size: 3rem !important;
        margin-bottom: 2rem;
    }
    
    h2, h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: #2d3748 !important;
    }
    
    /* Estilos específicos para títulos de Streamlit con mayor especificidad */
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    h1[data-testid="stMarkdownContainer"],
    h2[data-testid="stMarkdownContainer"],
    h3[data-testid="stMarkdownContainer"],
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        color: #2d3748 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Asegurar que los títulos siempre sean visibles en cualquier tema */
    .element-container h1,
    .element-container h2,
    .element-container h3,
    .stTitle h1,
    .stTitle h2,
    .stTitle h3 {
        color: #2d3748 !important;
    }
    
    /* Forzar color negro para títulos en todos los contextos */
    h1, h2, h3, h4, h5, h6 {
        color: #2d3748 !important;
    }
    
    /* Regla global para prevenir colores blancos en títulos */
    * h1, * h2, * h3 {
        color: #2d3748 !important;
    }
    
    /* Asegurar visibilidad en cualquier tema - regla más específica */
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .main h1,
    .main h2,
    .main h3,
    .block-container h1,
    .block-container h2,
    .block-container h3 {
        color: #2d3748 !important;
    }
    
    /* Prevenir que el tema oscuro afecte los colores */
    @media (prefers-color-scheme: dark) {
        h1, h2, h3, h4, h5, h6 {
            color: #2d3748 !important;
        }
        .stApp h1,
        .stApp h2,
        .stApp h3 {
            color: #2d3748 !important;
        }
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
        if st.button("🌤️ METEOROLOGÍA", use_container_width=True):
            st.session_state["page"] = "Weather"
            st.rerun()

    with col2:
        if st.button("📊 DATOS HISTÓRICOS", use_container_width=True):
            st.session_state["page"] = "Histórico"
            st.rerun()

    with col3:
        if st.button("🔮 PREDICCIONES", use_container_width=True):
            st.session_state["page"] = "Predicciones"
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
                "Seleccionar rango (zoom inicial):",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="stack_range_selector"
            )
        
        # Cargar TODOS los datos con granularidad de 15 minutos
        stack_data_full = data_stack[['Datetime', 'DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].copy()
        stack_data_full.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
        
        if isinstance(date_range_stack, tuple) and len(date_range_stack) == 2:
            stack_x_range_start = pd.to_datetime(date_range_stack[0])
            stack_x_range_end = pd.to_datetime(date_range_stack[1]) + pd.Timedelta(days=1)
            days_stack = (date_range_stack[1] - date_range_stack[0]).days
        else:
            single_date = date_range_stack if not isinstance(date_range_stack, tuple) else date_range_stack[0]
            stack_x_range_start = pd.to_datetime(single_date)
            stack_x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            days_stack = 1
        
        st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>📊 Granularidad: **15 minutos** ({days_stack} días) - Arrastra para desplazarte</span>", unsafe_allow_html=True)
        
        # Crear gráfico Plotly stacked area
        fig_stack = go.Figure()
        fig_stack.add_trace(go.Scatter(
            x=stack_data_full['Fecha'], y=stack_data_full['Consumo Directo (W)'],
            name='Consumo Directo', stackgroup='one', line=dict(color='#FF6347')
        ))
        fig_stack.add_trace(go.Scatter(
            x=stack_data_full['Fecha'], y=stack_data_full['Descarga Batería (W)'],
            name='Descarga Batería', stackgroup='one', line=dict(color='#1E90FF')
        ))
        fig_stack.add_trace(go.Scatter(
            x=stack_data_full['Fecha'], y=stack_data_full['Suministro Externo (W)'],
            name='Suministro Externo', stackgroup='one', line=dict(color='#3CB371')
        ))
        fig_stack.update_layout(
            title={'text': 'Fuentes de Energía', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
            xaxis=dict(title='Fecha', range=[stack_x_range_start, stack_x_range_end],
                      rangeslider=dict(visible=True, thickness=0.05),
                      titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
            yaxis=dict(title='Potencia (W)', gridcolor='rgba(200,200,200,0.3)',
                      titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#2d3748')),
            height=500, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=60, r=20, t=80, b=80), hovermode='x unified'
        )
        st.plotly_chart(fig_stack, use_container_width=True)
        
        # Marcar que usamos Plotly
        stack_view_mode_plotly = True
    
    # Solo mostrar Altair si no es Periodo Específico
    if stack_view_mode != "Periodo Específico":
        # Crear stacked area chart con Altair
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
                "Seleccionar rango (zoom inicial):",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="consumption_range_selector"
            )
        
        # Cargar TODOS los datos con granularidad de 15 minutos
        consumption_data_full = data_hist[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
        consumption_data_full.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            cons_x_range_start = pd.to_datetime(date_range[0])
            cons_x_range_end = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
            days_cons = (date_range[1] - date_range[0]).days
        else:
            single_date = date_range if not isinstance(date_range, tuple) else date_range[0]
            cons_x_range_start = pd.to_datetime(single_date)
            cons_x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            days_cons = 1
        
        st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>📊 Granularidad: **15 minutos** ({days_cons} días) - Arrastra para desplazarte</span>", unsafe_allow_html=True)
        
        # Crear gráficos Plotly
        cols_plotly_cons = st.columns(2, gap='large')
        
        with cols_plotly_cons[0]:
            fig_cons_total = go.Figure()
            fig_cons_total.add_trace(go.Scatter(
                x=consumption_data_full['Fecha'], y=consumption_data_full['Consumo Total (W)'],
                mode='lines', name='Consumo Total', line=dict(color='#805AD5', width=2),
                fill='tozeroy', fillcolor='rgba(128, 90, 213, 0.1)'
            ))
            fig_cons_total.update_layout(
                title={'text': 'Consumo Total', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(title='Fecha', range=[cons_x_range_start, cons_x_range_end],
                          rangeslider=dict(visible=True, thickness=0.05),
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                yaxis=dict(title='Consumo Total (W)', gridcolor='rgba(200,200,200,0.3)',
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_cons_total, use_container_width=True)
        
        with cols_plotly_cons[1]:
            fig_cons_heating = go.Figure()
            fig_cons_heating.add_trace(go.Scatter(
                x=consumption_data_full['Fecha'], y=consumption_data_full['Calefacción (W)'],
                mode='lines', name='Calefacción', line=dict(color='#E53E3E', width=2),
                fill='tozeroy', fillcolor='rgba(229, 62, 62, 0.1)'
            ))
            fig_cons_heating.update_layout(
                title={'text': 'Sistema de Calefacción', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(title='Fecha', range=[cons_x_range_start, cons_x_range_end],
                          rangeslider=dict(visible=True, thickness=0.05),
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                yaxis=dict(title='Calefacción (W)', gridcolor='rgba(200,200,200,0.3)',
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_cons_heating, use_container_width=True)
    
    # Solo mostrar Altair si no es Periodo Específico
    if consumption_view_mode != "Periodo Específico":
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

    st.divider()

    # Nueva sección: Scatter Plots de Correlación
    st.subheader("🔗 Correlación Consumo vs Variables Meteorológicas")
    st.write("")

    # Preparar datos para scatter plots con franja horaria
    scatter_data = data[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)', 'temperature', 'radiation']].copy()
    scatter_data.columns = ['Datetime', 'Consumo Total (W)', 'Calefacción (W)', 'Temperatura (°C)', 'Radiación (W/m²)']
    
    # Crear columna de franja horaria
    def get_time_slot(hour):
        if 0 <= hour < 4:
            return '00:00 - 04:00'
        elif 4 <= hour < 8:
            return '04:00 - 08:00'
        elif 8 <= hour < 12:
            return '08:00 - 12:00'
        elif 12 <= hour < 16:
            return '12:00 - 16:00'
        elif 16 <= hour < 20:
            return '16:00 - 20:00'
        else:
            return '20:00 - 24:00'
    
    scatter_data['Franja Horaria'] = scatter_data['Datetime'].dt.hour.apply(get_time_slot)
    
    # Colores para cada franja horaria (paleta distinguible)
    time_slot_colors = [
        '#1E3A5F',  # 00-04: Azul oscuro (noche profunda)
        '#6366F1',  # 04-08: Índigo (amanecer)
        '#F59E0B',  # 08-12: Ámbar (mañana)
        '#EF4444',  # 12-16: Rojo (mediodía)
        '#F97316',  # 16-20: Naranja (tarde)
        '#8B5CF6'   # 20-24: Violeta (noche)
    ]
    
    time_slot_domain = ['00:00 - 04:00', '04:00 - 08:00', '08:00 - 12:00', 
                        '12:00 - 16:00', '16:00 - 20:00', '20:00 - 24:00']

    # Selección interactiva para filtrar por franja horaria (clickable en leyenda)
    selection1 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection2 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection3 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection4 = alt.selection_point(fields=['Franja Horaria'], bind='legend')

    # Primera fila: Consumo Total vs Temperatura y Radiación
    scatter_cols1 = st.columns(2, gap='large')

    with scatter_cols1[0]:
        scatter_temp_total = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Temperatura (°C):Q', 
                    title='Temperatura (°C)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Consumo Total (W):Q', 
                    title='Consumo Total (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                           scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                           legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection1, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Temperatura (°C):Q', format='.2f'),
                alt.Tooltip('Consumo Total (W):Q', format='.2f')
            ]
        ).add_params(
            selection1
        ).properties(
            height=400,
            title=alt.TitleParams(text='Consumo Total vs Temperatura', fontSize=18, color='#2d3748', anchor='middle')
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
        
        st.altair_chart(scatter_temp_total, use_container_width=True)

    with scatter_cols1[1]:
        scatter_rad_total = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Radiación (W/m²):Q', 
                    title='Radiación (W/m²)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Consumo Total (W):Q', 
                    title='Consumo Total (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                           scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                           legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection2, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Radiación (W/m²):Q', format='.2f'),
                alt.Tooltip('Consumo Total (W):Q', format='.2f')
            ]
        ).add_params(
            selection2
        ).properties(
            height=400,
            title=alt.TitleParams(text='Consumo Total vs Radiación', fontSize=18, color='#2d3748', anchor='middle')
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
        
        st.altair_chart(scatter_rad_total, use_container_width=True)

    st.write("")

    # Segunda fila: Calefacción vs Temperatura y Radiación
    scatter_cols2 = st.columns(2, gap='large')

    with scatter_cols2[0]:
        scatter_temp_heating = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Temperatura (°C):Q', 
                    title='Temperatura (°C)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Calefacción (W):Q', 
                    title='Consumo Calefacción (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                           scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                           legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection3, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Temperatura (°C):Q', format='.2f'),
                alt.Tooltip('Calefacción (W):Q', format='.2f')
            ]
        ).add_params(
            selection3
        ).properties(
            height=400,
            title=alt.TitleParams(text='Calefacción vs Temperatura', fontSize=18, color='#2d3748', anchor='middle')
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
        
        st.altair_chart(scatter_temp_heating, use_container_width=True)

    with scatter_cols2[1]:
        scatter_rad_heating = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Radiación (W/m²):Q', 
                    title='Radiación (W/m²)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Calefacción (W):Q', 
                    title='Consumo Calefacción (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                           scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                           legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection4, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Radiación (W/m²):Q', format='.2f'),
                alt.Tooltip('Calefacción (W):Q', format='.2f')
            ]
        ).add_params(
            selection4
        ).properties(
            height=400,
            title=alt.TitleParams(text='Calefacción vs Radiación', fontSize=18, color='#2d3748', anchor='middle')
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
        
        st.altair_chart(scatter_rad_heating, use_container_width=True)

    st.divider()

    # Scatter plots de Generación PV vs Variables Meteorológicas (solo cuando hay radiación)
    st.subheader("☀️ Generación Fotovoltaica vs Variables Meteorológicas")
    st.markdown("<span style='color: #718096; font-size: 14px;'>*Solo datos con radiación solar > 0*</span>", unsafe_allow_html=True)
    st.write("")

    # Filtrar datos donde hay radiación solar > 0
    pv_data = data[data['radiation'] > 0][['Datetime', 'PV_PowerGeneration(W)', 'temperature', 'radiation']].copy()
    pv_data.columns = ['Datetime', 'Generación PV (W)', 'Temperatura (°C)', 'Radiación (W/m²)']
    
    # Crear columna de franja horaria para colorear
    pv_data['Franja Horaria'] = pv_data['Datetime'].dt.hour.apply(get_time_slot)

    # Selecciones interactivas para los scatter plots de PV
    selection_pv1 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection_pv2 = alt.selection_point(fields=['Franja Horaria'], bind='legend')

    scatter_pv_cols = st.columns(2, gap='large')

    with scatter_pv_cols[0]:
        scatter_pv_temp = alt.Chart(pv_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Temperatura (°C):Q', 
                    title='Temperatura (°C)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Generación PV (W):Q', 
                    title='Generación PV (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                           scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                           legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection_pv1, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Temperatura (°C):Q', format='.2f'),
                alt.Tooltip('Generación PV (W):Q', format='.2f')
            ]
        ).add_params(
            selection_pv1
        ).properties(
            height=400,
            title=alt.TitleParams(text='Generación PV vs Temperatura', fontSize=18, color='#2d3748', anchor='middle')
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
        
        st.altair_chart(scatter_pv_temp, use_container_width=True)

    with scatter_pv_cols[1]:
        scatter_pv_rad = alt.Chart(pv_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Radiación (W/m²):Q', 
                    title='Radiación (W/m²)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Generación PV (W):Q', 
                    title='Generación PV (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                           scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                           legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection_pv2, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Radiación (W/m²):Q', format='.2f'),
                alt.Tooltip('Generación PV (W):Q', format='.2f')
            ]
        ).add_params(
            selection_pv2
        ).properties(
            height=400,
            title=alt.TitleParams(text='Generación PV vs Radiación', fontSize=18, color='#2d3748', anchor='middle')
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
        
        st.altair_chart(scatter_pv_rad, use_container_width=True)

    st.divider()

    # Gráfico Combinado de Todas las Variables (Meteorología + Consumo)
    st.subheader("🌍 Vista Combinada - Todas las Variables")
    
    # Selector de rango de fechas (solo para zoom inicial)
    col_hist_combined1, col_hist_combined2 = st.columns([1, 2])
    
    with col_hist_combined1:
        hist_combined_range_option = st.radio(
            "Vista inicial:",
            ["Todo el periodo", "Rango personalizado"],
            horizontal=True,
            key="hist_combined_range_option"
        )
    
    # Preparar datos raw (15 minutos)
    hist_combined_raw = data[['Datetime', 'temperature', 'precipitation', 'radiation', 
                              'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
    hist_combined_raw.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 'Radiación (W/m²)',
                                  'Consumo Total (W)', 'Calefacción (W)']
    
    min_date_hist = hist_combined_raw['Fecha'].min()
    max_date_hist = hist_combined_raw['Fecha'].max()
    
    # Definir rango inicial de zoom
    x_range_start_hist = None
    x_range_end_hist = None
    
    if hist_combined_range_option == "Rango personalizado":
        with col_hist_combined2:
            hist_combined_date_range = st.date_input(
                "Seleccionar rango:",
                value=(min_date_hist.date(), min_date_hist.date() + pd.Timedelta(days=7)),
                min_value=min_date_hist.date(),
                max_value=max_date_hist.date(),
                key="hist_combined_date_range"
            )
        
        if isinstance(hist_combined_date_range, tuple) and len(hist_combined_date_range) == 2:
            x_range_start_hist = pd.to_datetime(hist_combined_date_range[0])
            x_range_end_hist = pd.to_datetime(hist_combined_date_range[1]) + pd.Timedelta(days=1)
            days_selected_hist = (hist_combined_date_range[1] - hist_combined_date_range[0]).days
            
            # Usar datos con granularidad de 15 minutos para rango personalizado
            hist_combined_data = hist_combined_raw.copy()
            hist_granularity_msg = f"📊 Granularidad: **15 minutos** ({days_selected_hist} días) - Arrastra para desplazarte"
        else:
            single_date_hist = hist_combined_date_range if not isinstance(hist_combined_date_range, tuple) else hist_combined_date_range[0]
            x_range_start_hist = pd.to_datetime(single_date_hist)
            x_range_end_hist = pd.to_datetime(single_date_hist) + pd.Timedelta(days=1)
            
            # Usar datos con granularidad de 15 minutos
            hist_combined_data = hist_combined_raw.copy()
            hist_granularity_msg = "📊 Granularidad: **15 minutos** (1 día) - Arrastra para desplazarte"
    else:
        # Todo el periodo - agregar por día para mejor visualización
        hist_combined_raw['Dia'] = hist_combined_raw['Fecha'].dt.date
        hist_combined_data = hist_combined_raw.groupby('Dia').agg({
            'Temperatura (°C)': 'mean',
            'Precipitación (mm/h)': 'mean', 
            'Radiación (W/m²)': 'mean',
            'Consumo Total (W)': 'mean',
            'Calefacción (W)': 'mean'
        }).reset_index()
        hist_combined_data.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 
                                      'Radiación (W/m²)', 'Consumo Total (W)', 'Calefacción (W)']
        hist_combined_data['Fecha'] = pd.to_datetime(hist_combined_data['Fecha'])
        hist_granularity_msg = "📊 Granularidad: **Diaria** (todo el periodo)"
    
    st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>{hist_granularity_msg}</span>", unsafe_allow_html=True)

    # Calcular rangos para alinear el 0 en todos los ejes
    min_temp_hist = hist_combined_data['Temperatura (°C)'].min()
    max_temp_hist = hist_combined_data['Temperatura (°C)'].max()
    max_consumption_hist = hist_combined_data['Consumo Total (W)'].max()
    max_rad_hist = hist_combined_data['Radiación (W/m²)'].max()
    
    temp_margin_hist = (max_temp_hist - min_temp_hist) * 0.1
    min_temp_range_hist = min_temp_hist - temp_margin_hist
    max_temp_range_hist = max_temp_hist + temp_margin_hist
    
    temp_range_total_hist = max_temp_range_hist - min_temp_range_hist
    zero_position_hist = abs(min_temp_range_hist) / temp_range_total_hist if temp_range_total_hist > 0 else 0
    
    if zero_position_hist > 0 and zero_position_hist < 1:
        max_consumption_range_hist = max_consumption_hist * 1.1
        max_rad_range_hist = max_rad_hist * 1.1
        min_consumption_range_hist = -max_consumption_range_hist * zero_position_hist / (1 - zero_position_hist)
        min_rad_range_hist = -max_rad_range_hist * zero_position_hist / (1 - zero_position_hist)
    else:
        min_consumption_range_hist = 0
        min_rad_range_hist = 0
        max_consumption_range_hist = max_consumption_hist * 1.1
        max_rad_range_hist = max_rad_hist * 1.1

    # Crear gráfico con 3 ejes Y
    from plotly.subplots import make_subplots
    
    fig_hist_combined = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Temperatura
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Temperatura (°C)'],
            name='Temperatura (°C)',
            line=dict(color='#EF4444', width=2.5, shape='spline'),
            mode='lines'
        ),
        secondary_y=False
    )
    
    # Consumo Total
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Consumo Total (W)'],
            name='Consumo Total (W)',
            line=dict(color='#805AD5', width=2.5, shape='spline'),
            mode='lines'
        ),
        secondary_y=True
    )
    
    # Calefacción (tercer eje)
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Calefacción (W)'],
            name='Calefacción (W)',
            line=dict(color='#38A169', width=2.5, shape='spline'),
            mode='lines',
            yaxis='y3'
        )
    )
    
    # Radiación (cuarto eje)
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Radiación (W/m²)'],
            name='Radiación (W/m²)',
            line=dict(color='#F97316', width=2, shape='spline', dash='dot'),
            mode='lines',
            yaxis='y4'
        )
    )
    
    fig_hist_combined.update_layout(
        title={
            'text': 'Variables Combinadas: Meteorología + Consumo',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748', 'family': 'Poppins'}
        },
        xaxis=dict(
            title='Fecha',
            titlefont=dict(color='#2d3748'),
            tickfont=dict(color='#2d3748'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            domain=[0.12, 0.82],
            type='date',
            range=[x_range_start_hist, x_range_end_hist] if x_range_start_hist is not None else None,
            rangeslider=dict(visible=True, thickness=0.05)
        ),
        yaxis=dict(
            title='Temperatura (°C)',
            titlefont=dict(color='#EF4444'),
            tickfont=dict(color='#EF4444'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            side='left',
            range=[min_temp_range_hist, max_temp_range_hist],
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis2=dict(
            title='Consumo Total (W)',
            titlefont=dict(color='#805AD5'),
            tickfont=dict(color='#805AD5'),
            overlaying='y',
            side='right',
            position=0.82,
            range=[min_consumption_range_hist, max_consumption_range_hist],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis3=dict(
            title='Calefacción (W)',
            titlefont=dict(color='#38A169'),
            tickfont=dict(color='#38A169'),
            overlaying='y',
            side='right',
            position=0.91,
            range=[min_consumption_range_hist, max_consumption_range_hist],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis4=dict(
            title='Radiación (W/m²)',
            titlefont=dict(color='#F97316'),
            tickfont=dict(color='#F97316'),
            overlaying='y',
            side='left',
            position=0.05,
            range=[min_rad_range_hist, max_rad_range_hist],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='#2d3748')
        ),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        margin=dict(l=80, r=80, t=80, b=80),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_hist_combined, use_container_width=True)


# ============================================================================
# Página de Predicciones
# ============================================================================
if page == "Predicciones":
    st.title("🔮 Predicciones de Carga Térmica")
    
    # Menú de navegación
    show_navigation_menu()
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); 
                padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px;'>
        <p style='color: #4a5568; margin: 0; font-size: 15px;'>
            Este módulo utiliza modelos de predicción basados en <b>Changepoint</b> para estimar la carga térmica 
            del edificio en función de las condiciones meteorológicas. Selecciona un modelo y proporciona los datos de entrada.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Importar el servicio de predicción
    import sys
    import importlib.util
    import os
    from pathlib import Path
    
    def get_prediction_service():
        """Carga el servicio de predicción BentoML"""
        try:
            # Intentar múltiples rutas posibles para service.py
            possible_paths = [
                Path(__file__).parent.parent / "service.py",  # Desde src/ hacia arriba
                Path.cwd() / "service.py",  # Directorio de trabajo actual
                Path.cwd().parent / "service.py",  # Un nivel arriba del cwd
                Path(__file__).parent / ".." / "service.py",  # Relativo desde src
            ]
            
            service_module_path = None
            for p in possible_paths:
                resolved = p.resolve()
                if resolved.exists():
                    service_module_path = resolved
                    break
            
            # Verificar que el archivo existe
            if service_module_path is None:
                paths_tried = "\n".join([f"  - {p.resolve()}" for p in possible_paths])
                return None, f"Archivo service.py no encontrado.\n\nRutas intentadas:\n{paths_tried}\n\nDirectorio actual: {Path.cwd()}"
            
            spec = importlib.util.spec_from_file_location("service", service_module_path)
            service_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(service_module)
            return service_module.service_instance, None
        except Exception as e:
            import traceback
            return None, f"{str(e)}\n\n{traceback.format_exc()}"
    
    service, service_error = get_prediction_service()
    
    if service:
        # Selector de modelo
        st.markdown("### 🎯 Selección de Modelo")
        
        col_model1, col_model2 = st.columns([1, 2])
        
        with col_model1:
            model_type = st.radio(
                "Tipo de Modelo:",
                ["Time-of-Week (ToW)", "Cluster-PRED (CART)"],
                horizontal=False,
                help="ToW: 168 modelos horarios (uno por hora de la semana). Cluster-PRED: Usa clasificador CART para predicción de clusters."
            )
        
        with col_model2:
            with st.expander("ℹ️ Información del Modelo", expanded=False):
                if model_type == "Time-of-Week (ToW)":
                    st.markdown(f"""
                    <div style='padding: 10px;'>
                        <p style='color: #2d3748;'><b>Tipo:</b> {service.tow_model_type}</p>
                        <p style='color: #2d3748;'><b>Número de Modelos:</b> {service.tow_num_models}</p>
                        <p style='color: #718096; font-size: 13px;'>
                            Utiliza parámetros de changepoint específicos para cada hora de la semana (0-167).
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='padding: 10px;'>
                        <p style='color: #2d3748;'><b>Tipo:</b> {service.cluster_pred_model_type}</p>
                        <p style='color: #2d3748;'><b>Número de Clusters:</b> {service.cluster_pred_num_clusters}</p>
                        <p style='color: #718096; font-size: 13px;'>
                            Modelo basado en clustering con clasificador CART para asignación de clusters.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        
        # Sección de inputs
        st.markdown("### 📝 Parámetros de Entrada")
        
        col_input1, col_input2 = st.columns(2, gap="large")
        
        with col_input1:
            st.markdown("#### 🌡️ Condiciones Meteorológicas")
            
            temperature = st.number_input(
                "Temperatura (°C)",
                min_value=-30.0,
                max_value=50.0,
                value=15.0,
                step=0.5,
                help="Temperatura exterior en grados Celsius"
            )
            
            solar_irradiation = st.number_input(
                "Irradiación Solar (W/m²)",
                min_value=0.0,
                max_value=1200.0,
                value=250.0,
                step=10.0,
                help="Irradiación solar en Watts por metro cuadrado"
            )
        
        with col_input2:
            st.markdown("#### 🕐 Información Temporal")
            
            if model_type == "Time-of-Week (ToW)":
                use_datetime = st.checkbox("Usar Selector de Fecha/Hora", value=True)
                
                if use_datetime:
                    selected_date = st.date_input(
                        "Fecha",
                        value=datetime.now().date(),
                        key="pred_date"
                    )
                    selected_time = st.time_input(
                        "Hora",
                        value=datetime.now().time(),
                        key="pred_time"
                    )
                    
                    # Calcular hora de la semana (0=Lunes 00:00, 167=Domingo 23:00)
                    weekday = selected_date.weekday()
                    hour = selected_time.hour
                    timestamp_week = weekday * 24 + hour
                    
                    day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                    st.markdown(f"""
                    <div style='background: #edf2f7; padding: 12px; border-radius: 8px; margin-top: 10px;'>
                        <p style='color: #4a5568; margin: 0; font-size: 14px;'>
                            <b>Hora de la Semana:</b> {timestamp_week} ({day_names[weekday]} {hour:02d}:00)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    timestamp_week = st.number_input(
                        "Hora de la Semana (0-167)",
                        min_value=0,
                        max_value=167,
                        value=42,
                        step=1,
                        help="0=Lunes 00:00, 167=Domingo 23:00"
                    )
                    
                    day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                    day_idx = timestamp_week // 24
                    hour_idx = timestamp_week % 24
                    st.markdown(f"""
                    <div style='background: #edf2f7; padding: 12px; border-radius: 8px; margin-top: 10px;'>
                        <p style='color: #4a5568; margin: 0; font-size: 14px;'>
                            <b>Corresponde a:</b> {day_names[day_idx]} {hour_idx:02d}:00
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:  # Cluster-PRED
                cluster_hour = st.number_input(
                    "ID Cluster-Hora",
                    min_value=0,
                    max_value=100,
                    value=15,
                    step=1,
                    help="Identificador cluster-hora predicho por el modelo CART"
                )
                st.markdown("""
                <div style='background: #edf2f7; padding: 12px; border-radius: 8px; margin-top: 10px;'>
                    <p style='color: #4a5568; margin: 0; font-size: 14px;'>
                        💡 Este modelo usa clusters predichos por CART (adecuado para despliegue prospectivo)
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Botón de predicción
        st.markdown("### 🚀 Predicción")
        
        if st.button("🔮 Calcular Predicción", type="primary", use_container_width=True):
            try:
                with st.spinner("Calculando predicción..."):
                    if model_type == "Time-of-Week (ToW)":
                        result = service.predict_tow(
                            timestamp_week,
                            temperature,
                            solar_irradiation
                        )
                        prediction = result["power_kw"]
                        input_summary = {
                            "Hora de la Semana": int(timestamp_week),
                            "Temperatura (°C)": temperature,
                            "Irradiación Solar (W/m²)": solar_irradiation
                        }
                    else:  # Cluster-PRED
                        result = service.predict_cluster_pred(
                            cluster_hour,
                            temperature,
                            solar_irradiation
                        )
                        prediction = result["power_kw"]
                        input_summary = {
                            "Cluster-Hora": int(cluster_hour),
                            "Temperatura (°C)": temperature,
                            "Irradiación Solar (W/m²)": solar_irradiation
                        }
                
                # Mostrar resultados
                st.markdown("""
                <div style='background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); 
                            padding: 15px; border-radius: 12px; margin: 20px 0;'>
                    <p style='color: white; margin: 0; font-size: 16px; font-weight: 600;'>
                        ✅ Predicción Completada
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col_result1, col_result2 = st.columns([1, 1])
                
                with col_result1:
                    st.metric(
                        label="Carga Térmica Predicha",
                        value=f"{prediction:.2f} kW",
                        delta=None
                    )
                
                with col_result2:
                    st.markdown("**Resumen de Entrada:**")
                    for key, value in input_summary.items():
                        st.markdown(f"• **{key}:** {value}")
                
                # Detalles adicionales
                with st.expander("📊 Detalles de la Predicción"):
                    st.markdown(f"**Modelo Utilizado:** {model_type}")
                    st.markdown(f"**Valor de Predicción:** {prediction:.4f} kW")
                    if model_type == "Time-of-Week (ToW)":
                        st.markdown(f"**Tipo de Modelo:** {service.tow_model_type}")
                    else:
                        st.markdown(f"**Tipo de Modelo:** {service.cluster_pred_model_type}")
                        
            except Exception as e:
                st.error(f"❌ Error en la predicción: {e}")
                st.info("Verifica que los valores de entrada sean válidos para el modelo seleccionado.")
        
        st.divider()
        
        # Sección de predicción por lotes
        st.markdown("### 📊 Predicción por Lotes (Opcional)")
        
        with st.expander("📤 Subir CSV para Predicciones en Lote"):
            st.markdown("""
            <div style='background: #f7fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                <p style='color: #4a5568; margin: 0; font-size: 14px;'>
                    Sube un archivo CSV con las siguientes columnas:
                </p>
                <ul style='color: #4a5568; margin: 10px 0 0 20px; font-size: 13px;'>
                    <li>Para modelo <b>ToW</b>: <code>timestamp_week</code>, <code>temperature</code>, <code>solar_irradiation</code></li>
                    <li>Para modelo <b>Cluster-PRED</b>: <code>cluster_hour</code>, <code>temperature</code>, <code>solar_irradiation</code></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("Selecciona un archivo CSV", type="csv", key="batch_file")
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.markdown("**Vista previa de los datos:**")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    if st.button("🚀 Ejecutar Predicción en Lote", key="batch_predict"):
                        with st.spinner("Procesando predicciones en lote..."):
                            if model_type == "Time-of-Week (ToW)":
                                result = service.predict_batch_tow(
                                    df['timestamp_week'].values.tolist(),
                                    df['temperature'].values.tolist(),
                                    df['solar_irradiation'].values.tolist()
                                )
                                predictions = np.array(result["predictions"])
                            else:  # Cluster-PRED
                                result = service.predict_batch_cluster_pred(
                                    df['cluster_hour'].values.tolist(),
                                    df['temperature'].values.tolist(),
                                    df['solar_irradiation'].values.tolist()
                                )
                                predictions = np.array(result["predictions"])
                            
                            df['predicted_power_kw'] = predictions
                            
                            st.success("✅ Predicciones en lote completadas!")
                            st.dataframe(df, use_container_width=True)
                            
                            # Botón de descarga
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Descargar Resultados CSV",
                                data=csv,
                                file_name="predicciones.csv",
                                mime="text/csv"
                            )
                            
                            # Estadísticas básicas
                            st.markdown("#### 📈 Estadísticas")
                            col_stats1, col_stats2, col_stats3 = st.columns(3)
                            with col_stats1:
                                st.metric("Media", f"{predictions.mean():.2f} kW")
                            with col_stats2:
                                st.metric("Mínimo", f"{predictions.min():.2f} kW")
                            with col_stats3:
                                st.metric("Máximo", f"{predictions.max():.2f} kW")
                            
                except Exception as e:
                    st.error(f"Error procesando el archivo: {e}")
    
    else:
        st.error("❌ No se pudo inicializar el servicio de predicción.")
        
        # Mostrar el error real para diagnóstico
        if service_error:
            with st.expander("🔍 Ver detalles del error", expanded=True):
                st.code(service_error, language="text")
        
        st.markdown("""
        <div style='background: #fed7d7; padding: 20px; border-radius: 12px; border: 1px solid #fc8181;'>
            <p style='color: #c53030; margin: 0 0 10px 0; font-weight: 600;'>Archivos requeridos:</p>
            <ul style='color: #c53030; margin: 0; padding-left: 20px;'>
                <li><code>output/data_06_Changepoint_Pars_summ_TOW2.csv</code></li>
                <li><code>output/data_09_Changepoint_Pars_summ_CLUST_PRED.csv</code></li>
                <li><code>output/data_09_cart_model.pkl</code></li>
            </ul>
            <p style='color: #c53030; margin: 15px 0 0 0; font-size: 13px;'>
                Ejecuta el pipeline de análisis para generar estos archivos.
            </p>
        </div>
        """, unsafe_allow_html=True)


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
                "Seleccionar rango (zoom inicial):",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="weather_range_selector"
            )
        
        # Cargar TODOS los datos con granularidad de 15 minutos
        temp_data = data_copy[['Datetime', 'temperature']].copy()
        temp_data.columns = ['Fecha', 'Temperatura Media (°C)']
        
        prec_data = data_copy[['Datetime', 'precipitation']].copy()
        prec_data.columns = ['Fecha', 'Precipitación Media (mm/h)']
        
        # Establecer rango inicial de zoom
        if isinstance(date_range_weather, tuple) and len(date_range_weather) == 2:
            weather_x_range_start = pd.to_datetime(date_range_weather[0])
            weather_x_range_end = pd.to_datetime(date_range_weather[1]) + pd.Timedelta(days=1)
            days_weather = (date_range_weather[1] - date_range_weather[0]).days
        else:
            single_date = date_range_weather if not isinstance(date_range_weather, tuple) else date_range_weather[0]
            weather_x_range_start = pd.to_datetime(single_date)
            weather_x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            days_weather = 1
        
        st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>📊 Granularidad: **15 minutos** ({days_weather} días) - Arrastra para desplazarte</span>", unsafe_allow_html=True)
        
        # Usar Plotly para gráficos interactivos con rangeslider
        cols_plotly = st.columns([1, 1], gap='large')
        
        with cols_plotly[0]:
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=temp_data['Fecha'],
                y=temp_data['Temperatura Media (°C)'],
                mode='lines',
                name='Temperatura',
                line=dict(color='#EF4444', width=2),
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.1)'
            ))
            fig_temp.update_layout(
                title={'text': '🌡️ Temperatura', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(title='Fecha', range=[weather_x_range_start, weather_x_range_end],
                          rangeslider=dict(visible=True, thickness=0.05),
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                yaxis=dict(title='Temperatura (°C)', gridcolor='rgba(200,200,200,0.3)',
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with cols_plotly[1]:
            fig_prec = go.Figure()
            fig_prec.add_trace(go.Scatter(
                x=prec_data['Fecha'],
                y=prec_data['Precipitación Media (mm/h)'],
                mode='lines',
                name='Precipitación',
                line=dict(color='#3B82F6', width=2),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            fig_prec.update_layout(
                title={'text': '💧 Precipitación', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(title='Fecha', range=[weather_x_range_start, weather_x_range_end],
                          rangeslider=dict(visible=True, thickness=0.05),
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                yaxis=dict(title='Precipitación (mm/h)', gridcolor='rgba(200,200,200,0.3)',
                          titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_prec, use_container_width=True)
    
    # Solo mostrar gráficos de Altair si no es Periodo Específico
    if weather_view_mode != "Periodo Específico":
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

        # Gráfico de Radiación (solo para Semanal/Diario)
        st.markdown("### ☀️ Radiación (2024 - 2025)")
        st.write("")
        
        if weather_view_mode == "Semanal":
            weekly_rad = data_copy.groupby('YearWeek')['radiation'].mean().reset_index()
            weekly_rad.columns = ['Fecha', 'Radiación Media (W/m²)']
            rad_data = weekly_rad
        else:  # Diario
            daily_rad = data_copy[data_copy['Datetime'].dt.date == selected_weather_date].copy()
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
    
    else:
        # Gráfico de Radiación para Periodo Específico (Plotly)
        st.divider()
        st.markdown("### ☀️ Radiación (2024 - 2025)")
        st.write("")
        
        rad_data_full = data_copy[['Datetime', 'radiation']].copy()
        rad_data_full.columns = ['Fecha', 'Radiación (W/m²)']
        
        fig_rad = go.Figure()
        fig_rad.add_trace(go.Scatter(
            x=rad_data_full['Fecha'],
            y=rad_data_full['Radiación (W/m²)'],
            mode='lines',
            name='Radiación',
            line=dict(color='#F97316', width=2),
            fill='tozeroy',
            fillcolor='rgba(249, 115, 22, 0.1)'
        ))
        fig_rad.update_layout(
            title={'text': '☀️ Radiación Solar', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
            xaxis=dict(title='Fecha', range=[weather_x_range_start, weather_x_range_end],
                      rangeslider=dict(visible=True, thickness=0.05),
                      titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
            yaxis=dict(title='Radiación (W/m²)', gridcolor='rgba(200,200,200,0.3)',
                      titlefont=dict(color='#2d3748'), tickfont=dict(color='#2d3748')),
            height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=60, r=20, t=60, b=80)
        )
        st.plotly_chart(fig_rad, use_container_width=True)

    st.divider()

    # Gráfico Combinado de Variables Meteorológicas
    st.markdown("### 🌍 Vista Combinada - Variables Meteorológicas")
    
    # Selector de rango de fechas (solo para zoom inicial)
    col_combined1, col_combined2 = st.columns([1, 2])
    
    with col_combined1:
        combined_range_option = st.radio(
            "Vista inicial:",
            ["Todo el periodo", "Rango personalizado"],
            horizontal=True,
            key="combined_range_option"
        )
    
    # Preparar datos raw (15 minutos)
    combined_weather_raw = data_copy[['Datetime', 'temperature', 'precipitation', 'radiation']].copy()
    combined_weather_raw.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 'Radiación (W/m²)']
    
    min_date_combined = combined_weather_raw['Fecha'].min()
    max_date_combined = combined_weather_raw['Fecha'].max()
    
    # Definir rango inicial de zoom
    x_range_start = None
    x_range_end = None
    
    if combined_range_option == "Rango personalizado":
        with col_combined2:
            combined_date_range = st.date_input(
                "Seleccionar rango:",
                value=(min_date_combined.date(), min_date_combined.date() + pd.Timedelta(days=7)),
                min_value=min_date_combined.date(),
                max_value=max_date_combined.date(),
                key="combined_date_range"
            )
        
        if isinstance(combined_date_range, tuple) and len(combined_date_range) == 2:
            x_range_start = pd.to_datetime(combined_date_range[0])
            x_range_end = pd.to_datetime(combined_date_range[1]) + pd.Timedelta(days=1)
            days_selected = (combined_date_range[1] - combined_date_range[0]).days
            
            # Usar datos con granularidad de 15 minutos para rango personalizado
            combined_weather = combined_weather_raw.copy()
            granularity_msg = f"📊 Granularidad: **15 minutos** ({days_selected} días) - Arrastra para desplazarte"
        else:
            single_date = combined_date_range if not isinstance(combined_date_range, tuple) else combined_date_range[0]
            x_range_start = pd.to_datetime(single_date)
            x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            
            # Usar datos con granularidad de 15 minutos
            combined_weather = combined_weather_raw.copy()
            granularity_msg = "📊 Granularidad: **15 minutos** (1 día) - Arrastra para desplazarte"
    else:
        # Todo el periodo - agregar por día para mejor visualización
        combined_weather_raw['Dia'] = combined_weather_raw['Fecha'].dt.date
        combined_weather = combined_weather_raw.groupby('Dia').agg({
            'Temperatura (°C)': 'mean',
            'Precipitación (mm/h)': 'mean', 
            'Radiación (W/m²)': 'mean'
        }).reset_index()
        combined_weather.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 'Radiación (W/m²)']
        combined_weather['Fecha'] = pd.to_datetime(combined_weather['Fecha'])
        granularity_msg = "📊 Granularidad: **Diaria** (todo el periodo)"
    
    st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>{granularity_msg}</span>", unsafe_allow_html=True)

    # Calcular rangos para alinear el 0 en todos los ejes
    min_temp = combined_weather['Temperatura (°C)'].min()
    max_temp = combined_weather['Temperatura (°C)'].max()
    max_prec = combined_weather['Precipitación (mm/h)'].max()
    max_rad = combined_weather['Radiación (W/m²)'].max()
    
    # Añadir margen del 10%
    temp_margin = (max_temp - min_temp) * 0.1
    min_temp_range = min_temp - temp_margin
    max_temp_range = max_temp + temp_margin
    
    # Calcular la posición proporcional del 0 en el eje de temperatura
    temp_range_total = max_temp_range - min_temp_range
    zero_position = abs(min_temp_range) / temp_range_total  # Proporción desde el fondo
    
    # Ajustar los otros ejes para que el 0 esté en la misma posición
    # Si zero_position es la proporción donde está el 0, necesitamos extender hacia abajo
    if zero_position > 0:
        # Calcular el rango inferior necesario para los otros ejes
        max_prec_range = max_prec * 1.1
        max_rad_range = max_rad * 1.1
        
        # El mínimo de los otros ejes debe ser negativo para alinear el 0
        min_prec_range = -max_prec_range * zero_position / (1 - zero_position) if zero_position < 1 else 0
        min_rad_range = -max_rad_range * zero_position / (1 - zero_position) if zero_position < 1 else 0
    else:
        min_prec_range = 0
        min_rad_range = 0
        max_prec_range = max_prec * 1.1
        max_rad_range = max_rad * 1.1

    # Crear gráfico con múltiples ejes Y usando Plotly
    from plotly.subplots import make_subplots
    
    fig_combined = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Línea de Temperatura (eje Y izquierdo) - Rojo
    fig_combined.add_trace(
        go.Scatter(
            x=combined_weather['Fecha'],
            y=combined_weather['Temperatura (°C)'],
            name='Temperatura (°C)',
            line=dict(color='#EF4444', width=2.5, shape='spline'),
            mode='lines',
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ),
        secondary_y=False
    )
    
    # Línea de Precipitación (eje Y derecho) - Azul
    fig_combined.add_trace(
        go.Scatter(
            x=combined_weather['Fecha'],
            y=combined_weather['Precipitación (mm/h)'],
            name='Precipitación (mm/h)',
            line=dict(color='#3B82F6', width=2.5, shape='spline'),
            mode='lines'
        ),
        secondary_y=True
    )
    
    # Para la Radiación, creamos un tercer eje Y - Naranja
    fig_combined.add_trace(
        go.Scatter(
            x=combined_weather['Fecha'],
            y=combined_weather['Radiación (W/m²)'],
            name='Radiación (W/m²)',
            line=dict(color='#F97316', width=2.5, shape='spline'),
            mode='lines',
            yaxis='y3'
        )
    )
    
    # Configurar el layout con 3 ejes Y - todos empiezan en 0
    fig_combined.update_layout(
        title={
            'text': 'Variables Meteorológicas Combinadas',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748', 'family': 'Poppins'}
        },
        xaxis=dict(
            title='Fecha',
            titlefont=dict(color='#2d3748'),
            tickfont=dict(color='#2d3748'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            domain=[0.1, 0.85],
            type='date',
            range=[x_range_start, x_range_end] if x_range_start is not None else None,
            rangeslider=dict(visible=True, thickness=0.05)
        ),
        yaxis=dict(
            title='Temperatura (°C)',
            titlefont=dict(color='#EF4444'),
            tickfont=dict(color='#EF4444'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            side='left',
            range=[min_temp_range, max_temp_range],
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis2=dict(
            title='Precipitación (mm/h)',
            titlefont=dict(color='#3B82F6'),
            tickfont=dict(color='#3B82F6'),
            overlaying='y',
            side='right',
            position=0.85,
            range=[min_prec_range, max_prec_range],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis3=dict(
            title='Radiación (W/m²)',
            titlefont=dict(color='#F97316'),
            tickfont=dict(color='#F97316'),
            overlaying='y',
            side='right',
            position=0.95,
            range=[min_rad_range, max_rad_range],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='#2d3748')
        ),
        height=550,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        margin=dict(l=60, r=100, t=80, b=60),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)