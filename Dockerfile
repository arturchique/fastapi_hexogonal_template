FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY src /app/src
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache
RUN ls -la

# Run the application.
CMD ["uv", "run", "uvicorn", "src.server:app", "--port", "8088", "--host", "0.0.0.0"]
