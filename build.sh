#!/bin/bash

# Create necessary directories
mkdir -p data/codebase
mkdir -p data/migrations/users
mkdir -p data/migrations/haspro_app
mkdir -p data/db

cp -r haspro/ data/codebase/

# Clean up __pycache__ directories
find data/codebase -type d -name __pycache__ -exec rm -rf {} +

printf "Building helper Docker images...\n"

# Build the Docker image for the Python base
docker build -t haspro/helper_python:latest -f docker/helper_python .

# Build the Docker image for the Node base
docker build -t haspro/helper_node:latest -f docker/helper_node .

# create a static directory
mkdir -p data/staticfiles

printf "Collecting static files...\n"
# Collect static files using the Python base image
docker run --rm \
    -v "$(pwd)/data/staticfiles:/app/staticfiles" \
    -e STATIC_ROOT=/app/staticfiles \
    haspro/helper_python:latest \
    /bin/bash -c "python haspro/manage.py collectstatic --noinput"

printf "Minifying static files...\n"
# Minify JavaScript and CSS files using the Node base image
docker run --rm \
    -v "$(pwd)/data/staticfiles:/app/staticfiles" \
    haspro/helper_node:latest \
    /bin/bash -c "find /app/staticfiles -name "*.js" -exec terser {} -c -m -o {} \;"
docker run --rm \
    -v "$(pwd)/data/staticfiles:/app/staticfiles" \
    haspro/helper_node:latest \
    /bin/bash -c "find /app/staticfiles -name "*.css" -exec cleancss -o {} {} \;"

printf "Minifying making migrations...\n"
# Make migrations using the Python base image
docker run --rm \
    -v "$(pwd)/data/migrations/users:/app/haspro/users/migrations" \
    -v "$(pwd)/data/migrations/haspro_app:/app/haspro/haspro_app/migrations" \
    haspro/helper_python:latest \
    /bin/bash -c "python haspro/manage.py makemigrations users"


docker run --rm \
    -v "$(pwd)/data/migrations/users:/app/haspro/users/migrations" \
    -v "$(pwd)/data/migrations/haspro_app:/app/haspro/haspro_app/migrations" \
    haspro/helper_python:latest \
    /bin/bash -c "\
        python haspro/manage.py makemigrations users \
        && python haspro/manage.py makemigrations haspro_app"

printf "Migrating the database...\n"
# Migarate the database using the Python base image
docker run --rm \
    -v "$(pwd)/data/migrations/users:/app/haspro/users/migrations" \
    -v "$(pwd)/data/migrations/haspro_app:/app/haspro/haspro_app/migrations" \
    -v "$(pwd)/data/db:/app/data" \
    -e DATABASE_NAME=/app/data/db.sqlite3 \
    haspro/helper_python:latest \
    /bin/bash -c "python haspro/manage.py migrate --noinput"

printf "Minifying templates...\n"
docker run --rm \
    -v "$(pwd)/data/codebase/haspro:/app/haspro/" \
    -v "$(pwd)/scripts:/app/scripts" \
    -e TEMPLATE_DIR=/app/haspro/haspro_app/templates \
    haspro/helper_python:latest \
    /bin/bash -c "python scripts/minify_templates.py"


printf "Building the production image...\n"
# Build the production image
docker build -t haspro/${ENV}:latest -f docker/production .