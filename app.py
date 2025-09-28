import streamlit as st
import json
import os
from auth import GoogleOAuth, require_auth, get_user_role
from config import ROLES, check_role_permission

st.set_page_config(
    page_title="UTEM Canvas Auth",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_user_data():
    """Load user data from JSON file"""
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def main():
    st.title("🎓 UTEM Canvas Authentication System")
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # Authentication check
    if not st.session_state.authenticated:
        st.markdown("### Acceso con Google OAuth")
        st.info("Por favor, inicia sesión con tu cuenta de Google para acceder al sistema.")
        
        # OAuth login
        oauth = GoogleOAuth()
        if st.button("🔐 Iniciar Sesión con Google", type="primary"):
            auth_url = oauth.get_auth_url()
            st.write(f"[Haz clic aquí para autenticarte]({auth_url})")
            
        # Handle OAuth callback
        query_params = st.query_params
        if 'code' in query_params:
            try:
                user_info = oauth.handle_callback(query_params['code'])
                if user_info:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.rerun()
            except Exception as e:
                st.error(f"Error en autenticación: {str(e)}")
        
        return
    
    # Main application for authenticated users
    user_info = st.session_state.user_info
    user_role = get_user_role(user_info['email'])
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown("### 👤 Información del Usuario")
        st.write(f"**Nombre:** {user_info.get('name', 'N/A')}")
        st.write(f"**Email:** {user_info.get('email', 'N/A')}")
        st.write(f"**Rol:** {user_role}")
        
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()
    
    # Main content based on role
    st.markdown(f"### Bienvenido, {user_info.get('name', 'Usuario')}")
    
    # Role-based navigation
    if user_role == 'admin':
        show_admin_panel()
    elif user_role == 'profesor':
        show_professor_panel()
    elif user_role == 'estudiante':
        show_student_panel()
    else:
        st.warning("Rol no reconocido. Contacta al administrador.")

@require_auth
def show_admin_panel():
    st.markdown("## 🛠️ Panel de Administrador")
    
    tabs = st.tabs(["Usuarios", "Configuración", "Estadísticas"])
    
    with tabs[0]:
        st.subheader("Gestión de Usuarios")
        users_data = load_user_data()
        
        if users_data:
            for email, user_data in users_data.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{user_data.get('name', 'N/A')}** ({email})")
                with col2:
                    st.write(f"Rol: {user_data.get('role', 'N/A')}")
                with col3:
                    if st.button(f"Editar", key=f"edit_{email}"):
                        st.info("Función de edición en desarrollo")
        else:
            st.info("No hay usuarios registrados")
    
    with tabs[1]:
        st.subheader("Configuración del Sistema")
        st.json(ROLES)
    
    with tabs[2]:
        st.subheader("Estadísticas de Uso")
        st.info("Estadísticas en desarrollo")

@require_auth
def show_professor_panel():
    st.markdown("## 📚 Panel de Profesor")
    
    if not check_role_permission(get_user_role(st.session_state.user_info['email']), 'manage_courses'):
        st.error("No tienes permisos para acceder a esta sección")
        return
    
    tabs = st.tabs(["Mis Cursos", "Calificaciones", "Recursos"])
    
    with tabs[0]:
        st.subheader("Gestión de Cursos")
        st.info("Interfaz de cursos en desarrollo")
    
    with tabs[1]:
        st.subheader("Calificaciones")
        st.info("Sistema de calificaciones en desarrollo")
    
    with tabs[2]:
        st.subheader("Recursos Didácticos")
        st.info("Biblioteca de recursos en desarrollo")

@require_auth
def show_student_panel():
    st.markdown("## 📖 Panel de Estudiante")
    
    if not check_role_permission(get_user_role(st.session_state.user_info['email']), 'view_courses'):
        st.error("No tienes permisos para acceder a esta sección")
        return
    
    tabs = st.tabs(["Mis Cursos", "Tareas", "Calificaciones"])
    
    with tabs[0]:
        st.subheader("Cursos Inscritos")
        st.info("Lista de cursos en desarrollo")
    
    with tabs[1]:
        st.subheader("Tareas Pendientes")
        st.info("Sistema de tareas en desarrollo")
    
    with tabs[2]:
        st.subheader("Mis Calificaciones")
        st.info("Historial de calificaciones en desarrollo")

if __name__ == "__main__":
    main()