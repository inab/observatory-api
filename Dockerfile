FROM python:3.6-alpine
FROM ubuntu


# Copy configuration file
COPY config_db.ini ./config_db.ini

# Copy the dependencies
COPY requirements.txt ./

# need git to install dependencies from github
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git python3-pip

# Install the dependencies
RUN pip3 install FAIRsoft --extra-index-url https://gitlab-observatory-api:8zfe-4zvgbgk44DCsU-A@gitlab.bsc.es/api/v4/projects/1151/packages/pypi/simple
RUN pip3 install -r requirements.txt

# Copy the files
COPY . .

EXPOSE 3000

# Executable commands
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=3000"]