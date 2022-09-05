FROM python:3.6-alpine
FROM ubuntu as intermediate

# Working directory
WORKDIR /app

# Copy the dependencies
COPY requirements.txt ./

# need git to install dependencies from github
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# Install the dependencies
RUN pip3 install -r requirements.txt

# Copy the files
COPY . .

EXPOSE 3000

# Executable commands
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=3000"]