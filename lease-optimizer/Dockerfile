FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Sync project dependencies
RUN UV_DEFAULT_INDEX=https://pypi.org/simple uv sync --frozen --no-dev

# Expose Cloud Run port
EXPOSE 8080

# Command to run Streamlit
CMD ["uv", "run", "streamlit", "run", "frontend/streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]
