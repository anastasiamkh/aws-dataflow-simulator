# Use the official Python 3.11 slim base image
FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc libpq-dev && pip install --upgrade pip

# Set the working directory
WORKDIR /app
ENV PYTHONPATH=/app

# Install Poetry
RUN pip install poetry

# Copy Poetry configuration files
COPY . /app
RUN chmod +x /app

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main \
    && poetry run pip install -e .

EXPOSE 80
# Command to run your Python script
ENTRYPOINT ["poetry", "run"]
CMD ["dataflowsim", "flow", "stream"]
