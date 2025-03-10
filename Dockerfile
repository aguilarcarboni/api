# Use an official Python runtime as the base image
FROM python:3.9-slim

# Add labels for metadata
LABEL maintainer="laserfocus"
LABEL name="laserfocus-api"
LABEL version="1.0"
LABEL description=""

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for persistent storage
RUN mkdir -p /app/src/db
RUN mkdir -p /app/cache

# Create volume mount points
VOLUME /app/src/db
VOLUME /app/cache

# Copy the application code
COPY . .

# Make run script executable
RUN chmod +x run.sh

# Set the default environment variables
ARG JWT_SECRET_KEY
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}

ARG AUTHENTICATION_TOKEN
ENV AUTHENTICATION_TOKEN=${AUTHENTICATION_TOKEN}

ARG PORT
ENV PORT=${PORT}

EXPOSE ${PORT}

ENTRYPOINT ["./run.sh"]