# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install git and other dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    pip install pytest && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

#
ENV CONFIG_PATH='/api-variables/config_db.ini'

# Make port 3500 available to the world outside this container
EXPOSE 3800

# Run the application
CMD ["uvicorn", "main:app", "--root-path", "/api-test",  "--host", "0.0.0.0", "--port", "3800", "--reload"]


