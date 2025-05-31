FROM python:3.9-slim
RUN pip install boto3
COPY main.py .
CMD ["python", "main.py"]
