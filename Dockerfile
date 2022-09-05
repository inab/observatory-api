FROM python:3.6-alpine

# Working directory
WORKDIR /app

# Copy the dependencies
COPY requirements.txt ./

# Install the dependencies
RUN pip3 install -r requirements.txt

# Copy the files
COPY . .

EXPOSE 3000

# Executable commands
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=3000"]