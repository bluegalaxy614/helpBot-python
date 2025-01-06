FROM python:3.12-slim AS poetry

# Upgrade pip and install Poetry
RUN pip install --upgrade pip && pip install poetry

# Install the Poetry Export Plugin
RUN poetry self add poetry-plugin-export

# Set the working directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --without-hashes --output requirements.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Copy the exported requirements from the previous stage
COPY --from=poetry /app/requirements.txt .

# Install runtime dependencies
RUN pip install -r requirements.txt

# Copy the project files to the container
COPY . .

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
