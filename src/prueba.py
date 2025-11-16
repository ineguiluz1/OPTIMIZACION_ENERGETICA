import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt

# -------------------------
# Carga de datos
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/inversor_data_with_heating.csv", parse_dates=["Datetime"])
    # Por comodidad, pasamos todo a kW
    cols_kw = [
        "DirectConsumption(W)", "BatteryDischarging(W)",
        "ExternalEnergySupply(W)", "TotalConsumption(W)",
        "GridFeedIn(W)", "BatteryCharging(W)",
        "PV_PowerGeneration(W)"
    ]
    for c in cols_kw:
        df[c.replace("(W)", "(kW)")] = df[c] / 1000.0
    return df

df = load_data()

st.set_page_config(
    page_title="Dashboard energético - Prototipo",
    layout="wide"
)

st.title("Dashboard energético de autoconsumo (prototipo)")

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

# -------------------------
# SIDEBAR – filtros globales
# -------------------------
# Logo y título
st.sidebar.image("media/logo.png")
st.sidebar.markdown("---")

# Sección 1: Filtro Temporal
st.sidebar.markdown("### 📅 Filtro Temporal")
st.sidebar.caption("Selecciona el rango de fechas para analizar")

min_date = df["Datetime"].min().date()
max_date = df["Datetime"].max().date()

date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    label_visibility="collapsed"
)

if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

# Sección 2: Granularidad de Datos
st.sidebar.markdown("### ⚙️ Granularidad de Datos")
st.sidebar.caption("Define el nivel de detalle temporal")

granularity_options = {
    "15 minutos (Original)": "15T",
    "30 minutos": "30T",
    "1 hora": "1H",
    "2 horas": "2H",
    "4 horas": "4H",
    "1 día": "1D"
}

selected_granularity = st.sidebar.selectbox(
    "Selecciona la granularidad",
    options=list(granularity_options.keys()),
    index=0,
    label_visibility="collapsed"
)

granularity_value = granularity_options[selected_granularity]

st.sidebar.markdown("---")

# Aplicar filtros
mask = (df["Datetime"].dt.date >= start_date) & (df["Datetime"].dt.date <= end_date)
df_filtered = df[mask].copy()

# Aplicar granularidad (resampleo)
if granularity_value != "15T":
    df_filtered = df_filtered.set_index("Datetime")
    
    # Definir agregaciones apropiadas para cada columna
    agg_dict = {
        'DirectConsumption(W)': 'mean',
        'BatteryDischarging(W)': 'mean',
        'ExternalEnergySupply(W)': 'mean',
        'TotalConsumption(W)': 'mean',
        'GridFeedIn(W)': 'mean',
        'BatteryCharging(W)': 'mean',
        'PV_PowerGeneration(W)': 'mean',
        'DirectConsumption(kW)': 'mean',
        'BatteryDischarging(kW)': 'mean',
        'ExternalEnergySupply(kW)': 'mean',
        'TotalConsumption(kW)': 'mean',
        'GridFeedIn(kW)': 'mean',
        'BatteryCharging(kW)': 'mean',
        'PV_PowerGeneration(kW)': 'mean',
        'temperature': 'mean',
        'radiation': 'mean'
    }
    
    df_filtered = df_filtered.resample(granularity_value).agg(agg_dict).reset_index()

# Mostrar estadísticas del filtro actual
st.sidebar.markdown("### 📈 Datos Filtrados")
st.sidebar.metric("Registros mostrados", f"{len(df_filtered):,}")
if len(df_filtered) > 0:
    days_selected = (df_filtered["Datetime"].max() - df_filtered["Datetime"].min()).days + 1
    st.sidebar.metric("Días seleccionados", days_selected)

# -------------------------
# TABS principales
# -------------------------
tab1, tab2, tab3 = st.tabs(["Flujo instantáneo", "Consumo vs tiempo", "Previsión meteo"])

# ============================================================
# TAB 1 – Sankeys (flujo instantáneo)
# ============================================================
with tab1:
    st.subheader("Flujo energético instantáneo")

    if df_filtered.empty:
        st.warning("No hay datos en el rango seleccionado.")
    else:
        # Crear y mostrar el diagrama Sankey
        fig_sankey = create_sankey_diagram(df_filtered)
        st.plotly_chart(fig_sankey, use_container_width=True)

# ============================================================
# TAB 2 – Stacked Area Chart
# ============================================================
with tab2:
    st.subheader("Composición del consumo a lo largo del tiempo")

    if df_filtered.empty:
        st.warning("No hay datos en el rango seleccionado.")
    else:
        # Elegimos un día concreto dentro del filtro
        unique_days = sorted(df_filtered["Datetime"].dt.date.unique())
        selected_day = st.selectbox("Selecciona un día", unique_days)
        mask_day = df_filtered["Datetime"].dt.date == selected_day
        df_day = df_filtered[mask_day].copy()

        # Reordenamos por tiempo
        df_day.sort_values("Datetime", inplace=True)

        # Preparamos datos en formato 'long' para area apilada
        plot_df = pd.melt(
            df_day,
            id_vars="Datetime",
            value_vars=[
                "DirectConsumption(kW)",
                "BatteryDischarging(kW)",
                "ExternalEnergySupply(kW)"
            ],
            var_name="Fuente",
            value_name="Potencia_kW"
        )

        fig_area = px.area(
            plot_df,
            x="Datetime",
            y="Potencia_kW",
            color="Fuente",
            title=f"Composición del consumo - {selected_day}"
        )

        st.plotly_chart(fig_area, use_container_width=True)
        # fig_stacked = create_stacked_area_chart(df_day)
        # st.pyplot(fig_stacked)

# ============================================================
# TAB 3 – Previsión meteorológica
# ============================================================
with tab3:
    st.subheader("Previsión meteorológica (prototipo)")

    st.info(
        "En una versión futura, estos datos podrían venir de una API "
        "meteorológica externa. De momento usamos un ejemplo/placeholder."
    )

    # Placeholder simple: agregamos por día a partir del propio dataset
    meteo = (
        df_filtered
        .groupby(df_filtered["Datetime"].dt.date)
        .agg(
            Radiation_mean=("radiation", "mean"),
            TempMax=("temperature", "max"),
            TempMin=("temperature", "min")
        )
        .reset_index()
        .rename(columns={"Datetime": "Date"})
    )

    st.dataframe(
        meteo,
        use_container_width=True
    )
