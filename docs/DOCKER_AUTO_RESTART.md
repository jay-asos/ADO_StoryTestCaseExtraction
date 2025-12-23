# Docker Auto-Restart Feature

## Overview
When configuration changes are saved via the UI Dashboard, the system automatically detects if it's running in a Docker container and triggers a graceful restart to apply the new environment variables.

## How It Works

### Detection
The system checks if it's running in Docker using two methods:
1. Checking for `/.dockerenv` file (present in Docker containers)
2. Checking the `RUNNING_IN_DOCKER` environment variable

### Restart Process
When a configuration save is triggered via the **Save Configuration** button:

1. Configuration is updated in both `.env` files (root and `config/`)
2. Configuration is saved to `monitor_config.json`
3. System detects Docker environment
4. Creates a restart marker file at `/tmp/restart_required`
5. Schedules a graceful shutdown after 2 seconds (to allow response to return)
6. Sends SIGTERM signal to the process
7. Docker automatically restarts the container due to `restart: unless-stopped` policy
8. Container loads new environment variables on startup

### User Experience
- UI displays message: "Configuration updated successfully. Docker container will restart to apply changes."
- Response includes `"docker_restart": true` flag
- Container restarts within 2-3 seconds
- Services resume with new configuration

### Local Development
When running locally (not in Docker):
- No restart is triggered
- User sees: "Configuration updated successfully"
- Manual restart required if environment variable changes need to be applied

## Configuration Files

### docker-compose.yml
```yaml
environment:
  - RUNNING_IN_DOCKER=true

restart: unless-stopped
```

### Mounted Volumes
Both `.env` files are mounted as volumes to persist UI changes:
```yaml
volumes:
  - ../config/.env:/app/config/.env
  - ../.env:/app/.env
```

## API Response

### Success with Docker Restart
```json
{
  "success": true,
  "message": "Configuration updated successfully. Docker container will restart to apply changes.",
  "docker_restart": true,
  "changes_made": {
    "check_interval_minutes": {"old": 5, "new": 10},
    "env_REQUIREMENT_TYPE": {"old": "Epic", "new": "Feature"}
  }
}
```

### Success without Docker (Local)
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "changes_made": {
    "check_interval_minutes": {"old": 5, "new": 10}
  }
}
```

## Troubleshooting

### Container Doesn't Restart
1. Check if `RUNNING_IN_DOCKER=true` is set in docker-compose.yml
2. Verify `restart: unless-stopped` policy is configured
3. Check container logs: `docker logs stax-app`

### Configuration Not Applied After Restart
1. Verify `.env` files are mounted as volumes in docker-compose.yml
2. Check that both root and config `.env` files are updated
3. Restart manually: `docker-compose restart`

### Manual Restart
If auto-restart fails, restart manually:
```bash
cd deploy
docker-compose restart
```

## Benefits
- ✅ Seamless configuration updates in production
- ✅ No manual intervention required
- ✅ Environment variables reload automatically
- ✅ Zero downtime (2-3 second restart)
- ✅ User-friendly experience
