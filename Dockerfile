# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .  # This will copy GeoLite2-City.mmdb and all other files

# Ensure the GeoIP database is readable by your application
RUN chmod 644 GeoLite2-City.mmdb

# Specify the command to run on container start
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app