FROM python:3.9-slim

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files in your current directory
COPY *.py .

# Run your main script
CMD ["python", "main.py"]
