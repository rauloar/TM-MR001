# TM-MR001 Importer

TM-MR001 Importer es un sistema de gestión de asistencia y usuarios, diseñado para importar, visualizar y administrar registros de asistencia de empleados. Incluye una interfaz gráfica moderna desarrollada en Python con PySide6, y está estructurado para facilitar la integración de módulos externos y la escalabilidad.

## Características principales

- **Gestión de usuarios:** Alta, baja y modificación de usuarios del sistema.
- **Gestión de empleados:** Administración de empleados y sus datos asociados.
- **Importación de movimientos:** Importa registros de asistencia desde archivos o dispositivos compatibles.
- **Visualización de movimientos:** Consulta y análisis de registros de asistencia.
- **Módulo externo "Proceso":** Permite integrar lógica adicional sin modificar el núcleo del sistema.
- **Seguridad:** Autenticación de usuarios y manejo seguro de contraseñas.
- **Base de datos local:** Utiliza una base de datos local para almacenar toda la información.
- **Interfaz intuitiva:** Basada en pestañas (tabs) para fácil navegación.

## Estructura del proyecto

- `attendance/` - Código principal del sistema.
  - `core/` - Lógica de base de datos y seguridad.
  - `models/` - Modelos de datos (usuarios, empleados, asistencia).
  - `services/` - Servicios auxiliares (importación, etc).
  - `ui/` - Interfaz gráfica y pestañas.
- `proceso/` - Módulo externo para lógica adicional.
- `.gitignore` - Ignora carpetas de entorno, backups y builds.

## Instalación y uso

1. Clona el repositorio.
2. Crea y activa un entorno virtual (recomendado).
3. Instala las dependencias:
   ```
   pip install -r attendance/requirements.txt
   ```
4. Ejecuta la aplicación:
   ```
   python attendance/main.py
   ```

## Notas
- Las carpetas `att`, `backup`, `dist` y `build` están ignoradas en el control de versiones.
- El sistema está preparado para ampliaciones mediante módulos externos en la carpeta `proceso`.

---

Desarrollado por rauloar.
