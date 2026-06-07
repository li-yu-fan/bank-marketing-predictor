FROM python:3.11-slim

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

COPY app.py .
COPY src/ ./src/

# Streamlit default port
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
