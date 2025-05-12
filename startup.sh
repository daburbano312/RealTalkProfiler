#!/bin/bash

# Actualizar repositorios de paquetes
apt-get update

# Instalar dependencias necesarias para PyAudio
apt-get install -y portaudio19-dev gcc python3-dev

# Ejecutar la aplicación Flask (asegúrate de que tu app se ejecute desde el archivo correcto)
python3 app.py
