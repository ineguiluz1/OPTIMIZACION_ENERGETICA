import math
import joblib
import pandas as pd
import streamlit as st
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR

from utils import show_navigation_menu


def render():
    """Pestaña para entrenar modelos de predicción fotovoltaica"""
    st.title("☀️ Entrenamiento de Modelos PV")
    show_navigation_menu()

    st.markdown(
        """
        <div style='background:#f8fafc;border:1px solid #e2e8f0;
        padding:16px;border-radius:10px;color:#2d3748;'>
        Sube un CSV, elige la columna objetivo y entrena un modelo sencillo para
        potencia PV. Usa columnas numéricas como variables de entrada.
        </div>
        """,
        unsafe_allow_html=True,
    )

    model_choice = st.radio(
        "Modelo a entrenar",
        ["RandomForest", "SVM", "GradientBoost"],
        horizontal=True,
        key="pv_model_choice",
    )

    uploaded = st.file_uploader("Dataset (CSV)", type="csv", key="pv_train_csv")

    if not uploaded:
        st.info("Sube un dataset para continuar.")
        return

    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"No se pudo leer el CSV: {exc}")
        return

    if df.empty:
        st.warning("El archivo está vacío.")
        return

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_cols) < 2:
        st.error("Se necesitan al menos dos columnas numéricas para entrenar.")
        return

    st.success(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
    st.dataframe(df.head(8))

    target_col = st.selectbox("Columna objetivo (PV)", numeric_cols, key="pv_target_col")
    default_features = [c for c in numeric_cols if c != target_col]
    feature_cols = st.multiselect(
        "Variables de entrada",
        numeric_cols,
        default=default_features,
        key="pv_feature_cols",
    )

    test_size = st.slider("Proporción de test", 0.1, 0.4, 0.2, step=0.05)

    col_a, col_b = st.columns(2)
    if model_choice == "RandomForest":
        with col_a:
            n_estimators = st.slider("Árboles", 50, 500, 200, step=50)
        with col_b:
            max_depth_option = st.selectbox(
                "Profundidad máxima", ["Sin límite", 5, 10, 20, 30], index=0
            )
            max_depth = None if max_depth_option == "Sin límite" else max_depth_option
    elif model_choice == "SVM":
        with col_a:
            svm_kernel = st.selectbox("Kernel", ["rbf", "linear", "poly"])
        with col_b:
            svm_c = st.slider("C", 0.1, 10.0, 1.0, step=0.1)
        epsilon = st.slider("Epsilon", 0.01, 1.0, 0.1, step=0.01)
    else:  # GradientBoost
        with col_a:
            gb_estimators = st.slider("N.º de estimadores", 50, 500, 150, step=50)
        with col_b:
            gb_lr = st.slider("Learning rate", 0.01, 0.5, 0.1, step=0.01)

    if st.button("Entrenar modelo", type="primary"):
        if not feature_cols:
            st.error("Selecciona al menos una variable de entrada.")
            return

        X = df[feature_cols].dropna()
        y = df.loc[X.index, target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        if model_choice == "RandomForest":
            model = RandomForestRegressor(
                n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1
            )
        elif model_choice == "SVM":
            model = SVR(kernel=svm_kernel, C=svm_c, epsilon=epsilon, gamma="scale")
        else:
            model = GradientBoostingRegressor(
                n_estimators=gb_estimators, learning_rate=gb_lr, random_state=42
            )

        with st.spinner("Entrenando..."):
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

        mae = mean_absolute_error(y_test, preds)
        rmse = math.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("MAE", f"{mae:,.3f}")
        col_m2.metric("RMSE", f"{rmse:,.3f}")
        col_m3.metric("R²", f"{r2:,.3f}")

        if hasattr(model, "feature_importances_"):
            importance = (
                pd.DataFrame(
                    {"feature": feature_cols, "importancia": model.feature_importances_}
                )
                .sort_values("importancia", ascending=False)
                .reset_index(drop=True)
            )
            st.markdown("#### Importancia de variables")
            st.dataframe(importance)

        # Guardar el modelo en el directorio models/
        models_dir = Path(__file__).parent.parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        model_filename_map = {
            "RandomForest": "pv_rf_model.pkl",
            "SVM": "pv_svm_model.pkl",
            "GradientBoost": "pv_gb_model.pkl",
        }
        
        
        import json

        model_path = models_dir / model_filename_map[model_choice]
        metadata_path = models_dir / "pv_metadata.json"
        
        # 1. Guardar el modelo (binario puro)
        try:
            joblib.dump(model, model_path)
            st.success(f"✅ Modelo guardado en: `{model_path}`")
        except Exception as e:
            st.error(f"❌ Error al guardar el modelo: {e}")
            return

        # 2. Guardar/Actualizar metadatos en JSON
        metadata = {}
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception:
                metadata = {}
        
        metadata[model_choice] = feature_cols
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
            st.info(f"Metadatos actualizados en `{metadata_path}`")
            st.info(f"Variables registradas: {', '.join(feature_cols)}")
        except Exception as e:
            st.warning(f"⚠️ No se pudo guardar el archivo de metadatos JSON: {e}")