# Deploy Directory

This directory contains all deployment-related files for the STAX application.

## 🐳 Docker Commands

### Development
```bash
# Start with logs
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down
```

### Production
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Stop production services
docker-compose -f docker-compose.prod.yml down
```

## 📁 Files in this directory

- `Dockerfile*` - Docker build configurations
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `nginx.conf` - Nginx configuration
- `azure-pipelines.yml` - CI/CD pipeline
- `docker-entrypoint.sh` - Container entry point script

## 🔧 Path References

All paths in docker-compose files are relative to the parent directory:
- `../config/` - Configuration files
- `../logs/` - Log files
- `../snapshots/` - Snapshot files
- `../src/` - Source code