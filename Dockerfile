# Use an official Python runtime as the base image
FROM python:3.9-slim

# Add labels for metadata
LABEL maintainer="aguilarcarboni"
LABEL name="laserfocus-api"
LABEL version="1.0"
LABEL description="LaserFocus API container"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:laserfocus"]