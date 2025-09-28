"""
Configuración de roles y permisos para el sistema UTEM Canvas Auth
"""

# Definición de roles y sus permisos
ROLES = {
    'admin': {
        'name': 'Administrador',
        'description': 'Acceso completo al sistema',
        'permissions': [
            'manage_users',
            'manage_roles',
            'manage_courses',
            'manage_system',
            'view_analytics',
            'export_data',
            'view_courses',
            'manage_content',
            'grade_assignments',
            'view_grades'
        ]
    },
    'profesor': {
        'name': 'Profesor',
        'description': 'Gestión de cursos y estudiantes',
        'permissions': [
            'manage_courses',
            'view_courses',
            'manage_content',
            'grade_assignments',
            'view_grades',
            'manage_students_in_course',
            'create_assignments',
            'view_course_analytics'
        ]
    },
    'estudiante': {
        'name': 'Estudiante',
        'description': 'Acceso a cursos inscritos',
        'permissions': [
            'view_courses',
            'view_assignments',
            'submit_assignments',
            'view_grades',
            'access_course_materials',
            'participate_discussions'
        ]
    },
    'invitado': {
        'name': 'Invitado',
        'description': 'Acceso limitado',
        'permissions': [
            'view_public_courses',
            'view_public_materials'
        ]
    }
}

# Configuración específica de UTEM
UTEM_CONFIG = {
    'university_name': 'Universidad Tecnológica Metropolitana',
    'university_code': 'UTEM',
    'academic_year': 2024,
    'semester': 1,
    'canvas_instance': 'https://canvas.utem.cl',
    'supported_email_domains': [
        '@utem.cl',
        '@utem.ac.cl',
        '@gmail.com'  # Para desarrollo y casos especiales
    ],
    'admin_emails': [
        'admin@utem.cl',
        'sistemas@utem.cl',
        'canvas-admin@utem.cl'
    ]
}

# Configuración de facultades y departamentos UTEM
FACULTADES = {
    'FIN': {
        'name': 'Facultad de Ingeniería',
        'departamentos': [
            'Ingeniería Civil Industrial',
            'Ingeniería Civil en Computación',
            'Ingeniería Civil Electrónica',
            'Ingeniería Civil Mecánica',
            'Ingeniería en Informática'
        ]
    },
    'FAD': {
        'name': 'Facultad de Administración y Economía',
        'departamentos': [
            'Ingeniería Comercial',
            'Contador Público y Auditor',
            'Ingeniería en Administración'
        ]
    },
    'FCN': {
        'name': 'Facultad de Ciencias Naturales, Matemáticas y del Medio Ambiente',
        'departamentos': [
            'Química Industrial',
            'Biotecnología',
            'Medio Ambiente'
        ]
    },
    'FCS': {
        'name': 'Facultad de Ciencias de la Construcción y Ordenamiento Territorial',
        'departamentos': [
            'Arquitectura',
            'Construcción Civil',
            'Prevención de Riesgos'
        ]
    },
    'FHC': {
        'name': 'Facultad Humanística y Tecnológica',
        'departamentos': [
            'Trabajo Social',
            'Diseño',
            'Bibliotecología'
        ]
    }
}

def check_role_permission(role, permission):
    """
    Verifica si un rol tiene un permiso específico
    
    Args:
        role (str): El rol del usuario
        permission (str): El permiso a verificar
    
    Returns:
        bool: True si el rol tiene el permiso, False en caso contrario
    """
    if role not in ROLES:
        return False
    
    return permission in ROLES[role]['permissions']

def get_role_info(role):
    """
    Obtiene información completa de un rol
    
    Args:
        role (str): El rol del usuario
    
    Returns:
        dict: Información del rol o None si no existe
    """
    return ROLES.get(role, None)

def get_user_permissions(role):
    """
    Obtiene todos los permisos de un rol
    
    Args:
        role (str): El rol del usuario
    
    Returns:
        list: Lista de permisos del rol
    """
    role_info = get_role_info(role)
    return role_info['permissions'] if role_info else []

def is_utem_email(email):
    """
    Verifica si un email pertenece al dominio UTEM
    
    Args:
        email (str): Email a verificar
    
    Returns:
        bool: True si es email UTEM, False en caso contrario
    """
    return any(email.endswith(domain) for domain in UTEM_CONFIG['supported_email_domains'])

def is_admin_email(email):
    """
    Verifica si un email está en la lista de administradores
    
    Args:
        email (str): Email a verificar
    
    Returns:
        bool: True si es email de admin, False en caso contrario
    """
    return email in UTEM_CONFIG['admin_emails']

def get_default_role_for_email(email):
    """
    Determina el rol por defecto basado en el email
    
    Args:
        email (str): Email del usuario
    
    Returns:
        str: Rol por defecto
    """
    if is_admin_email(email):
        return 'admin'
    elif email.endswith('@utem.cl'):
        # Lógica más sofisticada basada en patrones de email
        if any(keyword in email.lower() for keyword in ['prof', 'docente', 'academico']):
            return 'profesor'
        return 'estudiante'
    elif email.endswith('@gmail.com'):
        return 'invitado'
    else:
        return 'invitado'

def validate_role(role):
    """
    Valida si un rol existe en el sistema
    
    Args:
        role (str): Rol a validar
    
    Returns:
        bool: True si el rol existe, False en caso contrario
    """
    return role in ROLES

def get_all_roles():
    """
    Obtiene todos los roles disponibles
    
    Returns:
        list: Lista de todos los roles
    """
    return list(ROLES.keys())

def get_role_hierarchy():
    """
    Define la jerarquía de roles (mayor a menor privilegio)
    
    Returns:
        list: Roles ordenados por jerarquía
    """
    return ['admin', 'profesor', 'estudiante', 'invitado']

def can_manage_role(manager_role, target_role):
    """
    Verifica si un rol puede gestionar otro rol
    
    Args:
        manager_role (str): Rol del gestor
        target_role (str): Rol objetivo
    
    Returns:
        bool: True si puede gestionar, False en caso contrario
    """
    hierarchy = get_role_hierarchy()
    try:
        manager_level = hierarchy.index(manager_role)
        target_level = hierarchy.index(target_role)
        return manager_level < target_level  # Menor índice = mayor privilegio
    except ValueError:
        return False