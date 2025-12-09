import base64
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from utils import show_navigation_menu


def render():
    """Pestaña para predicciones PV usando el servicio BentoML local."""
    st.title("🔮 Predicciones PV")
    show_navigation_menu()

    st.markdown(
        """
        <div style='background:#f8fafc;border:1px solid #e2e8f0;
        padding:16px;border-radius:10px;color:#2d3748;'>
        Usa el servicio BentoML local (modelos en <code>output/</code>). Sube un CSV con
        columnas de entrada para predecir potencia PV.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cargar servicio de predicción PV
    @st.cache_resource
    def get_prediction_service():
        """Carga el servicio BentoML desde service.py"""
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
        st.info("Sube un CSV para predecir.")
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
    st.dataframe(df.head(8))

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_cols) < 2:
        st.error("Se requieren al menos dos columnas numéricas (ej: temperatura e irradiación).")
        return

    st.markdown("#### 🎯 Modelo y columnas")
    model_choice = st.radio(
        "Modelo PV",
        ["RandomForest", "GradientBoost", "SVM"],
        horizontal=True,
        key="pv_model_choice_infer",
    )

    st.markdown("#### 📥 Columnas de entrada")
    col_a, col_b = st.columns(2)
    with col_a:
        temp_col = st.selectbox("Columna Temperatura (°C)", numeric_cols, key="pv_temp_col")
    with col_b:
        irrad_col = st.selectbox("Columna Irradiación (W/m²)", numeric_cols, key="pv_irrad_col")

    time_col = st.selectbox(
        "Columna tiempo (opcional para gráfico)",
        options=["(ninguna)"] + df.columns.tolist(),
        index=0,
        key="pv_time_col",
    )

    if st.button("🚀 Ejecutar predicción PV", type="primary", use_container_width=True):
        temps = df[temp_col].to_numpy().tolist()
        irrads = df[irrad_col].to_numpy().tolist()

        with st.spinner("Prediciendo..."):
            result = service.predict_batch_pv(model_choice, temps, irrads)

        if isinstance(result, dict) and "error" in result:
            st.error(f"❌ Error del servicio: {result['error']}")
            st.info("Verifica que exista el modelo en output/pv_rf_model.pkl.")
            return

        preds = np.array(result.get("predictions", []))
        if preds.size == 0:
            st.warning("No se recibieron predicciones.")
            return

        preds = np.maximum(0.0, preds)
        df_out = df.copy()
        df_out["pv_pred_w"] = preds
        df_out["pv_pred_kw"] = preds / 1000

        st.success(f"✅ Predicciones generadas: {len(preds)} filas")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Media (W)", f"{preds.mean():,.1f}")
        col_m2.metric("Desv. Est. (W)", f"{preds.std():,.1f}")
        col_m3.metric("Mín (W)", f"{preds.min():,.1f}")
        col_m4.metric("Máx (W)", f"{preds.max():,.1f}")

        if time_col != "(ninguna)":
            try:
                df_out["datetime_pred"] = pd.to_datetime(df_out[time_col])
                chart = (
                    alt.Chart(df_out)
                    .mark_line(color="#805AD5", strokeWidth=2)
                    .encode(
                        x=alt.X("datetime_pred:T", title="Tiempo"),
                        y=alt.Y("pv_pred_w:Q", title="Potencia PV (W)"),
                        tooltip=[
                            alt.Tooltip("datetime_pred:T", title="Tiempo", format="%Y-%m-%d %H:%M"),
                            alt.Tooltip("pv_pred_w:Q", title="Potencia (W)", format=",.1f"),
                        ],
                    )
                    .properties(title="Potencia PV predicha", height=320)
                    .configure(background="white")
                    .configure_view(strokeWidth=0, fill="white")
                )
                st.altair_chart(chart, use_container_width=True)
            except Exception:
                st.warning("No se pudo graficar con la columna seleccionada.")

        st.markdown("#### 📋 Resultados")
        st.dataframe(df_out[[temp_col, irrad_col, "pv_pred_w", "pv_pred_kw"]], height=300)

        csv_out = df_out.to_csv(index=False)
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

