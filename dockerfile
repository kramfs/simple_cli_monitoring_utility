FROM python:slim

# Set app working directory
WORKDIR /app

# Install app dependencies
COPY src/requirements.txt ./

RUN pip install -r requirements.txt

# Use a non-privilege user
USER nobody

# Bundle app source
COPY src/ /app