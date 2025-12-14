# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# We need gnupg to handle the keys manually since apt-key is gone
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    --no-install-recommends

# --- FIX: INSTALL GOOGLE CHROME (New Way) ---
# 1. Download key -> Convert to gpg -> Save in keyrings
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg && \
# 2. Add repo using the signed-by tag
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
# 3. Install Chrome
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
