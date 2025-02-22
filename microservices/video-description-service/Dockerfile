FROM python:3.11-slim

# Install curl for downloading Ollama
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -L https://ollama.ai/install.sh | sh

# Set up the Python application
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose the FastAPI port
EXPOSE 5000

# Create a startup script
COPY <<EOF /app/start.sh
#!/bin/bash
# Start Ollama in the background
ollama serve &
# Wait for Ollama to be ready
sleep 5
# Pull the required model
ollama pull llama3.2:1b
# Start the FastAPI application
uvicorn app:app --host 0.0.0.0 --port 5000
EOF

RUN chmod +x /app/start.sh

# Set the startup command
CMD ["/app/start.sh"] 