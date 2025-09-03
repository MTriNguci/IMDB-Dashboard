# Use Python 3.9 slim image as base
FROM python:3.9-slim-bullseye


# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wkhtmltopdf \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir openpyxl

# Copy application code and data
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8050

# Set environment variables
ENV PYTHONPATH=/app
ENV DASH_DEBUG=False

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/_dash-dependencies || exit 1

# Create startup script
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 &\nexport DISPLAY=:99\npython app.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
