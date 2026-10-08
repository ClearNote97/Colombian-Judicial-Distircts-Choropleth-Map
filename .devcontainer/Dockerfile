# This Dockerfile is used for the development container in VS Code Remote Containers.
# It sets up a Python environment with the necessary tools for development.
FROM python:3.14.5-slim-bookworm

# Set the working directory in the container
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages and clean up apt cache to reduce image size.
#   build-essential, ca-certificates  -> template baseline
#   ghostscript                       -> required by camelot (PDF table extraction)
#   libgdal-dev, libgeos-dev,
#   libproj-dev, gdal-bin             -> system libs so the geospatial stack
#                                        (fiona/pyogrio/shapely/pyproj) can build
#                                        from source if no wheels exist for the
#                                        Python version (fallback to source build)
#   libglib2.0-0                      -> runtime lib imported by opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    ghostscript \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Help source builds of fiona/pyogrio find GDAL headers/config when wheels are absent.
ENV GDAL_CONFIG=/usr/bin/gdal-config

# Install uv, a Python package manager, to manage dependencies in the development environment
COPY --from=ghcr.io/astral-sh/uv:0.11.13 /uv /uvx /bin/
