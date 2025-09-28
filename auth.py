"""
Sistema de Autenticación para Dashboard Canvas UTEM
Autor: Sistema de Autenticación UTEM
Fecha: 2025
Descripción: Módulo principal de autenticación con Google OAuth y gestión de roles
"""

import streamlit as st
from streamlit_oauth import OAuth2Component
import json
import hashlib
import datetime
import os
from typing import Optional, Dict, List, Tuple
import time
from functools import wraps
import logging

# Configurar logging
logging.basicConfig(
    filename='auth_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AuthenticationSystem:
    """
    Sistema de autenticación principal para Dashboard UTEM
    Gestiona login con Google OAuth, roles y permisos
    """
    
    def __init__(self, users_file: str = "users.json", config_file: str = "config.json"):
        """
        Inicializa el sistema de autenticación
        
        Args:
            users_file: Archivo con base de datos de usuarios
            config_file: Archivo de configuración de roles y permisos
        """
        self.users_file = users_file
        self.config_file = config_file
        self.load_users()
        self.load_config()
        self.init_session_state()
        
        # Configuración OAuth (actualizar con tus credenciales)
        self.oauth_config = {
            'client_id': st.secrets.get("GOOGLE_CLIENT_ID", ""),
            'client_secret': st.secrets.get("GOOGLE_CLIENT_SECRET", ""),
            'redirect_uri': st.secrets.get("REDIRECT_URI", "http://localhost:8501"),
            'authorize_endpoint': "https://accounts.google.com/o/oauth2/v2/auth",
            'token_endpoint': "https://oauth2.googleapis.com/token",
            'scope': "openid email profile"
        }
        
        # Rate limiting
        self.login_attempts = {}
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutos
    
    def init_session_state(self):
        """Inicializa las variables de sesión de Streamlit"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = None
    
    def load_users(self):
        """Carga la base de datos de usuarios desde archivo"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users_db = json.load(f)
            else:
                # Crear archivo con usuarios de ejemplo
                self.create_default_users()
        except Exception as e:
            logging.error(f"Error cargando usuarios: {e}")
            self.users_db = {}
    
    def load_config(self):
        """Carga la configuración de roles y permisos"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Crear configuración por defecto
                self.create_default_config()
        except Exception as e:
            logging.error(f"Error cargando configuración: {e}")
            self.config = {}
    
    def create_default_users(self):
        """Crea archivo de usuarios por defecto para testing"""
        default_users = {
            "admin@utem.cl": {
                "nombre": "Administrador Sistema",
                "rol": "admin",
                "facultad": "todas",
                "departamento": "sistemas",
                "permisos": ["lectura", "escritura", "exportacion", "admin"],
                "activo": True,
                "fecha_creacion": datetime.datetime.now().isoformat()
            },
            "victor.escobar@utem.cl": {
                "nombre": "Victor Escobar",
                "rol": "director_informatica",
                "facultad": "ingenieria",
                "departamento": "informatica",
                "permisos": ["lectura", "exportacion", "reportes"],
                "activo": True,
                "fecha_creacion": datetime.datetime.now().isoformat()
            },
            "maria.garcia@utem.cl": {
                "nombre": "María García",
                "rol": "director_ciencias",
                "facultad": "ciencias",
                "departamento": "ciencias",
                "permisos": ["lectura", "exportacion", "reportes"],
                "activo": True,
                "fecha_creacion": datetime.datetime.now().isoformat()
            },
            "juan.perez@utem.cl": {
                "nombre": "Juan Pérez",
                "rol": "profesor",
                "facultad": "ingenieria",
                "departamento": "informatica",
                "permisos": ["lectura"],
                "activo": True,
                "fecha_creacion": datetime.datetime.now().isoformat()
            },
            "ana.torres@utem.cl": {
                "nombre": "Ana Torres",
                "rol": "decano",
                "facultad": "quimica",
                "departamento": "quimica",
                "permisos": ["lectura", "exportacion", "reportes", "gestion"],
                "activo": True,
                "fecha_creacion": datetime.datetime.now().isoformat()
            }
        }
        
        self.users_db = default_users
        self.save_users()
    
    def create_default_config(self):
        """Crea configuración por defecto de roles y permisos"""
        default_config = {
            "roles": {
                "admin": {
                    "nombre": "Administrador",
                    "nivel": 100,
                    "permisos_base": ["lectura", "escritura", "exportacion", "admin", "gestion", "reportes"],
                    "acceso_completo": True
                },
                "decano": {
                    "nombre": "Decano",
                    "nivel": 80,
                    "permisos_base": ["lectura", "exportacion", "reportes", "gestion"],
                    "acceso_completo": False
                },
                "director_informatica": {
                    "nombre": "Director de Informática",
                    "nivel": 70,
                    "permisos_base": ["lectura", "exportacion", "reportes"],
                    "acceso_completo": False
                },
                "director_ciencias": {
                    "nombre": "Director de Ciencias",
                    "nivel": 70,
                    "permisos_base": ["lectura", "exportacion", "reportes"],
                    "acceso_completo": False
                },
                "profesor": {
                    "nombre": "Profesor",
                    "nivel": 30,
                    "permisos_base": ["lectura"],
                    "acceso_completo": False
                }
            },
            "dominios_permitidos": ["@utem.cl", "@profesores.utem.cl", "@alumnos.utem.cl"],
            "timeout_sesion": 3600,  # 1 hora
            "max_intentos_login": 5,
            "duracion_bloqueo": 300  # 5 minutos
        }
        
        self.config = default_config
        self.save_config()
    
    def save_users(self):
        """Guarda la base de datos de usuarios en archivo"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users_db, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando usuarios: {e}")
    
    def save_config(self):
        """Guarda la configuración en archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando configuración: {e}")
    
    def check_rate_limit(self, email: str) -> Tuple[bool, str]:
        """
        Verifica rate limiting para prevenir ataques de fuerza bruta
        
        Returns:
            Tuple (permitido, mensaje)
        """
        current_time = time.time()
        
        if email in self.login_attempts:
            attempts_info = self.login_attempts[email]
            
            # Verificar si está en periodo de bloqueo
            if attempts_info['locked_until'] and current_time < attempts_info['locked_until']:
                remaining = int(attempts_info['locked_until'] - current_time)
                return False, f"Cuenta bloqueada. Intente nuevamente en {remaining} segundos."
            
            # Resetear si pasó el periodo de bloqueo
            if attempts_info['locked_until'] and current_time >= attempts_info['locked_until']:
                self.login_attempts[email] = {
                    'attempts': 0,
                    'last_attempt': current_time,
                    'locked_until': None
                }
        else:
            self.login_attempts[email] = {
                'attempts': 0,
                'last_attempt': current_time,
                'locked_until': None
            }
        
        return True, "OK"
    
    def record_login_attempt(self, email: str, success: bool):
        """Registra intento de login para rate limiting"""
        current_time = time.time()
        
        if email not in self.login_attempts:
            self.login_attempts[email] = {
                'attempts': 0,
                'last_attempt': current_time,
                'locked_until': None
            }
        
        if not success:
            self.login_attempts[email]['attempts'] += 1
            self.login_attempts[email]['last_attempt'] = current_time
            
            # Bloquear si excede máximo de intentos
            if self.login_attempts[email]['attempts'] >= self.max_attempts:
                self.login_attempts[email]['locked_until'] = current_time + self.lockout_duration
                logging.warning(f"Cuenta bloqueada por múltiples intentos fallidos: {email}")
        else:
            # Resetear en login exitoso
            self.login_attempts[email] = {
                'attempts': 0,
                'last_attempt': current_time,
                'locked_until': None
            }
    
    def validate_domain(self, email: str) -> bool:
        """Valida que el email pertenezca a dominios permitidos"""
        for domain in self.config.get('dominios_permitidos', []):
            if email.endswith(domain):
                return True
        return False
    
    def authenticate_google(self) -> Optional[Dict]:
        """
        Maneja autenticación con Google OAuth
        
        Returns:
            Datos del usuario autenticado o None
        """
        oauth2 = OAuth2Component(
            client_id=self.oauth_config['client_id'],
            client_secret=self.oauth_config['client_secret'],
            authorize_endpoint=self.oauth_config['authorize_endpoint'],
            token_endpoint=self.oauth_config['token_endpoint'],
        )
        
        result = oauth2.authorize_button(
            name="Iniciar sesión con Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri=self.oauth_config['redirect_uri'],
            scope=self.oauth_config['scope'],
            key="google_auth",
            extras_params={"access_type": "offline"},
            use_container_width=True
        )
        
        if result:
            return result
        return None
    
    def login(self, email: str = None, google_auth: bool = True) -> Tuple[bool, str]:
        """
        Proceso de login principal
        
        Args:
            email: Email del usuario (para login manual)
            google_auth: Si es autenticación con Google
        
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Verificar rate limiting
            allowed, message = self.check_rate_limit(email)
            if not allowed:
                return False, message
            
            # Validar dominio
            if not self.validate_domain(email):
                self.record_login_attempt(email, False)
                logging.warning(f"Intento de login con dominio no autorizado: {email}")
                return False, "Dominio de email no autorizado. Use su cuenta @utem.cl"
            
            # Verificar si usuario existe en base de datos
            if email not in self.users_db:
                self.record_login_attempt(email, False)
                logging.warning(f"Intento de login de usuario no registrado: {email}")
                return False, "Usuario no registrado en el sistema. Contacte al administrador."
            
            user_data = self.users_db[email]
            
            # Verificar si usuario está activo
            if not user_data.get('activo', False):
                self.record_login_attempt(email, False)
                logging.warning(f"Intento de login de usuario inactivo: {email}")
                return False, "Usuario inactivo. Contacte al administrador."
            
            # Login exitoso
            st.session_state.authenticated = True
            st.session_state.user = email
            st.session_state.user_data = user_data
            st.session_state.login_time = datetime.datetime.now()
            st.session_state.last_activity = datetime.datetime.now()
            
            self.record_login_attempt(email, True)
            logging.info(f"Login exitoso: {email}")
            
            return True, f"Bienvenido {user_data.get('nombre', email)}"
            
        except Exception as e:
            logging.error(f"Error en login: {e}")
            return False, "Error en el proceso de autenticación"
    
    def logout(self):
        """Cierra la sesión del usuario actual"""
        if st.session_state.user:
            logging.info(f"Logout: {st.session_state.user}")
        
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_data = None
        st.session_state.login_time = None
        st.session_state.last_activity = None
        
        st.rerun()
    
    def check_session_timeout(self):
        """Verifica si la sesión ha expirado"""
        if st.session_state.authenticated and st.session_state.last_activity:
            timeout = self.config.get('timeout_sesion', 3600)
            elapsed = (datetime.datetime.now() - st.session_state.last_activity).total_seconds()
            
            if elapsed > timeout:
                logging.info(f"Sesión expirada por inactividad: {st.session_state.user}")
                self.logout()
                return False
            
            # Actualizar última actividad
            st.session_state.last_activity = datetime.datetime.now()
        
        return True
    
    def get_user_role(self) -> Optional[str]:
        """Obtiene el rol del usuario actual"""
        if st.session_state.authenticated and st.session_state.user_data:
            return st.session_state.user_data.get('rol')
        return None
    
    def get_user_permissions(self) -> List[str]:
        """Obtiene los permisos del usuario actual"""
        if st.session_state.authenticated and st.session_state.user_data:
            return st.session_state.user_data.get('permisos', [])
        return []
    
    def is_authorized(self, permission: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico
        
        Args:
            permission: Permiso a verificar
        
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        if not st.session_state.authenticated:
            return False
        
        user_role = self.get_user_role()
        
        # Admin tiene todos los permisos
        if user_role == 'admin':
            return True
        
        # Verificar permisos del usuario
        user_permissions = self.get_user_permissions()
        return permission in user_permissions
    
    def filter_data_by_role(self, data, department_column: str = 'departamento'):
        """
        Filtra datos según el rol y permisos del usuario
        
        Args:
            data: DataFrame con los datos a filtrar
            department_column: Columna que contiene el departamento
        
        Returns:
            DataFrame filtrado según permisos
        """
        if not st.session_state.authenticated:
            return None
        
        user_role = self.get_user_role()
        user_data = st.session_state.user_data
        
        # Admin ve todo
        if user_role == 'admin':
            return data
        
        # Filtrar por facultad/departamento
        if user_data.get('facultad') == 'todas':
            return data
        
        # Filtrar por departamento específico
        user_dept = user_data.get('departamento')
        if user_dept and department_column in data.columns:
            return data[data[department_column].str.lower() == user_dept.lower()]
        
        return data
    
    def login_required(self, func):
        """
        Decorador para proteger funciones que requieren autenticación
        
        Uso:
            @auth.login_required
            def mi_funcion():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not st.session_state.authenticated:
                st.error("⚠️ Debe iniciar sesión para acceder a esta función")
                st.stop()
            
            # Verificar timeout de sesión
            if not self.check_session_timeout():
                st.error("⚠️ Su sesión ha expirado. Por favor, inicie sesión nuevamente.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    
    def render_login_form(self):
        """Renderiza el formulario de login"""
        st.markdown("""
        <style>
        .login-container {
            max-width: 500px;
            margin: auto;
            padding: 2rem;
            border-radius: 10px;
            background-color: #f0f2f6;
        }
        .login-header {
            text-align: center;
            color: #1f4788;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="login-header">', unsafe_allow_html=True)
            st.title("🎓 Dashboard Canvas UTEM")
            st.subheader("Sistema de Gestión Académica")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.info("👤 Use su cuenta institucional @utem.cl para acceder")
            
            # Opción 1: Login con Google OAuth
            if st.button("🔐 Iniciar sesión con Google", use_container_width=True, type="primary"):
                google_result = self.authenticate_google()
                if google_result:
                    email = google_result.get('email')
                    success, message = self.login(email, google_auth=True)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            st.divider()
            
            # Opción 2: Login manual (para testing)
            with st.expander("🔧 Login manual (solo desarrollo)"):
                email = st.text_input("Email", placeholder="usuario@utem.cl")
                if st.button("Iniciar sesión", use_container_width=True):
                    if email:
                        success, message = self.login(email, google_auth=False)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Por favor ingrese su email")
            
            # Información de contacto
            st.markdown("---")
            st.caption("💡 ¿Problemas para acceder? Contacte a soporte.ti@utem.cl")
    
    def render_user_sidebar(self):
        """Renderiza información del usuario en el sidebar"""
        if st.session_state.authenticated:
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 Usuario Actual")
                
                user_data = st.session_state.user_data
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown("👨‍💼")
                
                with col2:
                    st.markdown(f"**{user_data.get('nombre', 'Usuario')}**")
                    st.caption(st.session_state.user)
                
                # Información del rol y permisos
                role = user_data.get('rol', 'Sin rol')
                role_info = self.config['roles'].get(role, {})
                
                st.info(f"**Rol:** {role_info.get('nombre', role)}")
                st.caption(f"**Facultad:** {user_data.get('facultad', 'N/A').title()}")
                st.caption(f"**Departamento:** {user_data.get('departamento', 'N/A').title()}")
                
                # Permisos
                with st.expander("🔐 Permisos"):
                    permisos = user_data.get('permisos', [])
                    for permiso in permisos:
                        st.write(f"✅ {permiso.title()}")
                
                # Información de sesión
                if st.session_state.login_time:
                    tiempo_sesion = datetime.datetime.now() - st.session_state.login_time
                    st.caption(f"⏱️ Sesión activa: {str(tiempo_sesion).split('.')[0]}")
                
                # Botón de logout
                st.markdown("---")
                if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
                    self.logout()
    
    def add_user(self, email: str, user_info: Dict) -> Tuple[bool, str]:
        """
        Agrega un nuevo usuario al sistema
        
        Args:
            email: Email del usuario
            user_info: Diccionario con información del usuario
        
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            if email in self.users_db:
                return False, "Usuario ya existe"
            
            # Validar dominio
            if not self.validate_domain(email):
                return False, "Dominio de email no válido"
            
            # Agregar timestamp
            user_info['fecha_creacion'] = datetime.datetime.now().isoformat()
            user_info['activo'] = user_info.get('activo', True)
            
            self.users_db[email] = user_info
            self.save_users()
            
            logging.info(f"Nuevo usuario agregado: {email}")
            return True, "Usuario agregado exitosamente"
            
        except Exception as e:
            logging.error(f"Error agregando usuario: {e}")
            return False, f"Error al agregar usuario: {str(e)}"
    
    def update_user(self, email: str, updates: Dict) -> Tuple[bool, str]:
        """
        Actualiza información de un usuario existente
        
        Args:
            email: Email del usuario
            updates: Diccionario con campos a actualizar
        
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            if email not in self.users_db:
                return False, "Usuario no existe"
            
            # Actualizar campos
            for key, value in updates.items():
                self.users_db[email][key] = value
            
            # Agregar timestamp de modificación
            self.users_db[email]['fecha_modificacion'] = datetime.datetime.now().isoformat()
            
            self.save_users()
            
            logging.info(f"Usuario actualizado: {email}")
            return True, "Usuario actualizado exitosamente"
            
        except Exception as e:
            logging.error(f"Error actualizando usuario: {e}")
            return False, f"Error al actualizar usuario: {str(e)}"
    
    def delete_user(self, email: str) -> Tuple[bool, str]:
        """
        Elimina un usuario del sistema
        
        Args:
            email: Email del usuario a eliminar
        
        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            if email not in self.users_db:
                return False, "Usuario no existe"
            
            # No permitir eliminar al admin principal
            if email == "admin@utem.cl":
                return False, "No se puede eliminar al administrador principal"
            
            del self.users_db[email]
            self.save_users()
            
            logging.info(f"Usuario eliminado: {email}")
            return True, "Usuario eliminado exitosamente"
            
        except Exception as e:
            logging.error(f"Error eliminando usuario: {e}")
            return False, f"Error al eliminar usuario: {str(e)}"
    
    def get_all_users(self) -> Dict:
        """Obtiene todos los usuarios del sistema"""
        return self.users_db
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Obtiene información de un usuario específico"""
        return self.users_db.get(email)


# Funciones de utilidad para uso directo
def create_auth_system():
    """Crea una instancia del sistema de autenticación"""
    return AuthenticationSystem()

def login_required(func):
    """Decorador para proteger páginas/funciones"""
    auth = create_auth_system()
    return auth.login_required(func)

def get_current_user():
    """Obtiene el usuario actual"""
    if st.session_state.authenticated:
        return st.session_state.user
    return None

def get_current_user_data():
    """Obtiene los datos completos del usuario actual"""
    if st.session_state.authenticated:
        return st.session_state.user_data
    return None

def is_admin():
    """Verifica si el usuario actual es administrador"""
    if st.session_state.authenticated:
        user_data = st.session_state.user_data
        return user_data.get('rol') == 'admin'
    return False