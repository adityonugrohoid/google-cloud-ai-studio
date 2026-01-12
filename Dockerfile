FROM python:3.12-slim

# Set working directory
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy application files
COPY pyproject.toml .
COPY app.py .

# Install dependencies
# Using --system to install into the system python environment (no venv needed in container)
RUN uv pip install --system .

# Expose the Streamlit port
EXPOSE 8080

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
