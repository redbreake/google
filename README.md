# 📧 Mi Bandeja de Gmail - Django Gmail Client

Una aplicación web moderna construida con Django que permite acceder y gestionar tu bandeja de entrada de Gmail a través de la API de Google. Incluye una interfaz de usuario moderna y responsiva con Bootstrap 5.

## ✨ Características

- 🔐 **Autenticación OAuth 2.0** con Google
- 📱 **Interfaz responsiva** y moderna con Bootstrap 5
- 📧 **Vista de bandeja de entrada** con paginación
- 🔍 **Búsqueda avanzada** de emails con sintaxis de Gmail
- 📄 **Vista detallada** de mensajes con soporte HTML
- 📊 **Exportación CSV** de correos
- 🎨 **Diseño moderno** con sidebar navegable y efectos visuales
- 🌙 **Responsive design** para desktop y móvil

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/redbreake/google.git
cd google
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install django google-api-python-client google-auth google-auth-oauthlib python-dotenv django-bootstrap5 bleach
```

### 4. Configurar Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la Gmail API
4. Crea credenciales OAuth 2.0:
   - Tipo de aplicación: Aplicación web
   - URIs de redireccionamiento autorizados: `http://localhost:8000/google/callback`
5. Descarga el archivo JSON de credenciales y renómbralo como `credentials.json`

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
GOOGLE_REDIRECT_URI=http://localhost:8000/google/callback
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Ejecutar el servidor

```bash
# Para desarrollo local:
$env:OAUTHLIB_INSECURE_TRANSPORT = "1"  # Solo en Windows PowerShell
python manage.py runserver
```

Visita `http://localhost:8000` en tu navegador.

## 📁 Estructura del Proyecto

```
mibandejagmail/
├── gmailbox/                 # Aplicación principal
│   ├── templates/
│   │   └── gmailbox/
│   │       ├── base.html     # Template base con Bootstrap
│   │       ├── inbox.html    # Vista de bandeja de entrada
│   │       └── message_detail.html  # Vista detallada de mensaje
│   ├── views.py              # Lógica de vistas
│   ├── urls.py               # URLs de la aplicación
│   └── models.py             # Modelos de datos
├── mibandejagmail/           # Configuración del proyecto
│   ├── settings.py           # Configuración Django
│   ├── urls.py               # URLs principales
│   └── wsgi.py              # Configuración WSGI
├── .env                      # Variables de entorno
├── credentials.json          # Credenciales Google (descargar)
├── manage.py                 # Script de gestión Django
└── README.md                 # Este archivo
```

## 🔧 Configuración de Producción

Para desplegar en producción:

1. Cambia `DEBUG = False` en `settings.py`
2. Configura `ALLOWED_HOSTS` con tu dominio
3. Usa HTTPS en producción
4. Configura variables de entorno seguras
5. Considera usar PostgreSQL en lugar de SQLite

## 🎨 Personalización

### Tema de Colores

Los colores se definen en `gmailbox/templates/gmailbox/base.html`:

```css
:root {
    --primary-color: #4285f4;
    --secondary-color: #34a853;
    --danger-color: #ea4335;
    --warning-color: #fbbc04;
}
```

### Funcionalidades Adicionales

La aplicación incluye:
- **Búsqueda avanzada** con sintaxis de Gmail
- **Paginación** automática
- **Soporte HTML** en mensajes
- **Exportación CSV** con metadata completa

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🐛 Solución de Problemas

### Error de transporte inseguro
Si obtienes el error `insecure_transport`, ejecuta:
```bash
$env:OAUTHLIB_INSECURE_TRANSPORT = "1"
```

### Credenciales no encontradas
Asegúrate de que `credentials.json` esté en la raíz del proyecto.

### Problemas de permisos OAuth
Verifica que las URIs de redireccionamiento en Google Cloud Console coincidan exactamente.

## 📞 Soporte

Para soporte, abre un issue en GitHub o contacta al desarrollador.

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!

