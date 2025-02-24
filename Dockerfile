# ---------------------------------------------
# Base Stage: Install Poetry and System Setup
# ---------------------------------------------
FROM python:3.13-alpine3.21 AS base

# Setting up work directory
WORKDIR /home/tiqets
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml poetry.lock ./
COPY README.md ./

RUN pip3 install --user poetry==1.8.5

# ---------------------------------------------
# Build Stage: Install All Dependencies, Build the Package
# ---------------------------------------------
FROM base AS builder

WORKDIR /home/tiqets

# Copying the source code
COPY vouchers_cli vouchers_cli

# Install only production dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --without dev,test --no-interaction --no-ansi

# Building the package (this will create the dist/ folder and requirements.txt)
RUN poetry build
RUN poetry export --without dev,test --without-hashes -f requirements.txt > requirements.txt

# ---------------------------------------------
# Production Stage: Minimal Python Environment
# ---------------------------------------------
FROM python:3.13-alpine3.21 AS production

# Setting up work directory
WORKDIR /home/tiqets

# Copy the built package and requirements.txt from the builder stage
COPY --from=builder /home/tiqets/dist /home/tiqets/dist
COPY --from=builder /home/tiqets/requirements.txt /home/tiqets/requirements.txt

# Install only production dependencies
RUN pip install --no-cache-dir -r /home/tiqets/requirements.txt
RUN pip install --no-cache-dir /home/tiqets/dist/*.whl

# Expose the production environment variables
ENV PYTHONUNBUFFERED=1

# Default production command
ENTRYPOINT ["tiqets-vouchers"]

# ---------------------------------------------
# Development Stage: Install Dev Dependencies
# ---------------------------------------------
FROM base AS development

RUN apk add make

WORKDIR /home/tiqets

# Copy the entire project
COPY . .

# Install all dependencies including dev and test
RUN poetry config virtualenvs.create false \
    && poetry install --with dev,test --no-interaction --no-ansi

# Expose dev environment variables
ENV PYTHONUNBUFFERED=1