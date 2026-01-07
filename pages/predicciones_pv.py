import base64
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from utils import show_navigation_menu


def render():
    """Pestaña para predicciones PV usando el servicio BentoML local."""
    st.title("🧙‍♂️ Predicciones PV")
    show_navigation_menu()

    st.markdown(
        """
        <div style='background:#f8fafc;border:1px solid #e2e8f0;
        padding:16px;border-radius:10px;color:#2d3748;'>
        Usa el servicio BentoML local (modelos en <code>models/</code>). Sube un CSV con
        columnas de entrada para predecir potencia PV.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cargar servicio de predicción PV
    @st.cache_resource
    def get_prediction_service():
        """Carga el servicio BentoML desde service.py"""
        from pathlib import Path
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

            import importlib.util

            spec = importlib.util.spec_from_file_location("service", service_module_path)
            service_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(service_module)
            return service_module.service_instance, None
        except Exception as e:
            import traceback
            return None, f"{str(e)}\n\n{traceback.format_exc()}"

    service, service_error = get_prediction_service()

    if not service:
        st.error("❌ No se pudo inicializar el servicio de predicción PV.")
        if service_error:
            with st.expander("Ver error"):
                st.code(service_error)
        return

    st.markdown("### 📊 Dataset de predicción")

    uploaded_csv = st.file_uploader("Dataset (CSV)", type="csv", key="pv_pred_csv")
    if not uploaded_csv:
        st.info("Sube un CSV con: fecha/hora, temperatura y radiación solar.")
        return

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        sep = st.selectbox("Separador", [",", ";", "\t", "|"], index=0)
    with col_cfg2:
        enc = st.selectbox("Codificación", ["utf-8", "latin-1", "iso-8859-1", "cp1252"], index=0)

    try:
        df = pd.read_csv(uploaded_csv, sep=sep, encoding=enc)
    except Exception as exc:
        st.error(f"No se pudo leer el CSV: {exc}")
        return

    if df.empty:
        st.warning("El CSV está vacío.")
        return

    st.success(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Configurar columnas
    st.markdown("#### 📅 Configuración de columnas")
    all_cols = df.columns.tolist()
    
    col_cfg3, col_cfg4, col_cfg5 = st.columns(3)
    with col_cfg3:
        datetime_col = st.selectbox("Columna de fecha/hora", all_cols, key="datetime_col_pred")
    with col_cfg4:
        temp_col = st.selectbox("Columna de temperatura", all_cols, key="temp_col_pred")
    with col_cfg5:
        rad_col = st.selectbox("Columna de radiación solar", all_cols, key="rad_col_pred")
    
    # Verificar que las columnas sean diferentes
    selected_cols = [datetime_col, temp_col, rad_col]
    if len(set(selected_cols)) != 3:
        st.error("❌ Debes seleccionar 3 columnas diferentes.")
        return

    st.markdown("#### 🎯 Seleccionar Modelo")
    model_choice = st.radio(
        "Modelo PV",
        ["RandomForest", "GradientBoost", "SVM","Ridge","Lasso","ElasticNet"],
        horizontal=True,
        key="pv_model_choice_infer",
    )

    # Obtener features requeridas por el modelo
    model_info = service.get_pv_model_info(model_choice)
    
    if "error" in model_info:
        st.warning(f"⚠️ {model_info['error']}. Asegúrate de haber entrenado el modelo.")
        return

    if st.button("🚀 Ejecutar predicción PV", type="primary", width='stretch'):
        try:
            # Procesamiento de datos similar al entrenamiento
            df_proc = df[[datetime_col, temp_col, rad_col]].copy()
            df_proc['Datetime'] = pd.to_datetime(df_proc[datetime_col])
            df_proc = df_proc.set_index('Datetime')
            df_proc = df_proc.drop(columns=[datetime_col])
            
            # Renombrar columnas
            df_proc = df_proc.rename(columns={
                temp_col: 'temperature',
                rad_col: 'radiation'
            })
            
            # Resampleo diario
            df_day = df_proc.resample('D').agg(
                temperature=pd.NamedAgg(column='temperature', aggfunc='mean'),
                radiation_sum=pd.NamedAgg(column='radiation', aggfunc='sum')
            )
            
            df_day['temperature'] = df_day['temperature'].round(2)
            df_day = df_day.sort_index()
            df_day = df_day.dropna()
            
            # Ingeniería de características
            df_day['dayofyear'] = df_day.index.dayofyear
            df_day['month'] = df_day.index.month
            
            # Transformaciones cíclicas
            df_day['month_sin'] = np.sin(2 * np.pi * df_day['month'] / 12)
            df_day['month_cos'] = np.cos(2 * np.pi * df_day['month'] / 12)
            df_day['dayofyear_sin'] = np.sin(2 * np.pi * df_day['dayofyear'] / 365)
            df_day['dayofyear_cos'] = np.cos(2 * np.pi * df_day['dayofyear'] / 365)
            
            df_day = df_day.drop(columns=['month', 'dayofyear'])
            
            # Normalizar con el scaler guardado
            from sklearn.preprocessing import StandardScaler
            import joblib
            from pathlib import Path
            
            scaler_path = Path(__file__).parent.parent / "models" / "pv_scaler.pkl"
            if scaler_path.exists():
                scaler = joblib.load(scaler_path)
                df_day[['temperature', 'radiation_sum']] = scaler.transform(df_day[['temperature', 'radiation_sum']])
            else:
                st.warning("⚠️ Scaler no encontrado. Usando datos sin normalizar.")
            
            # Preparar matriz de entrada
            input_matrix = df_day.to_numpy().tolist()
            
        except Exception as e:
            st.error(f"❌ Error procesando datos: {e}")
            import traceback
            st.code(traceback.format_exc())
            return

        with st.spinner("Prediciendo..."):
            result = service.predict_batch_pv(model_choice, input_matrix)

        if isinstance(result, dict) and "error" in result:
            st.error(f"❌ Error del servicio: {result['error']}")
            st.info("Verifica que exista el modelo en models/. Entrena un modelo en la pestaña 'Entrenamiento de Modelos PV'.")
            return

        preds = np.array(result.get("predictions", []))
        if preds.size == 0:
            st.warning("No se recibieron predicciones.")
            return

        preds = np.maximum(0.0, preds)
        
        # Crear DataFrame de salida con fechas diarias
        df_out = df_day.copy()
        df_out["pv_pred_w"] = preds
        df_out["pv_pred_kw"] = preds / 1000
        df_out = df_out.reset_index()  # Datetime como columna

        st.success(f"✅ Predicciones generadas: {len(preds)} días")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Media diaria (W)", f"{preds.mean():,.1f}")
        col_m2.metric("Desv. Est. (W)", f"{preds.std():,.1f}")
        col_m3.metric("Mín diario (W)", f"{preds.min():,.1f}")
        col_m4.metric("Máx diario (W)", f"{preds.max():,.1f}")

        # Gráfico de predicciones
        try:
            chart = (
                alt.Chart(df_out)
                .mark_line(color="#805AD5", strokeWidth=2)
                .encode(
                    x=alt.X("Datetime:T", title="Fecha"),
                    y=alt.Y("pv_pred_w:Q", title="Generación PV Diaria (W)"),
                    tooltip=[
                        alt.Tooltip("Datetime:T", title="Fecha", format="%Y-%m-%d"),
                        alt.Tooltip("pv_pred_w:Q", title="Potencia diaria (W)", format=",.1f"),
                        alt.Tooltip("pv_pred_kw:Q", title="Potencia diaria (kW)", format=",.3f"),
                    ],
                )
                .properties(title="Generación PV Diaria Predicha", height=320)
                    .configure(background="white")
                    .configure_view(strokeWidth=0, fill="white")
                    .configure_title(color="#000000", fontSize=16, font='Poppins')
                    .configure_axis(labelColor="#000000", titleColor="#000000", grid=False)
                    .configure_legend(labelColor="#000000", titleColor="#000000")
                    .configure_header(labelColor="#000000")
                )
            st.altair_chart(chart, width='stretch')
        except Exception as e:
            st.warning(f"No se pudo graficar: {e}")

        st.markdown("#### 📋 Resultados (agregados diarios)")
        display_cols = ['Datetime', 'temperature', 'radiation_sum', 'pv_pred_w', 'pv_pred_kw']
        st.dataframe(df_out[display_cols], height=300)

        csv_out = df_out[display_cols].to_csv(index=False)
        try:
            b64 = base64.b64encode(csv_out.encode()).decode()
            href = f"data:text/csv;base64,{b64}"
            html = (
                f'<a download="predicciones_pv.csv" href="{href}" '
                "style='background: white; color: #2d3748; padding: 8px 12px; "
                "border-radius: 8px; border: 1px solid #e2e8f0; text-decoration: none;'>"
                "📥 Descargar CSV</a>"
            )
            st.markdown(html, unsafe_allow_html=True)
        except Exception:
            st.download_button(
                label="📥 Descargar CSV",
                data=csv_out,
                file_name="predicciones_pv.csv",
                mime="text/csv",
            )

