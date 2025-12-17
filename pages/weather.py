import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from utils import show_navigation_menu


def render(data, temp_min, temp_max, prec_min, prec_max, wind_min, wind_max, radiation_min, radiation_max):
    """Renderiza la página de meteorología"""
    st.title("🌤️ Datos Meteorológicos")
    
    # Menú de navegación
    show_navigation_menu()
    
    # Descripción principal
    st.markdown("<p style='color: #000000; font-size: 16px;'>Análisis de las variables meteorológicas que influyen en la generación fotovoltaica y el consumo energético del sistema.</p>", unsafe_allow_html=True)
    st.write("")
    
    # Sección de métricas
    st.markdown("### 📊 Resumen de Datos")
    st.markdown("<p style='color: #000000; font-size: 14px;'>Valores extremos registrados para temperatura, precipitación, velocidad del viento y radiación solar durante el periodo de estudio.</p>", unsafe_allow_html=True)
    
    # Controles de filtrado para estadísticas
    col_stats1, col_stats2 = st.columns([1, 2])
    
    with col_stats1:
        stats_mode = st.radio(
            "Periodo de estadísticas:",
            ["Todo el periodo", "Rango específico"],
            horizontal=True,
            key="stats_mode"
        )
    
    # Datos para calcular estadísticas
    stats_data = data.copy()
    
    if stats_mode == "Rango específico":
        with col_stats2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            stats_date_range = st.date_input(
                "Seleccionar rango:",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="stats_date_range"
            )
        
        # Filtrar datos según el rango seleccionado
        if isinstance(stats_date_range, tuple) and len(stats_date_range) == 2:
            stats_data = data[(data['Datetime'].dt.date >= stats_date_range[0]) & 
                             (data['Datetime'].dt.date <= stats_date_range[1])]
        else:
            single_date = stats_date_range if not isinstance(stats_date_range, tuple) else stats_date_range[0]
            stats_data = data[data['Datetime'].dt.date == single_date]
    
    # Calcular estadísticas sobre los datos filtrados o completos
    temp_min_display = stats_data['temperature'].min()
    temp_max_display = stats_data['temperature'].max()
    prec_min_display = stats_data['precipitation'].loc[stats_data['precipitation'] != 0].min() if (stats_data['precipitation'] != 0).any() else 0
    prec_max_display = stats_data['precipitation'].max()
    wind_min_display = stats_data['WindSpeed'].loc[stats_data['WindSpeed'] != 0].min() if (stats_data['WindSpeed'] != 0).any() else 0
    wind_max_display = stats_data['WindSpeed'].max()
    radiation_min_display = stats_data['radiation'].loc[stats_data['radiation'] != 0].min() if (stats_data['radiation'] != 0).any() else 0
    radiation_max_display = stats_data['radiation'].max()
    
    st.write("")
    
    # Temperatura
    with st.container():
        cols = st.columns(4, gap='medium')
        
        with cols[0]:
            st.metric("🌡️ Temp. Máxima", f"{temp_max_display:.2f} °C")
        
        with cols[1]:
            st.metric("❄️ Temp. Mínima", f"{temp_min_display:.2f} °C")
        
        with cols[2]:
            st.metric("💧 Precip. Máxima", f"{prec_max_display:.2f} mm/h")
        
        with cols[3]:
            st.metric("💧 Precip. Mínima", f"{prec_min_display:.2f} mm/h")

    # Viento y Radiación
    with st.container():
        cols = st.columns(4, gap='medium')
        
        with cols[0]:
            st.metric("💨 Viento Máx.", f"{wind_max_display:.2f} km/h")
        
        with cols[1]:
            st.metric("🍃 Viento Mín.", f"{wind_min_display:.2f} km/h")
        
        with cols[2]:
            st.metric("☀️ Radiación Máx.", f"{radiation_max_display:.2f} W/m²")
        
        with cols[3]:
            st.metric("🌤️ Radiación Mín.", f"{radiation_min_display:.2f} W/m²")

    st.divider()

    # Checkbox para datos raw
    raw_data = st.checkbox("📋 Mostrar Datos Crudos")

    if raw_data:
        st.dataframe(
            data[['Datetime', 'temperature', 'precipitation', 'WindSpeed', 'radiation']],
            width='stretch'
        )

    st.divider()

    # Preparar datos para gráficos
    data_copy = data.copy()
    data_copy['Year'] = data_copy['Datetime'].dt.year
    data_copy['Week'] = data_copy['Datetime'].dt.isocalendar().week
    data_copy['YearWeek'] = data_copy['Datetime'].dt.to_period('W').apply(lambda r: r.start_time)

    # Gráficos de Temperatura y Precipitación
    st.markdown("### 📈 Temperatura y Precipitación (2024 - 2025)")
    st.markdown("<p style='color: #000000; font-size: 14px;'>Evolución temporal de la temperatura ambiente y precipitación. Estas variables afectan directamente el rendimiento de los paneles solares y las necesidades de calefacción.</p>", unsafe_allow_html=True)
    st.write("")
    
    # Controles de visualización para gráficos de meteorología
    col_weather1, col_weather2 = st.columns([1, 1])
    
    with col_weather1:
        weather_view_mode = st.radio(
            "Modo de visualización de meteorología:",
            ["Semanal", "Diario", "Periodo Específico"],
            horizontal=True,
            key="weather_view_mode"
        )
    
    if weather_view_mode == "Semanal":
        # Calcular datos semanales
        weekly_temp = data_copy.groupby('YearWeek')['temperature'].mean().reset_index()
        weekly_temp.columns = ['Fecha', 'Temperatura Media (°C)']
        
        weekly_prec = data_copy.groupby('YearWeek')['precipitation'].mean().reset_index()
        weekly_prec.columns = ['Fecha', 'Precipitación Media (mm/h)']
        
        temp_data = weekly_temp
        prec_data = weekly_prec
        date_format_weather = '%b %Y'
        tooltip_date_format_weather = '%d %b %Y'
    elif weather_view_mode == "Diario":
        with col_weather2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_weather_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="weather_date_selector"
            )
            
        daily_weather = data_copy[data_copy['Datetime'].dt.date == selected_weather_date].copy()
        
        temp_data = daily_weather[['Datetime', 'temperature']].copy()
        temp_data.columns = ['Fecha', 'Temperatura Media (°C)']
        
        prec_data = daily_weather[['Datetime', 'precipitation']].copy()
        prec_data.columns = ['Fecha', 'Precipitación Media (mm/h)']
        
        date_format_weather = '%H:%M'
        tooltip_date_format_weather = '%H:%M'
    else:  # Periodo Específico
        with col_weather2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            date_range_weather = st.date_input(
                "Seleccionar rango (zoom inicial):",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="weather_range_selector"
            )
        
        # Cargar TODOS los datos con granularidad de 15 minutos
        temp_data = data_copy[['Datetime', 'temperature']].copy()
        temp_data.columns = ['Fecha', 'Temperatura Media (°C)']
        
        prec_data = data_copy[['Datetime', 'precipitation']].copy()
        prec_data.columns = ['Fecha', 'Precipitación Media (mm/h)']
        
        # Establecer rango inicial de zoom
        if isinstance(date_range_weather, tuple) and len(date_range_weather) == 2:
            weather_x_range_start = pd.to_datetime(date_range_weather[0])
            weather_x_range_end = pd.to_datetime(date_range_weather[1]) + pd.Timedelta(days=1)
            days_weather = (date_range_weather[1] - date_range_weather[0]).days
        else:
            single_date = date_range_weather if not isinstance(date_range_weather, tuple) else date_range_weather[0]
            weather_x_range_start = pd.to_datetime(single_date)
            weather_x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            days_weather = 1
        
        st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>📊 Granularidad: **15 minutos** ({days_weather} días) - Arrastra para desplazarte</span>", unsafe_allow_html=True)
        
        # Usar Plotly para gráficos interactivos con rangeslider
        cols_plotly = st.columns([1, 1], gap='large')
        
        with cols_plotly[0]:
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=temp_data['Fecha'],
                y=temp_data['Temperatura Media (°C)'],
                mode='lines',
                name='Temperatura',
                line=dict(color='#EF4444', width=2),
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.1)'
            ))
            fig_temp.update_layout(
                title={'text': '🌡️ Temperatura', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(
                    title=dict(text='Fecha', font=dict(color='#2d3748')),
                    range=[weather_x_range_start, weather_x_range_end],
                    rangeslider=dict(visible=True, thickness=0.05),
                    tickfont=dict(color='#2d3748')
                ),
                yaxis=dict(
                    title=dict(text='Temperatura (°C)', font=dict(color='#2d3748')),
                    gridcolor='rgba(200,200,200,0.3)',
                    tickfont=dict(color='#2d3748')
                ),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_temp, width='stretch')
        
        with cols_plotly[1]:
            fig_prec = go.Figure()
            fig_prec.add_trace(go.Scatter(
                x=prec_data['Fecha'],
                y=prec_data['Precipitación Media (mm/h)'],
                mode='lines',
                name='Precipitación',
                line=dict(color='#3B82F6', width=2),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            fig_prec.update_layout(
                title={'text': '💧 Precipitación', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(
                    title=dict(text='Fecha', font=dict(color='#2d3748')),
                    range=[weather_x_range_start, weather_x_range_end],
                    rangeslider=dict(visible=True, thickness=0.05),
                    tickfont=dict(color='#2d3748')
                ),
                yaxis=dict(
                    title=dict(text='Precipitación (mm/h)', font=dict(color='#2d3748')),
                    gridcolor='rgba(200,200,200,0.3)',
                    tickfont=dict(color='#2d3748')
                ),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_prec, width='stretch')
    
    # Solo mostrar Altair si no es Periodo Específico
    if weather_view_mode != "Periodo Específico":
        cols = st.columns([1, 1], gap='large')

        with cols[0]:
            chart = alt.Chart(temp_data).mark_area(
                line={'color': '#EF4444'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#EF4444', offset=0),
                        alt.GradientStop(color='rgba(239,68,68,0.1)', offset=1)
                    ],
                    x1=0, x2=0, y1=0, y2=1
                )
            ).encode(
                x=alt.X('Fecha:T', title='Fecha' if weather_view_mode == 'Semanal' else 'Hora', 
                        axis=alt.Axis(format=date_format_weather, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                y=alt.Y('Temperatura Media (°C):Q', title='Temperatura Media (°C)', 
                        axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                tooltip=[
                    alt.Tooltip('Fecha:T', title='Semana' if weather_view_mode == 'Semanal' else 'Hora', 
                                format=tooltip_date_format_weather),
                    alt.Tooltip('Temperatura Media (°C):Q', format='.2f', title='Temperatura (°C)')
                ]
            ).properties(
                height=400,
                title=alt.TitleParams(text='🌡️ Temperatura', fontSize=18, color='#2d3748', anchor='middle')
            ).configure(
                background='white'
            ).configure_view(
                strokeWidth=0,
                fill='white'
            ).configure_axis(
                gridColor='#f7fafc',
                domainColor='#e2e8f0'
            ).interactive()
        
            st.altair_chart(chart, width='stretch')

        with cols[1]:
            chart_prec = alt.Chart(prec_data).mark_area(
                line={'color': '#3B82F6'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#3B82F6', offset=0),
                        alt.GradientStop(color='rgba(59,130,246,0.1)', offset=1)
                    ],
                    x1=0, x2=0, y1=0, y2=1
                )
            ).encode(
                x=alt.X('Fecha:T', title='Fecha' if weather_view_mode == 'Semanal' else 'Hora', 
                        axis=alt.Axis(format=date_format_weather, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                y=alt.Y('Precipitación Media (mm/h):Q', title='Precipitación Media (mm/h)', 
                        axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                tooltip=[
                    alt.Tooltip('Fecha:T', title='Semana' if weather_view_mode == 'Semanal' else 'Hora', 
                                format=tooltip_date_format_weather),
                    alt.Tooltip('Precipitación Media (mm/h):Q', format='.2f', title='Precipitación (mm/h)')
                ]
            ).properties(
                height=400,
                title=alt.TitleParams(text='💧 Precipitación', fontSize=18, color='#2d3748', anchor='middle')
            ).configure(
                background='white'
            ).configure_view(
                strokeWidth=0,
                fill='white'
            ).configure_axis(
                gridColor='#f7fafc',
                domainColor='#e2e8f0'
            ).interactive()
            
            st.altair_chart(chart_prec, width='stretch')

        st.divider()
        
        # Gráfico de Radiación (solo para Semanal/Diario)
        st.markdown("### ☀️ Radiación (2024 - 2025)")
        st.markdown("<p style='color: #000000; font-size: 14px;'>Radiación solar incidente, principal factor determinante de la generación fotovoltaica. Medida en vatios por metro cuadrado (W/m²).</p>", unsafe_allow_html=True)
        st.write("")
        
        if weather_view_mode == "Semanal":
            weekly_rad = data_copy.groupby('YearWeek')['radiation'].mean().reset_index()
            weekly_rad.columns = ['Fecha', 'Radiación Media (W/m²)']
            rad_data = weekly_rad
        else:  # Diario
            daily_rad = data_copy[data_copy['Datetime'].dt.date == selected_weather_date].copy()
            rad_data = daily_rad[['Datetime', 'radiation']].copy()
            rad_data.columns = ['Fecha', 'Radiación Media (W/m²)']
        
        chart_rad = alt.Chart(rad_data).mark_area(
            line={'color': '#F97316'},
            color=alt.Gradient(
                gradient='linear',
                stops=[
                    alt.GradientStop(color='#F97316', offset=0),
                    alt.GradientStop(color='rgba(249,115,22,0.1)', offset=1)
                ],
                x1=0, x2=0, y1=0, y2=1
            )
        ).encode(
            x=alt.X('Fecha:T', title='Fecha' if weather_view_mode == 'Semanal' else 'Hora', 
                    axis=alt.Axis(format=date_format_weather, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Radiación Media (W/m²):Q', title='Radiación Media (W/m²)', 
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            tooltip=[
                alt.Tooltip('Fecha:T', title='Semana' if weather_view_mode == 'Semanal' else 'Hora', 
                            format=tooltip_date_format_weather),
                alt.Tooltip('Radiación Media (W/m²):Q', format='.2f', title='Radiación (W/m²)')
            ]
        ).properties(
            height=400,
            title=alt.TitleParams(text='☀️ Radiación Solar', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).interactive()
        
        st.altair_chart(chart_rad, width='stretch')
    
    else:
        # Gráfico de Radiación para Periodo Específico (Plotly)
        st.divider()
        st.markdown("### ☀️ Radiación (2024 - 2025)")
        st.markdown("<p style='color: #000000; font-size: 14px;'>Radiación solar incidente, principal factor determinante de la generación fotovoltaica. Medida en vatios por metro cuadrado (W/m²).</p>", unsafe_allow_html=True)
        st.write("")
        
        rad_data_full = data_copy[['Datetime', 'radiation']].copy()
        rad_data_full.columns = ['Fecha', 'Radiación (W/m²)']
        
        fig_rad = go.Figure()
        fig_rad.add_trace(go.Scatter(
            x=rad_data_full['Fecha'],
            y=rad_data_full['Radiación (W/m²)'],
            mode='lines',
            name='Radiación',
            line=dict(color='#F97316', width=2),
            fill='tozeroy',
            fillcolor='rgba(249, 115, 22, 0.1)'
        ))
        fig_rad.update_layout(
            title={'text': '☀️ Radiación Solar', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
            xaxis=dict(
                title=dict(text='Fecha', font=dict(color='#2d3748')),
                range=[weather_x_range_start, weather_x_range_end],
                rangeslider=dict(visible=True, thickness=0.05),
                tickfont=dict(color='#2d3748')
            ),
            yaxis=dict(
                title=dict(text='Radiación (W/m²)', font=dict(color='#2d3748')),
                gridcolor='rgba(200,200,200,0.3)',
                tickfont=dict(color='#2d3748')
            ),
            height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=60, r=20, t=60, b=80)
        )
        st.plotly_chart(fig_rad, width='stretch')

    st.divider()

    # Gráfico Combinado de Variables Meteorológicas
    st.markdown("### 🌍 Vista Combinada - Variables Meteorológicas")
    st.markdown("<p style='color: #000000; font-size: 14px;'>Comparación simultánea de temperatura, precipitación y radiación para identificar correlaciones y patrones climáticos que impactan en el sistema energético.</p>", unsafe_allow_html=True)
    st.write("")
    
    # Selector de rango de fechas (solo para zoom inicial)
    col_combined1, col_combined2 = st.columns([1, 2])
    
    with col_combined1:
        combined_range_option = st.radio(
            "Vista inicial:",
            ["Todo el periodo", "Rango personalizado"],
            horizontal=True,
            key="combined_range_option"
        )
    
    # Preparar datos raw (15 minutos)
    combined_weather_raw = data_copy[['Datetime', 'temperature', 'precipitation', 'radiation']].copy()
    combined_weather_raw.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 'Radiación (W/m²)']
    
    min_date_combined = combined_weather_raw['Fecha'].min()
    max_date_combined = combined_weather_raw['Fecha'].max()
    
    # Definir rango inicial de zoom
    x_range_start = None
    x_range_end = None
    
    if combined_range_option == "Rango personalizado":
        with col_combined2:
            combined_date_range = st.date_input(
                "Seleccionar rango:",
                value=(min_date_combined.date(), min_date_combined.date() + pd.Timedelta(days=7)),
                min_value=min_date_combined.date(),
                max_value=max_date_combined.date(),
                key="combined_date_range"
            )
        
        if isinstance(combined_date_range, tuple) and len(combined_date_range) == 2:
            x_range_start = pd.to_datetime(combined_date_range[0])
            x_range_end = pd.to_datetime(combined_date_range[1]) + pd.Timedelta(days=1)
            days_selected = (combined_date_range[1] - combined_date_range[0]).days
            
            # Usar datos con granularidad de 15 minutos para rango personalizado
            combined_weather = combined_weather_raw.copy()
            granularity_msg = f"📊 Granularidad: **15 minutos** ({days_selected} días) - Arrastra para desplazarte"
        else:
            single_date = combined_date_range if not isinstance(combined_date_range, tuple) else combined_date_range[0]
            x_range_start = pd.to_datetime(single_date)
            x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            
            # Usar datos con granularidad de 15 minutos
            combined_weather = combined_weather_raw.copy()
            granularity_msg = "📊 Granularidad: **15 minutos** (1 día) - Arrastra para desplazarte"
    else:
        # Todo el periodo - agregar por día para mejor visualización
        combined_weather_raw['Dia'] = combined_weather_raw['Fecha'].dt.date
        combined_weather = combined_weather_raw.groupby('Dia').agg({
            'Temperatura (°C)': 'mean',
            'Precipitación (mm/h)': 'mean', 
            'Radiación (W/m²)': 'mean'
        }).reset_index()
        combined_weather.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 'Radiación (W/m²)']
        combined_weather['Fecha'] = pd.to_datetime(combined_weather['Fecha'])
        granularity_msg = "📊 Granularidad: **Diaria** (todo el periodo)"
    
    st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>{granularity_msg}</span>", unsafe_allow_html=True)

    # Calcular rangos para alinear el 0 en todos los ejes
    min_temp = combined_weather['Temperatura (°C)'].min()
    max_temp = combined_weather['Temperatura (°C)'].max()
    max_prec = combined_weather['Precipitación (mm/h)'].max()
    max_rad = combined_weather['Radiación (W/m²)'].max()
    
    # Añadir margen del 10%
    temp_margin = (max_temp - min_temp) * 0.1
    min_temp_range = min_temp - temp_margin
    max_temp_range = max_temp + temp_margin
    
    # Calcular la posición proporcional del 0 en el eje de temperatura
    temp_range_total = max_temp_range - min_temp_range
    zero_position = abs(min_temp_range) / temp_range_total  # Proporción desde el fondo
    
    # Ajustar los otros ejes para que el 0 esté en la misma posición
    # Si zero_position es la proporción donde está el 0, necesitamos extender hacia abajo
    if zero_position > 0:
        # Calcular el rango inferior necesario para los otros ejes
        max_prec_range = max_prec * 1.1
        max_rad_range = max_rad * 1.1
        
        # El mínimo de los otros ejes debe ser negativo para alinear el 0
        min_prec_range = -max_prec_range * zero_position / (1 - zero_position) if zero_position < 1 else 0
        min_rad_range = -max_rad_range * zero_position / (1 - zero_position) if zero_position < 1 else 0
    else:
        min_prec_range = 0
        min_rad_range = 0
        max_prec_range = max_prec * 1.1
        max_rad_range = max_rad * 1.1

    # Crear gráfico con múltiples ejes Y usando Plotly
    from plotly.subplots import make_subplots
    
    fig_combined = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Línea de Temperatura (eje Y izquierdo) - Rojo
    fig_combined.add_trace(
        go.Scatter(
            x=combined_weather['Fecha'],
            y=combined_weather['Temperatura (°C)'],
            name='Temperatura (°C)',
            line=dict(color='#EF4444', width=2.5, shape='spline'),
            mode='lines',
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ),
        secondary_y=False
    )
    
    # Línea de Precipitación (eje Y derecho) - Azul
    fig_combined.add_trace(
        go.Scatter(
            x=combined_weather['Fecha'],
            y=combined_weather['Precipitación (mm/h)'],
            name='Precipitación (mm/h)',
            line=dict(color='#3B82F6', width=2.5, shape='spline'),
            mode='lines'
        ),
        secondary_y=True
    )
    
    # Para la Radiación, creamos un tercer eje Y - Naranja
    fig_combined.add_trace(
        go.Scatter(
            x=combined_weather['Fecha'],
            y=combined_weather['Radiación (W/m²)'],
            name='Radiación (W/m²)',
            line=dict(color='#F97316', width=2.5, shape='spline'),
            mode='lines',
            yaxis='y3'
        )
    )
    
    # Configurar el layout con 3 ejes Y - todos empiezan en 0
    fig_combined.update_layout(
        title={
            'text': 'Variables Meteorológicas Combinadas',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748', 'family': 'Poppins'}
        },
        xaxis=dict(
            title=dict(text='Fecha', font=dict(color='#2d3748')),
            tickfont=dict(color='#2d3748'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            domain=[0.1, 0.85],
            type='date',
            range=[x_range_start, x_range_end] if x_range_start is not None else None,
            rangeslider=dict(visible=True, thickness=0.05)
        ),
        yaxis=dict(
            title=dict(text='Temperatura (°C)', font=dict(color='#EF4444')),
            tickfont=dict(color='#EF4444'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            side='left',
            range=[min_temp_range, max_temp_range],
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis2=dict(
            title=dict(text='Precipitación (mm/h)', font=dict(color='#3B82F6')),
            tickfont=dict(color='#3B82F6'),
            overlaying='y',
            side='right',
            position=0.85,
            range=[min_prec_range, max_prec_range],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis3=dict(
            title=dict(text='Radiación (W/m²)', font=dict(color='#F97316')),
            tickfont=dict(color='#F97316'),
            overlaying='y',
            side='right',
            position=0.95,
            range=[min_rad_range, max_rad_range],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='#2d3748')
        ),
        height=550,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        margin=dict(l=60, r=100, t=80, b=60),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_combined, width='stretch')
