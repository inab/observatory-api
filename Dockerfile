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
    pip install --no-cache-dir torch==2.12.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Bake the semantic-search encoder into the image, so containers never download it.
ENV HF_HOME=/opt/hf
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Alibaba-NLP/gte-modernbert-base', device='cpu')"
ENV HF_HUB_OFFLINE=1

# Copy the current directory contents into the container at /app
COPY . .

#
ENV CONFIG_PATH='/api-variables/config_db.ini'

# Make port 3500 available to the world outside this container
EXPOSE 3500

# Run the application
# uvicorn main:app --root-path /api --host 0.0.0.0 --port 3500 --reload

CMD ["uvicorn", "main:app",  "--host", "0.0.0.0", "--port", "3500", "--reload"]


