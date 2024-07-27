FROM python:slim

LABEL org.opencontainers.image.authors=""
LABEL description="A utility to interact with the service discovery API and allows to efficiently monitor deployed resources."

# Set app working directory
WORKDIR /app

# Install app dependencies
COPY src/requirements.txt ./

RUN pip install -r requirements.txt

# Use a non-privilege user
USER nobody

# Bundle app source
COPY src/ /app