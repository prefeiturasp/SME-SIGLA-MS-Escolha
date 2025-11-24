# Use Python 3.12.9 slim image as base
FROM python:3.12.9-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ADD . /code
WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    apt-get install libpq-dev -y && \
    python -m pip --no-cache install -U pip && \
  #    python -m pip --no-cache install Cython && \
  #    python -m pip --no-cache install numpy && \
  python -m pip --no-cache install -r requirements/production.txt


# Expose port
EXPOSE 8001
