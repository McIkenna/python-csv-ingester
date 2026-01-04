FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    vim \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (pinned)
RUN pip install --no-cache-dir \
    datetime==5.5 \
    pandas==2.3.3 \
    numpy==2.0.2 

# Copy project files
COPY src/ /app/src/

# Set environment
ENV PYTHONPATH=/app

CMD ["python"]
