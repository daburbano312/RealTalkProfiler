# Imagen base con Python
FROM python:3.11-slim
 
# Instalar PortAudio (dependencia nativa de PyAudio)
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-dev \
    build-essential
 
# Establecer directorio de trabajo
WORKDIR /app
 
# Copiar tu proyecto
COPY . /app
 
# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
 
# Exponer el puerto 5000 (Flask)
EXPOSE 5000
 
# Comando para correr Flask (ajústalo si tu archivo principal no se llama app.py)
CMD ["python", "app.py"]