FROM python:3.11-slim

WORKDIR /app

COPY . /app/

RUN pip install boto3 cryptography fastapi Jinja2 PyMySQL python-dotenv python-multipart SQLAlchemy uvicorn

CMD ["uvicorn", "comprehend_app:app", "--host", "0.0.0.0", "--port", "8000"]
