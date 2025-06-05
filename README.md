# Delivery Route Planner

## Descripción
Delivery Route Planner es una aplicación de escritorio desarrollada en Python que permite planificar y optimizar rutas de entrega. La aplicación proporciona una interfaz gráfica intuitiva para gestionar paquetes y calcular rutas eficientes basadas en la ubicación y prioridad de las entregas.

## Características Principales
-	Interfaz gráfica moderna y fácil de usar
-	Geocodificación de direcciones
-	Soporte para coordenadas directas
-	Sistema de prioridades de entrega (Alta, Media, Baja)
-	Visualización de rutas en mapa interactivo
-	Cálculo de rutas optimizadas
-	Gestión de lista de paquetes
-	Información detallada de distancias y paradas

## Requisitos
- Python 3.7+
- Dependencias:
  bash
  pip install folium geopy pillow

Requisitos
**Ejecutar la aplicación:**
bash
python delivery_route_planner.py

**Agregar paquetes**:
•	Ingresar dirección o coordenadas
•	Seleccionar prioridad
•	Clic en "Add Package"
•	Calcular ruta:
•	Clic en "Calculate Route"
•	Ver la ruta en el mapa
•	Gestionar paquetes:
•	Ver lista de paquetes
•	Borrar todos los paquetes

**Funcionalidades**
Geocodificación: Convierte direcciones en coordenadas
Prioridades: Alta (1), Media (2), Baja (3)

**Visualización**: 
-	Mapa interactivo con marcadores de colores
-	Optimización: Cálculo de rutas considerando distancia y prioridad
-	Gestión: Interfaz para administrar paquetes
-	Detalles Técnicos
-	Interfaz: Tkinter con tema personalizado
-	Mapas: Folium (basado en Leaflet.js)
-	Geocodificación: Nominatim (OpenStreetMap)
-	Algoritmo de ruta: Vecino más cercano modificado con prioridades

**Contribuir**
-	Fork del repositorio
-	Crear rama feature: git checkout -b feature/NuevaFuncionalidad
-	Commit cambios: git commit -am 'Agregar nueva funcionalidad'
-	Push a la rama: git push origin feature/NuevaFuncionalidad
-	Crear Pull Request

**Autor**
Mayro Gameros XZ
Contacto: barriosgamerosmayro@gmail.com
Estado del Proyecto
En desarrollo activo - versión 1.0.0

**Agradecimientos**
OpenStreetMap por los servicios de geocodificación
Folium por la biblioteca de mapas
Comunidad Python por las herramientas utilizadas
