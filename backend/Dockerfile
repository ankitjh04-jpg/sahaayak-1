FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY pyproject.toml .
COPY app ./app
COPY server.py .
RUN pip install --no-cache-dir .
RUN useradd --create-home sahaayak && mkdir -p /app/backend/private_objects && chown -R sahaayak:sahaayak /app/backend
USER sahaayak
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]