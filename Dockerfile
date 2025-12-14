# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (wget, gnupg, curl, unzip)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    --no-install-recommends

# --- INSTALL GOOGLE CHROME ---
# Download and install the latest stable Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# --- INSTALL PYTHON DEPENDENCIES ---
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the test code into the container
COPY . /app

# Command to run the tests
CMD ["python", "test_automation.py"]
