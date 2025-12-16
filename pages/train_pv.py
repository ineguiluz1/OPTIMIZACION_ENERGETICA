import math
import joblib
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

from utils import show_navigation_menu


def render():
    """Pestaña para entrenar modelos de predicción fotovoltaica"""
    st.title("☀️ Entrenamiento de Modelos PV")
    show_navigation_menu()

    st.markdown(
        """
        <div style='background:#f8fafc;border:1px solid #e2e8f0;
        padding:16px;border-radius:10px;color:#2d3748;'>
        <b>Metodología de entrenamiento:</b><br>
        1. Sube un CSV con columna de <b>fecha/hora</b>, temperatura, radiación solar y generación PV<br>
        2. Los datos se resamplean a <b>nivel diario</b> (agregación diaria)<br>
        3. Se crean features cíclicas: <b>día del año y mes</b> (transformaciones sin/cos)<br>
        4. Se normalizan las variables continuas antes del entrenamiento<br>
        5. El modelo predecirá la <b>generación PV total diaria</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    model_choice = st.radio(
        "Modelo a entrenar",
        ["RandomForest", "SVM", "GradientBoost", "Ridge", "Lasso", "ElasticNet"],
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

    st.success(f"✅ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Paso 1: Seleccionar columnas necesarias
    st.markdown("#### 📅 Paso 1: Configuración de columnas")
    
    all_cols = df.columns.tolist()
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        datetime_col = st.selectbox("Columna de fecha/hora", all_cols, key="datetime_col")
    with col_cfg2:
        pv_col = st.selectbox("Columna de generación PV (W)", all_cols, key="pv_col")
    
    col_cfg3, col_cfg4 = st.columns(2)
    with col_cfg3:
        temp_col = st.selectbox("Columna de temperatura", all_cols, key="temp_col")
    with col_cfg4:
        rad_col = st.selectbox("Columna de radiación solar", all_cols, key="rad_col")
    
    # Verificar que las columnas sean diferentes
    selected_cols = [datetime_col, pv_col, temp_col, rad_col]
    if len(set(selected_cols)) != 4:
        st.error("❌ Debes seleccionar 4 columnas diferentes.")
        return
    
    # Paso 2: Procesamiento de datos
    st.markdown("#### ⚙️ Paso 2: Procesamiento de datos")
    
    try:
        # Convertir datetime
        df_proc = df[[datetime_col, temp_col, rad_col, pv_col]].copy()
        df_proc['Datetime'] = pd.to_datetime(df_proc[datetime_col])
        df_proc = df_proc.set_index('Datetime')
        
        # Renombrar columnas para estandarizar
        df_proc = df_proc.rename(columns={
            temp_col: 'temperature',
            rad_col: 'radiation',
            pv_col: 'pv_power'
        })
        
        st.success(f"✅ Datos con índice temporal: {df_proc.shape[0]} registros")
        
        # Resampleo diario
        with st.spinner("Resampleando a nivel diario..."):
            df_day = df_proc.resample('D').agg(
                temperature=pd.NamedAgg(column='temperature', aggfunc='mean'),
                pv_total=pd.NamedAgg(column='pv_power', aggfunc='sum'),
                radiation_sum=pd.NamedAgg(column='radiation', aggfunc='sum')
            )
            
            df_day['temperature'] = df_day['temperature'].round(2)
            df_day = df_day.sort_index()
            
            # Eliminar filas con NaN
            df_day = df_day.dropna()
            
        st.success(f"✅ Agregación diaria: {df_day.shape[0]} días")
        st.dataframe(df_day.head(10))
        
        # Ingeniería de características
        with st.spinner("Creando features temporales..."):
            # Características de calendario
            df_day['dayofyear'] = df_day.index.dayofyear
            df_day['month'] = df_day.index.month
            
            # Transformaciones cíclicas
            df_day['month_sin'] = np.sin(2 * np.pi * df_day['month'] / 12)
            df_day['month_cos'] = np.cos(2 * np.pi * df_day['month'] / 12)
            df_day['dayofyear_sin'] = np.sin(2 * np.pi * df_day['dayofyear'] / 365)
            df_day['dayofyear_cos'] = np.cos(2 * np.pi * df_day['dayofyear'] / 365)
            
            # Eliminar variables originales
            df_day = df_day.drop(columns=['month', 'dayofyear'])
        
        st.success("✅ Features creadas: temperature, radiation_sum, month_sin, month_cos, dayofyear_sin, dayofyear_cos")
        
        # Preparar X e y
        X = df_day.drop(columns=['pv_total'])
        y = df_day['pv_total']
        
        # Normalizar variables continuas
        scaler = StandardScaler()
        X[['temperature', 'radiation_sum']] = scaler.fit_transform(X[['temperature', 'radiation_sum']])
        
        st.info(f"📊 Datos finales: {X.shape[0]} muestras, {X.shape[1]} features")
        
        # Guardar el scaler para uso posterior
        scaler_data = {
            'mean_': scaler.mean_.tolist(),
            'scale_': scaler.scale_.tolist(),
            'features': ['temperature', 'radiation_sum']
        }
        
    except Exception as e:
        st.error(f"❌ Error procesando datos: {e}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Definir features finales
    feature_cols = X.columns.tolist()

    # Paso 3: Configuración del modelo
    st.markdown("#### 🤖 Paso 3: Configuración del modelo")
    
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
    elif model_choice == "GradientBoost":
        with col_a:
            gb_estimators = st.slider("N.º de estimadores", 50, 500, 150, step=50)
        with col_b:
            gb_lr = st.slider("Learning rate", 0.01, 0.5, 0.1, step=0.01)
    elif model_choice == "Ridge":
        with col_a:
            ridge_alpha = st.slider("Alpha (regularización)", 0.01, 100.0, 1.0, step=0.01)
        st.info("Ridge usa regularización L2 para reducir overfitting")
    elif model_choice == "Lasso":
        with col_a:
            lasso_alpha = st.slider("Alpha (regularización)", 0.01, 100.0, 1.0, step=0.01)
        st.info("Lasso usa regularización L1 y puede realizar selección de variables")
    else:  # ElasticNet
        with col_a:
            elasticnet_alpha = st.slider("Alpha (regularización)", 0.01, 100.0, 1.0, step=0.01)
        with col_b:
            elasticnet_l1_ratio = st.slider("L1 ratio", 0.0, 1.0, 0.5, step=0.01)
        st.info("ElasticNet combina regularización L1 y L2")

    if st.button("Entrenar modelo", type="primary", use_container_width=True):
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        if model_choice == "RandomForest":
            model = RandomForestRegressor(
                n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1
            )
        elif model_choice == "SVM":
            model = SVR(kernel=svm_kernel, C=svm_c, epsilon=epsilon, gamma="scale")
        elif model_choice == "GradientBoost":
            model = GradientBoostingRegressor(
                n_estimators=gb_estimators, learning_rate=gb_lr, random_state=42
            )
        elif model_choice == "Ridge":
            model = Ridge(alpha=ridge_alpha, random_state=42)
        elif model_choice == "Lasso":
            model = Lasso(alpha=lasso_alpha, random_state=42)
        else:  # ElasticNet
            model = ElasticNet(alpha=elasticnet_alpha, l1_ratio=elasticnet_l1_ratio, random_state=42)

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

        # Guardar el modelo y metadatos en el directorio models/
        models_dir = Path(__file__).parent.parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        model_filename_map = {
            "RandomForest": "pv_rf_model.pkl",
            "SVM": "pv_svm_model.pkl",
            "GradientBoost": "pv_gb_model.pkl",
            "Ridge": "pv_ridge_model.pkl",
            "Lasso": "pv_lasso_model.pkl",
            "ElasticNet": "pv_elasticnet_model.pkl",
        }
        
        import json

        model_path = models_dir / model_filename_map[model_choice]
        scaler_path = models_dir / "pv_scaler.pkl"
        metadata_path = models_dir / "pv_metadata.json"
        
        # 1. Guardar el modelo
        try:
            joblib.dump(model, model_path)
            st.success(f"✅ Modelo guardado en: `{model_path}`")
        except Exception as e:
            st.error(f"❌ Error al guardar el modelo: {e}")
            return
        
        # 2. Guardar el scaler
        try:
            joblib.dump(scaler, scaler_path)
            st.success(f"✅ Scaler guardado en: `{scaler_path}`")
        except Exception as e:
            st.warning(f"⚠️ Error al guardar el scaler: {e}")

        # 3. Guardar/Actualizar metadatos en JSON
        metadata = {}
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception:
                metadata = {}
        
        # Guardar features y detalles del procesamiento
        metadata[model_choice] = {
            'features': feature_cols,
            'scaler_params': scaler_data,
            'training_samples': X_train.shape[0],
            'test_samples': X_test.shape[0]
        }
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
            st.info(f"📋 Metadatos actualizados en `{metadata_path}`")
            st.info(f"🔧 Features: {', '.join(feature_cols)}")
            st.info(f"📈 Variables normalizadas: temperature, radiation_sum")
        except Exception as e:
            st.warning(f"⚠️ No se pudo guardar el archivo de metadatos JSON: {e}")