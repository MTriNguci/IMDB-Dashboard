# IMDB Dashboard - Docker Setup

This document explains how to run the IMDB Dashboard application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. Navigate to the project directory:
   ```bash
   cd IMDB-Dashboard
   ```

2. Build and run the application:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Open your web browser and go to: `http://localhost:8050`
   - The dashboard should be accessible and fully functional
   - Use the "Export Data" button to download all chart data as Excel file with embedded charts
   - Use the "Export PDF" button to download the entire dashboard as PDF using screenshots

4. To stop the application:
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker directly

1. Build the Docker image:
   ```bash
   docker build -t imdb-dashboard .
   ```

2. Run the container:
   ```bash
   docker run -p 8050:8050 imdb-dashboard
   ```

3. Access the application at `http://localhost:8050`

## Features

- **Automatic restart**: The container will restart automatically unless manually stopped
- **Health checks**: Built-in health monitoring
- **Volume mounting**: Data files are mounted as volumes for easy updates
- **Security**: Runs as a non-root user inside the container
- **Data Export**: Export all chart data to Excel file with multiple sheets and embedded charts
- **PDF Export**: Export entire dashboard as PDF using screenshots for accurate representation

## Troubleshooting

### Port already in use
If port 8050 is already in use, you can change it in the `docker-compose.yml` file:
```yaml
ports:
  - "8080:8050"  # Change 8080 to any available port
```

### Build issues
If you encounter build issues, try:
```bash
docker-compose build --no-cache
```

### Data file updates
The data files are mounted as volumes, so you can update them without rebuilding the container. Just restart the service:
```bash
docker-compose restart
```

## Container Management

- View logs: `docker-compose logs -f`
- Stop services: `docker-compose down`
- Remove containers and images: `docker-compose down --rmi all`
- View running containers: `docker ps`

## Environment Variables

You can customize the application by setting environment variables in the `docker-compose.yml` file:

- `DASH_DEBUG`: Set to `True` for debug mode (default: `False`)
- `PYTHONPATH`: Python path (default: `/app`)
