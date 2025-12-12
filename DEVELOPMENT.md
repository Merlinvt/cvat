# CVAT Development Setup Guide

This guide explains how to set up and run CVAT for local development, including the custom `bbox_keypoint` annotation type.

## Prerequisites

Before starting, ensure you have installed:

1. **Docker Desktop** - [Install Docker](https://docs.docker.com/get-docker/)
2. **Node.js** (v18 or higher) - [Install Node.js](https://nodejs.org/)
3. **Git** - For cloning the repository

Verify installations:
```bash
docker --version
node --version
npm --version
```

## Quick Start

### 1. Clone and Navigate to Repository
```bash
cd /path/to/cvat
```

### 2. Install Node Dependencies
```bash
npm install --legacy-peer-deps
```

**Note:** The `--legacy-peer-deps` flag is required due to peer dependency conflicts between eslint versions.

### 3. Start Docker Backend
```bash
docker compose up -d
```

This starts the following containers:
- `cvat_server` - Main Django backend (accessible via Traefik on port 8080)
- `cvat_db` - PostgreSQL database
- `cvat_redis_inmem` / `cvat_redis_ondisk` - Redis instances
- `cvat_worker_*` - Background workers for import/export/annotation tasks
- `traefik` - Reverse proxy

Wait for all containers to be healthy:
```bash
docker compose ps
```

### 4. Create Admin User (First Time Only)
```bash
docker exec -it cvat_server bash -ic 'python3 manage.py createsuperuser'
```

### 5. Start Frontend Dev Server
```bash
CVAT_UI_PORT=3001 npm run start:cvat-ui -- --env API_URL=http://localhost:8080
```

**Why port 3001?** Port 3000 conflicts with macOS AirTunes/AirPlay Receiver.

### 6. Access the Application
Open http://localhost:3001 in your browser and log in with your admin credentials.

## Architecture Overview

```
Browser (localhost:3001)
    |
    v
Webpack Dev Server (port 3001)
    |
    +-- Static files: served from cvat-ui (with hot reload)
    |
    +-- /api/* requests: proxied to localhost:8080
                |
                v
          Traefik (port 8080)
                |
                v
          cvat_server (Docker)
                |
                +-- cvat_db (PostgreSQL)
                +-- cvat_redis_* (Redis)
                +-- cvat_worker_* (Background tasks)
```

## Development Workflow

### Frontend Changes (TypeScript/React)

Files in `cvat-ui/`, `cvat-canvas/`, `cvat-core/` are hot-reloaded automatically.

For significant changes (e.g., new exports, interface changes):
```bash
# Rebuild dependent packages
npm run build --workspace=cvat-core
npm run build --workspace=cvat-canvas

# Hard refresh browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows/Linux)
```

### Backend Changes (Python)

**For volume-mounted files** (see docker-compose.yml volumes section):
```bash
# Just restart the server
docker compose restart cvat_server

# For worker changes (e.g., export functionality)
docker compose restart cvat_worker_export
```

**For non-mounted files** - Rebuild the image:
```bash
docker compose build --no-cache cvat_server
docker compose up -d --force-recreate cvat_server
```

### Current Volume Mounts (docker-compose.yml)

The following files are mounted for live development:
- `./cvat/settings/` - Django settings
- `./cvat/apps/engine/models.py` - Database models
- `./cvat/apps/engine/serializers.py` - API serializers
- `./cvat/apps/dataset_manager/formats/cvat.py` - CVAT export format

To add more files for live editing, add them to the `volumes` section in `docker-compose.yml`.

## Custom bbox_keypoint Shape Type

This fork includes a custom annotation type: `bbox_keypoint` - a bounding box with an attached keypoint.

### Data Format
6 values: `[xtl, ytl, xbr, ybr, kx, ky]`
- `xtl, ytl` - Top-left corner of bounding box
- `xbr, ybr` - Bottom-right corner of bounding box
- `kx, ky` - Keypoint coordinates (independent of bbox)

### Usage
1. Create a label with type `bbox_keypoint`
2. Select the draw tool and click 3 times:
   - Click 1: First corner of bbox
   - Click 2: Opposite corner of bbox
   - Click 3: Keypoint location

### Editing Behavior
- The keypoint can be moved independently of the bounding box
- Moving/resizing the bbox does NOT move the keypoint
- Each component (bbox, keypoint) can be edited separately

### Export
Use **"CVAT for images 1.1"** format for export. Example output:
```xml
<bbox_keypoint label="weed" xtl="535.53" ytl="583.40" xbr="675.96" ybr="711.06" kx="595.53" ky="647.23" />
```

## Troubleshooting

### "CSRF Failed" Error
Ensure `CSRF_TRUSTED_ORIGINS: http://localhost:3001` is set in docker-compose.yml under cvat_server environment, then restart:
```bash
docker compose restart cvat_server
```

### "Cannot GET /" or Server Not Responding
- Verify webpack dev server is running: `lsof -i :3001`
- Check you used the full command with `--env API_URL=http://localhost:8080`

### Backend Not Recognizing New Code
- Check if the file is volume-mounted in docker-compose.yml
- If not mounted, rebuild: `docker compose build --no-cache cvat_server`
- If mounted, restart: `docker compose restart cvat_server`

### Export Fails with "Unknown Shape Type"
The export worker needs the updated code too:
```bash
docker compose restart cvat_worker_export
```

### Port 3000 Already in Use (macOS)
Use port 3001 instead:
```bash
CVAT_UI_PORT=3001 npm run start:cvat-ui -- --env API_URL=http://localhost:8080
```

Or disable AirPlay Receiver: System Preferences > General > AirDrop & Handoff > AirPlay Receiver (off)

## Stopping the Environment

```bash
# Stop frontend dev server
Ctrl+C

# Stop Docker containers
docker compose down

# Stop and remove volumes (WARNING: deletes all data)
docker compose down -v
```

## Useful Commands

```bash
# View server logs
docker logs cvat_server -f

# View worker logs
docker logs cvat_worker_export -f

# Enter server container
docker exec -it cvat_server bash

# Run Django management commands
docker exec -it cvat_server python3 manage.py <command>

# Check container status
docker compose ps
```
