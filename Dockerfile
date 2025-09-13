FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Install the package
RUN pip install -e .

# Create data directory
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Create non-root user
RUN useradd -m -u 1000 quantuser && chown -R quantuser:quantuser /app
USER quantuser

# Default command
CMD ["python", "-m", "quantalertsystem.main"]