import streamlit as st
import pandas as pd

# Import pages
from pages import home, energetico, predicciones, predicciones_pv, train_pv, weather
from utils import load_data, apply_custom_css

# Configuración de página
st.set_page_config(
    page_title="Dashboard Energético",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aplicar CSS personalizado
apply_custom_css()

# Cargar datos
data = load_data()
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Calcular métricas globales
temp_min = data['temperature'].min()
temp_max = data['temperature'].max()

prec_min = data['precipitation'].loc[data['precipitation'] != 0].min()
prec_max = data['precipitation'].max()

wind_min = data['WindSpeed'].loc[data['WindSpeed'] != 0].min()
wind_max = data['WindSpeed'].max()

radiation_min = data['radiation'].loc[data['radiation'] != 0].min()
radiation_max = data['radiation'].max()

YEARS = data['Datetime'].dt.year.unique()

# Gestión de páginas
page = st.session_state.setdefault("page", "Inicio")

# Enrutamiento de páginas
if page == "Inicio":
    home.render()
elif page == "Energético":
    energetico.render(data)
elif page == "Predicciones":
    predicciones.render(data)
elif page == "Entrenar PV":
    train_pv.render()
elif page == "Predicciones PV":
    predicciones_pv.render()
elif page == "Weather":
    weather.render(data, temp_min, temp_max, prec_min, prec_max, wind_min, wind_max, radiation_min, radiation_max)
