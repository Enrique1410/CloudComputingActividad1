# Base stage: Common setup for all environments
FROM tiangolo/uvicorn-gunicorn:python3.10 AS carlemany-backend-base

RUN pip install --upgrade pip

COPY requirements/base.txt /tmp/requirements/
RUN pip install -r /tmp/requirements/base.txt

RUN mkdir /carlemany-backend
WORKDIR /carlemany-backend
COPY . ./

# Builder stage: Optional, for future scalability (e.g., compiling assets)
FROM carlemany-backend-base AS carlemany-backend-builder
# Add build-specific steps here if needed (e.g., installing build tools)
# For now, it’s a placeholder

# Development stage: Tools for local dev
FROM carlemany-backend-base AS carlemany-backend-dev
COPY requirements/dev.txt /tmp/requirements/
RUN pip install -r /tmp/requirements/dev.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "info", "--lifespan", "on"]

# Test stage: Isolated testing environment
FROM carlemany-backend-base AS carlemany-backend-test
COPY requirements/dev.txt /tmp/requirements/
RUN pip install -r /tmp/requirements/dev.txt
CMD ["pytest", "--maxfail=10"]

# Production stage: Optimized for deployment
FROM carlemany-backend-base AS carlemany-backend-prod
COPY requirements/prod.txt /tmp/requirements/
RUN pip install -r /tmp/requirements/prod.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "error", "--lifespan", "on"]