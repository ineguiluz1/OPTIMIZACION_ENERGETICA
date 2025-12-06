import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import importlib.util
import os
from pathlib import Path
from utils import show_navigation_menu


def render(data):
    """Renderiza la página de predicciones"""
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
    
    @st.cache_resource
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
