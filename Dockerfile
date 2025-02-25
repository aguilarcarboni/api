# Use an official Python runtime as the base image
FROM python:3.9-slim

# Add labels for metadata
LABEL maintainer="aguilarcarboni"
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
RUN mkdir -p /app/cache/websites
RUN mkdir -p /app/cache/tv

# Create volume mount points
VOLUME /app/src/db
VOLUME /app/cache

# Copy the application code
COPY . .

# Make run script executable
RUN chmod +x run.sh

# Authentication
ARG JWT_SECRET_KEY
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Database
ARG DATABASE_URL
ENV DATABASE_URL=${DATABASE_URL}

# Google Services
ARG GOOGLE_TOKEN
ARG GOOGLE_REFRESH_TOKEN
ARG GOOGLE_TOKEN_URI
ARG GOOGLE_CLIENT_ID
ARG GOOGLE_CLIENT_SECRET
ENV GOOGLE_TOKEN=${GOOGLE_TOKEN}
ENV GOOGLE_REFRESH_TOKEN=${GOOGLE_REFRESH_TOKEN}
ENV GOOGLE_TOKEN_URI=${GOOGLE_TOKEN_URI}
ENV GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
ENV GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}

# Home Assistant
ARG HOME_ASSISTANT_URL
ENV HOME_ASSISTANT_URL=${HOME_ASSISTANT_URL}

# API
ARG PORT
ENV PORT=${PORT}
EXPOSE ${PORT}

ENTRYPOINT ["./run.sh"]