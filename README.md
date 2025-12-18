# ⚡ Dashboard Energético - Sistema de Optimización

Dashboard interactivo desarrollado en Streamlit para la visualización, análisis y predicción de datos energéticos de un sistema de inversor solar con baterías.

## 📋 Descripción

Este dashboard proporciona una plataforma completa para monitorizar y analizar el rendimiento de un sistema energético solar, permitiendo:

- **Visualización de datos meteorológicos** en tiempo real
- **Análisis de flujos energéticos** (producción, consumo, almacenamiento)
- **Predicciones de carga térmica** mediante modelos de Machine Learning
- **Entrenamiento de modelos fotovoltaicos** para optimizar la producción solar
- **Predicciones de generación fotovoltaica** basadas en condiciones meteorológicas

## 🏗️ Estructura del Proyecto

```
OPTIMIZACION_ENERGETICA/
├── app.py                          # Aplicación principal
├── service.py                      # Servicio BentoML para predicciones
├── utils.py                        # Funciones auxiliares y procesamiento de datos
├── requirements.txt                # Dependencias del proyecto
├── pages/                          # Módulos del dashboard
│   ├── home.py                     # Página de inicio y navegación
│   ├── weather.py                  # Visualización meteorológica
│   ├── energetico.py              # Análisis de datos energéticos
│   ├── predicciones.py            # Predicciones de carga térmica
│   ├── train_pv.py                # Entrenamiento de modelos PV
│   └── predicciones_pv.py         # Predicciones fotovoltaicas
├── data/                           # Datos históricos del sistema
│   └── inversor_data_with_heating.csv
├── models/                         # Modelos entrenados
├── output/                         # Resultados de procesamiento
└── media/                          # Recursos multimedia
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar estructura de datos**
   
   Asegúrate de que el archivo `data/inversor_data_with_heating.csv` contiene las siguientes columnas:
   - `Datetime`: Fecha y hora de los registros
   - `temperature`: Temperatura ambiente (°C)
   - `precipitation`: Precipitación (mm)
   - `WindSpeed`: Velocidad del viento (m/s)
   - `radiation`: Radiación solar (W/m²)
   - `GridPower(W)`: Potencia de red
   - `BatteryPower(W)`: Potencia de batería
   - `PVPower(W)`: Potencia fotovoltaica
   - Y otras métricas energéticas

## 🎯 Ejecución

Para iniciar el dashboard, ejecuta:

```bash
streamlit run app.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📊 Funcionalidades por Módulo

### 🏠 Inicio (Home)

Página de bienvenida que proporciona navegación rápida a todos los módulos del dashboard mediante botones intuitivos.

**Características:**
- Logo corporativo centrado
- Navegación visual con iconos
- Acceso directo a las 5 secciones principales

---

### 🌤️ Meteorología (Weather)

Visualización completa de las condiciones meteorológicas que afectan al sistema energético.

**Características:**
- **Gráficos interactivos** de temperatura, precipitación, velocidad del viento y radiación solar
- **Filtros temporales**: Visualización por día, semana o histórico completo
- **Estadísticas descriptivas**: Valores mínimos, máximos, promedios y medianas
- **Análisis de correlación**: Relación entre variables meteorológicas
- **Gráficos de distribución**: Histogramas y box plots

**Visualizaciones disponibles:**
- Serie temporal de cada variable meteorológica
- Mapas de calor de correlaciones
- Distribuciones estadísticas
- Comparativas multianuales (si aplica)

---

### 📊 Datos Energéticos (Energético)

Análisis detallado de los flujos energéticos del sistema inversor.

**Características:**
- **Visualización de flujo energético**: 
  - Producción fotovoltaica (PV)
  - Consumo directo
  - Carga/descarga de baterías
  - Suministro de red externa
  - Excedente exportado a la red

- **Modos de visualización**:
  - Total histórico
  - Por día específico
  
- **Gráficos disponibles**:
  - Gráfico de área apilada (stacked area chart)
  - Comparativas de consumo vs generación
  - Balance energético neto
  - Eficiencia de autoconsumo
  - Estado de carga de baterías

**Métricas calculadas:**
- Porcentaje de autoconsumo
- Dependencia de la red
- Eficiencia del sistema
- Excedentes exportados
- Ahorro energético

---

### 🔮 Predicciones de Carga Térmica (Predicciones)

Módulo de predicción basado en modelos de Machine Learning para estimar la demanda de calefacción.

**Características:**
- **Modelo Changepoint**: Detecta cambios en el comportamiento térmico
- **Predicción por lotes**: Carga archivos CSV para múltiples predicciones
- **Servicio BentoML**: API de predicción lista para producción
- **Visualización de resultados**: Gráficos comparativos de predicciones

**Funcionamiento:**
1. Sube un archivo CSV con datos meteorológicos
2. El modelo analiza las condiciones
3. Predice la carga térmica necesaria
4. Muestra resultados visuales y numéricos
5. Permite descargar predicciones

**Columnas requeridas en el CSV:**
- Temperatura exterior
- Radiación solar
- Velocidad del viento
- Fecha y hora

---

### ☀️ Entrenar PV (Train PV)

Módulo para entrenar modelos de predicción de generación fotovoltaica.

**Características:**
- **Entrenamiento de modelos**: Scikit-learn, XGBoost, Random Forest
- **Validación cruzada**: Evaluación robusta del modelo
- **Optimización de hiperparámetros**: Grid Search o Random Search
- **Métricas de rendimiento**:
  - RMSE (Root Mean Square Error)
  - MAE (Mean Absolute Error)
  - R² Score
  - MAPE (Mean Absolute Percentage Error)

**Proceso de entrenamiento:**
1. Selección de features (temperatura, radiación, hora del día, etc.)
2. División de datos (train/test)
3. Entrenamiento del modelo
4. Validación y evaluación
5. Guardado del modelo entrenado

**Variables de entrada:**
- Radiación solar
- Temperatura ambiente
- Hora del día
- Mes del año
- Nubosidad (si disponible)

---

### 🧙‍♂️ Predicciones PV (Predicciones PV)

Predicción de generación fotovoltaica utilizando los modelos entrenados.

**Características:**
- **Predicciones en tiempo real**: Basadas en condiciones actuales
- **Predicciones a futuro**: Estimación de producción horaria/diaria
- **Comparativa con histórico**: Validación de predicciones
- **Visualización interactiva**: Gráficos de producción estimada vs real

**Utilidad:**
- Planificación energética
- Optimización de almacenamiento
- Gestión de carga
- Decisiones de compra/venta de energía

---

## 🛠️ Tecnologías Utilizadas

### Core
- **Streamlit**: Framework web para dashboards interactivos
- **Pandas**: Manipulación y análisis de datos
- **NumPy**: Cálculos numéricos

### Visualización
- **Plotly**: Gráficos interactivos avanzados
- **Altair**: Visualizaciones declarativas

### Machine Learning
- **Scikit-learn**: Modelos de predicción y preprocesamiento
- **Joblib**: Serialización de modelos
- **BentoML**: Servicio de modelos en producción

## 📁 Archivos de Datos

### Entrada Principal
- **`data/inversor_data_with_heating.csv`**: Dataset principal con histórico de:
  - Datos meteorológicos
  - Producción fotovoltaica
  - Consumo energético
  - Estado de baterías
  - Carga térmica

### Modelos Entrenados
- **`models/`**: Directorio con modelos de ML guardados
  - `pv_metadata.json`: Metadatos del modelo fotovoltaico
  - Modelos serializados (.pkl, .joblib)

### Outputs
- **`output/`**: Resultados de procesamiento y análisis
  - Datos formateados
  - Parámetros de changepoint
  - Asignaciones de clusters
  - Métricas de modelos
  - Matrices de confusión

## 🎨 Personalización

### CSS Personalizado
El archivo `utils.py` incluye la función `apply_custom_css()` que permite personalizar:
- Colores del tema
- Tipografía
- Espaciado
- Estilos de botones
- Diseño responsive

### Modificar Páginas
Cada módulo en `pages/` es independiente y puede modificarse sin afectar a los demás. Sigue la estructura:

```python
def render(data=None, **kwargs):
    """Renderiza la página"""
    st.title("Título de la página")
    show_navigation_menu()  # Menú de navegación
    
    # Tu código aquí
```

## 📈 Casos de Uso

1. **Monitorización en tiempo real**: Seguimiento continuo del sistema energético
2. **Análisis histórico**: Identificación de patrones y tendencias
3. **Optimización energética**: Decisiones basadas en predicciones
4. **Mantenimiento predictivo**: Detección de anomalías
5. **Reportes automáticos**: Generación de informes periódicos
6. **Planificación de carga**: Distribución óptima del consumo
