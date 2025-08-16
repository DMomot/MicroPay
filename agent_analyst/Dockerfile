FROM python:3.11-slim

# Install system dependencies for package compilation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set environment variables
ENV FORCE_HTTPS="true"
ENV BASE_URL="https://blockchain-analyst.up.railway.app"

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY blockchain_analyst/ ./blockchain_analyst/

# Install the package
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8080

# Default command (can be overridden)
CMD ["python", "-m", "blockchain_analyst.x402_server"]
