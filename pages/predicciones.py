import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
import sys
import importlib.util
import os
from pathlib import Path
from utils import show_navigation_menu
import base64


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
            del edificio. Sube un archivo CSV para realizar predicciones en lote.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar servicio de predicción
    @st.cache_resource
    def get_prediction_service():
        """Carga el servicio de predicción BentoML"""
        try:
            possible_paths = [
                Path(__file__).parent.parent / "service.py",
                Path.cwd() / "service.py",
                Path.cwd().parent / "service.py",
            ]
            
            service_module_path = None
            for p in possible_paths:
                resolved = p.resolve()
                if resolved.exists():
                    service_module_path = resolved
                    break
            
            if service_module_path is None:
                return None, "Archivo service.py no encontrado"
            
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
        
        model_type = st.radio(
            "Tipo de Modelo:",
            ["Time-of-Week (ToW)", "Cluster-PRED (CART)"],
            horizontal=True,
            help="ToW: 168 modelos horarios. Cluster-PRED: Clasificador CART para clusters."
        )
        
        with st.expander("ℹ️ Información del Modelo"):
            if model_type == "Time-of-Week (ToW)":
                st.write(f"**Tipo:** {service.tow_model_type}")
                st.write(f"**Número de Modelos:** {service.tow_num_models}")
            else:
                st.write(f"**Tipo:** {service.cluster_pred_model_type}")
                st.write(f"**Número de Clusters:** {service.cluster_pred_num_clusters}")
        
        st.divider()
        
        # PREDICCIÓN POR LOTES (CSV)
        st.markdown("### 📊 Predicción por Lotes")
        
        st.markdown("""
        <div style='background: white; color: #000; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 10px;'>
            <p style='margin: 0 0 8px 0;'>Sube un archivo CSV con columnas:</p>
            <ul style='margin: 0; padding-left: 18px;'>
                <li><strong>time</strong>: Fecha/hora (formato ISO, ej: 2025-11-01T00:00)</li>
                <li><strong>Temperature</strong>: Temperatura en °C</li>
                <li><strong>Solar Irradiation</strong>: Irradiación solar en W/m²</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Selecciona archivo CSV", type="csv", key="batch_upload")
        
        if uploaded_file is not None:
            # Mostrar información del archivo cargado (evita texto blanco sobre fondo blanco)
            try:
                file_name = uploaded_file.name
                file_size = getattr(uploaded_file, 'size', None)
                size_text = f"{file_size/1024:.1f} KB" if file_size else ""
            except Exception:
                file_name = "(archivo)"
                size_text = ""

            st.markdown(f"""
            <div style='background: white; color: #000; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 12px;'>
                <p style='margin: 0; font-weight: 600;'>{file_name}</p>
                <p style='margin: 0; font-size: 13px; color: #4a5568;'>{size_text}</p>
            </div>
            """, unsafe_allow_html=True)

            # Configuración de CSV
            st.markdown("#### ⚙️ Configuración del CSV")
            
            col_config1, col_config2 = st.columns(2)
            
            with col_config1:
                separator = st.selectbox(
                    "Separador CSV",
                    options=[",", ";", "\t", "|"],
                    index=0,
                    help="Carácter que separa las columnas"
                )
            
            with col_config2:
                encoding = st.selectbox(
                    "Codificación",
                    options=["utf-8", "latin-1", "iso-8859-1", "cp1252"],
                    index=0
                )
            
            st.markdown("**Nombres de Columnas**")
            col_name1, col_name2, col_name3 = st.columns(3)
            
            with col_name1:
                time_column = st.text_input("Columna Tiempo", value="time")
            with col_name2:
                temp_column = st.text_input("Columna Temperatura", value="Temperature")
            with col_name3:
                solar_column = st.text_input("Columna Irradiación", value="Solar Irradiation")
            
            try:
                # Cargar CSV
                df_batch = pd.read_csv(uploaded_file, sep=separator, encoding=encoding)
                
                st.success(f"✅ Archivo cargado: {len(df_batch)} filas, {len(df_batch.columns)} columnas")
                
                with st.expander("📋 Columnas disponibles"):
                    st.write(", ".join(df_batch.columns.tolist()))
                
                # Validar columnas
                missing_cols = []
                if time_column not in df_batch.columns:
                    missing_cols.append(time_column)
                if temp_column not in df_batch.columns:
                    missing_cols.append(temp_column)
                if solar_column not in df_batch.columns:
                    missing_cols.append(solar_column)
                
                if missing_cols:
                    st.error(f"❌ Columnas no encontradas: {', '.join(missing_cols)}")
                else:
                    # Renombrar columnas
                    df_batch = df_batch.rename(columns={
                        time_column: 'time',
                        temp_column: 'Temperature',
                        solar_column: 'Solar Irradiation'
                    })
                    
                    st.success("✅ Mapeo de columnas exitoso")
                    
                    with st.expander("📋 Vista previa (primeras 10 filas)"):
                        st.dataframe(df_batch.head(10))
                    
                    # Procesar timestamps
                    with st.spinner("Procesando timestamps..."):
                        try:
                            df_batch['datetime'] = pd.to_datetime(df_batch['time'])
                            df_batch['timestamp_week'] = df_batch['datetime'].dt.dayofweek * 24 + df_batch['datetime'].dt.hour
                            st.success("✅ Timestamps procesados")
                        except Exception as e:
                            st.error(f"❌ Error procesando timestamps: {e}")
                            st.stop()
                    
                    # Botón de predicción
                    if st.button("🚀 Ejecutar Predicción por Lotes", type="primary", width='stretch'):
                        try:
                            with st.spinner("Generando predicciones..."):
                                if model_type == "Time-of-Week (ToW)":
                                    result = service.predict_batch_tow(
                                        df_batch['timestamp_week'].values.tolist(),
                                        df_batch['Temperature'].values.tolist(),
                                        df_batch['Solar Irradiation'].values.tolist()
                                    )
                                    predictions = np.array(result["predictions"])
                                else:  # Cluster-PRED
                                    predictions = []
                                    cluster_predictions = []
                                    
                                    for idx, row in df_batch.iterrows():
                                        result = service.predict_cluster_pred(
                                            row['datetime'].strftime("%Y-%m-%d %H:%M:%S"),
                                            row['Temperature'],
                                            row['Solar Irradiation']
                                        )
                                        predictions.append(result["power_kw"])
                                        cluster_predictions.append(result["cluster_hour"])
                                    
                                    predictions = np.array(predictions)
                                    df_batch['predicted_cluster'] = cluster_predictions
                                
                                # Añadir predicciones (en W)
                                df_batch['predicted_power_w'] = predictions
                                df_batch['predicted_power_kw'] = predictions / 1000
                                
                                st.success(f"✅ Predicciones completadas: {len(predictions)} puntos procesados")
                                
                                # Estadísticas
                                st.markdown("#### 📈 Estadísticas de Predicción")
                                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                                
                                with col_stat1:
                                    st.metric("Media", f"{predictions.mean():.0f} W")
                                with col_stat2:
                                    st.metric("Desv. Est.", f"{predictions.std():.0f} W")
                                with col_stat3:
                                    st.metric("Mínimo", f"{predictions.min():.0f} W")
                                with col_stat4:
                                    st.metric("Máximo", f"{predictions.max():.0f} W")
                                
                                # Visualizaciones
                                st.markdown("#### 📊 Visualización de Resultados")
                                
                                # Gráfico 1: Potencia Predicha en el Tiempo
                                chart_power = alt.Chart(df_batch).mark_line(
                                    color='#805AD5',
                                    strokeWidth=2
                                ).encode(
                                    x=alt.X('datetime:T', 
                                            title='Tiempo',
                                            axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                    y=alt.Y('predicted_power_w:Q', 
                                            title='Potencia (W)',
                                            axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                    tooltip=[
                                        alt.Tooltip('datetime:T', title='Tiempo', format='%Y-%m-%d %H:%M'),
                                        alt.Tooltip('predicted_power_w:Q', title='Potencia (W)', format=',.0f'),
                                        alt.Tooltip('predicted_power_kw:Q', title='Potencia (kW)', format='.2f')
                                    ]
                                ).properties(
                                    title=alt.TitleParams(text='Carga Térmica Predicha en el Tiempo', fontSize=18, color='#2d3748', anchor='middle'),
                                    height=300
                                ).configure(
                                    background='white'
                                ).configure_view(
                                    strokeWidth=0,
                                    fill='white'
                                ).configure_axis(
                                    gridColor='#f7fafc',
                                    domainColor='#e2e8f0'
                                ).interactive()
                                
                                st.altair_chart(chart_power, width='stretch')
                                
                                # Gráfico 2: Temperatura
                                chart_temp = alt.Chart(df_batch).mark_line(
                                    color='#EF4444',
                                    strokeWidth=2
                                ).encode(
                                    x=alt.X('datetime:T', 
                                            title='Tiempo',
                                            axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                    y=alt.Y('Temperature:Q', 
                                            title='Temperatura (°C)',
                                            axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                    tooltip=[
                                        alt.Tooltip('datetime:T', title='Tiempo', format='%Y-%m-%d %H:%M'),
                                        alt.Tooltip('Temperature:Q', title='Temperatura', format='.1f')
                                    ]
                                ).properties(
                                    title=alt.TitleParams(text='Temperatura en el Tiempo', fontSize=18, color='#2d3748', anchor='middle'),
                                    height=250
                                ).configure(
                                    background='white'
                                ).configure_view(
                                    strokeWidth=0,
                                    fill='white'
                                ).configure_axis(
                                    gridColor='#f7fafc',
                                    domainColor='#e2e8f0'
                                ).interactive()
                                
                                st.altair_chart(chart_temp, width='stretch')
                                
                                # Gráfico 3: Irradiación Solar
                                chart_solar = alt.Chart(df_batch).mark_line(
                                    color='#F59E0B',
                                    strokeWidth=2
                                ).encode(
                                    x=alt.X('datetime:T', 
                                            title='Tiempo',
                                            axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                    y=alt.Y('Solar Irradiation:Q', 
                                            title='Irradiación Solar (W/m²)',
                                            axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                    tooltip=[
                                        alt.Tooltip('datetime:T', title='Tiempo', format='%Y-%m-%d %H:%M'),
                                        alt.Tooltip('Solar Irradiation:Q', title='Irradiación', format='.1f')
                                    ]
                                ).properties(
                                    title=alt.TitleParams(text='Irradiación Solar en el Tiempo', fontSize=18, color='#2d3748', anchor='middle'),
                                    height=250
                                ).configure(
                                    background='white'
                                ).configure_view(
                                    strokeWidth=0,
                                    fill='white'
                                ).configure_axis(
                                    gridColor='#f7fafc',
                                    domainColor='#e2e8f0'
                                ).interactive()
                                
                                st.altair_chart(chart_solar, width='stretch')
                                
                                # Scatter plots
                                st.markdown("#### 🔬 Relaciones entre Variables")
                                
                                col_scatter1, col_scatter2 = st.columns(2)
                                
                                with col_scatter1:
                                    scatter_temp = alt.Chart(df_batch).mark_circle(
                                        size=60,
                                        opacity=0.6,
                                        color='#EF4444'
                                    ).encode(
                                        x=alt.X('Temperature:Q', 
                                                title='Temperatura (°C)',
                                                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                        y=alt.Y('predicted_power_w:Q', 
                                                title='Potencia Predicha (W)',
                                                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                        tooltip=[
                                            alt.Tooltip('Temperature:Q', title='Temperatura', format='.1f'),
                                            alt.Tooltip('predicted_power_w:Q', title='Potencia (W)', format=',.0f'),
                                            alt.Tooltip('datetime:T', title='Tiempo', format='%Y-%m-%d %H:%M')
                                        ]
                                    ).properties(
                                        title=alt.TitleParams(text='Potencia vs Temperatura', fontSize=18, color='#2d3748', anchor='middle'),
                                        height=350
                                    ).configure(
                                        background='white'
                                    ).configure_view(
                                        strokeWidth=0,
                                        fill='white'
                                    ).configure_axis(
                                        gridColor='#f7fafc',
                                        domainColor='#e2e8f0'
                                    ).interactive()
                                    
                                    st.altair_chart(scatter_temp, width='stretch')
                                
                                with col_scatter2:
                                    scatter_solar = alt.Chart(df_batch).mark_circle(
                                        size=60,
                                        opacity=0.6,
                                        color='#F59E0B'
                                    ).encode(
                                        x=alt.X('Solar Irradiation:Q', 
                                                title='Irradiación Solar (W/m²)',
                                                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                        y=alt.Y('predicted_power_w:Q', 
                                                title='Potencia Predicha (W)',
                                                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                        tooltip=[
                                            alt.Tooltip('Solar Irradiation:Q', title='Irradiación', format='.1f'),
                                            alt.Tooltip('predicted_power_w:Q', title='Potencia (W)', format=',.0f'),
                                            alt.Tooltip('datetime:T', title='Tiempo', format='%Y-%m-%d %H:%M')
                                        ]
                                    ).properties(
                                        title=alt.TitleParams(text='Potencia vs Irradiación Solar', fontSize=18, color='#2d3748', anchor='middle'),
                                        height=350
                                    ).configure(
                                        background='white'
                                    ).configure_view(
                                        strokeWidth=0,
                                        fill='white'
                                    ).configure_axis(
                                        gridColor='#f7fafc',
                                        domainColor='#e2e8f0'
                                    ).interactive()
                                    
                                    st.altair_chart(scatter_solar, width='stretch')
                                
                                # Distribución de clusters (si aplica)
                                if model_type == "Cluster-PRED (CART)" and 'predicted_cluster' in df_batch.columns:
                                    st.markdown("#### 🎯 Distribución de Clusters")
                                    
                                    cluster_counts = df_batch['predicted_cluster'].value_counts().reset_index()
                                    cluster_counts.columns = ['cluster', 'count']
                                    cluster_counts = cluster_counts.sort_values('cluster')
                                    
                                    chart_clusters = alt.Chart(cluster_counts).mark_bar(
                                        color='#805AD5'
                                    ).encode(
                                        x=alt.X('cluster:O', 
                                                title='Cluster-Hora',
                                                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                        y=alt.Y('count:Q', 
                                                title='Frecuencia',
                                                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748')),
                                        tooltip=[
                                            alt.Tooltip('cluster:O', title='Cluster'),
                                            alt.Tooltip('count:Q', title='Frecuencia')
                                        ]
                                    ).properties(
                                        title=alt.TitleParams(text='Distribución de Clusters Predichos', fontSize=18, color='#2d3748', anchor='middle'),
                                        height=300
                                    ).configure(
                                        background='white'
                                    ).configure_view(
                                        strokeWidth=0,
                                        fill='white'
                                    ).configure_axis(
                                        gridColor='#f7fafc',
                                        domainColor='#e2e8f0'
                                    ).interactive()
                                    
                                    st.altair_chart(chart_clusters, width='stretch')
                                
                                # Tabla de resultados
                                st.markdown("#### 📋 Tabla de Resultados")
                                
                                display_cols = ['time', 'Temperature', 'Solar Irradiation', 
                                              'predicted_power_w', 'predicted_power_kw']
                                if 'predicted_cluster' in df_batch.columns:
                                    display_cols.insert(3, 'predicted_cluster')
                                
                                st.dataframe(df_batch[display_cols], height=300)
                                
                                # Botones de descarga
                                st.markdown("#### 💾 Descargar Resultados")
                                
                                col_download1, col_download2 = st.columns(2)
                                
                                with col_download1:
                                    csv_output = df_batch[display_cols].to_csv(index=False)
                                    # Enlace de descarga estilizado (fondo blanco, texto oscuro)
                                    try:
                                        b64 = base64.b64encode(csv_output.encode()).decode()
                                        href = f"data:text/csv;base64,{b64}"
                                        filename_dl = f"predicciones_{model_type.replace(' ', '_').lower()}.csv"
                                        html = f'<a download="{filename_dl}" href="{href}" style="background: white; color: #2d3748; padding: 8px 12px; border-radius: 8px; border: 1px solid #e2e8f0; text-decoration: none; display: inline-block;">📥 Descargar CSV (Resultados)</a>'
                                        st.markdown(html, unsafe_allow_html=True)
                                    except Exception:
                                        st.download_button(
                                            label="📥 Descargar CSV (Resultados)",
                                            data=csv_output,
                                            file_name=f"predicciones_{model_type.replace(' ', '_').lower()}.csv",
                                            mime="text/csv"
                                        )
                                
                                with col_download2:
                                    csv_full = df_batch.to_csv(index=False)
                                    try:
                                        b64_full = base64.b64encode(csv_full.encode()).decode()
                                        href_full = f"data:text/csv;base64,{b64_full}"
                                        filename_full = f"predicciones_completo_{model_type.replace(' ', '_').lower()}.csv"
                                        html_full = f'<a download="{filename_full}" href="{href_full}" style="background: white; color: #2d3748; padding: 8px 12px; border-radius: 8px; border: 1px solid #e2e8f0; text-decoration: none; display: inline-block;">📥 Descargar CSV (Completo)</a>'
                                        st.markdown(html_full, unsafe_allow_html=True)
                                    except Exception:
                                        st.download_button(
                                            label="📥 Descargar CSV (Completo)",
                                            data=csv_full,
                                            file_name=f"predicciones_completo_{model_type.replace(' ', '_').lower()}.csv",
                                            mime="text/csv"
                                        )
                        
                        except Exception as e:
                            st.error(f"❌ Error en predicción: {e}")
                            st.exception(e)
            
            except Exception as e:
                st.error(f"❌ Error leyendo CSV: {e}")
                st.exception(e)
                st.info("💡 Verifica el separador y la codificación del archivo.")
    
    else:
        st.error("❌ No se pudo inicializar el servicio de predicción.")
        
        if service_error:
            with st.expander("🔍 Ver detalles del error", expanded=True):
                st.code(service_error, language="text")
        
        st.markdown("""
        <div style='background: #fed7d7; padding: 20px; border-radius: 12px;'>
            <p style='color: #c53030; margin: 0 0 10px 0; font-weight: 600;'>Archivos requeridos:</p>
            <ul style='color: #c53030; margin: 0; padding-left: 20px;'>
                <li><code>output/data_06_Changepoint_Pars_summ_TOW2.csv</code></li>
                <li><code>output/data_09_Changepoint_Pars_summ_CLUST_PRED.csv</code></li>
                <li><code>output/data_09_cart_model.pkl</code></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

