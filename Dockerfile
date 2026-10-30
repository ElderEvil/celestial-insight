# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput --clear && python manage.py seed_demo && python manage.py loaddata admin_interface_theme_bootstrap.json && (python manage.py createsuperuser --noinput || echo 'superuser already present') && uvicorn celestial_insight.asgi:application --host 0.0.0.0 --port 9090"]
