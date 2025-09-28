# 🎓 UTEM Canvas Authentication System

Sistema de autenticación OAuth con Google para Canvas LMS de la Universidad Tecnológica Metropolitana (UTEM), desarrollado con Streamlit.

## 🚀 Características

- **Autenticación OAuth 2.0** con Google
- **Sistema de roles** universitarios (Admin, Profesor, Estudiante, Invitado)
- **Protección de rutas** basada en permisos
- **Gestión de usuarios** con base de datos JSON
- **Interfaz responsiva** con Streamlit
- **Configuración específica** para UTEM

## 📋 Requisitos Previos

- Python 3.8+
- Cuenta de Google Cloud Platform
- Credenciales OAuth 2.0 configuradas

## 🛠️ Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/canvas-auth-utem.git
cd canvas-auth-utem
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
```env
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
REDIRECT_URI=http://localhost:8501
```

## 🔧 Configuración OAuth Google

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar la Google+ API
4. Crear credenciales OAuth 2.0:
   - Tipo: Web application
   - Authorized redirect URIs: `http://localhost:8501`
5. Copiar Client ID y Client Secret al archivo `.env`

## 🚀 Ejecución

```bash
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

## 👥 Sistema de Roles

### Administrador
- Gestión completa de usuarios
- Configuración del sistema
- Acceso a estadísticas
- Gestión de roles y permisos

### Profesor
- Gestión de cursos asignados
- Calificaciones de estudiantes
- Recursos didácticos
- Análisis de cursos

### Estudiante
- Acceso a cursos inscritos
- Visualización de tareas
- Consulta de calificaciones
- Materiales del curso

### Invitado
- Acceso limitado a contenido público
- Sin permisos de modificación

## 📁 Estructura del Proyecto

```
canvas-auth-utem/
├── app.py              # Aplicación principal Streamlit
├── auth.py             # Lógica de autenticación OAuth
├── config.py           # Configuración de roles y permisos
├── users.json          # Base de datos de usuarios
├── requirements.txt    # Dependencias Python
├── .env.example        # Plantilla variables de entorno
├── .gitignore          # Archivos ignorados por Git
└── README.md           # Este archivo
```

## 🔒 Seguridad

- **OAuth 2.0** para autenticación segura
- **Verificación de estado** para prevenir CSRF
- **Gestión de sesiones** con Streamlit
- **Validación de dominios** UTEM
- **Protección de rutas** basada en roles

## 🎯 Uso

1. **Acceder** a la aplicación
2. **Iniciar sesión** con Google OAuth
3. **Navegación automática** según rol asignado
4. **Gestión de permisos** transparente

## ⚙️ Configuración UTEM

El sistema está preconfigurado para UTEM con:

- **Dominios de email** autorizados
- **Facultades y departamentos** UTEM
- **Roles académicos** específicos
- **Permisos granulares** por función

## 🐛 Solución de Problemas

### Error de autenticación OAuth
- Verificar credenciales en `.env`
- Confirmar redirect URI en Google Console
- Revisar permisos de la aplicación

### Problemas de permisos
- Verificar rol asignado en `users.json`
- Consultar configuración en `config.py`
- Contactar administrador del sistema

### Error al cargar usuarios
- Verificar formato JSON válido
- Comprobar permisos de archivo
- Restaurar desde backup si necesario

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Contacto

- **Email:** admin@utem.cl
- **Canvas UTEM:** https://canvas.utem.cl
- **Soporte:** sistemas@utem.cl

## 🔄 Actualizaciones

### v1.0.0
- Implementación inicial
- Autenticación OAuth Google
- Sistema de roles UTEM
- Interfaz básica Streamlit

---

**Universidad Tecnológica Metropolitana (UTEM)**  
Sistema desarrollado para optimizar la experiencia de Canvas LMS