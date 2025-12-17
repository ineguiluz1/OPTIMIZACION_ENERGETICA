import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from utils import *


def render(data):
    """Renderiza la página de datos energéticos"""
    st.title("📊 Datos Energéticos")
    
    # Menú de navegación
    show_navigation_menu()
    
    # Controles de filtrado
    col_filter1, col_filter2 = st.columns([1, 1])
    
    with col_filter1:
        view_mode = st.radio(
            "Modo de visualización:",
            ["Total Histórico", "Por Día"],
            horizontal=True
        )
    
    filtered_data = data.copy()
    chart_title = "Flujo de Energía - Total Histórico"
    
    if view_mode == "Por Día":
        with col_filter2:
            # Obtener límites de fechas
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )
            
            # Filtrar datos
            filtered_data = data[data['Datetime'].dt.date == selected_date]
            chart_title = f"Flujo de Energía - {selected_date.strftime('%d/%m/%Y')}"
    
    if filtered_data.empty:
        st.warning(f"No hay datos disponibles para la fecha seleccionada.")
    else:
        sankey_fig = create_sankey_diagram(filtered_data)
        # Actualizar título del gráfico
        sankey_fig.update_layout(title_text=chart_title)
        st.plotly_chart(sankey_fig, width='stretch')

        sankey_heating_fig = create_sankey_diagram_heating_system(filtered_data)
        st.plotly_chart(sankey_heating_fig, width='stretch')
        
        sankey_pv_fig = create_sankey_diagram_pv_distribution(filtered_data)
        st.plotly_chart(sankey_pv_fig, width='stretch')

    st.divider()

    # Nueva sección: Stacked Area Chart de Fuentes de Energía
    st.subheader("📊 Desglose de Fuentes de Energía")
    st.write("")

    # Controles de visualización para stacked area chart
    col_stack1, col_stack2 = st.columns([1, 1])
    
    with col_stack1:
        stack_view_mode = st.radio(
            "Modo de visualización de fuentes:",
            ["Semanal", "Diario", "Periodo Específico"],
            horizontal=True,
            key="stack_view_mode"
        )
    
    # Preparar datos para stacked area chart
    data_stack = data.copy()
    
    if stack_view_mode == "Semanal":
        # Usar función cacheada para preparar datos semanales
        stack_data = compute_weekly_sources(data)
        date_format_stack = '%b %Y'
        tooltip_date_format_stack = '%d %b %Y'
        stack_title_suffix = " - Media Semanal"
    elif stack_view_mode == "Diario":
        # Vista diaria con granularidad de 15 minutos
        with col_stack2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_stack_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="stack_date_selector"
            )
        
        # Filtrar datos para el día seleccionado (cacheado)
        stack_data = compute_daily_stack(data, selected_stack_date)
        date_format_stack = '%H:%M'
        tooltip_date_format_stack = '%H:%M'
        stack_title_suffix = f" - {selected_stack_date.strftime('%d/%m/%Y')}"
    else:  # Periodo Específico
        with col_stack2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            date_range_stack = st.date_input(
                "Seleccionar rango (zoom inicial):",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="stack_range_selector"
            )
        
        # Cargar TODOS los datos con granularidad de 15 minutos (cacheado)
        stack_data_full = compute_stack_full(data)
        
        if isinstance(date_range_stack, tuple) and len(date_range_stack) == 2:
            stack_x_range_start = pd.to_datetime(date_range_stack[0])
            stack_x_range_end = pd.to_datetime(date_range_stack[1]) + pd.Timedelta(days=1)
            days_stack = (date_range_stack[1] - date_range_stack[0]).days
        else:
            single_date = date_range_stack if not isinstance(date_range_stack, tuple) else date_range_stack[0]
            stack_x_range_start = pd.to_datetime(single_date)
            stack_x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            days_stack = 1
        
        st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>📊 Granularidad: **15 minutos** ({days_stack} días) - Arrastra para desplazarte</span>", unsafe_allow_html=True)
        
        # Crear gráfico Plotly stacked area
        fig_stack = go.Figure()
        fig_stack.add_trace(go.Scatter(
            x=stack_data_full['Fecha'], y=stack_data_full['Consumo Directo (W)'],
            name='Consumo Directo', stackgroup='one', line=dict(color='#FF6347')
        ))
        fig_stack.add_trace(go.Scatter(
            x=stack_data_full['Fecha'], y=stack_data_full['Descarga Batería (W)'],
            name='Descarga Batería', stackgroup='one', line=dict(color='#1E90FF')
        ))
        fig_stack.add_trace(go.Scatter(
            x=stack_data_full['Fecha'], y=stack_data_full['Suministro Externo (W)'],
            name='Suministro Externo', stackgroup='one', line=dict(color='#3CB371')
        ))
        fig_stack.update_layout(
            title={'text': 'Fuentes de Energía', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
            xaxis=dict(
                title=dict(text='Fecha', font=dict(color='#2d3748')),
                range=[stack_x_range_start, stack_x_range_end],
                rangeslider=dict(visible=True, thickness=0.05),
                tickfont=dict(color='#2d3748')
            ),
            yaxis=dict(
                title=dict(text='Potencia (W)', font=dict(color='#2d3748')),
                gridcolor='rgba(200,200,200,0.3)',
                tickfont=dict(color='#2d3748')
            ),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#2d3748')),
            height=500, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=60, r=20, t=80, b=80), hovermode='x unified'
        )
        st.plotly_chart(fig_stack, width='stretch')
        
        # Marcar que usamos Plotly
        stack_view_mode_plotly = True
    
    # Solo mostrar Altair si no es Periodo Específico
    if stack_view_mode != "Periodo Específico":
        # Crear stacked area chart con Altair
        stacked_chart = alt.Chart(stack_data).mark_area(
        opacity=0.8
    ).encode(
        x=alt.X('Fecha:T', 
                title='Fecha' if stack_view_mode == 'Semanal' else 'Hora',
                axis=alt.Axis(format=date_format_stack, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
        y=alt.Y('Potencia (W):Q', 
                title='Potencia (W)',
                axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
        color=alt.Color('Fuente:N',
                        scale=alt.Scale(
                            domain=['Consumo Directo (W)', 'Descarga Batería (W)', 'Suministro Externo (W)'],
                            range=['#FF6347', '#1E90FF', '#3CB371']  # Tomato, DodgerBlue, MediumSeaGreen
                        ),
                        legend=alt.Legend(title='Fuente de Energía', orient='top')),
        tooltip=[
            alt.Tooltip('Fecha:T', 
                        title='Semana' if stack_view_mode == 'Semanal' else 'Hora',
                        format=tooltip_date_format_stack),
            alt.Tooltip('Fuente:N', title='Fuente'),
            alt.Tooltip('Potencia (W):Q', format='.2f', title='Potencia (W)')
        ]
    ).properties(
            height=400,
            title=alt.TitleParams(text=f'Fuentes de Energía{stack_title_suffix}', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).configure_legend(
            labelColor='#2d3748',
            titleColor='#2d3748'
        ).interactive()
        
        st.altair_chart(stacked_chart, width='stretch')

    st.divider()

    st.subheader("📈 Evolución del Consumo (2024 - 2025)")
    st.write("")

    # Controles de visualización para gráficos de consumo
    col_view1, col_view2 = st.columns([1, 1])
    
    with col_view1:
        consumption_view_mode = st.radio(
            "Modo de visualización de consumo:",
            ["Semanal", "Diario", "Periodo Específico"],
            horizontal=True,
            key="consumption_view_mode"
        )
    
    # Preparar datos para gráficos de consumo
    data_hist = data.copy()
    
    if consumption_view_mode == "Semanal":
        # Vista semanal (comportamiento actual) - cacheada
        weekly_consumption = compute_weekly_consumption(data)
        consumption_data = weekly_consumption
        date_format = '%b %Y'
        tooltip_date_format = '%d %b %Y'
        chart_title_suffix = " - Media Semanal"
    elif consumption_view_mode == "Diario":
        # Vista diaria con granularidad de 15 minutos
        with col_view2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            selected_consumption_date = st.date_input(
                "Seleccionar día:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="consumption_date_selector"
            )
        
        # Filtrar datos para el día seleccionado (cacheado)
        consumption_data = compute_daily_consumption(data, selected_consumption_date)
        date_format = '%H:%M'
        tooltip_date_format = '%H:%M'
        chart_title_suffix = f" - {selected_consumption_date.strftime('%d/%m/%Y')}"
    else:  # Periodo Específico
        with col_view2:
            min_date = data['Datetime'].min().date()
            max_date = data['Datetime'].max().date()
            
            date_range = st.date_input(
                "Seleccionar rango (zoom inicial):",
                value=(min_date, min_date + pd.Timedelta(days=7)),
                min_value=min_date,
                max_value=max_date,
                key="consumption_range_selector"
            )
        
        # Cargar TODOS los datos con granularidad de 15 minutos (cacheado)
        consumption_data_full = compute_consumption_full(data)
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            cons_x_range_start = pd.to_datetime(date_range[0])
            cons_x_range_end = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
            days_cons = (date_range[1] - date_range[0]).days
        else:
            single_date = date_range if not isinstance(date_range, tuple) else date_range[0]
            cons_x_range_start = pd.to_datetime(single_date)
            cons_x_range_end = pd.to_datetime(single_date) + pd.Timedelta(days=1)
            days_cons = 1
        
        st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>📊 Granularidad: **15 minutos** ({days_cons} días) - Arrastra para desplazarte</span>", unsafe_allow_html=True)
        
        # Crear gráficos Plotly
        cols_plotly_cons = st.columns(2, gap='large')
        
        with cols_plotly_cons[0]:
            fig_cons_total = go.Figure()
            fig_cons_total.add_trace(go.Scatter(
                x=consumption_data_full['Fecha'], y=consumption_data_full['Consumo Total (W)'],
                mode='lines', name='Consumo Total', line=dict(color='#805AD5', width=2),
                fill='tozeroy', fillcolor='rgba(128, 90, 213, 0.1)'
            ))
            fig_cons_total.update_layout(
                title={'text': 'Consumo Total', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(
                    title=dict(text='Fecha', font=dict(color='#2d3748')),
                    range=[cons_x_range_start, cons_x_range_end],
                    rangeslider=dict(visible=True, thickness=0.05),
                    tickfont=dict(color='#2d3748')
                ),
                yaxis=dict(
                    title=dict(text='Consumo Total (W)', font=dict(color='#2d3748')),
                    gridcolor='rgba(200,200,200,0.3)',
                    tickfont=dict(color='#2d3748')
                ),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_cons_total, width='stretch')
        
        with cols_plotly_cons[1]:
            fig_cons_heating = go.Figure()
            fig_cons_heating.add_trace(go.Scatter(
                x=consumption_data_full['Fecha'], y=consumption_data_full['Calefacción (W)'],
                mode='lines', name='Calefacción', line=dict(color='#E53E3E', width=2),
                fill='tozeroy', fillcolor='rgba(229, 62, 62, 0.1)'
            ))
            fig_cons_heating.update_layout(
                title={'text': 'Sistema de Calefacción', 'x': 0.5, 'font': {'size': 18, 'color': '#2d3748'}},
                xaxis=dict(
                    title=dict(text='Fecha', font=dict(color='#2d3748')),
                    range=[cons_x_range_start, cons_x_range_end],
                    rangeslider=dict(visible=True, thickness=0.05),
                    tickfont=dict(color='#2d3748')
                ),
                yaxis=dict(
                    title=dict(text='Calefacción (W)', font=dict(color='#2d3748')),
                    gridcolor='rgba(200,200,200,0.3)',
                    tickfont=dict(color='#2d3748')
                ),
                height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=20, t=60, b=80)
            )
            st.plotly_chart(fig_cons_heating, width='stretch')
    
    # Solo mostrar Altair si no es Periodo Específico
    if consumption_view_mode != "Periodo Específico":
        cols = st.columns(2, gap='large')

        with cols[0]:
            chart_total = alt.Chart(consumption_data).mark_area(
                line={'color': '#805AD5'},  # Púrpura
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#805AD5', offset=0),
                        alt.GradientStop(color='rgba(128,90,213,0.1)', offset=1)
                    ],
                    x1=0, x2=0, y1=0, y2=1
                )
            ).encode(
                x=alt.X('Fecha:T', title='Fecha' if consumption_view_mode == 'Semanal' else 'Hora', 
                        axis=alt.Axis(format=date_format, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                y=alt.Y('Consumo Total (W):Q', title='Consumo Total (W)', 
                        axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                tooltip=[
                    alt.Tooltip('Fecha:T', title='Semana' if consumption_view_mode == 'Semanal' else 'Hora', 
                                format=tooltip_date_format),
                    alt.Tooltip('Consumo Total (W):Q', format='.2f', title='Consumo (W)')
                ]
            ).properties(
                height=400,
                title=alt.TitleParams(text=f'Consumo Total{chart_title_suffix}', fontSize=18, color='#2d3748', anchor='middle')
            ).configure(
                background='white'
            ).configure_view(
                strokeWidth=0,
                fill='white'
            ).configure_axis(
                gridColor='#f7fafc',
                domainColor='#e2e8f0'
            ).interactive()
        
            st.altair_chart(chart_total, width='stretch')

        with cols[1]:
            chart_heating = alt.Chart(consumption_data).mark_area(
                line={'color': '#E53E3E'},  # Rojo para calefacción
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#E53E3E', offset=0),
                        alt.GradientStop(color='rgba(229,62,62,0.1)', offset=1)
                    ],
                    x1=0, x2=0, y1=0, y2=1
                )
            ).encode(
                x=alt.X('Fecha:T', title='Fecha' if consumption_view_mode == 'Semanal' else 'Hora', 
                        axis=alt.Axis(format=date_format, labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                y=alt.Y('Calefacción (W):Q', title='Consumo Calefacción (W)', 
                        axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
                tooltip=[
                    alt.Tooltip('Fecha:T', title='Semana' if consumption_view_mode == 'Semanal' else 'Hora', 
                                format=tooltip_date_format),
                    alt.Tooltip('Calefacción (W):Q', format='.2f', title='Calefacción (W)')
                ]
            ).properties(
                height=400,
                title=alt.TitleParams(text=f'Sistema de Calefacción{chart_title_suffix}', fontSize=18, color='#2d3748', anchor='middle')
            ).configure(
                background='white'
            ).configure_view(
                strokeWidth=0,
                fill='white'
            ).configure_axis(
                gridColor='#f7fafc',
                domainColor='#e2e8f0'
            ).interactive()
        
            st.altair_chart(chart_heating, width='stretch')

    st.divider()

    # Nueva sección: Scatter Plots de Correlación
    st.subheader("🔗 Correlación Consumo vs Variables Meteorológicas")
    st.write("")

    # Selector de mes
    col_month_selector, col_month_info = st.columns([1, 2])
    
    with col_month_selector:
        month_names = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        # Obtener meses disponibles en los datos
        available_months = sorted(data['Datetime'].dt.month.unique())
        available_years = sorted(data['Datetime'].dt.year.unique())
        
        # Selector de mes (por defecto Enero)
        selected_month = st.selectbox(
            "Seleccionar mes:",
            options=available_months,
            format_func=lambda x: month_names[x],
            index=0 if 1 in available_months else 0,
            key="correlation_month_selector"
        )
    
    with col_month_info:
        # Información del mes seleccionado
        st.markdown(f"""
        <div style='background: #edf2f7; padding: 12px; border-radius: 8px; margin-top: 32px;'>
            <p style='color: #4a5568; margin: 0; font-size: 14px;'>
                📅 Mostrando datos de <b>{month_names[selected_month]}</b> - 
                Los gráficos muestran la correlación entre consumo y variables meteorológicas
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Preparar datos para scatter plots con franja horaria (cacheado)
    scatter_data_full = compute_scatter_data(data)
    
    # Filtrar datos por el mes seleccionado
    scatter_data = scatter_data_full[scatter_data_full['Datetime'].dt.month == selected_month].copy()
    
    # Mostrar contador de puntos
    st.markdown(f"<span style='color: #718096; font-size: 13px;'>Total de puntos en {month_names[selected_month]}: {len(scatter_data):,}</span>", unsafe_allow_html=True)
    st.write("")
    
    # Colores para cada franja horaria (paleta distinguible)
    time_slot_colors = [
        '#1E3A5F',  # 00-04: Azul oscuro (noche profunda)
        '#6366F1',  # 04-08: Índigo (amanecer)
        '#F59E0B',  # 08-12: Ámbar (mañana)
        '#EF4444',  # 12-16: Rojo (mediodía)
        '#F97316',  # 16-20: Naranja (tarde)
        '#8B5CF6'   # 20-24: Violeta (noche)
    ]
    
    time_slot_domain = ['00:00 - 04:00', '04:00 - 08:00', '08:00 - 12:00', 
                        '12:00 - 16:00', '16:00 - 20:00', '20:00 - 24:00']

    # Selección interactiva para filtrar por franja horaria (clickable en leyenda)
    selection1 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection2 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection3 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection4 = alt.selection_point(fields=['Franja Horaria'], bind='legend')

    # Primera fila: Consumo Total vs Temperatura y Radiación
    scatter_cols1 = st.columns(2, gap='large')

    with scatter_cols1[0]:
        scatter_temp_total = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Temperatura (°C):Q', 
                    title='Temperatura (°C)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Consumo Total (W):Q', 
                    title='Consumo Total (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                            scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                            legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection1, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Temperatura (°C):Q', format='.2f'),
                alt.Tooltip('Consumo Total (W):Q', format='.2f')
            ]
        ).add_params(
            selection1
        ).properties(
            height=400,
            title=alt.TitleParams(text='Consumo Total vs Temperatura', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).configure_legend(
            labelColor='#2d3748',
            titleColor='#2d3748'
        ).interactive()
        
        st.altair_chart(scatter_temp_total, width='stretch')

    with scatter_cols1[1]:
        scatter_rad_total = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Radiación (W/m²):Q', 
                    title='Radiación (W/m²)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Consumo Total (W):Q', 
                    title='Consumo Total (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                            scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                            legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection2, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Radiación (W/m²):Q', format='.2f'),
                alt.Tooltip('Consumo Total (W):Q', format='.2f')
            ]
        ).add_params(
            selection2
        ).properties(
            height=400,
            title=alt.TitleParams(text='Consumo Total vs Radiación', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).configure_legend(
            labelColor='#2d3748',
            titleColor='#2d3748'
        ).interactive()
        
        st.altair_chart(scatter_rad_total, width='stretch')

    st.write("")

    # Segunda fila: Calefacción vs Temperatura y Radiación
    scatter_cols2 = st.columns(2, gap='large')

    with scatter_cols2[0]:
        scatter_temp_heating = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Temperatura (°C):Q', 
                    title='Temperatura (°C)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Calefacción (W):Q', 
                    title='Consumo Calefacción (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                            scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                            legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection3, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Temperatura (°C):Q', format='.2f'),
                alt.Tooltip('Calefacción (W):Q', format='.2f')
            ]
        ).add_params(
            selection3
        ).properties(
            height=400,
            title=alt.TitleParams(text='Calefacción vs Temperatura', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).configure_legend(
            labelColor='#2d3748',
            titleColor='#2d3748'
        ).interactive()
        
        st.altair_chart(scatter_temp_heating, width='stretch')

    with scatter_cols2[1]:
        scatter_rad_heating = alt.Chart(scatter_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Radiación (W/m²):Q', 
                    title='Radiación (W/m²)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Calefacción (W):Q', 
                    title='Consumo Calefacción (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                            scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                            legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection4, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Radiación (W/m²):Q', format='.2f'),
                alt.Tooltip('Calefacción (W):Q', format='.2f')
            ]
        ).add_params(
            selection4
        ).properties(
            height=400,
            title=alt.TitleParams(text='Calefacción vs Radiación', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).configure_legend(
            labelColor='#2d3748',
            titleColor='#2d3748'
        ).interactive()
        
        st.altair_chart(scatter_rad_heating, width='stretch')

    st.divider()

    # Scatter plots de Generación PV vs Variables Meteorológicas (solo cuando hay radiación)
    st.subheader("☀️ Generación Fotovoltaica vs Variables Meteorológicas")
    st.markdown("<span style='color: #718096; font-size: 14px;'>*Solo datos con radiación solar > 0*</span>", unsafe_allow_html=True)
    st.write("")

    # Selector de mes para PV
    col_month_selector_pv, col_month_info_pv = st.columns([1, 2])
    
    with col_month_selector_pv:
        # Reutilizar el diccionario de nombres de meses
        month_names_pv = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        # Obtener meses disponibles en los datos
        available_months_pv = sorted(data['Datetime'].dt.month.unique())
        
        # Selector de mes (por defecto Enero)
        selected_month_pv = st.selectbox(
            "Seleccionar mes:",
            options=available_months_pv,
            format_func=lambda x: month_names_pv[x],
            index=0 if 1 in available_months_pv else 0,
            key="pv_month_selector"
        )
    
    with col_month_info_pv:
        # Información del mes seleccionado
        st.markdown(f"""
        <div style='background: #edf2f7; padding: 12px; border-radius: 8px; margin-top: 32px;'>
            <p style='color: #4a5568; margin: 0; font-size: 14px;'>
                📅 Mostrando datos de <b>{month_names_pv[selected_month_pv]}</b> - 
                Correlación entre generación fotovoltaica y variables meteorológicas
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Filtrar datos donde hay radiación solar > 0 (cacheado)
    pv_data_full = compute_pv_data(data)
    
    # Filtrar datos por el mes seleccionado
    pv_data = pv_data_full[pv_data_full['Datetime'].dt.month == selected_month_pv].copy()
    
    # Mostrar contador de puntos
    st.markdown(f"<span style='color: #718096; font-size: 13px;'>Total de puntos en {month_names_pv[selected_month_pv]}: {len(pv_data):,}</span>", unsafe_allow_html=True)
    st.write("")

    # Selecciones interactivas para los scatter plots de PV
    selection_pv1 = alt.selection_point(fields=['Franja Horaria'], bind='legend')
    selection_pv2 = alt.selection_point(fields=['Franja Horaria'], bind='legend')

    scatter_pv_cols = st.columns(2, gap='large')

    with scatter_pv_cols[0]:
        scatter_pv_temp = alt.Chart(pv_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Temperatura (°C):Q', 
                    title='Temperatura (°C)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Generación PV (W):Q', 
                    title='Generación PV (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                            scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                            legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection_pv1, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Temperatura (°C):Q', format='.2f'),
                alt.Tooltip('Generación PV (W):Q', format='.2f')
            ]
        ).add_params(
            selection_pv1
        ).properties(
            height=400,
            title=alt.TitleParams(text='Generación PV vs Temperatura', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).configure_legend(
            labelColor='#2d3748',
            titleColor='#2d3748'
        ).interactive()
        
        st.altair_chart(scatter_pv_temp, width='stretch')

    with scatter_pv_cols[1]:
        scatter_pv_rad = alt.Chart(pv_data).mark_circle(
            size=30
        ).encode(
            x=alt.X('Radiación (W/m²):Q', 
                    title='Radiación (W/m²)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            y=alt.Y('Generación PV (W):Q', 
                    title='Generación PV (W)',
                    axis=alt.Axis(labelColor='#2d3748', titleColor='#2d3748', titlePadding=15)),
            color=alt.Color('Franja Horaria:N',
                            scale=alt.Scale(domain=time_slot_domain, range=time_slot_colors),
                            legend=alt.Legend(title='Franja Horaria (click para filtrar)', orient='right')),
            opacity=alt.condition(selection_pv2, alt.value(0.6), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('Franja Horaria:N', title='Hora'),
                alt.Tooltip('Radiación (W/m²):Q', format='.2f'),
                alt.Tooltip('Generación PV (W):Q', format='.2f')
            ]
        ).add_params(
            selection_pv2
        ).properties(
            height=400,
            title=alt.TitleParams(text='Generación PV vs Radiación', fontSize=18, color='#2d3748', anchor='middle')
        ).configure(
            background='white'
        ).configure_view(
            strokeWidth=0,
            fill='white'
        ).configure_axis(
            gridColor='#f7fafc',
            domainColor='#e2e8f0'
        ).configure_legend(
            labelColor='#2d3748',
            titleColor='#2d3748'
        ).interactive()
        
        st.altair_chart(scatter_pv_rad, width='stretch')

    st.divider()

    # Gráfico Combinado de Todas las Variables (Meteorología + Consumo)
    st.subheader("🌍 Vista Combinada - Todas las Variables")
    
    # Selector de rango de fechas (solo para zoom inicial)
    col_hist_combined1, col_hist_combined2 = st.columns([1, 2])
    
    with col_hist_combined1:
        hist_combined_range_option = st.radio(
            "Vista inicial:",
            ["Todo el periodo", "Rango personalizado"],
            horizontal=True,
            key="hist_combined_range_option"
        )
    
    # Preparar datos raw (15 minutos)
    hist_combined_raw = data[['Datetime', 'temperature', 'precipitation', 'radiation', 
                                'TotalConsumption(W)', 'HeatingSystem(W)']].copy()
    hist_combined_raw.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 'Radiación (W/m²)',
                                    'Consumo Total (W)', 'Calefacción (W)']
    
    min_date_hist = hist_combined_raw['Fecha'].min()
    max_date_hist = hist_combined_raw['Fecha'].max()
    
    # Definir rango inicial de zoom
    x_range_start_hist = None
    x_range_end_hist = None
    
    if hist_combined_range_option == "Rango personalizado":
        with col_hist_combined2:
            hist_combined_date_range = st.date_input(
                "Seleccionar rango:",
                value=(min_date_hist.date(), min_date_hist.date() + pd.Timedelta(days=7)),
                min_value=min_date_hist.date(),
                max_value=max_date_hist.date(),
                key="hist_combined_date_range"
            )
        
        if isinstance(hist_combined_date_range, tuple) and len(hist_combined_date_range) == 2:
            x_range_start_hist = pd.to_datetime(hist_combined_date_range[0])
            x_range_end_hist = pd.to_datetime(hist_combined_date_range[1]) + pd.Timedelta(days=1)
            days_selected_hist = (hist_combined_date_range[1] - hist_combined_date_range[0]).days
            
            # Usar datos con granularidad de 15 minutos para rango personalizado
            hist_combined_data = hist_combined_raw.copy()
            hist_granularity_msg = f"📊 Granularidad: **15 minutos** ({days_selected_hist} días) - Arrastra para desplazarte"
        else:
            single_date_hist = hist_combined_date_range if not isinstance(hist_combined_date_range, tuple) else hist_combined_date_range[0]
            x_range_start_hist = pd.to_datetime(single_date_hist)
            x_range_end_hist = pd.to_datetime(single_date_hist) + pd.Timedelta(days=1)
            
            # Usar datos con granularidad de 15 minutos
            hist_combined_data = hist_combined_raw.copy()
            hist_granularity_msg = "📊 Granularidad: **15 minutos** (1 día) - Arrastra para desplazarte"
    else:
        # Todo el periodo - agregar por día para mejor visualización
        hist_combined_raw['Dia'] = hist_combined_raw['Fecha'].dt.date
        hist_combined_data = hist_combined_raw.groupby('Dia').agg({
            'Temperatura (°C)': 'mean',
            'Precipitación (mm/h)': 'mean', 
            'Radiación (W/m²)': 'mean',
            'Consumo Total (W)': 'mean',
            'Calefacción (W)': 'mean'
        }).reset_index()
        hist_combined_data.columns = ['Fecha', 'Temperatura (°C)', 'Precipitación (mm/h)', 
                                        'Radiación (W/m²)', 'Consumo Total (W)', 'Calefacción (W)']
        hist_combined_data['Fecha'] = pd.to_datetime(hist_combined_data['Fecha'])
        hist_granularity_msg = "📊 Granularidad: **Diaria** (todo el periodo)"
    
    st.markdown(f"<span style='color: #2d3748; font-size: 14px;'>{hist_granularity_msg}</span>", unsafe_allow_html=True)

    # Calcular rangos para alinear el 0 en todos los ejes
    min_temp_hist = hist_combined_data['Temperatura (°C)'].min()
    max_temp_hist = hist_combined_data['Temperatura (°C)'].max()
    max_consumption_hist = hist_combined_data['Consumo Total (W)'].max()
    max_rad_hist = hist_combined_data['Radiación (W/m²)'].max()
    
    temp_margin_hist = (max_temp_hist - min_temp_hist) * 0.1
    min_temp_range_hist = min_temp_hist - temp_margin_hist
    max_temp_range_hist = max_temp_hist + temp_margin_hist
    
    temp_range_total_hist = max_temp_range_hist - min_temp_range_hist
    zero_position_hist = abs(min_temp_range_hist) / temp_range_total_hist if temp_range_total_hist > 0 else 0
    
    if zero_position_hist > 0 and zero_position_hist < 1:
        max_consumption_range_hist = max_consumption_hist * 1.1
        max_rad_range_hist = max_rad_hist * 1.1
        min_consumption_range_hist = -max_consumption_range_hist * zero_position_hist / (1 - zero_position_hist)
        min_rad_range_hist = -max_rad_range_hist * zero_position_hist / (1 - zero_position_hist)
    else:
        min_consumption_range_hist = 0
        min_rad_range_hist = 0
        max_consumption_range_hist = max_consumption_hist * 1.1
        max_rad_range_hist = max_rad_hist * 1.1

    # Crear gráfico con 3 ejes Y
    from plotly.subplots import make_subplots
    
    fig_hist_combined = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Temperatura
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Temperatura (°C)'],
            name='Temperatura (°C)',
            line=dict(color='#EF4444', width=2.5, shape='spline'),
            mode='lines'
        ),
        secondary_y=False
    )
    
    # Consumo Total
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Consumo Total (W)'],
            name='Consumo Total (W)',
            line=dict(color='#805AD5', width=2.5, shape='spline'),
            mode='lines'
        ),
        secondary_y=True
    )
    
    # Calefacción (tercer eje)
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Calefacción (W)'],
            name='Calefacción (W)',
            line=dict(color='#38A169', width=2.5, shape='spline'),
            mode='lines',
            yaxis='y3'
        )
    )
    
    # Radiación (cuarto eje)
    fig_hist_combined.add_trace(
        go.Scatter(
            x=hist_combined_data['Fecha'],
            y=hist_combined_data['Radiación (W/m²)'],
            name='Radiación (W/m²)',
            line=dict(color='#F97316', width=2, shape='spline', dash='dot'),
            mode='lines',
            yaxis='y4'
        )
    )
    
    fig_hist_combined.update_layout(
        title={
            'text': 'Variables Combinadas: Meteorología + Consumo',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748', 'family': 'Poppins'}
        },
        xaxis=dict(
            title=dict(text='Fecha', font=dict(color='#2d3748')),
            tickfont=dict(color='#2d3748'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            domain=[0.12, 0.82],
            type='date',
            range=[x_range_start_hist, x_range_end_hist] if x_range_start_hist is not None else None,
            rangeslider=dict(visible=True, thickness=0.05)
        ),
        yaxis=dict(
            title=dict(text='Temperatura (°C)', font=dict(color='#EF4444')),
            tickfont=dict(color='#EF4444'),
            gridcolor='rgba(200, 200, 200, 0.3)',
            side='left',
            range=[min_temp_range_hist, max_temp_range_hist],
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis2=dict(
            title=dict(text='Consumo Total (W)', font=dict(color='#805AD5')),
            tickfont=dict(color='#805AD5'),
            overlaying='y',
            side='right',
            position=0.82,
            range=[min_consumption_range_hist, max_consumption_range_hist],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis3=dict(
            title=dict(text='Calefacción (W)', font=dict(color='#38A169')),
            tickfont=dict(color='#38A169'),
            overlaying='y',
            side='right',
            position=0.91,
            range=[min_consumption_range_hist, max_consumption_range_hist],
            showgrid=False,
            fixedrange=False,
            zeroline=True,
            zerolinecolor='rgba(150, 150, 150, 0.5)',
            zerolinewidth=1
        ),
        yaxis4=dict(
            title=dict(text='Radiación (W/m²)', font=dict(color='#F97316')),
            tickfont=dict(color='#F97316'),
            overlaying='y',
            side='left',
            position=0.05,
            range=[min_rad_range_hist, max_rad_range_hist],
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
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        margin=dict(l=80, r=80, t=80, b=80),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_hist_combined, width='stretch')


# ============================================================================
