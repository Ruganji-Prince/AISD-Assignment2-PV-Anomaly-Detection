ARG PYTHON_VERSION=3.14.10
FROM python:${PYTHON_VERSION}-slim
WORKDIR /app
COPY web/requirements.lock /app/web/requirements.lock
RUN pip install --no-cache-dir --require-hashes -r web/requirements.lock && useradd --create-home appuser
COPY src /app/src
COPY web /app/web
COPY models/rf_e4 /app/models/rf_e4
COPY deployment/example_cases.json /app/deployment/example_cases.json
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
