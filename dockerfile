# Use Python official image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the project folder to the working directory
COPY infotech_nepal /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the application port
EXPOSE 8000

# Default command
CMD ["gunicorn", "ecommerce.wsgi:application", "--bind", "0.0.0.0:8000"]
