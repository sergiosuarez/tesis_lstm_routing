Tesis Routing - Predicción de Tiempos de Viaje con LSTM

Descripción

Este proyecto es un frontend desarrollado para visualizar y utilizar un modelo de redes neuronales LSTM entrenado para predecir tiempos de viaje en una red de transporte. El modelo se basa en variables meteorológicas y datos de tráfico en tiempo real. Utiliza pgRouting para la generación de rutas y PyTorch para el entrenamiento y la inferencia del modelo LSTM.

Tecnologías Utilizadas

Frontend: React

Backend: Django + Django REST Framework

Modelo de Machine Learning: PyTorch (LSTM)

Base de datos geoespacial: PostgreSQL con PostGIS y pgRouting

API de tráfico: Integración con fuentes de datos en tiempo real

Instalación

Requisitos previos

Tener instalado Node.js y npm o yarn.

Un servidor backend con Django, PostgreSQL + PostGIS, y soporte para pgRouting.

Tener instalado PyTorch en el entorno del backend.

Pasos

Clonar el repositorio:

git clone https://github.com/tuusuario/tesis_routing.git
cd tesis_routing/frontend

Instalar las dependencias:

npm install  # o yarn install

Configurar las variables de entorno:

Crear un archivo .env en la raíz del proyecto con las variables necesarias para la API backend y fuentes de datos meteorológicos.

Ejecutar el frontend en modo desarrollo:

npm start  # o yarn start

Uso

Introducir los puntos de origen y destino en la interfaz.

Seleccionar las condiciones meteorológicas (o permitir la detección en tiempo real).

Ejecutar la consulta para obtener el tiempo estimado de viaje con base en el modelo LSTM.

Visualizar la ruta óptima generada con pgRouting.

Configuración del Modelo

El modelo LSTM se encuentra en el backend y está entrenado con datos históricos de tráfico y clima. Puedes actualizarlo o reentrenarlo con nuevos datos siguiendo estos pasos:

Asegurarse de que los datos están almacenados en PostgreSQL.

Ejecutar el script de entrenamiento en el backend:

python train_model.py --epochs 50 --batch_size 32

Para realizar predicciones desde el frontend, la API de backend expone un endpoint que recibe los parámetros de entrada y devuelve la estimación del tiempo de viaje.

Contacto

Para dudas o mejoras, puedes abrir un issue en el repositorio o contactarme en [tu correo o LinkedIn].
