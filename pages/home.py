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

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        if st.button("🌤️ METEOROLOGÍA", use_container_width=True):
            st.session_state["page"] = "Weather"
            st.rerun()

    with col2:
        if st.button("📊 DATOS ENERGÉTICOS", use_container_width=True):
            st.session_state["page"] = "Energético"
            st.rerun()

    with col3:
        if st.button("🔮 PREDICCIONES", use_container_width=True):
            st.session_state["page"] = "Predicciones"
            st.rerun()
