import streamlit as st
import pandas as pd
import plotly.graph_objects as go


@st.cache_data
def load_data(path: str = "data/inversor_data_with_heating.csv"):
    df = pd.read_csv(path)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df


# =====================
# Cached data processors
# =====================
@st.cache_data
def compute_weekly_sources(df: pd.DataFrame):
    data_stack = df.copy()
    data_stack['YearWeek'] = data_stack['Datetime'].dt.to_period('W').apply(lambda r: r.start_time)
    weekly_sources = data_stack.groupby('YearWeek')[['DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].mean().reset_index()
    weekly_sources.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
    stack_data = pd.melt(
        weekly_sources,
        id_vars=['Fecha'],
        value_vars=['Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)'],
        var_name='Fuente',
        value_name='Potencia (W)'
    )
    return stack_data


@st.cache_data
def compute_daily_stack(df: pd.DataFrame, selected_date):
    daily_stack_data = df[df['Datetime'].dt.date == selected_date].copy()
    daily_stack_data = daily_stack_data[['Datetime', 'DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].copy()
    daily_stack_data.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
    stack_data = pd.melt(
        daily_stack_data,
        id_vars=['Fecha'],
        value_vars=['Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)'],
        var_name='Fuente',
        value_name='Potencia (W)'
    )
    return stack_data


@st.cache_data
def compute_stack_full(df: pd.DataFrame):
    stack_data_full = df[['Datetime', 'DirectConsumption(W)', 'ExternalEnergySupply(W)', 'BatteryDischarging(W)']].copy()
    stack_data_full.columns = ['Fecha', 'Consumo Directo (W)', 'Suministro Externo (W)', 'Descarga Batería (W)']
    return stack_data_full


@st.cache_data
def compute_weekly_consumption(df: pd.DataFrame):
    data_hist = df.copy()
    data_hist['YearWeek'] = data_hist['Datetime'].dt.to_period('W').apply(lambda r: r.start_time)
    weekly_consumption = data_hist.groupby('YearWeek')[['TotalConsumption(W)', 'HeatingSystem(W)']].mean().reset_index()
    weekly_consumption.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
    return weekly_consumption


@st.cache_data
def compute_daily_consumption(df: pd.DataFrame, selected_date):
    daily_data = df[df['Datetime'].dt.date == selected_date].copy()
    daily_data = daily_data[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
    daily_data.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
    return daily_data


@st.cache_data
def compute_consumption_full(df: pd.DataFrame):
    consumption_data_full = df[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
    consumption_data_full.columns = ['Fecha', 'Consumo Total (W)', 'Calefacción (W)']
    return consumption_data_full


@st.cache_data
def compute_scatter_data(df: pd.DataFrame):
    scatter_data = df[['Datetime', 'TotalConsumption(W)', 'HeatingSystem(W)', 'temperature', 'radiation']].copy()
    scatter_data.columns = ['Datetime', 'Consumo Total (W)', 'Calefacción (W)', 'Temperatura (°C)', 'Radiación (W/m²)']

    def get_time_slot_inner(hour):
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

    scatter_data['Franja Horaria'] = scatter_data['Datetime'].dt.hour.apply(get_time_slot_inner)
    return scatter_data


@st.cache_data
def compute_pv_data(df: pd.DataFrame):
    pv_data = df[df['radiation'] > 0][['Datetime', 'PV_PowerGeneration(W)', 'temperature', 'radiation']].copy()
    pv_data.columns = ['Datetime', 'Generación PV (W)', 'Temperatura (°C)', 'Radiación (W/m²)']

    def get_time_slot_inner(hour):
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

    pv_data['Franja Horaria'] = pv_data['Datetime'].dt.hour.apply(get_time_slot_inner)
    return pv_data


@st.cache_data
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
                "Direct PV\n(Heating)",
                "Battery\n(Heating)",
                "External Grid\n(Heating)",
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
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    
    with col1:
        if st.button("🌤️ METEOROLOGÍA", key="nav_weather", width='stretch'):
            st.session_state["page"] = "Weather"
            st.rerun()
    
    with col2:
        if st.button("📊 DATOS ENERGÉTICOS", key="nav_historico", width='stretch'):
            st.session_state["page"] = "Energético"
            st.rerun()
    
    with col3:
        if st.button("🔮 PREDICCIONES", key="nav_realtime", width='stretch'):
            st.session_state["page"] = "Predicciones"
            st.rerun()

    with col4:
        if st.button("🔮 PREDICCIONES PV", key="nav_pred_pv", width='stretch'):
            st.session_state["page"] = "Predicciones PV"
            st.rerun()

    with col5:
        if st.button("☀️ ENTRENAR PV", key="nav_train_pv", width='stretch'):
            st.session_state["page"] = "Entrenar PV"
            st.rerun()
    
    st.markdown("---")


def apply_custom_css():
    """Aplica el CSS personalizado minimalista"""
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
        
        /* Expander: fondo blanco y texto negro */
        div[data-testid="stExpander"] {
            background-color: white !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
        }
        
        div[data-testid="stExpander"] > div {
            background-color: white !important;
        }
        
        /* Header del expander */
        div[data-testid="stExpander"] summary {
            background-color: white !important;
            color: #2d3748 !important;
        }
        
        div[data-testid="stExpander"] summary:hover {
            background-color: #f7fafc !important;
        }
        
        /* Contenido del expander */
        div[data-testid="stExpander"] > div > div {
            background-color: white !important;
            color: #0f1724 !important;
        }
        
        /* Texto dentro del expander */
        div[data-testid="stExpander"] p,
        div[data-testid="stExpander"] span,
        div[data-testid="stExpander"] div {
            color: #0f1724 !important;
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
            background-color: white !important;
        }
        
        div[data-baseweb="input"]:hover {
            border-color: #805AD5 !important;
            box-shadow: 0 2px 8px rgba(128, 90, 213, 0.15) !important;
        }
        
        div[data-baseweb="input"]:focus-within {
            border-color: #805AD5 !important;
            box-shadow: 0 0 0 3px rgba(128, 90, 213, 0.1) !important;
        }
        
        /* Inputs: usar texto oscuro para tema claro (evita texto blanco sobre fondo claro) */
        input[type="date"], input[type="text"], input[type="number"], textarea {
            font-size: 14px !important;
            color: #0f1724 !important;
            background-color: white !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Selectbox: eliminar todos los fondos oscuros */
        div[data-testid="stSelectbox"] {
            background-color: transparent !important;
        }
        
        div[data-testid="stSelectbox"] > div {
            background-color: transparent !important;
        }
        
        div[data-baseweb="select"] {
            background-color: transparent !important;
            border-radius: 8px !important;
        }
        
        div[data-baseweb="select"] > div {
            background-color: white !important;
            color: #0f1724 !important;
            border: 1.5px solid #cbd5e0 !important;
            border-radius: 8px !important;
        }
        
        div[data-baseweb="select"]:hover > div {
            border-color: #805AD5 !important;
        }
        
        /* Texto dentro de selectbox */
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: #0f1724 !important;
        }
        
        /* Dropdown del selectbox */
        div[role="listbox"] {
            background-color: white !important;
        }
        
        div[role="option"] {
            background-color: white !important;
            color: #0f1724 !important;
        }
        
        div[role="option"]:hover {
            background-color: #f7fafc !important;
        }
        
        /* Text input: eliminar completamente fondos oscuros */
        div[data-testid="stTextInput"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        div[data-testid="stTextInput"] > div {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        div[data-testid="stTextInput"] > div > div {
            background-color: transparent !important;
            border: none !important;
        }
        
        div[data-testid="stTextInput"] input {
            background-color: white !important;
            color: #0f1724 !important;
            border: 1.5px solid #cbd5e0 !important;
            border-radius: 8px !important;
        }
        
        div[data-testid="stTextInput"] input:focus {
            border-color: #805AD5 !important;
            box-shadow: 0 0 0 3px rgba(128, 90, 213, 0.1) !important;
        }
        
        /* Labels de inputs y selectbox: forzar transparencia total */
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextInput"] label {
            color: #2d3748 !important;
            font-weight: 600 !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Eliminar fondos oscuros de todos los contenedores internos */
        div[data-testid="stTextInput"] *:not(input),
        div[data-testid="stSelectbox"] *:not(div[data-baseweb="select"] > div) {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* File uploader: fondo blanco y texto oscuro para visibilidad */
        div[data-testid="stFileUploader"] {
            background: white !important;
            color: #0f1724 !important;
            border-radius: 8px !important;
            padding: 8px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
        }

        /* Forzar color en el input de archivo y en los labels internos */
        div[data-testid="stFileUploader"] input[type="file"] {
            color: #0f1724 !important;
        }
        div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] p {
            color: #0f1724 !important;
        }
        
        /* Dropzone (área de drag and drop): fondo blanco y texto negro */
        div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"],
        div[data-testid="stFileUploader"] section,
        div[data-testid="stFileUploader"] > div > section {
            background-color: white !important;
            border: 2px dashed #cbd5e0 !important;
            border-radius: 8px !important;
        }
        
        /* Texto dentro del dropzone: todo en negro */
        div[data-testid="stFileUploader"] section span,
        div[data-testid="stFileUploader"] section small,
        div[data-testid="stFileUploader"] section p,
        section[data-testid="stFileUploaderDropzone"] span,
        section[data-testid="stFileUploaderDropzone"] small {
            color: #0f1724 !important;
        }
        
        /* Botón "Browse files": fondo blanco y texto negro */
        div[data-testid="stFileUploader"] button,
        section[data-testid="stFileUploaderDropzone"] button {
            background-color: white !important;
            color: #0f1724 !important;
            border: 1.5px solid #cbd5e0 !important;
            border-radius: 6px !important;
            padding: 6px 16px !important;
            font-weight: 600 !important;
        }
        
        div[data-testid="stFileUploader"] button:hover {
            background-color: #f7fafc !important;
            border-color: #805AD5 !important;
        }
        
        /* Información del archivo subido (debajo del dropzone): texto negro sobre fondo blanco */
        div[data-testid="stFileUploader"] > div > div:not(section) {
            background-color: white !important;
            color: #0f1724 !important;
        }
        
        div[data-testid="stFileUploader"] span[data-testid="stMarkdownContainer"],
        div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {
            color: #0f1724 !important;
        }
        
        /* Archivo seleccionado (nombre del archivo debajo del dropzone): texto negro visible */
        div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
        div[data-testid="stFileUploader"] div[data-testid="stFileUploaderFileName"] span,
        div[data-testid="stFileUploader"] div[role="button"] span,
        div[data-testid="stFileUploader"] li span,
        div[data-testid="stFileUploader"] ul li {
            color: #0f1724 !important;
            background-color: transparent !important;
        }
        
        /* Forzar visibilidad del texto del archivo en todos los contextos */
        div[data-testid="stFileUploader"] * {
            color: #0f1724 !important;
        }
        
        /* Excepción: mantener el icono y botón browse con sus colores */
        div[data-testid="stFileUploader"] svg,
        div[data-testid="stFileUploader"] button {
            color: initial;
        }
        
        div[data-testid="stFileUploader"] button {
            color: #0f1724 !important;
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
        
        /* Tablas Streamlit: FORZAR TEMA CLARO */
        /* Contenedor principal con fondo blanco */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e0 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        /* Todos los contenedores internos con fondo blanco */
        div[data-testid="stDataFrame"] > div,
        div[data-testid="stTable"] > div,
        div[data-testid="stDataFrame"] > div > div,
        div[data-testid="stTable"] > div > div {
            background-color: #ffffff !important;
        }
        
        /* Canvas: invertir con ajustes para lograr blanco puro */
        div[data-testid="stDataFrame"] canvas,
        div[data-testid="stTable"] canvas {
            filter: invert(1) hue-rotate(180deg) brightness(1.05) contrast(0.95) !important;
        }
        
        /* Headers de tabla - fondo gris claro y texto oscuro */
        div[data-testid="stDataFrame"] th,
        div[data-testid="stTable"] th,
        div[data-testid="stDataFrame"] thead th,
        div[data-testid="stTable"] thead th,
        .dataframe thead th,
        table thead th {
            background-color: #e2e8f0 !important;
            color: #1a202c !important;
            font-weight: 700 !important;
            border: 1px solid #cbd5e0 !important;
            padding: 8px 12px !important;
        }
        
        /* Celdas de tabla - fondo blanco y texto oscuro */
        div[data-testid="stDataFrame"] td,
        div[data-testid="stTable"] td,
        div[data-testid="stDataFrame"] tbody td,
        div[data-testid="stTable"] tbody td,
        .dataframe tbody td,
        table tbody td {
            background-color: white !important;
            color: #1a202c !important;
            border: 1px solid #e2e8f0 !important;
            padding: 8px 12px !important;
        }
        
        /* Filas de tabla */
        div[data-testid="stDataFrame"] tr,
        div[data-testid="stTable"] tr,
        .dataframe tr,
        table tr {
            background-color: white !important;
        }
        
        /* Filas alternadas con gris muy claro */
        div[data-testid="stDataFrame"] tr:nth-child(even) td,
        div[data-testid="stTable"] tr:nth-child(even) td,
        div[data-testid="stDataFrame"] tbody tr:nth-child(even) td,
        div[data-testid="stTable"] tbody tr:nth-child(even) td,
        .dataframe tbody tr:nth-child(even) td,
        table tbody tr:nth-child(even) td {
            background-color: #f7fafc !important;
        }
        
        /* Hover en filas */
        div[data-testid="stDataFrame"] tr:hover td,
        div[data-testid="stTable"] tr:hover td,
        div[data-testid="stDataFrame"] tbody tr:hover td,
        div[data-testid="stTable"] tbody tr:hover td,
        .dataframe tbody tr:hover td,
        table tbody tr:hover td {
            background-color: #edf2f7 !important;
        }
        
        /* Índice de la tabla (primera columna) */
        div[data-testid="stDataFrame"] tbody th,
        div[data-testid="stTable"] tbody th,
        .dataframe tbody th,
        table tbody th {
            background-color: #edf2f7 !important;
            color: #2d3748 !important;
            font-weight: 600 !important;
            border: 1px solid #cbd5e0 !important;
            padding: 8px 12px !important;
        }
        
        /* Contenedor de tabla */
        .dataframe-container,
        div.dataframe-container,
        div[class*="dataframe"] {
            background-color: white !important;
        }
        
        /* Para tablas con virtualización/scroll - GRID */
        div[data-testid="stDataFrame"] [role="grid"],
        div[data-testid="stTable"] [role="grid"] {
            background-color: white !important;
            border: 1px solid #cbd5e0 !important;
        }
        
        /* Filas en grid */
        div[data-testid="stDataFrame"] [role="row"],
        div[data-testid="stTable"] [role="row"] {
            background-color: white !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        
        /* Celdas en grid (gridcell) */
        div[data-testid="stDataFrame"] [role="gridcell"],
        div[data-testid="stTable"] [role="gridcell"] {
            background-color: white !important;
            color: #1a202c !important;
            border-right: 1px solid #e2e8f0 !important;
            padding: 8px 12px !important;
        }
        
        /* Headers en grids virtualizados (columnheader) */
        div[data-testid="stDataFrame"] [role="columnheader"],
        div[data-testid="stTable"] [role="columnheader"] {
            background-color: #e2e8f0 !important;
            color: #1a202c !important;
            font-weight: 700 !important;
            border-right: 1px solid #cbd5e0 !important;
            border-bottom: 2px solid #cbd5e0 !important;
            padding: 8px 12px !important;
        }
        
        /* Texto dentro de celdas y headers - asegurar visibilidad */
        div[data-testid="stDataFrame"] [role="gridcell"] *,
        div[data-testid="stTable"] [role="gridcell"] *,
        div[data-testid="stDataFrame"] [role="columnheader"] *,
        div[data-testid="stTable"] [role="columnheader"] *,
        div[data-testid="stDataFrame"] td *,
        div[data-testid="stTable"] td *,
        div[data-testid="stDataFrame"] th *,
        div[data-testid="stTable"] th * {
            color: inherit !important;
        }
        
        /* Ocultar elementos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
