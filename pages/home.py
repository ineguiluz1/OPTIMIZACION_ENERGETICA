import streamlit as st


def render():
    """Renderiza la página de inicio"""
    st.write("")
    st.title("⚡ Dashboard Energético — Sistema de Inversor")
    st.write("")

    # Logo centrado
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        st.image("media/dashboard_logo.png")

    st.session_state.setdefault("page", "Weather")

    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5, gap="large")

    with col1:
        if st.button("🌤️ METEOROLOGÍA", width='stretch'):
            st.session_state["page"] = "Weather"
            st.rerun()

    with col2:
        if st.button("📊 DATOS ENERGÉTICOS", width='stretch'):
            st.session_state["page"] = "Energético"
            st.rerun()

    with col3:
        if st.button("🔮 PREDICCIONES", width='stretch'):
            st.session_state["page"] = "Predicciones"
            st.rerun()

    with col4:
        if st.button("🔮 PREDICCIONES PV", width='stretch'):
            st.session_state["page"] = "Predicciones PV"
            st.rerun()

    with col5:
        if st.button("☀️ ENTRENAR PV", width='stretch'):
            st.session_state["page"] = "Entrenar PV"
            st.rerun()
