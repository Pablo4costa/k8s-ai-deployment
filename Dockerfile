# Imagen base oficial de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero (optimiza cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app/

# Copiar variables de entorno
COPY .env.example .env

# Puerto que expone el contenedor
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]