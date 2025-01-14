# Use the official Python 3.11 base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /app

# Install system dependencies (e.g., for psycopg2 and other requirements)
# Copy the project folder to the working directory
# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Install pip (for version consistency) and then install the dependencies
COPY requirements.txt /app/

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install dependencies, but only if they are not installed already.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the Django management commands to prepare the app and start the server
CMD ["sh", "-c", "python manage.py resetsequence && python manage.py migrate user && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
