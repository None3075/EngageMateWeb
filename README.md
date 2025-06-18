# EngageMate Dashboard

![Django](https://img.shields.io/badge/Django-4.x-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)

## Descripción General

EngageMate es una aplicación de panel de control integral diseñada para mejorar la interacción en el aula con aprendizaje recíproco y asistencia inteligente de IoT. Construida con Django, esta aplicación web funciona en conjunto con el proyecto [WioMK](https://github.com/None3075/WioMK) para proporcionar análisis del aula, seguimiento de participación de estudiantes y herramientas de visualización interactiva.

## Características

- **Notificaciones de Estado en Tiempo Real**: Indicadores visuales del estado de la clase (en curso, en pausa, no en sesión)
- **Visualización de Datos**: Panel de análisis para métricas de participación en el aula
- **Autenticación de Usuario**: Sistema seguro de inicio de sesión y registro
- **Gestión de Datos CSV**: Capacidades de importación/exportación para datos del aula

## Requisitos Previos

- Python 3.x
- Django
- Dependencias listadas en requirements.txt
- **Importante**: El proyecto [WioMK](https://github.com/None3075/WioMK) debe estar configurado y funcionando con la IP de servidor correcta

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/None3075/EngageMateWeb.git
   cd EngageMateWeb
   ```

2. **Crear un entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**
   ```bash
   python manage.py makemigrations dashboardApp
   python manage.py migrate
   ```

5. **Crear un usuario administrador**
   ```bash
   python manage.py createsuperuser
   ```

6. **Configurar el token de usuario**
   - Accede a la interfaz de administración de Django en http://127.0.0.1:8000/admin/
   - Establece el token de usuario para tu usuario (El valor predeterminado de WioMK es "Patata")
   - Este token debe corresponder con tu token de usuario de WioMK

## Configuración

1. Añade la IP de tu servidor a `ALLOWED_HOSTS` en settings.py
2. Asegúrate de que el [proyecto WioMK](https://github.com/None3075/WioMK) esté instalado y configurado correctamente

## Ejecutar la Aplicación

```bash
python manage.py runserver 0.0.0.0:8000
```

Accede a la aplicación en:
- Local: http://127.0.0.1:8000/
- Red: http://[tu-ip]:8000/

## Estructura del Proyecto

```
EngageMateWeb/
├── dashboardApp/            # Aplicación principal
│   ├── models.py            # Modelos de base de datos
│   ├── views.py             # Controladores de vistas
│   ├── urls.py              # Enrutamiento de URL
│   ├── templates/           # Plantillas HTML
│   ├── static/              # CSS, JS, imágenes
│   └── Data/                # Datos CSV específicos del usuario
├── webDeustotech/           # Configuración del proyecto
├── Data/                    # Archivos CSV de datos globales recibidos
├── manage.py                # Script de administración de Django
└── requirements.txt         # Dependencias
```

## Uso

1. **Interfaz de Administración**
   - Inicia sesión en http://127.0.0.1:8000/admin/
   - Gestiona usuarios, permisos y datos de la aplicación

2. **Sesiones**
   - Visualiza información detallada sobre cada clase
   - Accede a datos adicionales y gráficos sobre la información recopilada durante las clases
   - Analiza métricas de participación de estudiantes por sesión
   - Monitoriza patrones históricos y tendencias entre diferentes clases

## Licencia
Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](LICENSE).

Proyecto dirigido por [Oihane Gomez Carmona](https://scholar.google.es/citations?hl=es&user=ptqq8JAAAAAJ).